from helper import get_travel_duration, get_liked_songs, create_playlist, sort_songs
from flask import Flask, render_template, request, url_for, flash 
from flask_simple_geoip import SimpleGeoIP

app = Flask(__name__)
app.secret_key = "YOUR-SECRET-KEY"

remote_addr = "YOUR-IP"
simple_geoip = SimpleGeoIP(app)
geoip = simple_geoip.get_geoip_data(remote_addr=remote_addr)

@app.route('/', methods=["GET", "POST"])
def index():

    origin = {'lat': geoip['location']['lat'], 'lng': geoip['location']['lng']}  
    destination = request.form.get("destination")
    transportation = request.form.get("transportation")
    playlist_name = request.form.get("playlist_name")
    
    error = None
    if request.method == "POST":
        if not destination:
            error = "Must provide destination!"
        elif not transportation:
            error = "Must provide form of transportation!"
        elif not playlist_name:
            error = "Must provide playlist name!"

        if error is None:
            try:
                duration = get_travel_duration(origin, 
                                                destination,  
                                                transportation.lower())
            except:
                error = "Could not find location"
                flash(error)
                return render_template('layout.html')                                   

            # Gets users liked songs and creates playlist from form values
            liked_songs = get_liked_songs()
            create_playlist(playlist_name, sort_songs(duration, liked_songs))

            return render_template("layout.html", duration=duration)

        flash(error)
    
    return render_template("layout.html")


