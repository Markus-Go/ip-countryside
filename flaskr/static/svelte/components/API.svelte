<script>

    let ip
    $: api_url = location.href.split('#')[0] + "api?ip=" + ip  
    let response_json


async function handle_search_by_api() {

    await fetch(api_url)
    .then(response => response.json())
    .then(data => {

        response_json = syntaxHighlight(data)
        console.debug(response_json)
        
    }).catch(error => {
        console.error(error);
        response_json = null
    })
    
    ip = "" 
}

function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'text-success';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'text-primary';
            } else {
                cls = 'text-info';
            }
        } else if (/true|false/.test(match)) {
            cls = 'text-danger';
        } else if (/null/.test(match)) {
            cls = 'text-secondary';
        }
        return '<span class="' + cls + '">' + match + '</span>';
        })
}

</script>
    

<div class="col-12 col-md-8 m-auto">
    
    <h2 class="api__block__title text-center m-auto py-5">API Demo</h2>

    <div class="api__block_content d-flex pb-3">

        <div class="input-group mr-2">

            <input bind:value="{ip}" type="text" class="form-control " name="ip" size = 15 placeholder="Enter an IPv4 or IPv6 address...">

        </div>

        <div class="input-group-append ml-2">

            <button on:click={handle_search_by_api} class="btn btn-primary" type="submit" value="Find">search</button>

        </div>

    </div>

    
    {#if response_json}
    
        <div class="p-3" style="background-color: #f5f2f0;">
            
            {@html response_json}
                
        </div>
    
    {/if}
        

</div>
    