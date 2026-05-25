<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let showForm = false;
	let editingId = null;

	let announcements = [
		{
			id: '1',
			title: 'Welcome to the new semester!',
			content: 'Dear students, welcome back! Please check your course materials and don\'t hesitate to ask questions.',
			audience: 'all',
			createdAt: Date.now() - 86400000 * 2,
			pinned: true
		},
		{
			id: '2',
			title: 'Assignment deadline reminder',
			content: 'Reminder: The first assignment is due this Friday. Make sure to upload your work before midnight.',
			audience: 'mathematics',
			createdAt: Date.now() - 86400000,
			pinned: false
		}
	];

	let form = { title: '', content: '', audience: 'all', pinned: false };

	function openCreateForm() { form = { title: '', content: '', audience: 'all', pinned: false }; editingId = null; showForm = true; }
	function openEditForm(a) { form = { title: a.title, content: a.content, audience: a.audience, pinned: a.pinned }; editingId = a.id; showForm = true; }
	function cancelForm() { showForm = false; editingId = null; }

	function saveAnnouncement() {
		if (!form.title.trim() || !form.content.trim()) return;
		if (editingId) {
			announcements = announcements.map(a => a.id === editingId ? { ...a, ...form } : a);
		} else {
			announcements = [{ id: String(Date.now()), ...form, createdAt: Date.now() }, ...announcements];
		}
		showForm = false; editingId = null;
	}

	function deleteAnnouncement(id) {
		if (!confirm('Delete this announcement?')) return;
		announcements = announcements.filter(a => a.id !== id);
	}

	function togglePin(id) {
		announcements = announcements.map(a => a.id === id ? { ...a, pinned: !a.pinned } : a);
	}

	function formatDate(ts) {
		const diff = Date.now() - ts;
		if (diff < 60000) return 'Just now';
		if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
		if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
		return new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}

	$: sorted = [...announcements].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0) || b.createdAt - a.createdAt);

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
	});
</script>

<svelte:head>
	<title>Announcements | Open Tutor</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />

	<div class="flex-1 md:ml-64 flex flex-col min-h-screen">
		<header class="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-30">
			<div class="flex items-center gap-4">
				<button class="md:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl" on:click={() => isSidebarOpen = true}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
				</button>
				<div>
					<h1 class="text-xl font-bold text-slate-900 dark:text-white">Announcements</h1>
					<p class="text-sm text-slate-500">{announcements.length} total</p>
				</div>
			</div>
			<div class="flex items-center gap-4">
				<button on:click={openCreateForm} class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition-all hover:-translate-y-0.5 active:scale-95">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
					New Announcement
				</button>
				{#if $user}
					<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 p-6 lg:p-10">
			<div class="max-w-3xl mx-auto space-y-6">

				<!-- Create/Edit Form -->
				{#if showForm}
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-indigo-200 dark:border-indigo-500/30 p-8 shadow-lg shadow-indigo-600/5">
						<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6">{editingId ? 'Edit Announcement' : 'New Announcement'}</h2>
						<div class="space-y-5">
							<div>
								<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Title <span class="text-rose-500">*</span></label>
								<input type="text" bind:value={form.title} placeholder="Announcement title..." class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all" />
							</div>
							<div>
								<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Message <span class="text-rose-500">*</span></label>
								<textarea bind:value={form.content} rows="4" placeholder="Write your announcement..." class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all resize-none"></textarea>
							</div>
							<div class="flex flex-wrap gap-4">
								<div class="flex-1 min-w-40">
									<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Audience</label>
									<select bind:value={form.audience} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 dark:text-white">
										<option value="all">All Students</option>
										<option value="mathematics">Mathematics</option>
										<option value="science">Science</option>
										<option value="computer-science">Computer Science</option>
										<option value="english">English</option>
										<option value="history">History</option>
										<option value="other">Other</option>
									</select>
								</div>
								<div class="flex items-end pb-0.5">
									<label class="flex items-center gap-3 cursor-pointer">
										<div class="relative">
											<input type="checkbox" bind:checked={form.pinned} class="sr-only" />
											<div class="w-12 h-6 rounded-full transition-colors {form.pinned ? 'bg-indigo-600' : 'bg-slate-200 dark:bg-slate-700'}"></div>
											<div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform {form.pinned ? 'translate-x-6' : ''}"></div>
										</div>
										<span class="text-sm font-semibold text-slate-700 dark:text-slate-300">Pin to top</span>
									</label>
								</div>
							</div>
							<div class="flex gap-3 pt-2">
								<button on:click={saveAnnouncement} disabled={!form.title.trim() || !form.content.trim()} class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-semibold rounded-xl transition-all">
									{editingId ? 'Save Changes' : 'Publish'}
								</button>
								<button on:click={cancelForm} class="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-xl transition-all">
									Cancel
								</button>
							</div>
						</div>
					</div>
				{/if}

				<!-- Announcements List -->
				{#if sorted.length === 0}
					<div class="bg-white dark:bg-slate-900 rounded-3xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-16 text-center">
						<div class="w-16 h-16 bg-indigo-50 dark:bg-indigo-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-3xl">📢</div>
						<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">No announcements yet</h3>
						<p class="text-slate-500 text-sm">Create your first announcement to notify students.</p>
					</div>
				{:else}
					{#each sorted as ann}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border {ann.pinned ? 'border-indigo-200 dark:border-indigo-500/30' : 'border-slate-200 dark:border-slate-800'} p-7 shadow-sm hover:shadow-md transition-all duration-200 group relative overflow-hidden">
							{#if ann.pinned}
								<div class="absolute top-0 left-0 w-1 h-full bg-indigo-500 rounded-l-3xl"></div>
							{/if}
							<div class="flex items-start justify-between gap-4">
								<div class="flex-1 min-w-0">
									<div class="flex items-center gap-3 mb-3 flex-wrap">
										{#if ann.pinned}
											<span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-xs font-bold rounded-lg">
												<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/></svg>
												Pinned
											</span>
										{/if}
										<span class="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-xs font-semibold rounded-lg capitalize">{ann.audience === 'all' ? 'All Students' : ann.audience}</span>
									</div>
									<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">{ann.title}</h3>
									<p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{ann.content}</p>
									<p class="text-xs text-slate-400 mt-4">{formatDate(ann.createdAt)}</p>
								</div>
								<div class="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
									<button on:click={() => togglePin(ann.id)} class="p-2.5 {ann.pinned ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400' : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-600'} rounded-xl transition-all" title="{ann.pinned ? 'Unpin' : 'Pin'}">
										<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/></svg>
									</button>
									<button on:click={() => openEditForm(ann)} class="p-2.5 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-xl transition-all" title="Edit">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
									</button>
									<button on:click={() => deleteAnnouncement(ann.id)} class="p-2.5 hover:bg-rose-50 dark:hover:bg-rose-500/10 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 rounded-xl transition-all" title="Delete">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
									</button>
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}
