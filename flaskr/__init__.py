from operator import ge, truediv
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings

from flask import Flask, request
from flask import render_template
from flask import request, jsonify
from flask_assets import Bundle, Environment

from geopy.geocoders import Nominatim


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

        if request.method == 'GET' and request.args.get('ip') is not None:
            ipaddress = request.args.get('ip')
            if ipaddress == "":
                ipaddress = os.popen('curl -s ifconfig.me').readline()
                temp = get_record_by_ip(ipaddress)
                country = temp[0] 
                flag = temp[1]
                try:
                    city = temp[2]
                except:
                    city ="-"
                address = temp[0]
                isValid = True
                comment = "-"
                try:
                    geolocator = Nominatim(user_agent="Your_Name")
                    location = geolocator.geocode(address)
                    lat = location.latitude
                    lon = location.longitude
                except:
                    isValid = False
                    lat = 0
                    lon = 0
                    comment = "Karte aktuell Leider nicht Verfügbar"
            else:
                temp = get_record_by_ip(ipaddress)
                if temp == False:
                    country = "-" 
                    flag = "Arrr"
                    city = "-"
                    comment = "No Valid IP-Adress"
                    lat = 0
                    lon = 0
                    address = "-"
                    isValid = False
                else:
                    country = temp[0] 
                    flag = temp[1]
                    address = temp[0]
                    try:
                        city = temp[2]
                    except:
                        city ="-"
                    isValid = True
                    comment = "-"
                    try:
                        geolocator = Nominatim(user_agent="Your_Name")
                        location = geolocator.geocode(address)
                        lat = location.latitude
                        lon = location.longitude
                    except:
                        isValid = False
                        lat = 0
                        lon = 0
                        comment = "Karte aktuell Leider nicht Verfügbar"
        else:
            ipaddress = os.popen('curl -s ifconfig.me').readline()
            temp = get_record_by_ip(ipaddress)
            country = temp[0] 
            flag = temp[1]
            try:
                    city = temp[2]
            except:
                city ="-"
            address = temp[0]
            comment = "-"
            isValid = True
            try:
                geolocator = Nominatim(user_agent="Your_Name")
                location = geolocator.geocode(address)
                lat = location.latitude
                lon = location.longitude
            except:
                isValid = False
                lat = 0
                lon = 0
                comment = "Karte aktuell Leider nicht Verfügbar"

        output = render_template('index.html', ip=ipaddress, lat=lat, lon=lon, add=address, flag=flag, country=country, comment=comment, isValid=isValid, city=city) 
        
        return output

    @app.route('/api/ip', methods=['GET'])
    def api_id():

        if 'id' in request.args:
            id = str(request.args['id'])
            results = read_mmdb("131.255.44.4")
            return jsonify(results)

        else:
            return "No id field provided. Please specify an id."



    return app
