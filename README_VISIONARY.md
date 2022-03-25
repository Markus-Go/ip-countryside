
To Run flask:

Windows (Power Shell & Visual Studio Code):

- py -3 -m venv venv

- venv\Scripts\activate
- pip install Flask
- pip install Flask-Scss
- $env:FLASK_APP = "flaskr"  
  $env:FLASK_ENV = "development"

- flask run


Nützliche Tools: 

https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv
https://github.com/mechatroner/RBQL

More Info: https://flask.palletsprojects.com/en/2.0.x/patterns/packages/

===================================================================

.
├── static                   # Compiled files
├── assets                   # Source files 
├── templates                # HTML files
├── __init__                 # Contains Flask application object creation
├── LICENSE
└── README.md

