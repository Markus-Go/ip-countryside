# @TODO 
# if parameter i is set then -> install depencdencies (python module) -> Done 
# 


# $i forces installing dependencies


param($i)

if ($null -ne $i) {
    # pip install geopy
    # pip install Flask
    # pip install Flask-Assets libsass
    # pip install jsmin 
    # pip install md5hash
    # pip install netaddr
    # pip install -U git+https://github.com/VimT/MaxMind-DB-Writer-python
    # pip install maxminddb
    
    # $npm_path = $PSScriptRoot.ToString() + "\flaskr\static"
    # Write-Host $npm_path
    # npm --prefix  $npm_path install
}



py -3 -m venv venv 
venv\Scripts\activate

if ($null -eq $env:FLASK_APP) { $env:FLASK_APP = "flaskr" }
if ($null -eq $env:FLASK_ENV) { $env:FLASK_ENV = "development" }



flask run