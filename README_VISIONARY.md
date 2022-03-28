Flask framework:

Installation:

  Windows (Power Shell & Visual Studio Code) in the root directory 
  of the project run:

  - py -3 -m venv venv
  - venv\Scripts\activate
  - pip install Flask
  - pip install Flask-Scss
  - $env:FLASK_APP = "flaskr"  
  - $env:FLASK_ENV = "development"
  - flask run

  also see https://flask.palletsprojects.com/en/2.0.x/installation/
 
  Docs: https://flask.palletsprojects.com/en/2.0.x/patterns/packages/

Useful Tools: 

  - Extension for csv reader for vs code: https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv
  - Rainbow Extension has an integrated SQL-like interface for csv files: https://github.com/mechatroner/RBQL
  - Large Text File Viewer: https://web.archive.org/web/20140908181354fw_/http://swiftgear.com/ltfviewer/features.html


===================================================================

.
├── static                   # Compiled files
├── assets                   # Source files 
├── templates                # HTML files
├── __init__                 # Contains Flask application object creation
├── LICENSE
└── README.md

