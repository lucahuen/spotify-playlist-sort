from flask import Flask, redirect, request, render_template
import os
from spotipy import SpotifyOAuth, Spotify
from dotenv import load_dotenv

from vibe_code_solution import update_playlist

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/run')
def run_spotify_script():
    update_playlist()
    return "✅ Playlist wurde aktualisiert!"
