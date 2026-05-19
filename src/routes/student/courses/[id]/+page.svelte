<script lang="ts">
	import { onMount, tick, getContext } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { TUTOR_BASE_URL, TUTOR_API_BASE_URL } from '$lib/constants';
	import { user } from '$lib/stores';

	const i18n = getContext('i18n');

	// ── Route params & query ─────────────────────────────────────────────────
	$: knowledgeId = $page.params.id;
	$: courseName   = decodeURIComponent($page.url.searchParams.get('name') || 'Cours');
	$: teacherName  = decodeURIComponent($page.url.searchParams.get('teacher') || '');

	// ── State ────────────────────────────────────────────────────────────────
	type Message = { role: 'user' | 'assistant'; content: string; done?: boolean };
	type ModelItem = { id: string; name: string };

	let messages: Message[] = [];
	let input = '';
	let isLoading = false;
	let chatContainer: HTMLElement;
	let inputEl: HTMLTextAreaElement;
	let kbInfo: any = null;

	// Model selection — fetched directly from the API
	let availableModels: ModelItem[] = [];
	let selectedModel = '';
	let modelsLoading = true;
	let showModelPicker = false;

	const suggestedQuestions = [
		"Quels sont les points clés de ce cours ?",
		"Explique-moi les concepts fondamentaux",
		"Fais un résumé de ce document",
		"Quelles sont les définitions importantes ?",
		"Donne-moi des exemples concrets",
	];

	// ── Lifecycle ────────────────────────────────────────────────────────────
	onMount(async () => {
		const token = localStorage.token;

		// ① Fetch models from the OpenWebUI aggregated API (Ollama + OpenAI)
		await loadModels(token);
		modelsLoading = false;

		// ② Fetch KB metadata for the info pill
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/knowledge/${knowledgeId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (res.ok) kbInfo = await res.json();
		} catch { /* no-op */ }

		await tick();
		inputEl?.focus();
	});

	// ── Helpers ──────────────────────────────────────────────────────────────
	async function loadModels(token?: string) {
		const tok = token || localStorage.token;
		try {
			// Primary: /api/models aggregates Ollama + OpenAI + workspace models
			const res = await fetch(`${TUTOR_BASE_URL}/api/models`, {
				headers: { Authorization: `Bearer ${tok}` }
			});
			if (res.ok) {
				const data = await res.json();
				const list: any[] = Array.isArray(data) ? data : (data?.data || []);
				availableModels = list
					.filter((m: any) => m.id)
					.map((m: any) => ({ id: m.id, name: m.name || m.id }));
				if (availableModels.length > 0) selectedModel = availableModels[0].id;
			}
		} catch (e) {
			console.error('Failed to load models', e);
		}
		if (availableModels.length === 0) {
			// Fallback: workspace models endpoint
			try {
				const res2 = await fetch(`${TUTOR_API_BASE_URL}/models/`, {
					headers: { Authorization: `Bearer ${tok}` }
				});
				if (res2.ok) {
					const data2 = await res2.json();
					const list2: any[] = Array.isArray(data2) ? data2 : (data2?.data || []);
					availableModels = list2
						.filter((m: any) => m.id)
						.map((m: any) => ({ id: m.id, name: m.name || m.id }));
					if (availableModels.length > 0) selectedModel = availableModels[0].id;
				}
			} catch { /* no-op */ }
		}
	}

	async function retryLoadModels() {
		modelsLoading = true;
		await loadModels();
		modelsLoading = false;
	}

	async function scrollToBottom() {
		await tick();
		if (chatContainer) chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
	}

	function autoResize(el: HTMLTextAreaElement) {
		el.style.height = 'auto';
		el.style.height = Math.min(el.scrollHeight, 160) + 'px';
	}

	// ── Core: RAG chat ────────────────────────────────────────────────────────
	async function sendMessage(text?: string) {
		const content = (text ?? input).trim();
		if (!content || isLoading) return;

		if (!selectedModel) {
			alert('Aucun modèle IA disponible. Assurez-vous qu\'Ollama ou un LLM est configuré dans OpenWebUI.');
			return;
		}

		input = '';
		if (inputEl) inputEl.style.height = 'auto';

		messages = [...messages, { role: 'user', content }];
		await scrollToBottom();

		isLoading = true;
		const assistantIdx = messages.length;
		messages = [...messages, { role: 'assistant', content: '', done: false }];

		try {
			const body = {
				model: selectedModel,
				stream: true,
				messages: [
					{
						role: 'system',
						content: 'Tu es un assistant pédagogique expert. Réponds UNIQUEMENT en te basant sur les documents du cours fournis. Si l\'information ne figure pas dans les documents, dis-le clairement. Sois précis, pédagogique et encourage l\'apprentissage actif.'
					},
					...messages.slice(0, -1).slice(-8).map((m) => ({ role: m.role, content: m.content })),
				],
				files: [{ type: 'collection', id: knowledgeId }],
			};

			const res = await fetch(`${TUTOR_BASE_URL}/api/chat/completions`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify(body),
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || err.message || `HTTP ${res.status}`);
			}

			const reader = res.body!.getReader();
			const decoder = new TextDecoder();
			let accumulated = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				const lines = decoder.decode(value, { stream: true }).split('\n').filter(l => l.startsWith('data: '));
				for (const line of lines) {
					const data = line.slice(6).trim();
					if (data === '[DONE]') break;
					try {
						const delta = JSON.parse(data).choices?.[0]?.delta?.content;
						if (delta) {
							accumulated += delta;
							messages[assistantIdx] = { role: 'assistant', content: accumulated, done: false };
							messages = [...messages];
							await scrollToBottom();
						}
					} catch { /* skip */ }
				}
			}

			messages[assistantIdx] = { role: 'assistant', content: accumulated, done: true };
			messages = [...messages];

		} catch (err: any) {
			messages[assistantIdx] = {
				role: 'assistant',
				content: `❌ **Erreur** : ${err.message || 'Impossible de contacter le serveur.'}`,
				done: true,
			};
			messages = [...messages];
		} finally {
			isLoading = false;
			await scrollToBottom();
			await tick();
			inputEl?.focus();
		}
	}

	function clearChat() { messages = []; }

	function renderMarkdown(text: string): string {
		return text
			.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
			.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
			.replace(/\*(.+?)\*/g, '<em>$1</em>')
			.replace(/`(.+?)`/g, '<code class="inline-code">$1</code>')
			.replace(/^#{3}\s+(.+)$/gm, '<h3 class="md-h3">$1</h3>')
			.replace(/^#{2}\s+(.+)$/gm, '<h2 class="md-h2">$1</h2>')
			.replace(/^#{1}\s+(.+)$/gm, '<h1 class="md-h1">$1</h1>')
			.replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>')
			.replace(/(<li>.*<\/li>\n?)+/g, match => `<ul class="md-ul">${match}</ul>`)
			.replace(/\n\n/g, '</p><p class="md-p">')
			.replace(/\n/g, '<br/>')
			.replace(/^(.+)$/, '<p class="md-p">$1</p>');
	}
</script>

<svelte:head>
	<title>{courseName} — Chat IA | OpenTutorAI</title>
</svelte:head>

<div class="flex flex-col h-full min-h-0 bg-gradient-to-b from-[#F4F7FE] to-white dark:from-gray-900 dark:to-gray-900">

	<!-- ── Top Bar ─────────────────────────────────────────────────────────── -->
	<div class="flex-shrink-0 flex items-center gap-3 px-4 md:px-6 py-3 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 shadow-sm">
		<button on:click={() => goto('/student/courses')}
			class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors flex-shrink-0">
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
			</svg>
		</button>

		<!-- Course info -->
		<div class="flex items-center gap-3 flex-1 min-w-0">
			<div class="w-9 h-9 flex-shrink-0 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-base shadow-md">📖</div>
			<div class="min-w-0">
				<h1 class="font-bold text-gray-900 dark:text-white text-sm truncate">{courseName}</h1>
				{#if teacherName}<p class="text-xs text-gray-400 truncate">Prof. {teacherName}</p>{/if}
			</div>
		</div>

		<!-- Model selector -->
		<div class="relative flex-shrink-0">
			<button
				on:click={() => showModelPicker = !showModelPicker}
				disabled={modelsLoading || availableModels.length === 0}
				class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-semibold text-gray-600 dark:text-gray-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all disabled:opacity-40 max-w-[160px]"
			>
				{#if modelsLoading}
					<svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
					Chargement…
				{:else if availableModels.length === 0}
					⚠️ Aucun modèle
				{:else}
					<span class="truncate">{availableModels.find(m => m.id === selectedModel)?.name || selectedModel}</span>
					<svg class="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
				{/if}
			</button>

			{#if showModelPicker && availableModels.length > 0}
				<!-- click-outside -->
				<button class="fixed inset-0 z-10" on:click={() => showModelPicker = false} tabindex="-1" aria-hidden="true"></button>
				<div class="absolute right-0 top-10 z-20 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-xl overflow-hidden">
					<div class="px-3 py-2 border-b border-gray-100 dark:border-gray-700 text-xs font-bold text-gray-400 uppercase tracking-wider">Choisir le modèle</div>
					<ul class="max-h-60 overflow-y-auto py-1">
						{#each availableModels as m}
							<li>
								<button
									on:click={() => { selectedModel = m.id; showModelPicker = false; }}
									class="w-full text-left px-4 py-2.5 text-sm hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors flex items-center gap-2
										{selectedModel === m.id ? 'text-indigo-600 dark:text-indigo-400 font-semibold bg-indigo-50 dark:bg-indigo-900/20' : 'text-gray-700 dark:text-gray-300'}"
								>
									{#if selectedModel === m.id}
										<svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
									{:else}
										<span class="w-3.5 h-3.5 flex-shrink-0"></span>
									{/if}
									<span class="truncate">{m.name}</span>
								</button>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>

		<!-- RAG pill -->
		<div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/40 rounded-full text-indigo-700 dark:text-indigo-400 text-xs font-bold flex-shrink-0">
			<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
			RAG · {kbInfo?.files?.length ?? '…'} doc{(kbInfo?.files?.length ?? 0) !== 1 ? 's' : ''}
		</div>

		{#if messages.length > 0}
			<button on:click={clearChat} class="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-400 hover:text-rose-500 transition-colors flex-shrink-0" title="Effacer">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
				</svg>
			</button>
		{/if}
	</div>

	<!-- No models warning banner -->
	{#if !modelsLoading && availableModels.length === 0}
		<div class="flex-shrink-0 flex items-center gap-3 px-5 py-3 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800/40 text-amber-800 dark:text-amber-300 text-sm">
			<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
			<span class="flex-1">Aucun modèle IA disponible. Ajoutez une clé <strong>OpenAI</strong> dans le fichier <code class="bg-amber-100 dark:bg-amber-800/40 px-1 rounded">.env</code> ou démarrez <strong>Ollama</strong>.</span>
			<button on:click={retryLoadModels} class="flex-shrink-0 px-3 py-1.5 bg-amber-200 dark:bg-amber-700 hover:bg-amber-300 dark:hover:bg-amber-600 text-amber-900 dark:text-amber-100 rounded-lg text-xs font-semibold transition-colors">
				↺ Réessayer
			</button>
		</div>
	{/if}

	<!-- ── Chat area ──────────────────────────────────────────────────────── -->
	<div bind:this={chatContainer} class="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-6 scroll-smooth">
		{#if messages.length === 0}
			<div class="flex flex-col items-center justify-center h-full min-h-[360px] text-center px-4 py-12 animate-fade-in">
				<div class="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-4xl shadow-xl shadow-indigo-500/25 mb-6 animate-float">🎓</div>
				<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
					Posez vos questions sur <span class="text-indigo-600 dark:text-indigo-400">{courseName}</span>
				</h2>
				<p class="text-gray-500 dark:text-gray-400 text-sm max-w-md mb-8 leading-relaxed">
					L'IA a accès aux documents de votre professeur. Posez n'importe quelle question — elle répondra uniquement à partir du contenu du cours.
				</p>
				<div class="flex flex-wrap justify-center gap-2 max-w-xl">
					{#each suggestedQuestions as q}
						<button on:click={() => sendMessage(q)}
							class="px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl text-sm text-gray-700 dark:text-gray-300 hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-500 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 font-medium">
							{q}
						</button>
					{/each}
				</div>
			</div>
		{:else}
			{#each messages as msg}
				<div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'} gap-3 animate-slide-in">
					{#if msg.role === 'assistant'}
						<div class="w-8 h-8 flex-shrink-0 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-sm shadow-md mt-1">🎓</div>
					{/if}
					<div class="max-w-[85%] md:max-w-[70%] {msg.role === 'user'
						? 'bg-gradient-to-br from-indigo-600 to-blue-700 text-white rounded-3xl rounded-tr-lg shadow-lg shadow-indigo-500/20'
						: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 rounded-3xl rounded-tl-lg shadow-sm'} px-5 py-3.5">
						{#if msg.role === 'assistant' && !msg.done && msg.content === ''}
							<div class="flex items-center gap-1.5 py-1">
								<span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style="animation-delay:0ms"></span>
								<span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style="animation-delay:150ms"></span>
								<span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style="animation-delay:300ms"></span>
							</div>
						{:else if msg.role === 'assistant'}
							<div class="prose-content text-sm leading-relaxed">
								{@html renderMarkdown(msg.content)}
								{#if !msg.done}<span class="inline-block w-2 h-4 bg-indigo-500 animate-pulse ml-0.5 rounded-sm align-middle"></span>{/if}
							</div>
						{:else}
							<p class="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
						{/if}
					</div>
					{#if msg.role === 'user'}
						<div class="w-8 h-8 flex-shrink-0 rounded-xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm font-bold text-gray-600 dark:text-gray-300 mt-1">
							{$user?.name?.charAt(0)?.toUpperCase() || '?'}
						</div>
					{/if}
				</div>
			{/each}
		{/if}
	</div>

	<!-- ── Input Bar ───────────────────────────────────────────────────────── -->
	<div class="flex-shrink-0 px-4 md:px-6 py-4 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-t border-gray-200 dark:border-gray-800">
		<div class="max-w-4xl mx-auto">
			<div class="flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500 mb-3 px-1">
				<svg class="w-3.5 h-3.5 flex-shrink-0 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
				</svg>
				<span>Réponses basées sur les documents de <strong class="text-indigo-500 dark:text-indigo-400">{courseName}</strong></span>
			</div>
			<div class="flex items-end gap-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 focus-within:border-indigo-400 dark:focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/10 transition-all shadow-sm">
				<textarea
					bind:this={inputEl}
					bind:value={input}
					on:keydown={handleKeydown}
					on:input={(e) => autoResize(e.currentTarget)}
					placeholder={availableModels.length === 0 ? 'Aucun modèle disponible…' : 'Posez votre question sur ce cours…'}
					rows="1"
					disabled={isLoading || availableModels.length === 0}
					class="flex-1 resize-none bg-transparent border-none outline-none text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 leading-relaxed max-h-40 disabled:opacity-60"
				/>
				<button
					on:click={() => sendMessage()}
					disabled={!input.trim() || isLoading || availableModels.length === 0}
					class="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all
						{input.trim() && !isLoading && availableModels.length > 0
							? 'bg-gradient-to-br from-indigo-600 to-blue-700 text-white shadow-md shadow-indigo-500/30 hover:opacity-90 hover:-translate-y-0.5 active:scale-95'
							: 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'}"
				>
					{#if isLoading}
						<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
					{:else}
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
					{/if}
				</button>
			</div>
			<p class="text-center text-xs text-gray-300 dark:text-gray-600 mt-2">Entrée pour envoyer · Maj+Entrée pour nouvelle ligne</p>
		</div>
	</div>
</div>

<style>
	:global(.prose-content .md-p) { margin: 0.35rem 0; }
	:global(.prose-content .md-h1) { font-size: 1.15rem; font-weight: 700; margin: 0.75rem 0 0.35rem; }
	:global(.prose-content .md-h2) { font-size: 1.05rem; font-weight: 700; margin: 0.6rem 0 0.25rem; }
	:global(.prose-content .md-h3) { font-size: 0.95rem; font-weight: 600; margin: 0.5rem 0 0.2rem; color: #6366f1; }
	:global(.prose-content .md-ul) { list-style-type: disc; padding-left: 1.25rem; margin: 0.35rem 0; }
	:global(.prose-content li) { margin: 0.15rem 0; }
	:global(.prose-content .inline-code) {
		background: rgba(99,102,241,0.1); color: #6366f1;
		padding: 0.1em 0.4em; border-radius: 0.35rem;
		font-size: 0.85em; font-family: ui-monospace, monospace;
	}
	:global(.dark .prose-content .md-h3) { color: #a5b4fc; }
	:global(.dark .prose-content .inline-code) { background: rgba(99,102,241,0.15); color: #a5b4fc; }

	@keyframes fade-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
	@keyframes slide-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
	@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
	.animate-fade-in { animation: fade-in 0.5s ease forwards; }
	.animate-slide-in { animation: slide-in 0.3s ease forwards; }
	.animate-float { animation: float 3s ease-in-out infinite; }
</style>
