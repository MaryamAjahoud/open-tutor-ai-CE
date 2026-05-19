<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import CourseManagementModal from '$lib/components/teacher/CourseManagementModal.svelte';
	import { getKnowledgeBases, createNewKnowledge, updateKnowledgeById, deleteKnowledgeById, addFileToKnowledgeById } from '$lib/apis/knowledge';
	import { uploadFile } from '$lib/apis/files';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let loading = true;
	let courses = [];
	let groupedCourses = {};
	let isModalOpen = false;
	let isSubmitting = false;
	let editCourseItem = null;
	let deletingCourseId = null;
	let searchQuery = '';
	// Track which knowledge base IDs are shared with the classroom
	let sharedCourseIds = new Set();
	let sharingCourseId = null; // currently toggling

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

	function processCoursesData(dataList) {
		const processed = dataList.map(course => {
			let parsedSubject = 'other';
			let cleanDescription = course.description || '';
			const match = cleanDescription.match(/^\[Subject:\s*([\w-]+)\]\s*(.*)$/is);
			if (match) {
				parsedSubject = match[1].toLowerCase();
				cleanDescription = match[2];
			}
			if (!subjectLabels[parsedSubject]) parsedSubject = 'other';
			return { ...course, parsedSubject, cleanDescription };
		});
		courses = processed;
	}

	async function fetchCourses() {
		try {
			const token = localStorage.token;
			if (!token) return;
			const data = await getKnowledgeBases(token);
			const rawList = Array.isArray(data) ? data : (data?.data || []);
			processCoursesData(rawList);
		} catch (err) {
			console.error('Failed to fetch courses', err);
			courses = [];
		}
	}

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
		await Promise.all([fetchCourses(), fetchSharedCourses()]);
		loading = false;
		// Auto-share all existing courses that aren't shared yet
		for (const course of courses) {
			autoShareCourse(course.id, course.name);
		}
	});

	async function fetchSharedCourses() {
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/shared-courses`, {
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) {
				const data = await res.json();
				sharedCourseIds = new Set(data.map((d) => d.knowledge_id));
			}
		} catch (e) { console.error(e); }
	}

	// Auto-share a single course silently (no UI feedback needed)
	async function autoShareCourse(courseId, courseName) {
		if (sharedCourseIds.has(courseId)) return; // already shared
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/share-course`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify({ knowledge_id: courseId, knowledge_name: courseName })
			});
			if (res.ok) {
				sharedCourseIds.add(courseId);
				sharedCourseIds = new Set(sharedCourseIds);
			}
		} catch (e) { /* silent */ }
	}

	async function toggleShareCourse(course) {
		if (sharingCourseId) return;
		sharingCourseId = course.id;
		const isShared = sharedCourseIds.has(course.id);
		try {
			if (isShared) {
				const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/share-course/${course.id}`, {
					method: 'DELETE',
					headers: { Authorization: `Bearer ${localStorage.token}` }
				});
				if (res.ok) {
					sharedCourseIds.delete(course.id);
					sharedCourseIds = new Set(sharedCourseIds); // trigger reactivity
				}
			} else {
				const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/share-course`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
					body: JSON.stringify({ knowledge_id: course.id, knowledge_name: course.name })
				});
				if (res.ok) {
					sharedCourseIds.add(course.id);
					sharedCourseIds = new Set(sharedCourseIds); // trigger reactivity
				}
			}
		} catch (e) {
			console.error('Toggle share failed', e);
		} finally {
			sharingCourseId = null;
		}
	}

	$: filteredCourses = searchQuery.trim()
		? courses.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()) || c.cleanDescription?.toLowerCase().includes(searchQuery.toLowerCase()))
		: courses;

	function openCreateModal() { editCourseItem = null; isModalOpen = true; }
	function openEditModal(course) { editCourseItem = course; isModalOpen = true; }

	async function handleSaveCourse(event) {
		const { id, name, description, files } = event.detail;
		isSubmitting = true;
		try {
			const token = localStorage.token;
			let courseId = id;
			if (courseId) {
				await updateKnowledgeById(token, courseId, { name, description });
			} else {
				const newCourse = await createNewKnowledge(token, name, description, null);
				courseId = newCourse?.id || newCourse?.data?.id;
				if (!courseId) throw new Error('Failed to create course');
			}
			if (courseId && files && files.length > 0) {
				for (const file of files) {
					const uploadedFile = await uploadFile(token, file);
					const fileId = uploadedFile?.id || uploadedFile?.data?.id || uploadedFile?.file_id;
					if (fileId) await addFileToKnowledgeById(token, courseId, fileId);
				}
			}
			// Auto-share the course with the classroom
			await autoShareCourse(courseId, name);
			await fetchCourses();
			isModalOpen = false;
		} catch (err) {
			alert('Failed to save course: ' + err);
		} finally {
			isSubmitting = false;
		}
	}

	async function handleDeleteCourse(id) {
		if (!confirm('Are you sure you want to delete this course?')) return;
		deletingCourseId = id;
		try {
			await deleteKnowledgeById(localStorage.token, id);
			// Also unshare from classroom
			if (sharedCourseIds.has(id)) {
				await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/share-course/${id}`, {
					method: 'DELETE',
					headers: { Authorization: `Bearer ${localStorage.token}` }
				}).catch(() => {});
				sharedCourseIds.delete(id);
				sharedCourseIds = new Set(sharedCourseIds);
			}
			await fetchCourses();
		} catch (err) {
			alert('Failed to delete course: ' + err);
		} finally {
			deletingCourseId = null;
		}
	}
</script>

<svelte:head>
	<title>My Courses | EduConnect</title>
</svelte:head>

<CourseManagementModal
	bind:isOpen={isModalOpen}
	{isSubmitting}
	editCourse={editCourseItem}
	on:save={handleSaveCourse}
	on:close={() => editCourseItem = null}
/>

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
					<input type="text" bind:value={searchQuery} placeholder="Search courses..." class="pl-12 pr-4 py-2.5 bg-slate-100 dark:bg-slate-800 border-transparent rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 w-72 dark:text-white transition-all placeholder-slate-400" />
				</div>
			</div>
			<div class="flex items-center gap-5">
				<button on:click={openCreateModal} class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition-all hover:-translate-y-0.5 active:scale-95">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
					New Course
				</button>
				{#if $user}
					<div class="flex items-center gap-3 pl-5 border-l border-slate-200 dark:border-slate-800">
						<div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">{$user.name.charAt(0).toUpperCase()}</div>
					</div>
				{/if}
			</div>
		</header>

		<main class="flex-1 p-6 lg:p-10">
			<!-- Page Title -->
			<div class="mb-8 flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">My Courses</h1>
					<p class="text-slate-500 dark:text-slate-400 mt-1">{courses.length} course{courses.length !== 1 ? 's' : ''} total</p>
				</div>
			</div>

			{#if loading}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{#each Array(8) as _}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden animate-pulse">
							<div class="h-24 bg-slate-200 dark:bg-slate-800"></div>
							<div class="p-6 space-y-3">
								<div class="h-4 bg-slate-200 dark:bg-slate-700 rounded-lg w-3/4"></div>
								<div class="h-3 bg-slate-100 dark:bg-slate-800 rounded-lg w-1/2"></div>
							</div>
						</div>
					{/each}
				</div>
			{:else if filteredCourses.length === 0}
				<div class="bg-white/50 dark:bg-slate-800/30 rounded-3xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-16 text-center">
					<div class="w-24 h-24 bg-indigo-50 dark:bg-indigo-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6 rotate-3">
						<svg class="w-12 h-12 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
					</div>
					<h3 class="text-2xl font-bold text-slate-900 dark:text-white mb-3">{searchQuery ? 'No courses found' : 'No courses yet'}</h3>
					<p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-8">{searchQuery ? 'Try a different search term.' : 'Create your first course to get started.'}</p>
					{#if !searchQuery}
						<button on:click={openCreateModal} class="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all shadow-lg shadow-indigo-600/20 hover:-translate-y-0.5">Create Your First Course</button>
					{/if}
				</div>
			{:else}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{#each filteredCourses as course}
						{@const subj = subjectLabels[course.parsedSubject] || subjectLabels['other']}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] hover:shadow-[0_8px_30px_-4px_rgba(0,0,0,0.12)] dark:hover:shadow-[0_8px_30px_rgba(0,0,0,0.4)] transition-all duration-300 hover:-translate-y-1 overflow-hidden group flex flex-col relative cursor-pointer"
							on:click={() => goto(`/teacher/courses/${course.id}`)}
							on:keydown={(e) => e.key === 'Enter' && goto(`/teacher/courses/${course.id}`)}>

							<!-- Action Buttons -->
							<div class="absolute top-4 right-4 z-10 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
								<button class="p-2.5 bg-white/95 hover:bg-indigo-50 dark:bg-slate-800/95 dark:hover:bg-indigo-500/20 text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400 rounded-xl shadow-sm border border-slate-200/50 dark:border-slate-700 transition-all"
									title="Edit Course"
									on:click|stopPropagation={() => openEditModal(course)}>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
								</button>
								<button class="p-2.5 bg-white/95 hover:bg-rose-50 dark:bg-slate-800/95 dark:hover:bg-rose-500/20 text-slate-600 hover:text-rose-600 dark:text-slate-300 dark:hover:text-rose-400 rounded-xl shadow-sm border border-slate-200/50 dark:border-slate-700 transition-all"
									title="Delete Course"
									disabled={deletingCourseId === course.id}
									on:click|stopPropagation={() => handleDeleteCourse(course.id)}>
									{#if deletingCourseId === course.id}
										<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
									{:else}
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
									{/if}
								</button>
							</div>

							<!-- Card Header with gradient -->
							<div class="h-28 bg-gradient-to-br {subj.color} flex items-end p-5 relative overflow-hidden">
								<div class="absolute top-3 right-3 text-3xl opacity-20">{subj.icon}</div>
								<div class="absolute inset-0 bg-black/10"></div>
								<div class="relative z-10">
									<span class="text-xs font-bold text-white/80 uppercase tracking-wider">{subj.label}</span>
									<h3 class="text-lg font-bold text-white line-clamp-1 mt-0.5">{course.name}</h3>
								</div>
							</div>

							<!-- Card Body -->
							<div class="p-5 flex-1 flex flex-col">
								{#if course.cleanDescription}
									<p class="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 mb-4 leading-relaxed">{course.cleanDescription}</p>
								{/if}
								<div class="mt-auto pt-3 border-t border-slate-100 dark:border-slate-800 space-y-2">
									<div class="flex items-center justify-between">
										<div class="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>
											{course.files?.length || 0} file{(course.files?.length || 0) !== 1 ? 's' : ''}
										</div>
										<span class="text-xs font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 group-hover:gap-2 transition-all">
											Open <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
										</span>
									</div>
									<!-- Share with class toggle -->
									<button
										on:click|stopPropagation={() => toggleShareCourse(course)}
										disabled={sharingCourseId === course.id}
										class="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold transition-all
											{sharedCourseIds.has(course.id)
												? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40 hover:bg-emerald-100 dark:hover:bg-emerald-900/30'
												: 'bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:text-indigo-600 dark:hover:text-indigo-400 hover:border-indigo-200'}"
									>
										{#if sharingCourseId === course.id}
											<svg class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
										{:else if sharedCourseIds.has(course.id)}
											<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
											Partagé avec la classe
										{:else}
											<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
											Partager avec la classe
										{/if}
									</button>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</main>
	</div>
</div>

{#if isSidebarOpen}
	<div class="fixed inset-0 bg-slate-900/50 z-40 md:hidden backdrop-blur-sm" on:click={() => isSidebarOpen = false}></div>
{/if}
