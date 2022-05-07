import API from './components/API.svelte';


let API_Block = document.getElementById("api__block")

const app = new API({
	
	target: API_Block,
	props: {
		ip: ip
	}

});


export default app;