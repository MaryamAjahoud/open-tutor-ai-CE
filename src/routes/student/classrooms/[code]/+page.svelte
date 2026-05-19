<script lang="ts">
	import { page } from '$app/stores';
	import { onMount, getContext } from 'svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let assignments = [];
	let loading = true;
	let error = '';
	let classCode = '';

	async function fetchAssignments() {
		loading = true;
		error = '';
		classCode = $page.params.code;
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/${classCode}/assignments`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) {
				assignments = await res.json();
			} else {
				const data = await res.json().catch(() => ({}));
				error = data.detail || 'Could not load assignments';
			}
		} catch (e) {
			error = 'Connection error';
			console.error(e);
		}
		loading = false;
	}

	function getTimeLeft(dueDate, dueTime) {
		const due = new Date(`${dueDate}T${dueTime || '23:59'}`);
		const diff = due.getTime() - Date.now();
		if (diff < 0) return { text: 'Overdue', urgent: true };
		const days = Math.floor(diff / 86400000);
		const hours = Math.floor((diff % 86400000) / 3600000);
		if (days > 0) return { text: `${days}d ${hours}h left`, urgent: days <= 1 };
		if (hours > 0) return { text: `${hours}h left`, urgent: true };
		return { text: 'Due soon', urgent: true };
	}

	function formatDueDate(date, time) {
		const d = new Date(`${date}T${time || '23:59'}`);
		return d.toLocaleDateString('fr-FR', { weekday: 'short', month: 'short', day: 'numeric' }) + ' à ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
	}

	onMount(() => fetchAssignments());
</script>

<div class="max-w-4xl mx-auto">
	<div class="flex items-center gap-3 mb-8">
		<a href="/student/classrooms" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors">
			<svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
		</a>
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">{$i18n.t('Class Assignments')}</h1>
			<p class="text-sm text-gray-500 font-mono">{$i18n.t('Code')}: {classCode}</p>
		</div>
	</div>

	{#if loading}
		<div class="space-y-4 animate-pulse">
			{#each Array(3) as _}<div class="h-40 bg-gray-200 dark:bg-gray-700 rounded-3xl"></div>{/each}
		</div>
	{:else if error}
		<div class="bg-white dark:bg-gray-800 rounded-3xl border border-rose-200 dark:border-rose-800/30 p-12 text-center">
			<div class="text-4xl mb-3">⚠️</div>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{error}</h3>
			<button on:click={fetchAssignments} class="mt-4 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all">{$i18n.t('Try Again')}</button>
		</div>
	{:else if assignments.length === 0}
		<div class="bg-white dark:bg-gray-800 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700 p-16 text-center">
			<div class="text-5xl mb-4">📋</div>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{$i18n.t('No assignments yet')}</h3>
			<p class="text-gray-500 text-sm">{$i18n.t('Your teacher hasn\'t posted any assignments yet.')}</p>
		</div>
	{:else}
		<div class="space-y-5">
			{#each assignments as a}
				{@const timeLeft = getTimeLeft(a.due_date, a.due_time)}
				<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300">
					<div class="h-1.5 bg-gradient-to-r {a.course_color || 'from-indigo-500 to-indigo-600'}"></div>
					<div class="p-7">
						<div class="flex items-start gap-5">
							<div class="w-14 h-14 bg-gradient-to-br {a.course_color || 'from-indigo-500 to-indigo-600'} rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md text-2xl">📋</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-3 mb-1 flex-wrap">
									{#if a.course}
										<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">{a.course}</span>
									{/if}
									<span class="px-2.5 py-0.5 text-xs font-bold rounded-full {timeLeft.urgent ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'}">
										{timeLeft.text}
									</span>
								</div>
								<h3 class="text-xl font-bold text-gray-900 dark:text-white">{a.title}</h3>
								{#if a.description}
									<p class="text-gray-500 dark:text-gray-400 text-sm mt-2 leading-relaxed">{a.description}</p>
								{/if}
								<div class="flex items-center gap-6 mt-4 flex-wrap">
									<span class="flex items-center gap-2 text-sm text-gray-500">
										<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
										{formatDueDate(a.due_date, a.due_time)}
									</span>
									<span class="flex items-center gap-2 text-sm font-bold text-gray-600 dark:text-gray-300">⭐ {a.points} pts</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
