import API from './components/API.svelte';
import TypeWriter from './components/TypeWriter.svelte';


let API_Block = document.getElementById("api__block")

const api = new API({
	
	target: API_Block,
	props: {
		ip: ip ? ip : ""
	}

});


// @Todo iterate over all elements with this class
let type_writer_elem = document.getElementsByClassName("typewriter__block")

if(type_writer_elem.length) {
	
	type_writer_elem = type_writer_elem[0]

	let elem_text = type_writer_elem.textContent
	type_writer_elem.textContent = ""

	const type_writer = new TypeWriter({
		
		target: type_writer_elem,
		props: {
			text: elem_text,
			speed: 100
		}

	});
}