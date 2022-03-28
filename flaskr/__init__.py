from operator import ge
import os
from pickle import TRUE
from sys import flags
from warnings import catch_warnings


from flask import Flask, request
from flask import render_template
from geopy.geocoders import Nominatim

from del_files_parser import get_country_code;

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.debug = True

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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

    @app.route('/', methods=['GET'])
    def index():
        if request.method == 'GET' and request.args.get('ip') is not None:
            ipaddress = request.args.get('ip')
            if ipaddress == "":
                ipaddress = os.popen('curl -s ifconfig.me').readline()
                temp = get_country_code(ipaddress)
                country = temp[0] 
                flag = temp[1]
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
                temp = get_country_code(ipaddress)
                if temp == False:
                    country = "-" 
                    flag = "Arrr"
                    comment = "No Valid IP-Adress"
                    lat = 0
                    lon = 0
                    address = "-"
                    isValid = False
                else:
                    country = temp[0] 
                    flag = temp[1]
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
            ipaddress = os.popen('curl -s ifconfig.me').readline()
            temp = get_country_code(ipaddress)
            country = temp[0] 
            flag = temp[1]
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

        return render_template('index.html', ip=ipaddress, lat=lat, lon=lon, add=address, flag=flag, country=country, comment=comment, isValid=isValid)

    return app
