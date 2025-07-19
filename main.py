from flask import Flask, render_template
import os
from dotenv import load_dotenv
import spotipy
from spotipy import SpotifyOAuth
from tqdm import tqdm

load_dotenv()
app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/run')
def run_spotify_script():
    import os

    import spotipy
    from dotenv import load_dotenv
    from spotipy import SpotifyOAuth
    from tqdm import tqdm

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI", "https://spotify-playlist-sort.onrender.com/callback")
    scope = 'playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    ))

    # Playlist mit bestimmtem Namen suchen
    playlist_name_to_find = "corekid forever"
    playlist = None

    # Hole alle Playlists (auch bei mehr als 50 – mit Pagination)
    offset = 0
    while True:
        playlists = sp.current_user_playlists(limit=50, offset=offset)
        items = playlists['items']
        if not items:
            break

        for pl in items:
            if pl['name'].lower() == playlist_name_to_find.lower():
                playlist = pl
                break

        if playlist:
            break
        offset += 50

    # Abbruch, falls nicht gefunden
    if not playlist:
        raise Exception(f"❌ Playlist mit dem Namen '{playlist_name_to_find}' nicht gefunden!")

    # Falls gefunden → hole ID und Name
    playlist_id = playlist['id']
    playlist_name = playlist['name']

    # Erste Anfrage, um Gesamtanzahl zu erfahren
    limit = 100
    initial = sp.playlist_items(playlist_id, limit=limit, offset=0)
    total_tracks = initial['total']
    all_tracks = initial['items']

    # Ladebalken vorbereiten
    print(f"\n📥 Lade alle {total_tracks} Songs aus Playlist: {playlist_name}")
    for offset in tqdm(range(limit, total_tracks, limit), desc="Lade Playlist"):
        results = sp.playlist_items(playlist_id, limit=limit, offset=offset)
        all_tracks.extend(results['items'])

    # Nach hinzugefügt-Datum sortieren (neueste zuerst)
    all_tracks.sort(key=lambda x: x['added_at'], reverse=True)

    # Top 50 ausgeben
    print(f"\n🆕 Top 50 Neueste Songs in Playlist: {playlist_name}\n")
    for i, item in enumerate(all_tracks[:100]):
        track = item['track']
        added_at = item['added_at'][:10]
        name = track['name']
        artists = ", ".join(artist['name'] for artist in track['artists'])
        print(f"{i + 1}. {name} – {artists} (hinzugefügt am {added_at})")

    # Hole die Track-URIs der 100 neuesten Songs
    track_uris = [item['track']['uri'] for item in all_tracks[:100]]

    # Hole aktuelle User-ID
    user_id = sp.current_user()['id']

    # Name der Zielplaylist
    target_playlist_name = "100 NEU"
    target_playlist = None

    # Suche nach bestehender Playlist mit genau diesem Namen
    playlists = sp.current_user_playlists(limit=50)
    for pl in playlists['items']:
        if pl['name'] == target_playlist_name:
            target_playlist = pl
            break

    # Falls nicht gefunden: Neue Playlist erstellen
    if not target_playlist:
        print(f"\n🆕 Erstelle neue Playlist: '{target_playlist_name}'")
        target_playlist = sp.user_playlist_create(
            user=user_id,
            name=target_playlist_name,
            public=False,
            description="Automatisch generierte Top 100 der neuesten Songs"
        )
    else:
        print(f"\n🧹 Leere bestehende Playlist: '{target_playlist_name}'")

        # Aktuelle Songs aus der Playlist holen (um sie zu löschen)
        existing_tracks = []
        offset = 0
        while True:
            response = sp.playlist_items(target_playlist['id'], limit=100, offset=offset)
            items = response['items']
            if not items:
                break
            uris_to_remove = [{'uri': item['track']['uri']} for item in items if item['track']]
            existing_tracks.extend(uris_to_remove)
            offset += 100

        # Playlist leeren (wenn Tracks vorhanden)
        if existing_tracks:
            sp.playlist_remove_all_occurrences_of_items(
                target_playlist['id'],
                [t['uri'] for t in existing_tracks]
            )

    # Neue Songs hinzufügen
    print(f"➕ Füge 100 neue Songs hinzu zur Playlist '{target_playlist_name}'")
    sp.playlist_add_items(target_playlist['id'], track_uris)

    print("✅ Fertig!")

    return "✅ Playlist wurde aktualisiert!"
