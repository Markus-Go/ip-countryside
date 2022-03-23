import os
from sys import flags


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

    # a simple page that says hello
    @app.route('/', methods=['GET'])
    def index():

        hello_string = "tss is a test"

        #ipaddress = os.popen('curl -s ifconfig.me').readline()
        ipaddress = ''
        address = "Ulm"
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        country = "none"
        flag = "none"

        if request.method == 'GET' and request.args.get('ip') is not None:
            ipaddress = request.args.get('ip')
            country = get_country_code(ipaddress)[0] 
            flag = get_country_code(ipaddress)[1]

        return render_template('index.html', str=hello_string, ip=ipaddress, lat=lat, lon=lon, add=address, flag=flag, country=country)

    return app
