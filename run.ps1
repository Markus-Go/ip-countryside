# @TODO 
# if parameter i is set then -> install depencdencies (python module) 


if ($null -eq $env:FLASK_APP) { $env:FLASK_APP = "flaskr" }
if ($null -eq $env:FLASK_ENV) { $env:FLASK_ENV = "development" }
flask run


