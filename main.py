from flask import Flask, redirect, request, render_template
import os
from spotipy import SpotifyOAuth, Spotify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/run')
def run_spotify_script():
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
    ))

    # ✂️ hier kommt dein Code rein (Playlists holen, sortieren, aktualisieren ...)
    return "✅ Playlist wurde aktualisiert!"
