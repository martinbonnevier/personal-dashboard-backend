from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
import datetime
import requests
from xml.etree import ElementTree

app = Flask(__name__, static_folder='static')

CORS(app)  # This will allow CORS for all routes

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/time', methods=['GET'])
def get_time():
    now = datetime.datetime.now()
    
    target_time = datetime.datetime(now.year, now.month, now.day, 16, 27)
    delta = target_time - now
    
    overtime = False
    if delta.total_seconds() < 0:
        overtime = True
        delta = now - target_time

    hours, remainder = divmod(abs(int(delta.total_seconds())), 3600)
    minutes, _ = divmod(remainder, 60)

    time_dict = {
        'current_time': {
            'hours': now.hour,
            'minutes': now.minute,
            'seconds': now.second
        },
        'overtime': overtime,
        'hours_remaining': hours,
        'minutes_remaining': minutes
    }

    return jsonify(time_dict)


@app.route('/week', methods=['GET'])
def get_week():
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, 1, 1)
    week = ((now - start).days // 7) + 1
    return jsonify({"week": week})

@app.route('/song-info', methods=['GET'])
def get_song_info():
    url = 'https://api.sr.se/api/v2/playlists/rightnow?channelid=203'
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)
    
    song = tree.find(".//song")
    if song is not None:
        artist = song.find("artist").text
        title = song.find("title").text
        song_info = f"{artist} - {title}"
        return jsonify({"song_info": song_info})
    else:
        return jsonify({"no_song_info": "No song information available"})


@app.route('/weather', methods=['GET'])
def get_weather():
    lat = 57.78145
    lon = 14.15618
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json"
    response = requests.get(url)
    data = response.json()

    latest_forecast = data['timeSeries'][0]
    temperature = next(param['values'][0] for param in latest_forecast['parameters'] if param['name'] == 't')
    wind_speed = next(param['values'][0] for param in latest_forecast['parameters'] if param['name'] == 'ws')
    wsymb2 = next(param['values'][0] for param in latest_forecast['parameters'] if param['name'] == 'Wsymb2')
    # icon_url = f"./weathericons/{wsymb2}.png"  # This URL will have to be adjusted based on how you serve the icons
    icon_url = f"http://localhost:5000{url_for('static', filename=f'weathericons/{wsymb2}.png')}"

    print("Generated icon URL:", icon_url)

    weather_data = {
        'temperature': temperature,
        'wind_speed': wind_speed,
        'icon_url': icon_url
    }

    return jsonify(weather_data)


if __name__ == '__main__':
    app.run(debug=True)
