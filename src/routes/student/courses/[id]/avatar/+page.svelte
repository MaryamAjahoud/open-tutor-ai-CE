<script lang="ts">
	import { onMount, tick, getContext } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { TUTOR_BASE_URL, TUTOR_API_BASE_URL } from '$lib/constants';
	import { user, settings } from '$lib/stores';
	import AvatarChat from '$lib/components/chat/AvatarChat.svelte';

	const i18n = getContext('i18n');

	// Route params & query
	$: knowledgeId = $page.params.id;
	$: courseName = decodeURIComponent($page.url.searchParams.get('name') || 'Cours');
	$: teacherName = decodeURIComponent($page.url.searchParams.get('teacher') || '');

	// State
	let input = '';
	let isLoading = false;
	let currentMessage = '';
	let speaking = false;
	let kbInfo: any = null;

	// Model selection
	let availableModels: { id: string; name: string }[] = [];
	let selectedModel = '';
	let modelsLoading = true;

	// Chat history for context
	let chatHistory: { role: string; content: string }[] = [];

	// Classroom settings
	let useClassroom = true;
	let classroomModel: 'default' | 'alternative' = 'default';

	onMount(async () => {
		const token = localStorage.token;

		// Force male avatar "The Scholar" for course avatar pages
		settings.update((s) => ({ ...s, selectedAvatarId: 'The Scholar' }));

		await loadModels(token);
		modelsLoading = false;

		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/knowledge/${knowledgeId}`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (res.ok) kbInfo = await res.json();
		} catch {}

		currentMessage = `Bonjour ! Je suis votre tuteur pour le cours "${courseName}". Posez-moi vos questions, je répondrai en me basant sur les documents du cours.`;
		speaking = true;
	});

	async function loadModels(token?: string) {
		const tok = token || localStorage.token;
		const headers = { Authorization: `Bearer ${tok}` };
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/available-models`, { headers });
			if (res.ok) {
				const list: any[] = await res.json();
				const models = list.filter((m) => m.id).map((m) => ({ id: m.id, name: m.name || m.id }));
				if (models.length > 0) { availableModels = models; selectedModel = models[0].id; return; }
			}
		} catch {}
		try {
			const res = await fetch(`${TUTOR_BASE_URL}/api/models`, { headers });
			if (res.ok) {
				const data = await res.json();
				const list: any[] = Array.isArray(data) ? data : (data?.data || []);
				const models = list.filter((m) => m.id).map((m) => ({ id: m.id, name: m.name || m.id }));
				if (models.length > 0) { availableModels = models; selectedModel = models[0].id; return; }
			}
		} catch {}
	}

	function extractResponseFromJson(content: string): string {
		if (typeof content !== 'string') return content || '';
		const m = content.match(/"response"\s*:\s*"([^"]+)"/);
		if (m?.[1]) return m[1];
		if (content.trim().startsWith('{') && content.trim().endsWith('}')) {
			try { const p = JSON.parse(content); if (p.response) return p.response; } catch {}
		}
		return content;
	}

	async function sendMessage() {
		const content = input.trim();
		if (!content || isLoading) return;
		if (!selectedModel) { currentMessage = "Aucun modèle IA disponible. Vérifiez qu'Ollama est démarré."; speaking = true; return; }

		input = '';
		isLoading = true;
		chatHistory = [...chatHistory, { role: 'user', content }];

		try {
			const body = {
				knowledge_id: knowledgeId,
				model: selectedModel,
				messages: chatHistory.slice(-10).map((m) => ({ role: m.role, content: m.content }))
			};

			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/rag-chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify(body)
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || `HTTP ${res.status}`);
			}

			const reader = res.body!.getReader();
			const decoder = new TextDecoder();
			let accumulated = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				const lines = decoder.decode(value, { stream: true }).split('\n').filter((l) => l.startsWith('data: '));
				for (const line of lines) {
					const data = line.slice(6).trim();
					if (data === '[DONE]') break;
					try {
						const delta = JSON.parse(data).choices?.[0]?.delta?.content;
						if (delta) accumulated += delta;
					} catch {}
				}
			}

			const finalText = extractResponseFromJson(accumulated);
			chatHistory = [...chatHistory, { role: 'assistant', content: finalText }];
			currentMessage = finalText;
			speaking = true;
		} catch (err: any) {
			currentMessage = `Erreur : ${err.message || 'Impossible de contacter le serveur.'}`;
			speaking = true;
		} finally {
			isLoading = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
	}
</script>

<svelte:head>
	<title>{courseName} — Avatar IA | OpenTutorAI</title>
</svelte:head>

<div class="flex flex-col h-full min-h-0 bg-gray-900 text-white">
	<!-- Top Bar -->
	<div class="flex-shrink-0 flex items-center gap-3 px-4 md:px-6 py-3 bg-gray-800/90 backdrop-blur-md border-b border-gray-700 shadow-sm z-10">
		<button on:click={() => goto('/student/courses')}
			class="p-2 rounded-xl hover:bg-gray-700 text-gray-400 transition-colors flex-shrink-0">
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
			</svg>
		</button>

		<div class="flex items-center gap-3 flex-1 min-w-0">
			<div class="w-9 h-9 flex-shrink-0 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-base shadow-md">🎓</div>
			<div class="min-w-0">
				<h1 class="font-bold text-white text-sm truncate">{courseName}</h1>
				{#if teacherName}<p class="text-xs text-gray-400 truncate">Prof. {teacherName}</p>{/if}
			</div>
		</div>

		<!-- Avatar mode badge -->
		<div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-purple-500/20 border border-purple-500/40 rounded-full text-purple-300 text-xs font-bold flex-shrink-0">
			<span class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
			Avatar · RAG · {kbInfo?.files?.length ?? '…'} doc{(kbInfo?.files?.length ?? 0) !== 1 ? 's' : ''}
		</div>

		<!-- Toggle classroom button -->
		<button on:click={() => useClassroom = !useClassroom}
			class="p-2 rounded-xl hover:bg-gray-700 text-gray-400 transition-colors flex-shrink-0" title="Basculer la salle de classe">
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
			</svg>
		</button>
	</div>

	<!-- No models warning -->
	{#if !modelsLoading && availableModels.length === 0}
		<div class="flex-shrink-0 flex items-center gap-3 px-5 py-3 bg-amber-900/30 border-b border-amber-700/40 text-amber-300 text-sm">
			<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
			<span class="flex-1">Aucun modèle IA disponible. Démarrez <strong>Ollama</strong> ou ajoutez une clé API.</span>
		</div>
	{/if}

	<!-- Avatar area -->
	<div class="flex-1 relative overflow-hidden">
		<AvatarChat
			className="w-full h-full"
			avatarOverride="The Scholar"
			{useClassroom}
			{classroomModel}
			{currentMessage}
			{speaking}
		/>
	</div>

	<!-- Input Bar -->
	<div class="flex-shrink-0 px-4 md:px-6 py-4 bg-gray-800/90 backdrop-blur-md border-t border-gray-700">
		<div class="max-w-4xl mx-auto">
			<div class="flex items-center gap-2 text-xs text-gray-500 mb-2 px-1">
				<svg class="w-3.5 h-3.5 flex-shrink-0 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
				</svg>
				<span>L'avatar répond à partir des documents de <strong class="text-purple-400">{courseName}</strong></span>
			</div>
			<div class="flex items-center gap-3">
				<input
					type="text"
					bind:value={input}
					on:keydown={handleKeydown}
					placeholder={availableModels.length === 0 ? 'Aucun modèle disponible…' : `Posez votre question sur ${courseName}…`}
					disabled={isLoading || availableModels.length === 0}
					class="flex-1 px-4 py-3 rounded-2xl bg-gray-700 border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all disabled:opacity-50 text-sm"
				/>
				<button
					on:click={sendMessage}
					disabled={!input.trim() || isLoading || availableModels.length === 0}
					class="flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center transition-all
						{input.trim() && !isLoading && availableModels.length > 0
							? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white shadow-md shadow-purple-500/30 hover:opacity-90 active:scale-95'
							: 'bg-gray-700 text-gray-500 cursor-not-allowed'}"
				>
					{#if isLoading}
						<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
					{:else}
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
					{/if}
				</button>
			</div>
			<p class="text-center text-xs text-gray-600 mt-2">Entrée pour envoyer</p>
		</div>
	</div>
</div>
