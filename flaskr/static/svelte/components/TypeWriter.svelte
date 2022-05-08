<script>

  	import Typewriter from 'svelte-typewriter'
	import { onMount } from 'svelte';

    export let text		// text to be type written
	export let speed	// milliseconds between each letter
	
	let isMounted = false

	onMount(() => setTimeout(
		() => {
			isMounted = true
		}, 1
	));

</script>

{#if isMounted}

	<Typewriter interval={speed}>
		{text}
	</Typewriter>

{/if}