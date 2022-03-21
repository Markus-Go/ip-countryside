
To Run flask:

Windows (Power Shell & Visual Studio Code):

- py -3 -m venv venv

- venv\Scripts\activate
- pip install Flask

- $env:FLASK_APP = "ipcountryside"  
  $env:FLASK_ENV = "development"

- flask run


More Info: https://flask.palletsprojects.com/en/2.0.x/patterns/packages/

===================================================================

.
├── static                   # Compiled files
├── assets                   # Source files 
├── templates                # HTML files
├── __init__                 # Contains Flask application object creation
├── LICENSE
└── README.md

