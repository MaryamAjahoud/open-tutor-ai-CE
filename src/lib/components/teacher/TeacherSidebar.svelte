<script>
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { user } from '$lib/stores';

	export let isOpen = false;

	const i18n = getContext('i18n');

	function logout() {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		user.set(null);
		goto('/auth');
	}

	// Navigation items
	const navItems = [
		{
			id: 'dashboard',
			label: 'Dashboard',
			href: '/teacher',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>`
		},
		{
			id: 'courses',
			label: 'Courses',
			href: '/teacher/courses',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>`
		},
		{
			id: 'announcements',
			label: 'Announcements',
			href: '/teacher/announcements',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path></svg>`
		},
		{
			id: 'students',
			label: 'Students',
			href: '/teacher/students',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>`
		},
		{
			id: 'assignments',
			label: 'Assignments',
			href: '/teacher/assignments',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>`
		},
		{
			id: 'settings',
			label: 'Settings',
			href: '/teacher/settings',
			icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`
		}
	];
</script>

<aside
	class="{isOpen
		? 'translate-x-0'
		: '-translate-x-full'} md:translate-x-0 fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-slate-300 border-r border-slate-800 transition-transform duration-300 ease-in-out flex flex-col shadow-2xl md:shadow-none"
>
	<div class="h-20 flex items-center px-6 border-b border-slate-800">
		<div class="flex items-center gap-3">
			<div class="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/20">O</div>
			<div class="text-xl font-bold tracking-tight text-white">
				Open Tutor
			</div>
		</div>
	</div>

	<nav class="flex-1 px-4 py-8 space-y-1.5 overflow-y-auto">
		{#each navItems as item}
			<a
				href={item.href}
				class="flex items-center px-4 py-3 rounded-xl transition-all duration-200 group {
					$page.url.pathname === item.href || ($page.url.pathname.startsWith(item.href) && item.href !== '/teacher')
						? 'bg-indigo-500/10 text-indigo-400 font-semibold'
						: 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
				}"
			>
				<div class="{$page.url.pathname === item.href ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'} transition-colors">
					{@html item.icon}
				</div>
				<span class="ml-3 text-sm tracking-wide">{$i18n ? $i18n.t(item.label) : item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="p-4 border-t border-slate-800 mt-auto space-y-3">
		<!-- Logout button -->
		<button
			on:click={logout}
			class="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all duration-200 group"
		>
			<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
			</svg>
			<span class="text-sm font-semibold">{$i18n ? $i18n.t('Logout') : 'Déconnexion'}</span>
		</button>

		<!-- Help card -->
		<div class="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50 relative overflow-hidden group hover:border-slate-600 transition-colors">
			<div class="absolute -right-4 -top-4 w-16 h-16 bg-indigo-500/10 rounded-full blur-xl group-hover:bg-indigo-500/20 transition-colors"></div>
			<h4 class="text-sm font-semibold text-slate-200 mb-1">{$i18n ? $i18n.t('Need Help?') : 'Need Help?'}</h4>
			<p class="text-xs text-slate-400 mb-3 leading-relaxed">{$i18n ? $i18n.t('Check our teacher guides') : 'Check our teacher guides'}</p>
			<a href="/docs" class="text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 py-2 px-4 rounded-xl w-full inline-block text-center transition-all shadow-md shadow-indigo-900/20 active:scale-95">
				{$i18n ? $i18n.t('View Guides') : 'View Guides'}
			</a>
		</div>
	</div>
</aside>

<!-- Overlay for mobile -->
{#if isOpen}
	<div
		class="fixed inset-0 bg-gray-900/50 dark:bg-black/50 z-40 md:hidden backdrop-blur-sm transition-opacity"
		on:click={() => (isOpen = false)}
		on:keydown={(e) => e.key === 'Escape' && (isOpen = false)}
		role="button"
		tabindex="0"
	></div>
{/if}
