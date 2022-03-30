# IP-Countryside
==============

This tool creates an ip-to-country database, which can be used in multiple 
applications for geolocating internet users based on  their IP address.

<b>If you only need the ip2country database itself (not the program creating 
it),  
you can <a 
href='https://github.com/Markus-Go/ip-countryside/blob/downloads/ip2country.zip?raw=true'>download 
it here</a> (updated weekly).</b>

A demo can be found <a href='https://www.goldiges.de/ip-countryside/' target='_BLANK'>here</a>.

## Detailed Information
--------------------
....


## Prerequisite
------------

The following files are required to build the database. The script 'ip_countryside_downloader.py' 
can be used for downloading them:

1.  ripencc Delegation file  
   ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
2.  ripencc Database  
   ftp://ftp.ripe.net/ripe/dbase/split
3.  apnic Delegation file  
   ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
4.  apnic Database  
   ftp://ftp.apnic.net/apnic/whois-data/APNIC/split
5.  arin Delegation file  
   ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest
6.  lacnic Delegation file  
   ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
7.  afrinic Delegation file  
   ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest


## Installation:
------------

  Dependencies:

  run theses commands in the root directory:

  - py -3 -m venv venv
  - venv\Scripts\activate
  - pip install geopy
  - pip install Flask
  - pip install Flask-Assets libsass
  - pip install jsmin 
  - pip install md5hash

  
  Flask framework:
  
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

## How it works
------------
...

===================================================================

## Copyright/ License/ Credits
---------------------------

Copyright 2006-2007 Deutsches Forschungszentrum fuer Kuenstliche Intelligenz  
Copyright 2008-2022 Markus Goldstein

This is free software. Licensed under the MIT (LICENSE.txt).  
There is NO WARRANTY, to the extent permitted by law.

![http://madm.dfki.de/lib/tpl/dfki/images/logo.jpg](http://madm.dfki.de/lib/tpl/dfki/images/logo.jpg)