import os
from typing import Optional, Any

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp

# This is a command line tool which takes a spotify user's library and creates a playlist for them based on the weather
# Understanding how to use the spotify api with examples from https://github.com/plamere/spotipy
# Also flask login help here https://github.com/plamere/spotipy/issues/287

import spotipy
import spotipy.oauth2
import os
import urllib
import sys
from datetime import date
from os import environ
import spotipy.util as util
import zipcodes
import json
import requests

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up global variables for login and spotify login stuff (this part comes mostly from documentation https://spotipy.readthedocs.io/en/2.12.0/)
os.environ["SPOTIPY_CLIENT_ID"] = "64f60e6e7bf049979ca8ae58c3acc11d"
SPOTIPY_CLIENT_ID = "64f60e6e7bf049979ca8ae58c3acc11d"
os.environ["SPOTIPY_CLIENT_SECRET"]= "aa16d11812484b3d8d7f8ad96b44ff16"
os.environ["SPOTIPY_REDIRECT_URI"]= "https://www.spotify.com/us/"
SPOTIPY_REDIRECT_URI = "https://www.spotify.com/us/"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
scope = 'user-library-read playlist-modify-public'

#Parameters to make the link from docs
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": SPOTIPY_REDIRECT_URI,
    "scope": scope,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": SPOTIPY_CLIENT_ID
}
url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in spotipy.auth_query_parameters.items()])
auth_url = "{}/?{}".format(spotipy.SPOTIFY_AUTH_URL, url_args)

#We are looking through the user's library
scope = 'user-library-read playlist-modify-public'

@app.route("/")
def start():
    return render_template('start.html')

@app.route('/', methods=['POST'])
def zip():
    #get zip
    zipcode = request.form['text']
    username = request.form['text']
    # Weather App Id
    WEATHER_APP_ID = environ.get('WEATHER_APP_ID')

    # Setting up the open weather map api
    WEATHER_API_BASE_URL = "http://api.openweathermap.org/data"
    WEATHER_API_VERSION = "2.5"
    WEATHER_API_URL = "{}/{}/weather".format(WEATHER_API_BASE_URL, WEATHER_API_VERSION)
    WEATHER_APP_ID = "0ccd5c89e6c8896ea99462c76c776ec9"

    def getWeather(zipcode):
        # gets the weather from a json
        state = 'us'
        weather_api_endpoint = "{}?zip={},{}&appid={}".format(WEATHER_API_URL, zipcode, state, WEATHER_APP_ID)
        weather_response = requests.get(weather_api_endpoint)
        weather_data = json.loads(weather_response.text)['weather'][0]

        return weather_data

    yourweather = getWeather(zipcode)

    weatherid = int(yourweather['id'])
    weatherdes = yourweather['description']

    # Fetching the descriptions from the website and making new ids from them

    # thunderstorms
    if weatherid <= 232 and weatherid >= 200:
        newid = 0
    # drizzle
    elif weatherid <= 321 and weatherid >= 300:
        newid = 1
    # rain
    elif weatherid <= 531 and weatherid >= 500:
        newid = 2
    # snow
    elif weatherid <= 622 and weatherid >= 600:
        newid = 3
    # clear
    elif weatherid == 800:
        newid = 4
    # clouds
    elif weatherid <= 804 and weatherid >= 801:
        newid = 5
    # atmospheric chill vibes i guess
    elif weatherid <= 762 and weatherid >= 701:
        newid = 6
    # squall or tornado AHHHH
    elif weatherid == 771 and weatherid == 781:
        newid = 7
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(auth=token)
    return redirect(auth_url)