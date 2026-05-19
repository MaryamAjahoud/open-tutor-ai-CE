<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	type SharedCourse = {
		knowledge_id: string;
		knowledge_name: string | null;
		shared_at: string | null;
		teacher_name?: string;
		classroom_name?: string;
		class_code?: string;
		file_count?: number;
		subject?: string;
	};

	let allCourses: SharedCourse[] = [];
	let loading = true;
	let error = '';

	const subjectColors = [
		'from-indigo-500 to-blue-600',
		'from-violet-500 to-purple-600',
		'from-emerald-500 to-teal-600',
		'from-amber-500 to-orange-500',
		'from-rose-500 to-pink-600',
		'from-cyan-500 to-sky-600',
	];

	const subjectIcons: Record<string, string> = {
		mathematics: '📊', science: '🔬', history: '🏛️',
		'computer-science': '💻', english: '📚', geography: '🌍',
		chemistry: '🧪', biology: '🌿', physics: '⚛️', other: '📖'
	};

	function getColorForId(id: string) {
		let hash = 0;
		for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) & 0xffffffff;
		return subjectColors[Math.abs(hash) % subjectColors.length];
	}

	async function fetchAllCourses() {
		loading = true;
		error = '';
		try {
			const token = localStorage.token;
			// Get all enrolled classrooms first
			const classRes = await fetch(`${TUTOR_API_BASE_URL}/teacher/my-classrooms`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!classRes.ok) throw new Error('Failed to load classrooms');
			const classrooms = await classRes.json();

			// For each classroom, fetch its shared courses
			const coursePromises = classrooms.map(async (c: any) => {
				try {
					const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/${c.class_code}/courses`, {
						headers: { Authorization: `Bearer ${token}` }
					});
					if (!res.ok) return [];
					const items = await res.json();
					return items.map((item: any) => ({
						...item,
						teacher_name: c.teacher_name,
						classroom_name: c.name,
						class_code: c.class_code,
					}));
				} catch { return []; }
			});

			const nested = await Promise.all(coursePromises);
			allCourses = nested.flat();
		} catch (e: any) {
			error = e.message || 'Erreur de chargement';
		}
		loading = false;
	}

	onMount(() => fetchAllCourses());
</script>

<svelte:head>
	<title>Mes Cours — OpenTutorAI</title>
</svelte:head>

<div class="max-w-5xl mx-auto space-y-8">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">{$i18n.t('My Courses')}</h1>
			<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
				{$i18n.t('Ask the AI questions about your teacher\'s course documents')}
			</p>
		</div>
		<div class="flex items-center gap-2 px-4 py-2 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/40 rounded-2xl text-indigo-700 dark:text-indigo-400 text-sm font-semibold">
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
			</svg>
			RAG Pedagogical Chat
		</div>
	</div>

	{#if loading}
		<!-- Skeleton loader -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each Array(6) as _}
				<div class="bg-white dark:bg-gray-800 rounded-3xl overflow-hidden animate-pulse shadow-sm">
					<div class="h-32 bg-gray-200 dark:bg-gray-700"></div>
					<div class="p-5 space-y-3">
						<div class="h-4 bg-gray-200 dark:bg-gray-700 rounded-lg w-3/4"></div>
						<div class="h-3 bg-gray-100 dark:bg-gray-800 rounded-lg w-1/2"></div>
						<div class="h-9 bg-gray-200 dark:bg-gray-700 rounded-xl w-full"></div>
					</div>
				</div>
			{/each}
		</div>

	{:else if error}
		<div class="bg-white dark:bg-gray-800 rounded-3xl border border-rose-200 dark:border-rose-800/30 p-12 text-center">
			<div class="text-5xl mb-4">⚠️</div>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{error}</h3>
			<button on:click={fetchAllCourses} class="mt-4 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all">
				{$i18n.t('Try Again')}
			</button>
		</div>

	{:else if allCourses.length === 0}
		<div class="bg-white dark:bg-gray-800 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700 p-16 text-center">
			<div class="w-20 h-20 bg-indigo-50 dark:bg-indigo-900/20 rounded-2xl flex items-center justify-center mx-auto mb-5 text-4xl">📚</div>
			<h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{$i18n.t('No courses available yet')}</h3>
			<p class="text-gray-500 dark:text-gray-400 text-sm max-w-sm mx-auto mb-4 leading-relaxed">
				{$i18n.t('To access course documents and chat with the AI, you need to:')}
			</p>
			<ol class="text-left max-w-xs mx-auto mb-6 space-y-2">
				<li class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
					<span class="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold mt-0.5">1</span>
					{$i18n.t('Join a classroom using your teacher\'s class code')}
				</li>
				<li class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
					<span class="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold mt-0.5">2</span>
					{$i18n.t('Wait for your teacher to upload course documents')}
				</li>
				<li class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
					<span class="flex-shrink-0 w-5 h-5 rounded-full bg-indigo-600 text-white text-xs flex items-center justify-center font-bold mt-0.5">3</span>
					{$i18n.t('Courses will appear here automatically')}
				</li>
			</ol>
			<a href="/student/classrooms" class="inline-flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
				{$i18n.t('My Classrooms')}
			</a>
		</div>


	{:else}
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each allCourses as course, i}
				{@const color = getColorForId(course.knowledge_id)}
				<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1.5 group flex flex-col">
					<!-- Gradient header -->
					<div class="h-32 bg-gradient-to-br {color} relative overflow-hidden flex-shrink-0">
						<div class="absolute inset-0 bg-black/10"></div>
						<div class="absolute top-3 right-3 text-4xl opacity-20">📖</div>
						<!-- RAG badge -->
						<div class="absolute top-3 left-3 flex items-center gap-1.5 bg-white/20 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-full">
							<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
							</svg>
							AI-Powered
						</div>
						<div class="absolute bottom-3 left-4 right-4">
							<p class="text-white/70 text-xs font-mono truncate">par {course.teacher_name || '?'}</p>
							<h3 class="text-white font-bold text-base line-clamp-1 mt-0.5">
								{course.knowledge_name || 'Cours sans titre'}
							</h3>
						</div>
					</div>

					<!-- Card body -->
					<div class="p-5 flex-1 flex flex-col gap-3">
						{#if course.classroom_name}
							<div class="flex items-center gap-2 text-xs text-gray-400">
								<svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
								</svg>
								<span class="truncate">{course.classroom_name}</span>
								<span class="font-mono text-gray-300 dark:text-gray-600 ml-auto flex-shrink-0">{course.class_code}</span>
							</div>
						{/if}

						<div class="mt-auto">
							<button
								on:click={() => goto(`/student/courses/${course.knowledge_id}?name=${encodeURIComponent(course.knowledge_name || '')}&teacher=${encodeURIComponent(course.teacher_name || '')}`)}
								class="w-full flex items-center justify-center gap-2.5 py-3 px-4 bg-gradient-to-r {color} text-white font-semibold rounded-2xl shadow-md hover:shadow-lg hover:opacity-90 transition-all active:scale-95 text-sm"
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
								</svg>
								{$i18n.t('Ask the AI')} 🤖
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
