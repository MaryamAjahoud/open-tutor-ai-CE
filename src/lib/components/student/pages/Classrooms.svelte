<!-- Classrooms.svelte — Student joins & views teacher classrooms -->
<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let classrooms = [];
	let loading = true;
	let joining = false;
	let joinCode = '';
	let joinError = '';
	let joinSuccess = '';
	let showJoinForm = true;

	async function fetchClassrooms() {
		loading = true;
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/my-classrooms`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) classrooms = await res.json();
		} catch (e) { console.error(e); }
		loading = false;
	}

	async function joinClassroom() {
		if (!joinCode.trim()) return;
		joining = true;
		joinError = '';
		joinSuccess = '';
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/join-classroom`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify({ code: joinCode.trim().toUpperCase() })
			});
			const data = await res.json();
			if (res.ok) {
				joinSuccess = data.message || 'Inscription réussie !';
				joinCode = '';
				await fetchClassrooms();
				setTimeout(() => joinSuccess = '', 4000);
			} else {
				joinError = data.detail || 'Code invalide';
			}
		} catch (e) {
			joinError = 'Erreur de connexion';
			console.error(e);
		}
		joining = false;
	}

	onMount(() => fetchClassrooms());
</script>

<div class="max-w-4xl mx-auto space-y-8">
	<!-- Join Classroom Card -->
	<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
		<div class="h-2 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500"></div>
		<div class="p-8">
			<div class="flex items-center gap-4 mb-6">
				<div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center text-2xl shadow-lg">🔑</div>
				<div>
					<h2 class="text-xl font-bold text-gray-900 dark:text-white">{$i18n.t('Join a Class')}</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400">{$i18n.t('Enter the code given by your teacher')}</p>
				</div>
			</div>
			<div class="flex gap-3 flex-wrap">
				<input type="text" bind:value={joinCode} placeholder="Ex: AB3K9Z"
					maxlength="8"
					on:keydown={(e) => e.key === 'Enter' && joinClassroom()}
					class="flex-1 min-w-[200px] px-5 py-3.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-2xl text-lg font-mono font-bold tracking-[0.2em] uppercase text-center focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 dark:text-white placeholder-gray-400 transition-all" />
				<button on:click={joinClassroom} disabled={!joinCode.trim() || joining}
					class="px-8 py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-2xl shadow-lg shadow-indigo-600/20 transition-all hover:-translate-y-0.5 active:scale-95 flex items-center gap-2">
					{#if joining}
						<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
					{/if}
					{$i18n.t('Join')}
				</button>
			</div>
			{#if joinError}
				<div class="mt-4 px-4 py-3 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/30 rounded-xl text-sm text-rose-700 dark:text-rose-400 font-semibold flex items-center gap-2">
					<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
					{joinError}
				</div>
			{/if}
			{#if joinSuccess}
				<div class="mt-4 px-4 py-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/30 rounded-xl text-sm text-emerald-700 dark:text-emerald-400 font-semibold flex items-center gap-2">
					<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
					{joinSuccess}
				</div>
			{/if}
		</div>
	</div>

	<!-- My Classrooms -->
	<div>
		<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-5">{$i18n.t('My Classes')}</h2>
		{#if loading}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
				{#each Array(4) as _}
					<div class="h-44 bg-gray-200 dark:bg-gray-700 rounded-3xl animate-pulse"></div>
				{/each}
			</div>
		{:else if classrooms.length === 0}
			<div class="bg-white dark:bg-gray-800 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700 p-16 text-center">
				<div class="text-5xl mb-4">📚</div>
				<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{$i18n.t('No classes yet')}</h3>
				<p class="text-gray-500 text-sm">{$i18n.t('Enter a class code above to join your teacher\'s class.')}</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
				{#each classrooms as c, i}
					{@const colors = ['from-blue-500 to-indigo-600','from-purple-500 to-violet-600','from-emerald-500 to-teal-600','from-amber-500 to-orange-600','from-rose-500 to-pink-600','from-cyan-500 to-sky-600']}
					{@const color = colors[i % colors.length]}
					<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 group">
						<div class="h-20 bg-gradient-to-br {color} relative overflow-hidden">
							<div class="absolute inset-0 bg-black/10"></div>
							<div class="absolute bottom-3 left-5 text-white/80 text-xs font-mono font-bold tracking-wider">{c.class_code}</div>
							<div class="absolute top-3 right-3 bg-white/20 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-full">{c.assignment_count} {$i18n.t('assignments')}</div>
						</div>
						<div class="p-5">
							<div class="flex items-center gap-3 mb-3">
								<div class="w-10 h-10 bg-gradient-to-br {color} rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-sm">{c.teacher_name?.charAt(0)?.toUpperCase() || '?'}</div>
								<div>
									<h3 class="font-bold text-gray-900 dark:text-white text-sm">{c.teacher_name}</h3>
									{#if c.teacher_email}
										<p class="text-xs text-gray-400 truncate">{c.teacher_email}</p>
									{/if}
								</div>
							</div>
							{#if c.name}
								<p class="text-sm text-gray-600 dark:text-gray-400 mb-3">{c.name}</p>
							{/if}
							<a href="/student/classrooms/{c.class_code}" class="inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:gap-2.5 transition-all">
								{$i18n.t('View assignments')}
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
							</a>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
