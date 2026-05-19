<!-- Assignments.svelte — Student views all assignments from joined classrooms -->
<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	function formatFileSize(bytes: number) {
		if (bytes < 1024) return bytes + ' B';
		if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
		return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
	}

	const i18n = getContext('i18n');
	let classrooms = [];
	let allAssignments = [];
	let mySubmissions = [];
	let loading = true;
	let activeTab = 'all';
	let submittingId = '';
	let submitContent = '';
	let showSubmitModal = false;
	let selectedAssignment = null;
	let submitError = '';
	let submitSuccess = '';

	async function fetchAll() {
		loading = true;
		try {
			const token = localStorage.token;
			const [crRes, subRes] = await Promise.all([
				fetch(`${TUTOR_API_BASE_URL}/teacher/my-classrooms`, { headers: { Authorization: `Bearer ${token}` } }),
				fetch(`${TUTOR_API_BASE_URL}/teacher/my-submissions`, { headers: { Authorization: `Bearer ${token}` } })
			]);
			if (crRes.ok) classrooms = await crRes.json();
			if (subRes.ok) mySubmissions = await subRes.json();

			// Fetch assignments for each classroom
			allAssignments = [];
			for (const c of classrooms) {
				try {
					const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/${c.class_code}/assignments`, {
						headers: { Authorization: `Bearer ${token}` }
					});
					if (res.ok) {
						const data = await res.json();
						allAssignments = [...allAssignments, ...data.map(a => ({ ...a, teacher_name: c.teacher_name, class_code: c.class_code }))];
					}
				} catch { /* skip */ }
			}
		} catch (e) { console.error(e); }
		loading = false;
	}

	function getSubmission(assignmentId) {
		return mySubmissions.find(s => s.assignment_id === assignmentId);
	}

	function getStatus(a) {
		const sub = getSubmission(a.id);
		if (sub) {
			if (sub.status === 'graded') return { label: $i18n.t('Graded'), color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400', icon: '✅' };
			if (sub.status === 'late') return { label: $i18n.t('Late'), color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', icon: '⏰' };
			return { label: $i18n.t('Submitted'), color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', icon: '📤' };
		}
		const due = new Date(`${a.due_date}T${a.due_time || '23:59'}`);
		if (Date.now() > due.getTime()) return { label: $i18n.t('Overdue'), color: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400', icon: '🚨' };
		return { label: $i18n.t('To do'), color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', icon: '📝' };
	}

	function getTimeLeft(dueDate, dueTime) {
		const due = new Date(`${dueDate}T${dueTime || '23:59'}`);
		const diff = due.getTime() - Date.now();
		if (diff < 0) return 'Overdue';
		const days = Math.floor(diff / 86400000);
		const hours = Math.floor((diff % 86400000) / 3600000);
		if (days > 0) return `${days}d ${hours}h`;
		if (hours > 0) return `${hours}h`;
		return 'Due soon';
	}

	function openSubmitModal(a) {
		selectedAssignment = a;
		submitContent = '';
		submitError = '';
		submitSuccess = '';
		showSubmitModal = true;
	}

	let submitFiles = [];

	async function submitWork() {
		if (!selectedAssignment || (!submitContent.trim() && submitFiles.length === 0)) return;
		// submitContent is optional if files are attached
		submittingId = selectedAssignment.id;
		submitError = '';
		try {
			const formData = new FormData();
			formData.append('assignment_id', selectedAssignment.id);
			formData.append('content', submitContent);
			for (const file of submitFiles) {
				formData.append('files', file);
			}
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/submissions`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${localStorage.token}` },
				body: formData
			});
			const data = await res.json();
			if (res.ok) {
				submitSuccess = $i18n.t('Submission successful!');
				mySubmissions = [...mySubmissions, data];
				setTimeout(() => { showSubmitModal = false; submitSuccess = ''; submitFiles = []; }, 2000);
			} else {
				submitError = data.detail || 'Submission failed';
			}
		} catch (e) {
			submitError = 'Connection error';
			console.error(e);
		}
		submittingId = '';
	}

	$: filtered = activeTab === 'all' ? allAssignments
		: activeTab === 'todo' ? allAssignments.filter(a => !getSubmission(a.id))
		: activeTab === 'submitted' ? allAssignments.filter(a => getSubmission(a.id))
		: allAssignments;

	onMount(() => fetchAll());
</script>

<div class="max-w-4xl mx-auto space-y-8">
	<div class="flex items-center justify-between flex-wrap gap-4">
		<div>
			<h2 class="text-2xl font-bold text-gray-900 dark:text-white">{$i18n.t('My Assignments')}</h2>
			<p class="text-sm text-gray-500 mt-1">{allAssignments.length} {$i18n.t('total from')} {classrooms.length} {$i18n.t('classes')}</p>
		</div>
		<button on:click={fetchAll} class="p-2.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors text-gray-500" title="Refresh">
			<svg class="w-5 h-5 {loading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
		</button>
	</div>

	<!-- Tabs -->
	<div class="flex gap-2 bg-white dark:bg-gray-800 rounded-2xl p-1.5 border border-gray-200 dark:border-gray-700 shadow-sm w-fit">
		{#each [['all', 'All'], ['todo', 'To do'], ['submitted', 'Submitted']] as [key, label]}
			<button on:click={() => activeTab = key} class="px-5 py-2 text-sm font-semibold rounded-xl transition-all {activeTab === key ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'}">{$i18n.t(label)}</button>
		{/each}
	</div>

	{#if loading}
		<div class="space-y-4 animate-pulse">
			{#each Array(3) as _}<div class="h-40 bg-gray-200 dark:bg-gray-700 rounded-3xl"></div>{/each}
		</div>
	{:else if filtered.length === 0}
		<div class="bg-white dark:bg-gray-800 rounded-3xl border-2 border-dashed border-gray-200 dark:border-gray-700 p-16 text-center">
			<div class="text-5xl mb-4">📋</div>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{$i18n.t('No assignments')}</h3>
			<p class="text-gray-500 text-sm">{activeTab === 'todo' ? $i18n.t('All caught up!') : $i18n.t('Join a class to see assignments.')}</p>
		</div>
	{:else}
		<div class="space-y-5">
			{#each filtered as a}
				{@const st = getStatus(a)}
				{@const sub = getSubmission(a.id)}
				<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 group">
					<div class="h-1.5 bg-gradient-to-r {a.course_color || 'from-indigo-500 to-indigo-600'}"></div>
					<div class="p-7">
						<div class="flex items-start gap-5">
							<div class="w-14 h-14 bg-gradient-to-br {a.course_color || 'from-indigo-500 to-indigo-600'} rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md text-2xl">{st.icon}</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-3 mb-1 flex-wrap">
									{#if a.teacher_name}
										<span class="text-xs font-bold text-gray-400">👤 {a.teacher_name}</span>
									{/if}
									{#if a.course}
										<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">• {a.course}</span>
									{/if}
									<span class="px-2.5 py-0.5 text-xs font-bold rounded-full {st.color}">{st.label}</span>
								</div>
								<h3 class="text-xl font-bold text-gray-900 dark:text-white">{a.title}</h3>
								{#if a.description}
									<p class="text-gray-500 dark:text-gray-400 text-sm mt-2 line-clamp-2 leading-relaxed">{a.description}</p>
								{/if}
								<div class="flex items-center justify-between mt-4 flex-wrap gap-4">
									<div class="flex items-center gap-5">
										<span class="text-sm text-gray-500">📅 {getTimeLeft(a.due_date, a.due_time)}</span>
										<span class="text-sm font-bold text-gray-600 dark:text-gray-300">⭐ {a.points} pts</span>
										{#if sub?.grade}
											<span class="text-sm font-bold text-purple-600 dark:text-purple-400">📊 {sub.grade}</span>
										{/if}
									</div>
									{#if !sub}
										<button on:click={() => openSubmitModal(a)} class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-all active:scale-95 shadow-md shadow-indigo-600/20">
											{$i18n.t('Submit')}
										</button>
									{/if}
								</div>
								{#if sub}
									<div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 space-y-2">
										{#if sub.grade}
											<div class="flex items-center gap-2 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700/40 rounded-xl px-4 py-2">
												<span class="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wide">Note</span>
												<span class="text-sm font-bold text-purple-700 dark:text-purple-300">{sub.grade}</span>
											</div>
										{/if}
										{#if sub.feedback}
											<div class="flex items-start gap-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700/40 rounded-xl px-4 py-2">
												<span class="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wide mt-0.5">Commentaire</span>
												<span class="text-sm text-blue-700 dark:text-blue-300">{sub.feedback}</span>
											</div>
										{/if}
										{#if sub.file_ids && sub.file_ids.length > 0}
											<div class="flex flex-wrap gap-2">
												{#each sub.file_ids as f}
													<a href="{TUTOR_API_BASE_URL}/teacher/submission-files/{f.id}"
														target="_blank"
														class="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 text-xs font-medium text-gray-700 dark:text-gray-300 rounded-lg transition-colors">
														<svg class="w-3.5 h-3.5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>
														{f.name} ({formatFileSize(f.size)})
													</a>
												{/each}
											</div>
										{/if}
									</div>
								{/if}
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Submit Modal -->
{#if showSubmitModal && selectedAssignment}
	<div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" on:click|self={() => showSubmitModal = false}>
		<div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 p-8 max-w-lg w-full shadow-2xl">
			<h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{$i18n.t('Submit Assignment')}</h3>
			<p class="text-sm text-gray-500 mb-6">{selectedAssignment.title}</p>
			<textarea bind:value={submitContent} rows="5" placeholder="{$i18n.t('Write your answer here...')}"
				class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 dark:text-white transition-all resize-none"></textarea>

			<!-- File Upload -->
			<div class="mt-4">
				<label class="block text-xs font-semibold text-gray-500 mb-2">📎 {$i18n.t('Attach files')} <span class="font-normal text-gray-400">(PDF, Word, images…)</span></label>
				<label class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-2xl cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/50 dark:hover:bg-indigo-500/5 transition-all">
					<input type="file" multiple accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.txt" class="hidden"
						on:change={(e) => { submitFiles = Array.from(e.target.files || []) }} />
					{#if submitFiles.length > 0}
						<div class="text-center px-4">
							{#each submitFiles as f}
								<p class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold truncate">📄 {f.name}</p>
							{/each}
						</div>
					{:else}
						<div class="text-center">
							<svg class="w-6 h-6 text-gray-400 mb-1 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
							<p class="text-xs text-gray-400">{$i18n.t('Click to upload or drag files here')}</p>
						</div>
					{/if}
				</label>
			</div>
			{#if submitError}
				<p class="mt-3 text-sm text-rose-600 font-semibold">{submitError}</p>
			{/if}
			{#if submitSuccess}
				<p class="mt-3 text-sm text-emerald-600 font-semibold flex items-center gap-1.5">✅ {submitSuccess}</p>
			{/if}
			<div class="flex gap-3 mt-6">
				<button on:click={submitWork} disabled={(!submitContent.trim() && submitFiles.length === 0) || !!submittingId}
					class="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-2xl transition-all flex items-center justify-center gap-2">
					{#if submittingId}
						<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
					{/if}
					{$i18n.t('Submit')}
				</button>
				<button on:click={() => showSubmitModal = false} class="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold rounded-2xl transition-all">{$i18n.t('Cancel')}</button>
			</div>
		</div>
	</div>
{/if}
