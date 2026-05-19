<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import { getKnowledgeBases } from '$lib/apis/knowledge';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let showUserMenu = false;
	let loading = true;
	let totalCourses = 0;
	let totalFiles = 0;
	let recentCourses = [];
	let studentCount = null; // null = loading, number = fetched

	const subjectLabels = {
		'mathematics': { label: 'Mathematics', icon: '📊', color: 'from-blue-500 to-blue-600' },
		'science': { label: 'Science', icon: '🔬', color: 'from-teal-500 to-teal-600' },
		'history': { label: 'History', icon: '🏛️', color: 'from-amber-500 to-amber-600' },
		'computer-science': { label: 'Computer Science', icon: '💻', color: 'from-indigo-500 to-indigo-600' },
		'english': { label: 'English', icon: '📚', color: 'from-purple-500 to-purple-600' },
		'geography': { label: 'Geography', icon: '🌍', color: 'from-green-500 to-green-600' },
		'chemistry': { label: 'Chemistry', icon: '🧪', color: 'from-rose-500 to-rose-600' },
		'biology': { label: 'Biology', icon: '🌿', color: 'from-emerald-500 to-emerald-600' },
		'physics': { label: 'Physics', icon: '⚛️', color: 'from-cyan-500 to-cyan-600' },
		'other': { label: 'Other', icon: '📌', color: 'from-slate-500 to-slate-600' }
	};

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
		try {
			// Fetch courses and student count in parallel
			const [data, studentsRes] = await Promise.all([
				getKnowledgeBases(localStorage.token),
				fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/students`, {
					headers: { Authorization: `Bearer ${localStorage.token}` }
				})
			]);

			// Courses
			const rawList = Array.isArray(data) ? data : (data?.data || []);
			totalCourses = rawList.length;
			totalFiles = rawList.reduce((acc, c) => acc + (c.data?.file_ids?.length || c.files?.length || 0), 0);
			recentCourses = rawList
				.slice(0, 4)
				.map(c => {
					let parsedSubject = 'other';
					let cleanDescription = c.description || '';
					const match = cleanDescription.match(/^\[Subject:\s*([\w-]+)\]\s*(.*)$/is);
					if (match) { parsedSubject = match[1].toLowerCase(); cleanDescription = match[2]; }
					if (!subjectLabels[parsedSubject]) parsedSubject = 'other';
					return { ...c, parsedSubject, cleanDescription };
				});

			// Student count from classroom enrollment
			if (studentsRes.ok) {
				const students = await studentsRes.json();
				studentCount = Array.isArray(students) ? students.length : 0;
			} else {
				studentCount = 0;
			}
		} catch (e) {
			console.error(e);
			studentCount = 0;
		}
		loading = false;
	});

	const quickActions = [
		{ label: 'Create Course', icon: '📚', href: '/teacher/courses', action: 'create', color: 'from-indigo-500 to-blue-600' },
		{ label: 'My Courses', icon: '🗂️', href: '/teacher/courses', color: 'from-purple-500 to-indigo-600' },
		{ label: 'Announcements', icon: '📢', href: '/teacher/announcements', color: 'from-amber-500 to-orange-600' },
		{ label: 'Students', icon: '👥', href: '/teacher/students', color: 'from-emerald-500 to-teal-600' }
	];

	function logout() {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		user.set(null);
		goto('/auth');
	}
</script>

<svelte:head>
	<title>Teacher Dashboard | EduConnect</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />

	<div class="flex-1 md:ml-64 flex flex-col min-h-screen">
		<!-- Header -->
		<header class="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-30">
			<div class="flex items-center gap-4">
				<button class="md:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl" on:click={() => isSidebarOpen = true}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
				</button>
			</div>
			{#if $user}
				<div class="relative">
					<button on:click={() => showUserMenu = !showUserMenu}
						class="flex items-center gap-3 pl-5 border-l border-slate-200 dark:border-slate-800 cursor-pointer">
						<div class="hidden md:block text-right">
							<p class="text-sm font-semibold text-slate-900 dark:text-white">{$user.name}</p>
							<p class="text-xs text-slate-500 capitalize">{$user.role}</p>
						</div>
						<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
					</button>
					{#if showUserMenu}
						<div class="absolute right-0 top-14 w-52 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl z-50 overflow-hidden">
							<div class="px-4 py-3 border-b border-slate-100 dark:border-slate-800">
								<p class="text-sm font-semibold text-slate-900 dark:text-white">{$user.name}</p>
								<p class="text-xs text-slate-500">{$user.email}</p>
							</div>
							<button on:click={logout} class="flex items-center gap-3 w-full px-4 py-3 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors text-sm font-semibold">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
								Déconnexion
							</button>
						</div>
					{/if}
				</div>
			{/if}
		</header>

		<main class="flex-1 p-6 lg:p-10 overflow-y-auto">
			{#if loading}
				<div class="animate-pulse space-y-6">
					<div class="h-48 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>
					<div class="grid grid-cols-4 gap-4">{#each Array(4) as _}<div class="h-24 bg-slate-100 dark:bg-slate-800 rounded-2xl"></div>{/each}</div>
				</div>
			{:else}
				<!-- Welcome Hero -->
				<div class="mb-10 relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-10 shadow-xl border border-slate-800">
					<div class="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-indigo-500 opacity-20 rounded-full blur-[80px]"></div>
					<div class="absolute bottom-0 left-20 -mb-10 w-48 h-48 bg-blue-500 opacity-20 rounded-full blur-[60px]"></div>
					<div class="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
						<div>
							<h1 class="text-4xl font-bold text-white mb-3 tracking-tight">
								Welcome back, <span class="text-indigo-300">{$user?.name.split(' ')[0]}</span>! 👋
							</h1>
							<p class="text-slate-300 text-lg font-light leading-relaxed max-w-xl">
								Manage your courses, upload materials and communicate with your students — all in one place.
							</p>
						</div>
						<a href="/teacher/courses" class="group inline-flex items-center px-7 py-3.5 bg-indigo-500 hover:bg-indigo-400 text-white font-semibold rounded-2xl shadow-lg shadow-indigo-500/30 transition-all hover:-translate-y-0.5 active:scale-95 whitespace-nowrap">
							<div class="bg-white/20 p-1.5 rounded-lg mr-3 group-hover:bg-white/30 transition-colors">
								<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
							</div>
							Go to Courses
						</a>
					</div>
				</div>

				<!-- Stats Row -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
					<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
						<div class="flex items-center justify-between mb-4">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Courses</p>
							<div class="w-10 h-10 bg-indigo-50 dark:bg-indigo-500/10 rounded-xl flex items-center justify-center text-xl">📚</div>
						</div>
						<p class="text-4xl font-bold text-slate-900 dark:text-white">{totalCourses}</p>
					</div>
					<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
						<div class="flex items-center justify-between mb-4">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Files</p>
							<div class="w-10 h-10 bg-blue-50 dark:bg-blue-500/10 rounded-xl flex items-center justify-center text-xl">📎</div>
						</div>
						<p class="text-4xl font-bold text-slate-900 dark:text-white">{totalFiles}</p>
					</div>
					<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
						<div class="flex items-center justify-between mb-4">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Announcements</p>
							<div class="w-10 h-10 bg-amber-50 dark:bg-amber-500/10 rounded-xl flex items-center justify-center text-xl">📢</div>
						</div>
						<p class="text-4xl font-bold text-slate-900 dark:text-white">2</p>
					</div>
					<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
						<div class="flex items-center justify-between mb-4">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Students</p>
							<div class="w-10 h-10 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl flex items-center justify-center text-xl">👥</div>
						</div>
						{#if studentCount === null}
							<div class="h-10 w-16 bg-slate-200 dark:bg-slate-700 rounded-lg animate-pulse"></div>
						{:else}
							<p class="text-4xl font-bold text-slate-900 dark:text-white">{studentCount}</p>
						{/if}
					</div>
				</div>

				<!-- Quick Actions -->
				<div class="mb-10">
					<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-5 tracking-tight">Quick Actions</h2>
					<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
						{#each quickActions as qa}
							<a href={qa.href} class="group bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 flex flex-col items-center text-center hover:border-indigo-300 dark:hover:border-indigo-500/40 hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
								<div class="w-14 h-14 bg-gradient-to-br {qa.color} rounded-2xl flex items-center justify-center text-2xl mb-4 shadow-md group-hover:scale-110 transition-transform">{qa.icon}</div>
								<span class="text-sm font-bold text-slate-700 dark:text-slate-300">{qa.label}</span>
							</a>
						{/each}
					</div>
				</div>

				<!-- Recent Courses -->
				{#if recentCourses.length > 0}
					<div>
						<div class="flex items-center justify-between mb-5">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Recent Courses</h2>
							<a href="/teacher/courses" class="text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">View all →</a>
						</div>
						<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
							{#each recentCourses as course}
								{@const subj = subjectLabels[course.parsedSubject] || subjectLabels['other']}
								<a href="/teacher/courses/{course.id}" class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 block group">
									<div class="h-16 bg-gradient-to-br {subj.color} flex items-center px-5 relative overflow-hidden">
										<div class="absolute right-3 text-3xl opacity-20">{subj.icon}</div>
										<span class="text-white font-bold text-sm truncate relative z-10">{course.name}</span>
									</div>
									<div class="p-4 flex items-center justify-between">
										<span class="text-xs text-slate-400">{subj.label}</span>
										<span class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold group-hover:gap-2 flex items-center gap-1">
											Open <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
										</span>
									</div>
								</a>
							{/each}
						</div>
					</div>
				{/if}
			{/if}
		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}
