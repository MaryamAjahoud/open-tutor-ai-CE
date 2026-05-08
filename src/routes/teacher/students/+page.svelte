<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let loading = true;
	let error = null;
	let searchQuery = '';
	let viewMode = 'grid';

	let students = [];

	// Deterministic color from name
	const COLORS = [
		'from-pink-500 to-rose-600',
		'from-blue-500 to-indigo-600',
		'from-emerald-500 to-teal-600',
		'from-amber-500 to-orange-600',
		'from-purple-500 to-violet-600',
		'from-cyan-500 to-sky-600',
		'from-green-500 to-emerald-600',
		'from-rose-500 to-pink-600',
		'from-indigo-500 to-blue-600',
		'from-teal-500 to-cyan-600'
	];
	function colorForName(name) {
		let hash = 0;
		for (const c of (name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash);
		return COLORS[Math.abs(hash) % COLORS.length];
	}
	function initials(name) {
		return (name || '?').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
	}
	function formatLastSeen(ts) {
		if (!ts) return 'Never';
		const diff = Date.now() - ts * 1000;
		if (diff < 60000) return 'Just now';
		if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
		if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
		if (diff < 86400000 * 7) return `${Math.floor(diff / 86400000)}d ago`;
		return new Date(ts * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}
	function formatJoined(ts) {
		if (!ts) return '—';
		return new Date(ts * 1000).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
	}
	function isRecent(ts) {
		if (!ts) return false;
		return Date.now() - ts * 1000 < 86400000;
	}

	async function fetchStudents() {
		loading = true;
		error = null;
		try {
			const token = localStorage.token;
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/students`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || `HTTP ${res.status}`);
			}
			const data = await res.json();
			students = (Array.isArray(data) ? data : []).map(s => ({
				...s,
				color: colorForName(s.name),
				avatar: initials(s.name)
			}));
		} catch (err) {
			error = err.message || 'Failed to load students';
			console.error('Students fetch error:', err);
		}
		loading = false;
	}

	$: filtered = students.filter(s =>
		!searchQuery ||
		s.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
		s.email?.toLowerCase().includes(searchQuery.toLowerCase())
	);

	$: recentCount = students.filter(s => isRecent(s.last_active_at)).length;

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
		await fetchStudents();
	});
</script>

<svelte:head><title>Students | EduConnect</title></svelte:head>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />
	<div class="flex-1 md:ml-64 flex flex-col min-h-screen">

		<!-- Header -->
		<header class="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-30">
			<div class="flex items-center gap-4">
				<button class="md:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl" on:click={() => isSidebarOpen = true}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
				</button>
				<div class="hidden sm:flex items-center relative">
					<svg class="w-5 h-5 text-slate-400 absolute left-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
					<input type="text" bind:value={searchQuery} placeholder="Search by name or email..." class="pl-12 pr-4 py-2.5 bg-slate-100 dark:bg-slate-800 border-transparent rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 w-72 dark:text-white placeholder-slate-400 transition-all" />
				</div>
			</div>
			<div class="flex items-center gap-3">
				<!-- Refresh -->
				<button on:click={fetchStudents} class="p-2.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 rounded-xl transition-all" title="Refresh">
					<svg class="w-5 h-5 {loading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
				</button>
				<!-- View Toggle -->
				<div class="flex bg-slate-100 dark:bg-slate-800 rounded-xl p-1">
					<button on:click={() => viewMode = 'grid'} class="p-2 rounded-lg transition-all {viewMode === 'grid' ? 'bg-white dark:bg-slate-700 shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'}">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
					</button>
					<button on:click={() => viewMode = 'list'} class="p-2 rounded-lg transition-all {viewMode === 'list' ? 'bg-white dark:bg-slate-700 shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'}">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
					</button>
				</div>
				{#if $user}
					<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 p-6 lg:p-10 overflow-y-auto">

			<!-- Stats Cards -->
			<div class="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm animate-slide-up">
					<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Students</p>
					<p class="text-4xl font-bold text-slate-900 dark:text-white">{students.length}</p>
					<p class="text-sm text-slate-500 mt-1">Registered accounts</p>
				</div>
				<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm animate-slide-up delay-100">
					<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Active Today</p>
					<p class="text-4xl font-bold text-emerald-600">{recentCount}</p>
					<p class="text-sm text-slate-500 mt-1">Seen in last 24h</p>
				</div>
				<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm animate-slide-up delay-200 col-span-2 lg:col-span-1">
					<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Search Results</p>
					<p class="text-4xl font-bold text-indigo-600">{filtered.length}</p>
					<p class="text-sm text-slate-500 mt-1">{searchQuery ? 'matching query' : 'students shown'}</p>
				</div>
			</div>

			<!-- Loading State -->
			{#if loading}
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
					{#each Array(8) as _}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden skeleton-shimmer">
							<div class="h-20"></div>
							<div class="p-5 space-y-3">
								<div class="h-4 bg-slate-200 dark:bg-slate-700 rounded-lg w-3/4"></div>
								<div class="h-3 bg-slate-100 dark:bg-slate-800 rounded-lg w-1/2"></div>
							</div>
						</div>
					{/each}
				</div>

			<!-- Error State -->
			{:else if error}
				<div class="bg-white dark:bg-slate-900 rounded-3xl border border-rose-200 dark:border-rose-800/30 p-12 text-center shadow-sm max-w-lg mx-auto">
					<div class="w-16 h-16 bg-rose-50 dark:bg-rose-900/20 rounded-2xl flex items-center justify-center mx-auto mb-5 text-3xl">⚠️</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">Failed to load students</h3>
					<p class="text-slate-500 text-sm mb-6 font-mono bg-slate-50 dark:bg-slate-800 px-4 py-2 rounded-xl">{error}</p>
					<button on:click={fetchStudents} class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all shadow-md">Try Again</button>
				</div>

			<!-- Empty State -->
			{:else if filtered.length === 0}
				<div class="bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-16 text-center">
					<div class="text-5xl mb-4">👥</div>
					<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-2">
						{searchQuery ? 'No students match your search' : 'No students registered yet'}
					</h3>
					<p class="text-slate-500 text-sm max-w-sm mx-auto">
						{searchQuery ? 'Try a different name or email.' : 'Students will appear here once they create an account with the "user" role.'}
					</p>
				</div>

			<!-- Grid View -->
			{:else if viewMode === 'grid'}
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
					{#each filtered as s, i}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 group card-shine animate-scale-in" style="animation-delay: {i * 30}ms">
							<!-- Top banner -->
							<div class="h-20 bg-gradient-to-br {s.color} relative overflow-hidden">
								<div class="absolute inset-0 bg-black/10"></div>
								{#if isRecent(s.last_active_at)}
									<div class="absolute top-3 right-3 flex items-center gap-1.5 bg-white/20 backdrop-blur-sm text-white text-xs font-bold px-2 py-1 rounded-full">
										<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
										Active
									</div>
								{/if}
							</div>

							<div class="px-5 pb-5">
								<!-- Avatar -->
								<div class="-mt-7 mb-3 w-14 h-14 rounded-2xl bg-gradient-to-br {s.color} flex items-center justify-center text-white font-bold text-lg shadow-lg ring-4 ring-white dark:ring-slate-900">
									{s.avatar}
								</div>

								<h3 class="font-bold text-slate-900 dark:text-white truncate">{s.name}</h3>
								<p class="text-xs text-slate-400 mt-0.5 truncate" title={s.email}>{s.email}</p>

								<div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2">
									<div class="flex items-center justify-between text-xs">
										<span class="text-slate-400">Joined</span>
										<span class="font-semibold text-slate-600 dark:text-slate-300">{formatJoined(s.created_at)}</span>
									</div>
									<div class="flex items-center justify-between text-xs">
										<span class="text-slate-400">Last seen</span>
										<span class="font-semibold {isRecent(s.last_active_at) ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-500'}">{formatLastSeen(s.last_active_at)}</span>
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>

			<!-- List View -->
			{:else}
				<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden animate-fade-in">
					<div class="px-8 py-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
						<h2 class="font-bold text-slate-900 dark:text-white">All Students</h2>
						<span class="text-sm text-slate-400">{filtered.length} result{filtered.length !== 1 ? 's' : ''}</span>
					</div>
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead>
								<tr class="border-b border-slate-50 dark:border-slate-800">
									<th class="text-left px-8 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Student</th>
									<th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider hidden md:table-cell">Email</th>
									<th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider hidden lg:table-cell">Joined</th>
									<th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Last Seen</th>
									<th class="text-left px-6 py-4 text-xs font-bold text-slate-400 uppercase tracking-wider">Status</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
								{#each filtered as s, i}
									<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors animate-fade-in" style="animation-delay: {i * 20}ms">
										<td class="px-8 py-4">
											<div class="flex items-center gap-4">
												<div class="w-10 h-10 rounded-xl bg-gradient-to-br {s.color} flex items-center justify-center text-white font-bold text-sm shadow-sm flex-shrink-0">{s.avatar}</div>
												<div>
													<p class="font-semibold text-slate-900 dark:text-white text-sm">{s.name}</p>
													<p class="text-xs text-slate-400 md:hidden truncate max-w-40">{s.email}</p>
												</div>
											</div>
										</td>
										<td class="px-6 py-4 text-sm text-slate-500 hidden md:table-cell">
											<a href="mailto:{s.email}" class="hover:text-indigo-600 transition-colors">{s.email}</a>
										</td>
										<td class="px-6 py-4 text-sm text-slate-400 hidden lg:table-cell">{formatJoined(s.created_at)}</td>
										<td class="px-6 py-4 text-sm {isRecent(s.last_active_at) ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : 'text-slate-400'}">{formatLastSeen(s.last_active_at)}</td>
										<td class="px-6 py-4">
											<span class="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full {isRecent(s.last_active_at) ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}">
												<span class="w-1.5 h-1.5 rounded-full {isRecent(s.last_active_at) ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}"></span>
												{isRecent(s.last_active_at) ? 'Active' : 'Offline'}
											</span>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{/if}

		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}
