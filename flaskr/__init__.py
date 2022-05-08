from fileinput import filename
from operator import ge, truediv
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings
import ipaddress
from datetime import datetime
import math
import json

from click import command

from flask import Flask, request, send_from_directory
from flask import render_template
from flask import request, jsonify
from flask_assets import Bundle, Environment

from ip_countryside_utilities import get_record_by_ip
from ip_countryside_db import read_mmdb, get_db_files, read_db_record
from geopy.geocoders import Nominatim


from config import *

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
        "dist/javascript/svelte_bundle.js",
        filters="jsmin",
        output="dist/javascript/generated.js"
    )
    
    assets.register("js_all", js)
    
    # Remove when not developing !!!!!!!!!!
    js.build()
  
    @app.route('/', methods=['GET'])
    def index():

        record      = []
        ip_from     = " "
        ip_to       = " "
        country     = "-" 
        flag        = "-"
        lat         = 0
        lon         = 0
        comment     = "-"
        isValid     = False
        hasLocation = False
        last_update = datetime.fromtimestamp(os.path.getmtime(IP2COUNTRY_DB_SQLLITE)).strftime('%Y-%m-%d %H:%M:%S')

        # process ip search request
        if request.method == 'GET':
            
            ip_address = request.args.get('ip', None)
           
            if ip_address is None or ip_address == "":

                ip_address = request.remote_addr
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
        
        output = render_template('index.html', ip_from=ip_from, ip_to=ip_to, lat=lat, lon=lon, flag=flag, country=country, isValid=isValid, hasLocation=hasLocation, ip=ip_address, comment=comment, db_files=db_files, last_update=last_update) 

        return output

    @app.route('/api', methods=['GET'])
    def api_id():

        if 'ip' in request.args:
            id = request.args['ip']
            return jsonify(read_mmdb(id))

        else:
            return "No id field provided. Please specify an id."

    @app.route('/download')
    def download_db_file():
         
        fname = request.args.get('fname', None)

        return send_from_directory(DB_DIR, fname, as_attachment=True)

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