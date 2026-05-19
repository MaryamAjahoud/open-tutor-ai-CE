<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount, getContext } from 'svelte';
	import TeacherSidebar from '$lib/components/teacher/TeacherSidebar.svelte';
	import { TUTOR_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');
	let isSidebarOpen = false;
	let showUserMenu = false;
	let loading = true;
	let saving = false;
	let copySuccess = false;
	let regenerating = false;
	let saveMessage = '';

	function logout() {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		user.set(null);
		goto('/auth');
	}

	let classroom = null;
	let settings = {
		language: 'fr-FR',
		timezone: 'Africa/Casablanca',
		notifications_enabled: true,
		email_notifications: true,
		theme: 'system'
	};

	const languages = [
		{ code: 'fr-FR', label: 'Français', flag: '🇫🇷' },
		{ code: 'en-US', label: 'English (US)', flag: '🇺🇸' },
		{ code: 'ar-MA', label: 'العربية (المغرب)', flag: '🇲🇦' }
	];

	const timezones = [
		{ value: 'Africa/Casablanca', label: 'Casablanca (GMT+1)' },
		{ value: 'Europe/Paris', label: 'Paris (GMT+2)' },
		{ value: 'Europe/London', label: 'London (GMT+1)' },
		{ value: 'America/New_York', label: 'New York (GMT-4)' },
		{ value: 'Asia/Dubai', label: 'Dubai (GMT+4)' }
	];

	const themes = [
		{ value: 'system', label: 'System', icon: '💻' },
		{ value: 'light', label: 'Light', icon: '☀️' },
		{ value: 'dark', label: 'Dark', icon: '🌙' }
	];

	async function fetchData() {
		loading = true;
		const token = localStorage.token;
		try {
			const [settingsRes, classroomRes] = await Promise.all([
				fetch(`${TUTOR_API_BASE_URL}/teacher/settings`, { headers: { Authorization: `Bearer ${token}` } }),
				fetch(`${TUTOR_API_BASE_URL}/teacher/classroom`, { headers: { Authorization: `Bearer ${token}` } })
			]);
			if (settingsRes.ok) settings = await settingsRes.json();
			if (classroomRes.ok) classroom = await classroomRes.json();
		} catch (e) { console.error(e); }
		loading = false;
	}

	function applyTheme(theme) {
		if (typeof document === 'undefined') return;
		const html = document.documentElement;
		if (theme === 'dark') {
			html.classList.add('dark');
		} else if (theme === 'light') {
			html.classList.remove('dark');
		} else {
			// system
			if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
				html.classList.add('dark');
			} else {
				html.classList.remove('dark');
			}
		}
		localStorage.setItem('theme', theme);
	}

	function applyLanguage(lang) {
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('locale', lang);
			if ($i18n?.changeLanguage) $i18n.changeLanguage(lang);
		}
		if (typeof document !== 'undefined') {
			const isRTL = lang.startsWith('ar');
			document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
			document.documentElement.lang = lang;
			localStorage.setItem('dir', isRTL ? 'rtl' : 'ltr');
		}
	}

	function onThemeChange(newTheme) {
		settings.theme = newTheme;
		applyTheme(newTheme);
		saveSettings();
	}

	function onLanguageChange(newLang) {
		settings.language = newLang;
		applyLanguage(newLang);
		saveSettings();
	}

	async function saveSettings() {
		saving = true;
		saveMessage = '';
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/settings`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.token}` },
				body: JSON.stringify(settings)
			});
			if (res.ok) {
				settings = await res.json();
				saveMessage = 'saved';
				applyTheme(settings.theme);
				applyLanguage(settings.language);
				setTimeout(() => saveMessage = '', 3000);
			} else { saveMessage = 'error'; }
		} catch (e) { saveMessage = 'error'; console.error(e); }
		saving = false;
	}

	async function copyCode() {
		if (!classroom?.class_code) return;
		try {
			await navigator.clipboard.writeText(classroom.class_code);
			copySuccess = true;
			setTimeout(() => copySuccess = false, 2000);
		} catch { /* fallback */ }
	}

	async function regenerateCode() {
		if (!confirm('Regenerate class code? Students with the old code will need the new one.')) return;
		regenerating = true;
		try {
			const res = await fetch(`${TUTOR_API_BASE_URL}/teacher/classroom/regenerate`, {
				method: 'POST',
				headers: { Authorization: `Bearer ${localStorage.token}` }
			});
			if (res.ok) classroom = await res.json();
		} catch (e) { console.error(e); }
		regenerating = false;
	}

	onMount(async () => {
		if (!$user) { goto('/auth'); return; }
		if ($user.role !== 'teacher' && $user.role !== 'admin') { goto(`/${$user.role}`); return; }
		await fetchData();
		applyTheme(settings.theme);
	});
</script>

<svelte:head><title>Settings | EduConnect</title></svelte:head>

<div class="h-screen bg-slate-50 dark:bg-slate-950 flex font-sans text-slate-800 dark:text-slate-200 overflow-hidden">
	<TeacherSidebar bind:isOpen={isSidebarOpen} />
	<div class="flex-1 md:ml-64 flex flex-col h-screen overflow-hidden">

		<header class="h-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 sticky top-0 z-30">
			<div class="flex items-center gap-4">
				<button class="md:hidden p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl" on:click={() => isSidebarOpen = true}>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
				</button>
				<div>
					<h1 class="text-xl font-bold text-slate-900 dark:text-white">Settings</h1>
					<p class="text-sm text-slate-500">Manage your preferences</p>
				</div>
			</div>
			{#if $user}
				<div class="relative">
					<button on:click={() => showUserMenu = !showUserMenu}
						class="flex items-center gap-3 pl-5 border-l border-slate-200 dark:border-slate-800 cursor-pointer group">
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
				<div class="max-w-3xl mx-auto space-y-6 animate-pulse">
					{#each Array(4) as _}<div class="h-40 bg-slate-200 dark:bg-slate-800 rounded-3xl"></div>{/each}
				</div>
			{:else}
				<div class="max-w-3xl mx-auto space-y-8">

					<!-- Class Code Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
						<div class="h-2 bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500"></div>
						<div class="p-8">
							<div class="flex items-center gap-3 mb-6">
								<div class="w-12 h-12 bg-indigo-50 dark:bg-indigo-500/10 rounded-2xl flex items-center justify-center text-2xl">🔑</div>
								<div>
									<h2 class="text-lg font-bold text-slate-900 dark:text-white">Class Code</h2>
									<p class="text-sm text-slate-500">Share this code with students to join your class</p>
								</div>
							</div>
							{#if classroom}
								<div class="flex items-center gap-4 flex-wrap">
									<div class="bg-slate-50 dark:bg-slate-800 border-2 border-dashed border-indigo-300 dark:border-indigo-500/40 rounded-2xl px-8 py-5 text-center">
										<p class="text-4xl font-black tracking-[0.3em] text-indigo-600 dark:text-indigo-400 font-mono">{classroom.class_code}</p>
										<p class="text-xs text-slate-400 mt-2">{classroom.student_count} student{classroom.student_count !== 1 ? 's' : ''} enrolled</p>
									</div>
									<div class="flex flex-col gap-2">
										<button on:click={copyCode} class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl shadow-md shadow-indigo-600/20 transition-all active:scale-95">
											{#if copySuccess}
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
												Copied!
											{:else}
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
												Copy Code
											{/if}
										</button>
										<button on:click={regenerateCode} disabled={regenerating} class="flex items-center gap-2 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-semibold rounded-xl transition-all disabled:opacity-40">
											<svg class="w-4 h-4 {regenerating ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
											Regenerate
										</button>
									</div>
								</div>
							{/if}
						</div>
					</div>

					<!-- Language Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
						<div class="flex items-center gap-3 mb-6">
							<div class="w-12 h-12 bg-emerald-50 dark:bg-emerald-500/10 rounded-2xl flex items-center justify-center text-2xl">🌍</div>
							<div>
								<h2 class="text-lg font-bold text-slate-900 dark:text-white">Language</h2>
								<p class="text-sm text-slate-500">Choose your preferred interface language</p>
							</div>
						</div>
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
							{#each languages as lang}
								<button on:click={() => onLanguageChange(lang.code)}
									class="flex items-center gap-3 p-4 rounded-2xl border-2 transition-all duration-200 hover:-translate-y-0.5 {settings.language === lang.code ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10 shadow-md shadow-indigo-500/10' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'}">
									<span class="text-2xl">{lang.flag}</span>
									<span class="text-sm font-semibold {settings.language === lang.code ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-700 dark:text-slate-300'}">{lang.label}</span>
									{#if settings.language === lang.code}
										<svg class="w-5 h-5 text-indigo-500 ml-auto" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
									{/if}
								</button>
							{/each}
						</div>
					</div>

					<!-- Theme Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
						<div class="flex items-center gap-3 mb-6">
							<div class="w-12 h-12 bg-purple-50 dark:bg-purple-500/10 rounded-2xl flex items-center justify-center text-2xl">🎨</div>
							<div>
								<h2 class="text-lg font-bold text-slate-900 dark:text-white">Theme</h2>
								<p class="text-sm text-slate-500">Choose your visual preference</p>
							</div>
						</div>
						<div class="grid grid-cols-3 gap-3">
							{#each themes as t}
								<button on:click={() => onThemeChange(t.value)}
									class="flex flex-col items-center gap-2 p-5 rounded-2xl border-2 transition-all duration-200 hover:-translate-y-0.5 {settings.theme === t.value ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10 shadow-md' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'}">
									<span class="text-2xl">{t.icon}</span>
									<span class="text-sm font-semibold {settings.theme === t.value ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-600 dark:text-slate-400'}">{t.label}</span>
								</button>
							{/each}
						</div>
					</div>

					<!-- Timezone Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
						<div class="flex items-center gap-3 mb-6">
							<div class="w-12 h-12 bg-amber-50 dark:bg-amber-500/10 rounded-2xl flex items-center justify-center text-2xl">⏰</div>
							<div>
								<h2 class="text-lg font-bold text-slate-900 dark:text-white">Timezone</h2>
								<p class="text-sm text-slate-500">Set your local timezone for deadlines</p>
							</div>
						</div>
						<select bind:value={settings.timezone} class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:text-white transition-all">
							{#each timezones as tz}
								<option value={tz.value}>{tz.label}</option>
							{/each}
						</select>
					</div>

					<!-- Notifications Section -->
					<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
						<div class="flex items-center gap-3 mb-6">
							<div class="w-12 h-12 bg-rose-50 dark:bg-rose-500/10 rounded-2xl flex items-center justify-center text-2xl">🔔</div>
							<div>
								<h2 class="text-lg font-bold text-slate-900 dark:text-white">Notifications</h2>
								<p class="text-sm text-slate-500">Manage how you receive updates</p>
							</div>
						</div>
						<div class="space-y-4">
							<label class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl cursor-pointer group hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
								<div>
									<p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Push Notifications</p>
									<p class="text-xs text-slate-400 mt-0.5">Get notified about new submissions</p>
								</div>
								<div class="relative">
									<input type="checkbox" bind:checked={settings.notifications_enabled} class="sr-only" />
									<div class="w-12 h-6 rounded-full transition-colors {settings.notifications_enabled ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}"></div>
									<div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform {settings.notifications_enabled ? 'translate-x-6' : ''}"></div>
								</div>
							</label>
							<label class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-2xl cursor-pointer group hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
								<div>
									<p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Email Notifications</p>
									<p class="text-xs text-slate-400 mt-0.5">Receive updates via email</p>
								</div>
								<div class="relative">
									<input type="checkbox" bind:checked={settings.email_notifications} class="sr-only" />
									<div class="w-12 h-6 rounded-full transition-colors {settings.email_notifications ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}"></div>
									<div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform {settings.email_notifications ? 'translate-x-6' : ''}"></div>
								</div>
							</label>
						</div>
					</div>

					<!-- Profile Section (read-only) -->
					{#if $user}
						<div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
							<div class="flex items-center gap-3 mb-6">
								<div class="w-12 h-12 bg-blue-50 dark:bg-blue-500/10 rounded-2xl flex items-center justify-center text-2xl">👤</div>
								<div>
									<h2 class="text-lg font-bold text-slate-900 dark:text-white">Profile</h2>
									<p class="text-sm text-slate-500">Your account information</p>
								</div>
							</div>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
								<div>
									<label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Name</label>
									<div class="px-4 py-3 bg-slate-50 dark:bg-slate-800 rounded-2xl text-sm text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">{$user.name}</div>
								</div>
								<div>
									<label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Email</label>
									<div class="px-4 py-3 bg-slate-50 dark:bg-slate-800 rounded-2xl text-sm text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">{$user.email}</div>
								</div>
								<div>
									<label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Role</label>
									<div class="px-4 py-3 bg-slate-50 dark:bg-slate-800 rounded-2xl text-sm text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 capitalize">{$user.role}</div>
								</div>
							</div>
						</div>
					{/if}

					<!-- Save Button -->
					<div class="flex items-center gap-4 pb-10">
						<button on:click={saveSettings} disabled={saving}
							class="flex items-center gap-2 px-8 py-3.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold rounded-2xl shadow-lg shadow-indigo-600/20 transition-all hover:-translate-y-0.5 active:scale-95">
							{#if saving}
								<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
							{/if}
							Save Settings
						</button>
						{#if saveMessage === 'saved'}
							<span class="text-sm font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 animate-fade-in">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
								Settings saved!
							</span>
						{:else if saveMessage === 'error'}
							<span class="text-sm font-semibold text-rose-600">Failed to save. Try again.</span>
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

<style>
	.animate-fade-in { animation: fadeIn 0.3s ease-out; }
	@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
</style>
