from operator import ge, truediv
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings
import ipaddress
from datetime import datetime

from flask import Flask, request
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

         
        ip_from     = "-"
        ip_to       = "-"
        country     = "-" 
        registry    = ""
        date        = "-"
        flag        = "Arrr"
        comment     = "No Valid IP-Adress"
        lat         = 0
        lon         = 0
        isValid     = False

        if request.method == 'GET' and request.args.get('ip') is not None:
            
            ip_address = request.args.get('ip')
            
            if not ip_address:

                ip_address = os.popen('curl -s ifconfig.me').readline()
                temp = get_record_by_ip(ip_address)

                if temp:

                    ip_from     = ipaddress.ip_address(temp[0])
                    ip_to       = ipaddress.ip_address(temp[1])
                    country     = COUNTRY_DICTIONARY[temp[2]] 
                    registry    = temp[3]
                    date        = datetime.strptime(str(temp[4]), '%Y%m%d').strftime('%Y.%m.%d')
                    comment     = temp[7]
                    isValid     = True
                    flag        = temp[2]
                    
                try:
                    geolocator = Nominatim(user_agent="Your_Name")
                    location = geolocator.geocode(ip_from)
                    lat = location.latitude
                    lon = location.longitude

                except:
                    isValid = False
                    lat = 0
                    lon = 0
                    comment = "Karte aktuell Leider nicht Verfügbar"

            else:
                
                temp = get_record_by_ip(ip_address)

                if temp:

                    ip_from     = ipaddress.ip_address(temp[0])
                    ip_to       = ipaddress.ip_address(temp[1])
                    country     = COUNTRY_DICTIONARY[temp[2]] 
                    registry    = temp[3]
                    date        = datetime.strptime(str(temp[4]), '%Y%m%d').strftime('%Y.%m.%d')
                    comment     = temp[7]
                    isValid     = True
                    flag        = temp[2]

                try:

                    [lat, lon]  = get_geolocation(country)

                except:

                    lat = 0
                    lon = 0
                    isValid = False
                    comment = "Karte aktuell Leider nicht Verfügbar"
                 
        else:
           
            ip_address = os.popen('curl -s ifconfig.me').readline()
            temp = get_record_by_ip(ip_address)

            
            if temp:

                ip_from     = ipaddress.ip_address(temp[0])
                ip_to       = ipaddress.ip_address(temp[1])
                country     = COUNTRY_DICTIONARY[temp[2]] 
                registry    = temp[3]
                date        = datetime.strptime(str(temp[4]), '%Y%m%d').strftime('%Y.%m.%d')
                comment     = temp[7]
                isValid     = True
                flag        = temp[2]

            try:
                geolocator = Nominatim(user_agent="Your_Name")
                location = geolocator.geocode(ip_from)
                lat = location.latitude
                lon = location.longitude
                
            except:

                isValid = False
                lat = 0
                lon = 0
                comment = "Karte aktuell Leider nicht Verfügbar"

        output = render_template('index.html', ip_from=ip_from, ip_to=ip_to, lat=lat, lon=lon, flag=flag, country=country, registry=registry, comment=comment, date=date, isValid=isValid) 
        
        return output 

    return app


def get_geolocation(address):

    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(address)
    lat = location.latitude
    lon = location.longitude
        
    return [lat, lon]

def validate_record(record):
    pass