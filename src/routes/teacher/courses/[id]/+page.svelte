<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import { getKnowledgeById } from '$lib/apis/knowledge';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let loading = true;
	let course = null;
	let files = [];
	let error = null;

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

	function getFileIcon(filename) {
		const ext = (filename || '').split('.').pop().toLowerCase();
		if (['pdf'].includes(ext)) return { icon: '📄', color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/20' };
		if (['doc', 'docx'].includes(ext)) return { icon: '📝', color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20' };
		if (['ppt', 'pptx'].includes(ext)) return { icon: '📊', color: 'text-orange-500', bg: 'bg-orange-50 dark:bg-orange-900/20' };
		if (['xls', 'xlsx'].includes(ext)) return { icon: '📈', color: 'text-green-500', bg: 'bg-green-50 dark:bg-green-900/20' };
		if (['txt', 'md'].includes(ext)) return { icon: '📃', color: 'text-slate-500', bg: 'bg-slate-50 dark:bg-slate-800' };
		if (['mp4', 'avi', 'mov'].includes(ext)) return { icon: '🎬', color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' };
		if (['mp3', 'wav'].includes(ext)) return { icon: '🎵', color: 'text-indigo-500', bg: 'bg-indigo-50 dark:bg-indigo-900/20' };
		if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext)) return { icon: '🖼️', color: 'text-pink-500', bg: 'bg-pink-50 dark:bg-pink-900/20' };
		return { icon: '📎', color: 'text-slate-500', bg: 'bg-slate-50 dark:bg-slate-800' };
	}

	function formatFileSize(bytes) {
		if (!bytes) return '—';
		if (bytes < 1024) return bytes + ' B';
		if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
		return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
	}

	function formatDate(ts) {
		if (!ts) return '—';
		return new Date(ts * 1000).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
	}

	async function downloadFile(fileId, fileName) {
		try {
			const token = localStorage.token;
			const res = await fetch(`${TUTOR_API_BASE_URL}/files/${fileId}/content`, {
				headers: { authorization: `Bearer ${token}` },
				credentials: 'include'
			});
			if (!res.ok) throw new Error('Download failed');
			const blob = await res.blob();
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = fileName || fileId;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		} catch (err) {
			alert('Failed to download file: ' + err.message);
		}
	}

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
		try {
			const courseId = $page.params.id;
			const token = localStorage.token;
			const data = await getKnowledgeById(token, courseId);
			if (!data) { error = 'Course not found'; loading = false; return; }

			let parsedSubject = 'other';
			let cleanDescription = data.description || '';
			const match = cleanDescription.match(/^\[Subject:\s*([\w-]+)\]\s*(.*)$/is);
			if (match) { parsedSubject = match[1].toLowerCase(); cleanDescription = match[2]; }
			if (!subjectLabels[parsedSubject]) parsedSubject = 'other';

			course = { ...data, parsedSubject, cleanDescription };
			files = data.files || [];
		} catch (err) {
			error = err.message || 'Failed to load course';
		}
		loading = false;
	});
</script>

<svelte:head>
	<title>{course?.name || 'Course Details'} | Open Tutor</title>
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
				<a href="/teacher/courses" class="flex items-center gap-2 text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors group">
					<svg class="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
					<span class="text-sm font-medium">Back to Courses</span>
				</a>
			</div>
			{#if $user}
				<div class="flex items-center gap-3 pl-5 border-l border-slate-200 dark:border-slate-800">
					<div class="hidden md:block text-right">
						<p class="text-sm font-semibold text-slate-900 dark:text-white">{$user.name}</p>
						<p class="text-xs text-slate-500 capitalize">{$user.role}</p>
					</div>
					<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
				</div>
			{/if}
		</header>

		<main class="flex-1 p-6 lg:p-10">
			{#if loading}
				<div class="max-w-4xl mx-auto space-y-6 animate-pulse">
					<div class="h-48 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>
					<div class="grid grid-cols-3 gap-4">
						{#each Array(3) as _}<div class="h-24 bg-slate-100 dark:bg-slate-800 rounded-2xl"></div>{/each}
					</div>
					<div class="h-64 bg-white dark:bg-slate-900 rounded-3xl"></div>
				</div>
			{:else if error}
				<div class="max-w-md mx-auto text-center py-20">
					<div class="w-20 h-20 bg-rose-50 dark:bg-rose-900/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
						<svg class="w-10 h-10 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
					</div>
					<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-2">Course Not Found</h2>
					<p class="text-slate-500 mb-6">{error}</p>
					<a href="/teacher/courses" class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl inline-block transition-all">Back to Courses</a>
				</div>
			{:else if course}
				{@const subj = subjectLabels[course.parsedSubject] || subjectLabels['other']}
				<div class="max-w-4xl mx-auto space-y-8">

					<!-- Hero Banner -->
					<div class="rounded-3xl overflow-hidden bg-gradient-to-br {subj.color} relative shadow-xl shadow-indigo-900/10">
						<div class="absolute inset-0 bg-black/20"></div>
						<div class="absolute top-6 right-8 text-8xl opacity-10">{subj.icon}</div>
						<div class="relative z-10 p-10">
							<div class="flex items-center gap-3 mb-4">
								<span class="px-3 py-1 bg-white/20 text-white text-xs font-bold rounded-full uppercase tracking-wider backdrop-blur-sm">{subj.label}</span>
								<span class="px-3 py-1 bg-white/20 text-white text-xs font-bold rounded-full backdrop-blur-sm">{files.length} file{files.length !== 1 ? 's' : ''}</span>
							</div>
							<h1 class="text-4xl font-bold text-white mb-3 tracking-tight">{course.name}</h1>
							{#if course.cleanDescription}
								<p class="text-white/80 text-lg max-w-2xl leading-relaxed">{course.cleanDescription}</p>
							{/if}
							<div class="mt-6 flex items-center gap-6 text-white/60 text-sm">
								<span class="flex items-center gap-2">
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
									Created {formatDate(course.created_at)}
								</span>
								<span class="flex items-center gap-2">
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
									Updated {formatDate(course.updated_at)}
								</span>
							</div>
						</div>
					</div>

					<!-- Stats Row -->
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
						<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Total Materials</p>
							<p class="text-3xl font-bold text-slate-900 dark:text-white">{files.length}</p>
							<p class="text-sm text-slate-500 mt-1">Uploaded files</p>
						</div>
						<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Subject</p>
							<p class="text-3xl">{subj.icon}</p>
							<p class="text-sm text-slate-500 mt-1">{subj.label}</p>
						</div>
						<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
							<p class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Last Updated</p>
							<p class="text-xl font-bold text-slate-900 dark:text-white">{formatDate(course.updated_at)}</p>
							<p class="text-sm text-slate-500 mt-1">Course materials</p>
						</div>
					</div>

					<!-- Files Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
						<div class="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Course Materials</h2>
							<span class="text-sm font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-xl">{files.length} file{files.length !== 1 ? 's' : ''}</span>
						</div>

						{#if files.length === 0}
							<div class="p-16 text-center">
								<div class="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
									<svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
								</div>
								<p class="text-slate-500 font-medium">No materials uploaded yet.</p>
								<p class="text-slate-400 text-sm mt-1">Edit this course to upload files.</p>
							</div>
						{:else}
							<ul class="divide-y divide-slate-100 dark:divide-slate-800">
								{#each files as file}
									{@const fname = file.name || file.meta?.name || file.filename || 'Unnamed file'}
									{@const fileInfo = getFileIcon(fname)}
									<li class="flex items-center gap-5 px-8 py-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group">
										<!-- File Icon -->
										<div class="w-12 h-12 {fileInfo.bg} rounded-2xl flex items-center justify-center flex-shrink-0 text-2xl shadow-sm">
											{fileInfo.icon}
										</div>

										<!-- File Info -->
										<div class="flex-1 min-w-0">
											<p class="font-semibold text-slate-800 dark:text-slate-200 truncate">{fname}</p>
											<div class="flex items-center gap-3 mt-1 text-xs text-slate-400">
												{#if file.meta?.size}
													<span>{formatFileSize(file.meta.size)}</span>
													<span>•</span>
												{/if}
												{#if file.created_at}
													<span>Added {formatDate(file.created_at)}</span>
												{/if}
											</div>
										</div>

										<!-- Actions -->
										<div class="flex items-center gap-2 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
											<!-- Download Button -->
											<button
												on:click={() => downloadFile(file.id, fname)}
												class="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-sm shadow-indigo-600/20 transition-all active:scale-95"
												title="Download">
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
												Download
											</button>
										</div>
									</li>
								{/each}
							</ul>
						{/if}
					</div>

				</div>
			{/if}
		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}
