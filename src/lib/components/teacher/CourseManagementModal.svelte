<script>
	import { createEventDispatcher, getContext, onMount } from 'svelte';
	
	export let isOpen = false;
	export let isSubmitting = false;
	export let editCourse = null; // If provided, modal is in Edit Mode

	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	let courseName = '';
	let courseSubject = 'mathematics';
	let courseDescription = '';
	let selectedFiles = [];

	const subjects = [
		{ id: 'mathematics', label: 'Mathematics', icon: '📊' },
		{ id: 'science', label: 'Science', icon: '🔬' },
		{ id: 'history', label: 'History', icon: '🏛️' },
		{ id: 'computer-science', label: 'Computer Science', icon: '💻' },
		{ id: 'english', label: 'English', icon: '📚' },
		{ id: 'geography', label: 'Geography', icon: '🌍' },
		{ id: 'chemistry', label: 'Chemistry', icon: '🧪' },
		{ id: 'biology', label: 'Biology', icon: '🌿' },
		{ id: 'physics', label: 'Physics', icon: '⚛️' },
		{ id: 'other', label: 'Other', icon: '📌' }
	];

	// Watch for editCourse changes to populate fields
	$: if (isOpen) {
		if (editCourse) {
			courseName = editCourse.name || '';
			courseSubject = editCourse.parsedSubject || 'mathematics';
			courseDescription = editCourse.cleanDescription || '';
			selectedFiles = []; // File uploading is usually separate, but we allow new files here
		} else if (!isSubmitting) {
			// If not editing, and not submitting, reset (but don't reset if just opening normally unless needed, 
			// actually we can rely on closeModal to reset)
		}
	}

	function closeModal() {
		if (!isSubmitting) {
			isOpen = false;
			courseName = '';
			courseSubject = 'mathematics';
			courseDescription = '';
			selectedFiles = [];
			dispatch('close');
		}
	}

	function handleFileChange(event) {
		const files = event.target.files;
		if (files && files.length > 0) {
			selectedFiles = Array.from(files);
		} else {
			selectedFiles = [];
		}
	}

	function removeSelectedFile(index) {
		selectedFiles = selectedFiles.filter((_, i) => i !== index);
	}

	function handleSubmit() {
		if (courseName.trim()) {
			// Encode subject into description
			const encodedDescription = `[Subject: ${courseSubject}] ${courseDescription.trim()}`;
			
			dispatch('save', {
				id: editCourse ? editCourse.id : null,
				name: courseName.trim(),
				description: encodedDescription,
				files: selectedFiles
			});
		}
	}
</script>

{#if isOpen}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0">
		<div class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity" on:click={closeModal}></div>
		
		<div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg z-10 flex flex-col transform transition-all max-h-[90vh]">
			<div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
				<h3 class="text-xl font-bold text-gray-900 dark:text-white">
					{editCourse ? ($i18n ? $i18n.t('Edit Course') : 'Edit Course') : ($i18n ? $i18n.t('Create New Course') : 'Create New Course')}
				</h3>
				<button class="text-gray-400 hover:text-gray-500 focus:outline-none" on:click={closeModal} disabled={isSubmitting}>
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
			
			<div class="p-6 space-y-4 overflow-y-auto">
				<div>
					<label for="courseName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n ? $i18n.t('Course Name') : 'Course Name'} <span class="text-red-500">*</span>
					</label>
					<input 
						type="text" 
						id="courseName" 
						bind:value={courseName}
						disabled={isSubmitting}
						class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors"
						placeholder={$i18n ? $i18n.t('e.g., Advanced Mathematics 101') : 'e.g., Advanced Mathematics 101'}
					/>
				</div>

				<div>
					<label for="courseSubject" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n ? $i18n.t('Subject') : 'Subject'} <span class="text-red-500">*</span>
					</label>
					<div class="relative">
						<select 
							id="courseSubject" 
							bind:value={courseSubject}
							disabled={isSubmitting}
							class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors appearance-none"
						>
							{#each subjects as subject}
								<option value={subject.id}>{subject.icon} {$i18n ? $i18n.t(subject.label) : subject.label}</option>
							{/each}
						</select>
						<div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
						</div>
					</div>
				</div>
				
				<div>
					<label for="courseDesc" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n ? $i18n.t('Course Description') : 'Course Description'}
					</label>
					<textarea 
						id="courseDesc" 
						bind:value={courseDescription}
						disabled={isSubmitting}
						rows="3"
						class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white transition-colors resize-none"
						placeholder={$i18n ? $i18n.t('Briefly describe the topics and learning objectives...') : 'Briefly describe the topics and learning objectives...'}
					></textarea>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						{editCourse ? ($i18n ? $i18n.t('Upload Additional Materials') : 'Upload Additional Materials') : ($i18n ? $i18n.t('Upload Course Materials') : 'Upload Course Materials')}
					</label>
					
					<div class="flex items-center justify-center w-full">
						<label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 transition-colors">
							<div class="flex flex-col items-center justify-center pt-5 pb-6">
								<svg class="w-8 h-8 mb-3 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
								<p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
									<span class="font-semibold">{$i18n ? $i18n.t('Click to upload') : 'Click to upload'}</span> {$i18n ? $i18n.t('or drag and drop') : 'or drag and drop'}
								</p>
								<p class="text-xs text-gray-500 dark:text-gray-400">PDF, DOCX, TXT, MD</p>
							</div>
							<input id="dropzone-file" type="file" class="hidden" multiple on:change={handleFileChange} disabled={isSubmitting} />
						</label>
					</div>

					{#if selectedFiles.length > 0}
						<ul class="mt-4 space-y-2 max-h-32 overflow-y-auto pr-2">
							{#each selectedFiles as file, index}
								<li class="flex items-center justify-between p-2 text-sm bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
									<div class="flex items-center truncate mr-2">
										<svg class="w-4 h-4 mr-2 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
										<span class="truncate text-gray-700 dark:text-gray-300">{file.name}</span>
									</div>
									<button 
										type="button" 
										class="text-red-500 hover:text-red-700 p-1 flex-shrink-0"
										on:click={() => removeSelectedFile(index)}
										disabled={isSubmitting}
									>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
									</button>
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			</div>
			
			<div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-100 dark:border-gray-700 flex justify-end space-x-3 rounded-b-2xl">
				<button 
					type="button" 
					class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
					on:click={closeModal}
					disabled={isSubmitting}
				>
					{$i18n ? $i18n.t('Cancel') : 'Cancel'}
				</button>
				<button 
					type="button" 
					class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
					on:click={handleSubmit}
					disabled={!courseName.trim() || isSubmitting}
				>
					{#if isSubmitting}
						<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{/if}
					{editCourse ? ($i18n ? $i18n.t('Save Changes') : 'Save Changes') : ($i18n ? $i18n.t('Create Course') : 'Create Course')}
				</button>
			</div>
		</div>
	</div>
{/if}
