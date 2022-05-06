import API from './components/API.svelte';


let API_Block = document.body.getElementsByClassName("api__block")[0]

const app = new API({
	
	target: API_Block,
	props: {
	
	}

});


export default app;
