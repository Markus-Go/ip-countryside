from operator import ge, truediv
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings
import ipaddress
from datetime import datetime
import math

from flask import Flask, request, redirect
from flask import render_template
from flask_assets import Bundle, Environment

from geopy.geocoders import Nominatim
from config import COUNTRY_DICTIONARY


from ip_countryside_utilities import get_record_by_ip;


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
        registry    = "-"
        date        = "-"
        flag        = "-"
        comment     = "-"
        lat         = 0
        lon         = 0
        isValid     = False

        if request.method == 'GET':
            
            ip_address = request.args.get('ip', None)

            if ip_address is None or ip_address == "":

                ip_address = os.popen('curl -s ifconfig.me').readline()
                record = get_record_by_ip(ip_address)

            else:
    
                record = get_record_by_ip(ip_address)

            if record:

                ip_from     = ipaddress.ip_address(record[0])
                ip_to       = ipaddress.ip_address(record[1])
                country     = COUNTRY_DICTIONARY[record[2]] 
                registry    = record[3]
                date        = datetime.strptime(str(record[4]), '%Y%m%d').strftime('%Y.%m.%d')
                status      = record[6]
                comment     = record[7] if record[7]  else "-"
                isValid     = True
                flag        = record[2]
               
                if record[2] == "ZZ":

                    comment = status
                    lat = 0
                    lon = 0

                else: 
        
                    [lat, lon, isValid]  = get_geolocation(country)
             
            else:

                isValid = False


        output = render_template('index.html', ip_from=ip_from, ip_to=ip_to, lat=lat, lon=lon, flag=flag, country=country, registry=registry, comment=comment, date=date, isValid=isValid) 
        
        return output 
    
    return app


def get_geolocation(address):

    try:

        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        isValid = True

    except:
        
        lat = 0
        lon = 0
        isValid = False

    return [lat, lon, isValid]