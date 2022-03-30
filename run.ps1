# @TODO 
# if parameter i is set then -> install depencdencies (python module) 

# - py -3 -m venv venv
# - venv\Scripts\activate
# - pip install geopy
# - pip install Flask
# - pip install Flask-Assets libsass
# - pip install jsmin 
# - pip install md5hash

if ($null -eq $env:FLASK_APP) { $env:FLASK_APP = "flaskr" }
if ($null -eq $env:FLASK_ENV) { $env:FLASK_ENV = "development" }
flask run


