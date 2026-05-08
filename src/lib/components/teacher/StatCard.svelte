<script>
	export let title = '';
	export let value = '';
	export let icon = '';
	export let trend = null; // e.g., { value: '+5%', isPositive: true }
	export let colorClass = 'text-blue-600 dark:text-blue-400';
	export let bgClass = 'bg-blue-50 dark:bg-blue-900/20';
</script>

<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 hover:shadow-md transition-shadow duration-300 group">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-gray-500 dark:text-gray-400 text-sm font-medium">{title}</h3>
		<div class="p-2 rounded-lg {bgClass} {colorClass} group-hover:scale-110 transition-transform duration-300">
			{@html icon}
		</div>
	</div>
	
	<div class="flex items-end justify-between">
		<div>
			<span class="text-3xl font-bold text-gray-900 dark:text-white">{value}</span>
		</div>
		
		{#if trend}
			<div class="flex items-center text-sm font-medium {trend.isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} bg-opacity-10 px-2 py-1 rounded-full {trend.isPositive ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'}">
				{#if trend.isPositive}
					<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
				{:else}
					<svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path></svg>
				{/if}
				{trend.value}
			</div>
		{/if}
	</div>
</div>
