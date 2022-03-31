# @TODO 
# if parameter i is set then -> install depencdencies (python module) 

# $i forces installing dependencies
# $u forces updating packets

param($i, $u)
if ($null -ne $i) {
    # pip install geopy
    # pip install Flask
    # pip install Flask-Assets libsass
    # pip install jsmin 
    # pip install md5hash
    
    # $npm_path = $PSScriptRoot.ToString() + "\flaskr\static"
    # Write-Host $npm_path
    # npm --prefix  $npm_path install
    

}

if ($null -ne $u) {
    
}


# py -3 -m venv venv 


# venv\Scripts\activate


if ($null -eq $env:FLASK_APP) { $env:FLASK_APP = "flaskr" }
if ($null -eq $env:FLASK_ENV) { $env:FLASK_ENV = "development" }
# flask run