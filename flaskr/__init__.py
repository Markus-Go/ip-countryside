import os
from sys import flags


from flask import Flask, request
from flask import render_template
from geopy.geocoders import Nominatim

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
    @app.route('/')
    def variables():
        hello_string = "tss is a test"
        ipaddress = os.popen('curl -s ifconfig.me').readline()

        address = "Ulm"
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        flag = "de"

        return render_template('indextest.html', str=hello_string, ip=ipaddress, lat=lat, lon=lon, add=address, flag=flag)

    @app.route('/', methods=['POST'])
    def my_form_post():
        hello_string = "tss is a test"
        ipaddress = os.popen('curl -s ifconfig.me').readline()

        address = "Ulm"
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        flag = request.form['text']

        return render_template('indextest.html', str=hello_string, ip=ipaddress, lat=lat, lon=lon, add=address, flag=flag)

    return app
