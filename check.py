# This is a command line tool which takes a spotify user's library and creates a playlist for them based on the weather
# Understanding how to use the spotify api with examples from https://github.com/plamere/spotipy

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
from datetime import date
from os import environ
import spotipy.util as util
import zipcodes
import json
import requests

# Set up global variables for login
os.environ["SPOTIPY_CLIENT_ID"] = "64f60e6e7bf049979ca8ae58c3acc11d"
os.environ["SPOTIPY_CLIENT_SECRET"]= "aa16d11812484b3d8d7f8ad96b44ff16"
os.environ["SPOTIPY_REDIRECT_URI"]= "https://www.spotify.com/us/"

#We are looking through the user's library
scope = 'user-library-read playlist-modify-public'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

#Command line argument is the username and your zipcode
if len(sys.argv) > 2:
    username = sys.argv[1]
    zipcode = sys.argv[2]
else:
    print("Usage: %s username %s zipcode" % (sys.argv[0],))
    sys.exit()

# Make sure the user inputted a real zipcode
if not zipcodes.is_real(zipcode):
    print("Usage: You must input a valid zipcode" % (sys.argv[0],))
    sys.exit()

# Token to authenticate spotify
token = util.prompt_for_user_token(username, scope)
sp = spotipy.Spotify(auth=token)



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
    weather_api_endpoint = "{}?zip={},{}&appid={}".format(WEATHER_API_URL,zipcode,state,WEATHER_APP_ID)
    weather_response = requests.get(weather_api_endpoint)
    weather_data = json.loads(weather_response.text)['weather'][0]
    return weather_data

yourweather = getWeather(zipcode)

weatherid = int(yourweather['id'])
weatherdes = yourweather['description']

#Fetching the descriptions from the website and making new ids from them
newid=0
#thunderstorms
if weatherid <=232 and weatherid>=200:
    newid = 0
#drizzle
elif weatherid <=321 and weatherid>=300:
    newid = 1
#rain
elif weatherid <=531 and weatherid>=500:
    newid = 2
#snow
elif weatherid <=622 and weatherid>=600:
    newid = 3
#clear
elif weatherid == 800:
    newid = 4
#clouds
elif weatherid <=804 and weatherid>=801:
    newid = 5
#atmospheric chill vibes i guess
elif weatherid <=762 and weatherid>=701:
    newid = 6
#squall or tornado AHHHH
elif weatherid ==771 and weatherid==781:
    newid = 7


if token:
    list=[]
    endlist=[]

    results = sp.current_user_saved_tracks(limit=50)
    features = {}
    song_ids = []
    for item in results['items']:
        track = item['track']
        features = sp.audio_features(track['id'])
        for new in features:
                if newid == 0:
                    # Thunderstorm
                    if new['energy'] > 0.7 and new['valence'] < 0.4:
                        song_ids.append(new['id'])
                elif newid == 1:
                        # Drizzle
                            if new['acousticness'] > 0.5 and new['energy'] < 0.4:
                                song_ids.append(new['id'])
                elif newid == 2:
                        # Rain
                            if new['valence'] < 0.4 and new['energy'] > 0.4:
                                song_ids.append(new['id'])
                elif newid == 3:
                        # Snow .6 and .5
                            if new['valence'] > 0.6 and new['danceability'] > 0.5:
                                song_ids.append(new['id'])
                elif newid == 4:
                        # Clear .6 and .6
                        if new['valence'] > 0.6 and new['danceability'] > 0.6:
                            song_ids.append(new['id'])
                elif newid == 5:
                        # clouds
                        if new['valence'] < 0.5 and new['danceability'] < 0.5:
                            song_ids.append(new['id'])
                elif newid == 6:
                        # Atmospheric
                        if new['danceability'] < .3 and new['instrumentalness'] < .2:
                            song_ids.append(new['id'])
                elif newid == 7:
                        # squall or tornado AHHHH
                        if new['energy'] > 0.75 and new['valence']<0.3:
                            song_ids.append(new['id'])
else:
    print("Token not working for", username)

# Get today's date and make it into a string for the playlist name
today = str(date.today())
namepl = weatherdes + " " +today

# Make the playlist
playlist = sp.user_playlist_create(username, name=namepl, description = "This playlist is curated using a program that analyzes current weather conditions. Anna Tender 2020 (Github: @annathxresa). ",public=True)
playlistID = playlist['id']

sp.user_playlist_add_tracks(username, playlistID, song_ids)


