<script>
    import {isIP} from 'is-ip';
    
    export let ip
    console.log(ip)
    let  isValid
    $: api_url = "/api?ip=" + ip  

    let response_json

async function handle_search_by_api() {

    isValid = ValidateIPaddress(ip)

    if(isValid)
        await fetch(api_url)
        .then(response => response.json())
        .then(data => {

            response_json = syntaxHighlight(data)
            
        }).catch(error => {
            console.error(error);
            response_json = null
        })
    else {
        
        response_json = { "status": "fail", "message":"unvalid input", "input":ip }
        response_json  = syntaxHighlight(response_json)
        console.log(response_json)
    }
    
    ip = "" 
    
}

function ValidateIPaddress(ip) {  
	return isIP(ip) 
} 


</script>
    

<div class="col-12 col-md-8 m-auto">
    
    <h2 class="api__block__title text-center m-auto py-5">API Demo</h2>

    <div class="api__block_content d-flex pb-3">

        <div class="input-group mr-2">

            <input bind:value="{ip}" type="text" class="form-control " name="ip" size = 15 placeholder="Enter an IPv4 or IPv6 address...">

        </div>

        <div class="input-group-append ml-2">

            <button on:click={handle_search_by_api} class="btn btn-primary" type="button" value="Find">search</button>

        </div>

    </div>

    
    {#if response_json}
    
        <div class="p-3" style="background-color: #f5f2f0;">
            
            {@html response_json}
                
        </div>
    
    {/if}
        

</div>
    