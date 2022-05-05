from fileinput import filename
from operator import ge, truediv
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings
import ipaddress
from datetime import datetime
import math
from click import command

from flask import Flask, request, send_from_directory
from flask import render_template
from flask import request, jsonify
from flask_assets import Bundle, Environment

from geopy.geocoders import Nominatim
from config import *


from ip_countryside_utilities import get_record_by_ip;
from ip_countryside_db import read_mmdb, read_db_record
import json


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.debug = True

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        ASSETS_DEBUG=True,
        DEBUG=truediv
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
     
    # Adds SCSS and JS from node js to the website 
    assets = Environment(app)
    assets.url = app.static_url_path
    assets.debug = True

    # Bootstrap JS files
    js = Bundle(
        "node_modules/jquery/dist/jquery.min.js",
        "node_modules/popper.js/dist/popper.min.js",
        "node_modules/bootstrap/dist/js/bootstrap.min.js",
        filters="jsmin",
        output="dist/javascript/generated.js"
    )
  
    # Bootstrap and SCSS files
    scss = Bundle(
        "src/scss/main.scss",  # 1. will read this scss file and generate a css file based on it
        filters="libsass",   # using this filter: https://webassets.readthedocs.io/en/latest/builtin_filters.html#libsass
        output="dist/css/scss-generated.css",  # 2. and output the generated .css file in the static/css folder
        extra={'rel': 'stylesheet/css'}
    )
    
    assets.register("js_all", js)
    assets.register("scss_all", scss) 

    # Remove when not developing !!!!!!!!!!
    js.build()
    scss.build()
   
    
    @app.route('/', methods=['GET'])
    def index():

        record = []
        ip_from     = " "
        ip_to       = " "
        country     = "-" 
        flag        = "-"
        lat         = 0
        lon         = 0
        comment     = "-"
        isValid     = False
        hasLocation = False

        # process ip search request
        if request.method == 'GET':
            
            ip_address = request.args.get('ip', None)
           
            if ip_address is None or ip_address == "":

                ip_address = os.popen('curl -s ifconfig.me').readline()
                record = get_record_by_ip(ip_address)

            else:
                
                ip_address = ip_address.strip()
                record = get_record_by_ip(ip_address)

            if record:
                
                ip_from     = record[0]
                ip_to       = record[1]
                flag        = record[2]
                country     = COUNTRY_DICTIONARY[record[2]] 
                status      = record[3]
                isValid     = True
               
                if record[2] == "ZZ":
                    
                    comment = status
                    lat = 0
                    lon = 0

                else: 
        
                    [lat, lon, isValid, hasLocation]  = get_geolocation(country)
             
            else:

                isValid = False

        # get download files data for templates
        db_files = get_db_files()
        
        output = render_template('index.html', ip_from=ip_from, ip_to=ip_to, lat=lat, lon=lon, flag=flag, country=country, isValid=isValid, hasLocation=hasLocation, ip=ip_address, comment=comment, db_files=db_files) 
        
        return output

    @app.route('/api/ip', methods=['GET'])
    def api_id():

        if 'id' in request.args:
            id = request.args['id']
            return jsonify(read_mmdb(id))

        else:
            return "No id field provided. Please specify an id."

    @app.route('/download')
    def download_db_file():
         
        fname = request.args.get('fname', None)

        return send_from_directory(DEL_FILES_DIR, fname, as_attachment=True)


    return app


def get_geolocation(address):

    try:

        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        isValid = True
        hasLocation = True

    except:
        
        lat = 0
        lon = 0
        isValid = False
        hasLocation = False

    return [lat, lon, isValid, hasLocation]


def get_db_files():

    db_files = [
        IP2COUNTRY_DB          ,
        IP2COUNTRY_DB_IPV4     ,
        IP2COUNTRY_DB_IPV6     ,
        IP2COUNTRY_DB_JSON     ,   
        IP2COUNTRY_DB_YAML     ,  
        IP2COUNTRY_DB_MYSQL    ,
        IP2COUNTRY_DB_SQLLITE  ,
        IP2COUNTRY_DB_MMDB_V4  ,  
        IP2COUNTRY_DB_MMDB_V6  ,   
    ]

    data = []

    for file in db_files:

        if os.path.exists(file):
            
            data.append(os.path.basename(file))
            
    return data