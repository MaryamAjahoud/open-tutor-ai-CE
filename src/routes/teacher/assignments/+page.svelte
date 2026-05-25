<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let showUserMenu = false;
	let showForm = false;
	let editingId = null;
	let activeTab = 'all';
	let loading = true;
	let savingAssignment = false;
	let saveError = '';

	let assignments = [];
	// Submissions panel state
	let submissionsPanel = null; // assignment id being viewed
	let submissions = [];        // submissions for current panel
	let loadingSubs = false;
	let gradeInputs = {};        // { [subId]: { grade, feedback } }
	let savingGrade = {};        // { [subId]: bool }


	let form = {
		title: '',
		description: '',
		course: '',
		course_color: 'from-indigo-500 to-indigo-600',
		due_date: '',
		due_time: '23:59',
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

	async function fetchAssignments() {
		loading = true;
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/assignments`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) {
				const data = await res.json();
				assignments = data.map(a => ({
					...a,
					courseColor: a.course_color || 'from-indigo-500 to-indigo-600',
					dueDate: a.due_date,
					dueTime: a.due_time || '23:59',
					submissions: a.submission_count || 0,
					createdAt: a.created_at
				}));
			}
		} catch (e) { console.error(e); }
		loading = false;
	}

	async function openSubmissionsPanel(assignmentId) {
		if (submissionsPanel === assignmentId) { submissionsPanel = null; return; }
		submissionsPanel = assignmentId;
		loadingSubs = true;
		submissions = [];
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/assignments/${assignmentId}/submissions`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) {
				submissions = await res.json();
				// init grade inputs
				gradeInputs = {};
				for (const s of submissions) {
					gradeInputs[s.id] = { grade: s.grade || '', feedback: s.feedback || '' };
				}
			}
		} catch (e) { console.error(e); }
		loadingSubs = false;
	}

	async function saveGrade(submissionId) {
		savingGrade = { ...savingGrade, [submissionId]: true };
		try {
			const { grade, feedback } = gradeInputs[submissionId] || {};
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/submissions/${submissionId}/grade`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify({ grade, feedback })
			});
			if (res.ok) {
				const updated = await res.json();
				submissions = submissions.map(s => s.id === submissionId ? { ...s, ...updated } : s);
				await fetchAssignments();
			}
		} catch (e) { console.error(e); }
		savingGrade = { ...savingGrade, [submissionId]: false };
	}

	function openCreateForm() {
		form = { title: '', description: '', course: '', course_color: 'from-indigo-500 to-indigo-600', due_date: '', due_time: '23:59', points: 100 };
		editingId = null;
		showForm = true;
		setTimeout(() => document.getElementById('assign-title')?.focus(), 100);
	}

	function openEditForm(a) {
		form = { title: a.title, description: a.description || '', course: a.course || '', course_color: a.course_color || a.courseColor, due_date: a.due_date || a.dueDate, due_time: a.due_time || a.dueTime, points: a.points };
		editingId = a.id;
		showForm = true;
	}

	function cancelForm() { showForm = false; editingId = null; }

	async function saveAssignment() {
		if (!form.title.trim() || !form.due_date) return;
		savingAssignment = true;
		saveError = '';
		try {
			const body = {
				title: form.title,
				description: form.description,
				course: form.course,
				course_color: form.course_color,
				due_date: form.due_date,
				due_time: form.due_time || '23:59',
				points: form.points || 100
			};
			let res;
			if (editingId) {
				res = await fetch(`${TUTOR_API_BASE_URL}/teacher/assignments/${editingId}`, {
					method: 'PUT',
					headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
					body: JSON.stringify(body)
				});
			} else {
				res = await fetch(`${TUTOR_API_BASE_URL}/teacher/assignments`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
					body: JSON.stringify(body)
				});
			}
			if (res.ok) {
				await fetchAssignments();
				showForm = false;
				editingId = null;
			} else {
				const errData = await res.json().catch(() => ({}));
				saveError = errData.detail || `Error ${res.status}: Failed to save assignment`;
			}
		} catch (e) {
			console.error(e);
			saveError = 'Network error. Please check your connection and try again.';
		}
		savingAssignment = false;
	}

	async function deleteAssignment(id) {
		if (!confirm('Delete this assignment?')) return;
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/assignments/${id}`, {
				method: 'DELETE',
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) assignments = assignments.filter(a => a.id !== id);
		} catch (e) { console.error(e); }
	}

	function logout() {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		user.set(null);
		goto('/auth');
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
		await fetchAssignments();
	});
</script>

<svelte:head><title>Assignments | Open Tutor</title></svelte:head>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />
	<div class="flex-1 md:ml-64 flex flex-col min-h-screen">

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
					<div class="relative">
						<button on:click={() => showUserMenu = !showUserMenu}
							class="flex items-center gap-3 pl-4 border-l border-slate-200 dark:border-slate-800 cursor-pointer">
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
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Title <span class="text-rose-500">*</span></label>
									<input id="assign-title" type="text" bind:value={form.title} placeholder="e.g. Chapter 5 Review Questions" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Instructions</label>
									<textarea bind:value={form.description} rows="4" placeholder="Describe what students need to do..." class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all resize-none"></textarea>
								</div>
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Course</label>
									<input type="text" bind:value={form.course} placeholder="e.g. Mathematics 101" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Points</label>
									<div class="relative">
										<input type="number" bind:value={form.points} min="0" max="1000" class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all pr-16" />
										<span class="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-400">pts</span>
									</div>
								</div>
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Due Date <span class="text-rose-500">*</span></label>
									<input type="date" bind:value={form.due_date} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<div>
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Due Time</label>
									<input type="time" bind:value={form.due_time} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
								</div>
								<div class="md:col-span-2">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Color Theme</label>
									<div class="flex gap-3 flex-wrap">
										{#each courseColors as c}
											<button type="button" on:click={() => form.course_color = c.value}
												class="w-8 h-8 rounded-xl bg-gradient-to-br {c.value} transition-all hover:scale-110 {form.course_color === c.value ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : ''}">
											</button>
										{/each}
									</div>
								</div>
							</div>
							<div class="flex gap-3 mt-8 pt-6 border-t border-slate-100 dark:border-slate-800">
								<button on:click={saveAssignment} disabled={!form.title.trim() || !form.due_date || savingAssignment} class="px-7 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-2xl transition-all hover:-translate-y-0.5 shadow-md shadow-indigo-600/20 flex items-center gap-2">
									{#if savingAssignment}<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>{/if}
									{editingId ? 'Save Changes' : '📋 Assign'}
								</button>
								<button on:click={cancelForm} class="px-7 py-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-2xl transition-all">Cancel</button>
							</div>
						{#if saveError}
							<div class="mt-4 p-4 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-500/30 rounded-2xl text-sm text-rose-700 dark:text-rose-400 font-medium flex items-center gap-2">
								<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
								{saveError}
							</div>
						{/if}
						</div>
					</div>
				{/if}

				<!-- Loading -->
				{#if loading}
					<div class="space-y-5 animate-pulse">
						{#each Array(3) as _}<div class="h-48 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>{/each}
					</div>
				{:else}
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
								{@const timeLeft = getTimeLeft(a.dueDate || a.due_date, a.dueTime || a.due_time)}
								<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 group">
									<div class="h-1.5 bg-gradient-to-r {a.courseColor || a.course_color || 'from-indigo-500 to-indigo-600'}"></div>
									<div class="p-7">
										<div class="flex items-start gap-5">
											<div class="w-14 h-14 bg-gradient-to-br {a.courseColor || a.course_color || 'from-indigo-500 to-indigo-600'} rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md text-2xl">📋</div>
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
												<div class="flex items-center gap-6 mt-4 flex-wrap">
													<span class="flex items-center gap-2 text-sm text-slate-500">
														<svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
														Due {formatDueDate(a.dueDate || a.due_date, a.dueTime || a.due_time)}
													</span>
													<span class="flex items-center gap-2 text-sm font-bold text-slate-600 dark:text-slate-300">
														<svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
														{a.points} pts
													</span>
												</div>
												<div class="mt-5 pt-5 border-t border-slate-100 dark:border-slate-800">
													<div class="flex items-center justify-between text-sm">
														<span class="font-semibold text-slate-700 dark:text-slate-300">Soumissions</span>
														<button on:click={() => openSubmissionsPanel(a.id)} class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all {submissionsPanel === a.id ? 'bg-indigo-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'}">
															{a.submissions || a.submission_count || 0} soumission{(a.submissions || a.submission_count || 0) !== 1 ? 's' : ''} {submissionsPanel === a.id ? '▲' : '▼'}
														</button>
													</div>
												</div>
											</div>
										</div>
									</div>
								</div>

								<!-- Submissions Grading Panel -->
								{#if submissionsPanel === a.id}
								<div class="border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 px-7 py-6 animate-in">
									<h4 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">👥 Soumissions — {a.title}</h4>
									{#if loadingSubs}
										<div class="flex items-center gap-2 text-sm text-slate-500 py-4"><svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>Chargement...</div>
									{:else if submissions.length === 0}
										<div class="text-center py-8 text-slate-400"><div class="text-3xl mb-2">📭</div><p class="text-sm">Aucune soumission pour ce devoir.</p></div>
									{:else}
										<div class="space-y-4">
											{#each submissions as sub}
												<div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 p-5">
													<div class="flex items-center justify-between mb-3 flex-wrap gap-2">
														<div class="flex items-center gap-3">
															<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center font-bold text-sm">{(sub.student_name || '?').charAt(0).toUpperCase()}</div>
															<div><p class="text-sm font-semibold text-slate-800 dark:text-slate-200">{sub.student_name || 'Étudiant'}</p><p class="text-xs text-slate-400">{sub.student_email || ''}</p></div>
														</div>
														<span class="px-2.5 py-1 rounded-full text-xs font-bold {sub.status === 'graded' ? 'bg-purple-100 text-purple-700' : sub.status === 'late' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}">{sub.status === 'graded' ? '✅ Noté' : sub.status === 'late' ? '⏰ En retard' : '📤 Soumis'}</span>
													</div>
													{#if sub.content}<div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-3 mb-3 text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap max-h-36 overflow-y-auto border border-slate-200 dark:border-slate-700">{sub.content}</div>{/if}
									{#if sub.file_ids && sub.file_ids.length > 0}
										<div class="flex flex-wrap gap-2 mb-3">
											{#each sub.file_ids as f}
												<a href="{TUTOR_API_BASE_URL}/teacher/submission-files/{f.id}?token={localStorage?.token}" target="_blank"
													class="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700/40 text-xs font-semibold text-indigo-700 dark:text-indigo-300 rounded-lg hover:bg-indigo-100 transition-colors">
													<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
													{f.name}
												</a>
											{/each}
										</div>
									{/if}
													{#if gradeInputs[sub.id]}
													<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
														<div><label class="block text-xs font-semibold text-slate-500 mb-1">Note (ex: 15/20)</label><input type="text" bind:value={gradeInputs[sub.id].grade} placeholder="Note..." class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:border-indigo-500 dark:text-white"/></div>
														<div><label class="block text-xs font-semibold text-slate-500 mb-1">Commentaire</label><input type="text" bind:value={gradeInputs[sub.id].feedback} placeholder="Feedback..." class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:border-indigo-500 dark:text-white"/></div>
													</div>
													<button on:click={() => saveGrade(sub.id)} disabled={savingGrade[sub.id]} class="mt-3 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-bold rounded-xl transition-all flex items-center gap-2">{#if savingGrade[sub.id]}<svg class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>{/if}💾 Enregistrer la note</button>
													{/if}
												</div>
											{/each}
										</div>
									{/if}
								</div>
								{/if}
							{/each}
						</div>
					{/if}
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
