Flask framework:

Installation & Dependencies:

  run theses commands in the root directory:

  - py -3 -m venv venv
  - venv\Scripts\activate
  - pip install Flask
  - pip install Flask-Assets libsass
  - pip install geopy
  - pip install jsmin 
  - pip install geotext 

  static assets uses node_modules, if you can install all 
  dependencies simlpy with the following command:

  - npm install 

Starting the app:

  - $env:FLASK_APP = "flaskr"  
  - $env:FLASK_ENV = "development"
  - flask run

  also see https://flask.palletsprojects.com/en/2.0.x/installation/
 
  Docs: https://flask.palletsprojects.com/en/2.0.x/patterns/packages/

Templating:

  Flask uses for its templating Jinja. It worth it to have a look
  there! (see https://jinja.palletsprojects.com/en/3.0.x/templates/)

Useful Tools: 

  - Extension for csv reader for vs code: https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv
  - Rainbow Extension has an integrated SQL-like interface for csv files: https://github.com/mechatroner/RBQL
  - Large Text File Viewer: https://web.archive.org/web/20140908181354fw_/http://swiftgear.com/ltfviewer/features.html
  - Jinja Templating: https://jinja.palletsprojects.com/en/3.0.x/templates/

===================================================================

.
├── static                   # Compiled files
├── assets                   # Source files 
├── templates                # HTML files
├── __init__                 # Contains Flask application object creation
├── LICENSE
└── README.md

