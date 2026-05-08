<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let showForm = false;
	let editingId = null;
	let activeTab = 'all'; // all | upcoming | submitted | overdue

	let assignments = [
		{
			id: '1',
			title: 'Algebra Problem Set #1',
			description: 'Solve all exercises from Chapter 3. Show your work clearly. Scan or photograph your answers and upload as PDF.',
			course: 'Mathematics 101',
			courseColor: 'from-blue-500 to-blue-600',
			dueDate: new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0],
			dueTime: '23:59',
			points: 100,
			status: 'active',
			submissions: 5,
			totalStudents: 22,
			createdAt: Date.now() - 86400000
		},
		{
			id: '2',
			title: 'Essay: Industrial Revolution',
			description: 'Write a 1000-word essay about the social impacts of the Industrial Revolution. Use at least 3 sources.',
			course: 'History',
			courseColor: 'from-amber-500 to-amber-600',
			dueDate: new Date(Date.now() - 86400000 * 2).toISOString().split('T')[0],
			dueTime: '23:59',
			points: 50,
			status: 'overdue',
			submissions: 18,
			totalStudents: 22,
			createdAt: Date.now() - 86400000 * 5
		}
	];

	let form = {
		title: '',
		description: '',
		course: '',
		courseColor: 'from-indigo-500 to-indigo-600',
		dueDate: '',
		dueTime: '23:59',
		points: 100
	};

	const courseColors = [
		{ label: 'Indigo', value: 'from-indigo-500 to-indigo-600' },
		{ label: 'Blue', value: 'from-blue-500 to-blue-600' },
		{ label: 'Purple', value: 'from-purple-500 to-purple-600' },
		{ label: 'Rose', value: 'from-rose-500 to-rose-600' },
		{ label: 'Amber', value: 'from-amber-500 to-amber-600' },
		{ label: 'Emerald', value: 'from-emerald-500 to-emerald-600' },
		{ label: 'Cyan', value: 'from-cyan-500 to-cyan-600' }
	];

	function openCreateForm() {
		form = { title: '', description: '', course: '', courseColor: 'from-indigo-500 to-indigo-600', dueDate: '', dueTime: '23:59', points: 100 };
		editingId = null;
		showForm = true;
		setTimeout(() => document.getElementById('assign-title')?.focus(), 100);
	}

	function openEditForm(a) {
		form = { title: a.title, description: a.description, course: a.course, courseColor: a.courseColor, dueDate: a.dueDate, dueTime: a.dueTime, points: a.points };
		editingId = a.id;
		showForm = true;
	}

	function cancelForm() { showForm = false; editingId = null; }

	function saveAssignment() {
		if (!form.title.trim() || !form.dueDate) return;
		const now = Date.now();
		const due = new Date(`${form.dueDate}T${form.dueTime}`);
		const status = due > new Date() ? 'active' : 'overdue';
		if (editingId) {
			assignments = assignments.map(a => a.id === editingId ? { ...a, ...form, status } : a);
		} else {
			assignments = [{ id: String(now), ...form, status, submissions: 0, totalStudents: 22, createdAt: now }, ...assignments];
		}
		showForm = false; editingId = null;
	}

	function deleteAssignment(id) {
		if (!confirm('Delete this assignment?')) return;
		assignments = assignments.filter(a => a.id !== id);
	}

	function getTimeLeft(dueDate, dueTime) {
		const due = new Date(`${dueDate}T${dueTime}`);
		const diff = due - Date.now();
		if (diff < 0) return { text: 'Overdue', urgent: true };
		const days = Math.floor(diff / 86400000);
		const hours = Math.floor((diff % 86400000) / 3600000);
		if (days > 0) return { text: `${days}d ${hours}h left`, urgent: days <= 1 };
		if (hours > 0) return { text: `${hours}h left`, urgent: true };
		return { text: 'Due soon', urgent: true };
	}

	function formatDueDate(date, time) {
		const d = new Date(`${date}T${time}`);
		return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) + ' at ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
	}

	$: filtered = activeTab === 'all' ? assignments
		: activeTab === 'active' ? assignments.filter(a => a.status === 'active')
		: activeTab === 'overdue' ? assignments.filter(a => a.status === 'overdue')
		: assignments;

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
	});
</script>

<svelte:head><title>Assignments | EduConnect</title></svelte:head>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />
	<div class="flex-1 md:ml-64 flex flex-col min-h-screen">

		<!-- Header -->
		<header class="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-30">
			<div class="flex items-center gap-4">
				<button class="md:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl" on:click={() => isSidebarOpen = true}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
				</button>
				<div>
					<h1 class="text-xl font-bold text-slate-900 dark:text-white">Assignments</h1>
					<p class="text-sm text-slate-500">{assignments.length} assignment{assignments.length !== 1 ? 's' : ''}</p>
				</div>
			</div>
			<div class="flex items-center gap-4">
				<button on:click={openCreateForm} class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition-all hover:-translate-y-0.5 active:scale-95">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
					Create Assignment
				</button>
				{#if $user}
					<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 p-6 lg:p-10">
			<div class="max-w-4xl mx-auto space-y-8">

				<!-- Create/Edit Form -->
				{#if showForm}
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-indigo-200 dark:border-indigo-500/30 shadow-xl shadow-indigo-600/5 overflow-hidden animate-in">
						<div class="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 bg-[length:200%_100%] animate-gradient"></div>
						<div class="p-8">
							<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8">{editingId ? '✏️ Edit Assignment' : '📝 New Assignment'}</h2>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<!-- Title -->
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Title <span class="text-rose-500">*</span></label>
									<input id="assign-title" type="text" bind:value={form.title} placeholder="e.g. Chapter 5 Review Questions" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<!-- Description -->
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Instructions</label>
									<textarea bind:value={form.description} rows="4" placeholder="Describe what students need to do, materials to use, submission format..." class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all resize-none"></textarea>
								</div>
								<!-- Course -->
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Course</label>
									<input type="text" bind:value={form.course} placeholder="e.g. Mathematics 101" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<!-- Points -->
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Points</label>
									<div class="relative">
										<input type="number" bind:value={form.points} min="0" max="1000" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all pr-16" />
										<span class="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">pts</span>
									</div>
								</div>
								<!-- Due Date -->
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Due Date <span class="text-rose-500">*</span></label>
									<input type="date" bind:value={form.dueDate} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<!-- Due Time -->
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Due Time</label>
									<input type="time" bind:value={form.dueTime} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<!-- Color -->
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Color Theme</label>
									<div class="flex gap-3 flex-wrap">
										{#each courseColors as c}
											<button type="button" on:click={() => form.courseColor = c.value}
												class="w-8 h-8 rounded-xl bg-gradient-to-br {c.value} transition-all hover:scale-110 {form.courseColor === c.value ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : ''}">
											</button>
										{/each}
									</div>
								</div>
							</div>
							<div class="flex gap-3 mt-8 pt-6 border-t border-slate-100 dark:border-slate-800">
								<button on:click={saveAssignment} disabled={!form.title.trim() || !form.dueDate} class="px-7 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-2xl transition-all hover:-translate-y-0.5 shadow-md shadow-indigo-600/20">
									{editingId ? 'Save Changes' : '📋 Assign'}
								</button>
								<button on:click={cancelForm} class="px-7 py-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-2xl transition-all">Cancel</button>
							</div>
						</div>
					</div>
				{/if}

				<!-- Tabs -->
				<div class="flex gap-2 bg-white dark:bg-slate-900 rounded-2xl p-1.5 border border-slate-200 dark:border-slate-800 shadow-sm w-fit">
					{#each [['all', 'All'], ['active', 'Active'], ['overdue', 'Overdue']] as [key, label]}
						<button on:click={() => activeTab = key} class="px-5 py-2 text-sm font-semibold rounded-xl transition-all {activeTab === key ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20' : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'}">{label}</button>
					{/each}
				</div>

				<!-- Assignment Cards -->
				{#if filtered.length === 0}
					<div class="bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-16 text-center">
						<div class="text-5xl mb-4">📋</div>
						<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">No assignments yet</h3>
						<p class="text-slate-500 text-sm">Create your first assignment to get started.</p>
					</div>
				{:else}
					<div class="space-y-5">
						{#each filtered as a}
							{@const timeLeft = getTimeLeft(a.dueDate, a.dueTime)}
							{@const progress = Math.round((a.submissions / a.totalStudents) * 100)}
							<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 group">
								<!-- Top color strip -->
								<div class="h-1.5 bg-gradient-to-r {a.courseColor}"></div>
								<div class="p-7">
									<div class="flex items-start gap-5">
										<!-- Icon -->
										<div class="w-14 h-14 bg-gradient-to-br {a.courseColor} rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md text-2xl">📋</div>
										<!-- Content -->
										<div class="flex-1 min-w-0">
											<div class="flex items-start justify-between gap-4 flex-wrap">
												<div>
													<div class="flex items-center gap-3 mb-1 flex-wrap">
														{#if a.course}
															<span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{a.course}</span>
														{/if}
														<span class="px-2.5 py-0.5 text-xs font-bold rounded-full {timeLeft.urgent ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'}">
															{timeLeft.text}
														</span>
													</div>
													<h3 class="text-xl font-bold text-slate-900 dark:text-white">{a.title}</h3>
												</div>
												<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
													<button on:click={() => openEditForm(a)} class="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-indigo-600 rounded-xl transition-all" title="Edit">
														<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
													</button>
													<button on:click={() => deleteAssignment(a.id)} class="p-2.5 hover:bg-rose-50 dark:hover:bg-rose-500/10 text-slate-400 hover:text-rose-600 rounded-xl transition-all" title="Delete">
														<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
													</button>
												</div>
											</div>

											{#if a.description}
												<p class="text-slate-500 dark:text-slate-400 text-sm mt-2 line-clamp-2 leading-relaxed">{a.description}</p>
											{/if}

											<!-- Meta row -->
											<div class="flex items-center gap-6 mt-4 flex-wrap">
												<span class="flex items-center gap-2 text-sm text-slate-500">
													<svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
													Due {formatDueDate(a.dueDate, a.dueTime)}
												</span>
												<span class="flex items-center gap-2 text-sm font-bold text-slate-600 dark:text-slate-300">
													<svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
													{a.points} pts
												</span>
											</div>

											<!-- Submissions progress bar -->
											<div class="mt-5 pt-5 border-t border-slate-100 dark:border-slate-800">
												<div class="flex items-center justify-between text-sm mb-2">
													<span class="font-semibold text-slate-700 dark:text-slate-300">Submissions</span>
													<span class="font-bold text-slate-900 dark:text-white">{a.submissions} <span class="text-slate-400 font-normal">/ {a.totalStudents}</span></span>
												</div>
												<div class="h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
													<div class="h-full bg-gradient-to-r {a.courseColor} rounded-full transition-all duration-700" style="width: {progress}%"></div>
												</div>
												<p class="text-xs text-slate-400 mt-1.5">{progress}% submitted</p>
											</div>
										</div>
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}

<style>
	@keyframes gradient { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
	.animate-gradient { animation: gradient 3s ease infinite; }
	.animate-in { animation: slideIn 0.3s ease-out; }
	@keyframes slideIn { from { opacity: 0; transform: translateY(-16px); } to { opacity: 1; transform: translateY(0); } }
</style>
