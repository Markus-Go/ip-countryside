import API from './components/App.svelte';


let API_Block = document.body.getElementsByClassName("api__block")[0]

const app = new App({
	
	target: API_Block,
	props: {
	
	}

});


export default app;
