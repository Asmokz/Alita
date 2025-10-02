# spotify_helper.py
import os
import time
from typing import Optional, List, Tuple

from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Chargement .env dès l'import
load_dotenv()

SCOPES = "user-read-playback-state user-modify-playback-state app-remote-control streaming"

class SpotifyController:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
            scope=SCOPES,
            open_browser=True,               # ouvre la fenêtre d'auth la 1ère fois
            cache_path=".cache-spotify-assistant"  # fichier token local
        ))

    # ---------- Devices ----------
    def list_devices(self) -> List[dict]:
        return self.sp.devices().get("devices", [])

    def get_active_device_id(self) -> Optional[str]:
        for d in self.list_devices():
            if d.get("is_active"):
                return d.get("id")
        return None

    def get_any_device_id(self) -> Optional[str]:
        devices = self.list_devices()
        return devices[0]["id"] if devices else None

    def ensure_device(self) -> Optional[str]:
        """
        Retourne un device prêt à jouer.
        - si un device est actif -> le retourne
        - sinon prend le 1er device dispo et lui transfère la lecture
        - retourne None si aucun device (ouvre Spotify sur PC/tel)
        """
        dev = self.get_active_device_id()
        if dev:
            return dev

        any_dev = self.get_any_device_id()
        if any_dev:
            try:
                self.sp.transfer_playback(device_id=any_dev, force_play=False)
                # petit délai pour que le device devienne 'actif'
                time.sleep(0.3)
                return any_dev
            except Exception:
                return any_dev
        return None

    # ---------- Recherche ----------
    def search_track(self, query: str, limit: int = 1) -> List[dict]:
        res = self.sp.search(q=query, type="track", limit=limit)
        return res.get("tracks", {}).get("items", [])

    def search_artist_top_track(self, artist: str) -> Optional[Tuple[str, str]]:
        """Retourne (uri, titre lisible) du top track d'un artiste."""
        res = self.sp.search(q=f"artist:{artist}", type="artist", limit=1)
        items = res.get("artists", {}).get("items", [])
        if not items:
            return None
        artist_id = items[0]["id"]
        top = self.sp.artist_top_tracks(artist_id=artist_id, country="FR")
        tracks = top.get("tracks", [])
        if not tracks:
            return None
        t = tracks[0]
        return t["uri"], f'{t["name"]} - {t["artists"][0]["name"]}'

    # ---------- Lecture ----------
    def play_query(self, query: str, prefer_top_artist: bool = True) -> str:
        """
        Joue soit le meilleur match de piste, soit le top track de l'artiste si prefer_top_artist=True
        Retourne un message utilisateur.
        """
        device = self.ensure_device()
        if not device:
            return "⚠️ Aucun appareil Spotify détecté. Ouvre Spotify sur ton PC ou ton téléphone."


        # 2) Sinon, prendre la meilleure piste
        tracks = self.search_track(query, limit=1)
        if not tracks:
            return f"❌ Je n'ai rien trouvé pour « {query} »."
        t = tracks[0]
        title = f'{t["name"]} - {t["artists"][0]["name"]}'
        self.sp.start_playback(device_id=device, uris=[t["uri"]])
        return f"▶️ Je lance {title}."

    def play_uri_or_url(self, uri_or_url: str) -> str:
        """
        Accepte un lien/URI Spotify (track/album/playlist/artist) et lance la lecture.
        """
        device = self.ensure_device()
        if not device:
            return "⚠️ Aucun appareil Spotify détecté. Ouvre Spotify sur ton PC ou ton téléphone."

        if "open.spotify.com/playlist" in uri_or_url or uri_or_url.startswith("spotify:playlist:"):
            playlist_id = uri_or_url.split("/")[-1].split("?")[0] if "open.spotify.com" in uri_or_url else uri_or_url.split(":")[-1]
            self.sp.start_playback(device_id=device, context_uri=f"spotify:playlist:{playlist_id}")
            return "▶️ Lecture de la playlist."
        if "open.spotify.com/album" in uri_or_url or uri_or_url.startswith("spotify:album:"):
            album_id = uri_or_url.split("/")[-1].split("?")[0] if "open.spotify.com" in uri_or_url else uri_or_url.split(":")[-1]
            self.sp.start_playback(device_id=device, context_uri=f"spotify:album:{album_id}")
            return "▶️ Lecture de l’album."
        if "open.spotify.com/artist" in uri_or_url or uri_or_url.startswith("spotify:artist:"):
            artist_id = uri_or_url.split("/")[-1].split("?")[0] if "open.spotify.com" in uri_or_url else uri_or_url.split(":")[-1]
            # On joue la radio/artiste via top tracks
            top = self.sp.artist_top_tracks(artist_id, country="FR").get("tracks", [])
            if not top:
                return "❌ Impossible de lire cet artiste."
            self.sp.start_playback(device_id=device, uris=[t["uri"] for t in top[:10]])
            return "▶️ Lecture des meilleurs titres de l’artiste."
        if "open.spotify.com/track" in uri_or_url or uri_or_url.startswith("spotify:track:"):
            track_id = uri_or_url.split("/")[-1].split("?")[0] if "open.spotify.com" in uri_or_url else uri_or_url.split(":")[-1]
            self.sp.start_playback(device_id=device, uris=[f"spotify:track:{track_id}"])
            return "▶️ Lecture du titre."
        return "❌ Lien/URI Spotify non reconnu."

    # ---------- Contrôles ----------
    def pause(self) -> str:
        dev = self.ensure_device()
        if not dev: return "⚠️ Aucun appareil Spotify."
        self.sp.pause_playback(device_id=dev)
        return "⏸️ Pause."

    def resume(self) -> str:
        dev = self.ensure_device()
        if not dev: return "⚠️ Aucun appareil Spotify."
        self.sp.start_playback(device_id=dev)
        return "▶️ Reprise."

    def next(self) -> str:
        dev = self.ensure_device()
        if not dev: return "⚠️ Aucun appareil Spotify."
        self.sp.next_track(device_id=dev)
        return "⏭️ Suivant."

    def prev(self) -> str:
        dev = self.ensure_device()
        if not dev: return "⚠️ Aucun appareil Spotify."
        self.sp.previous_track(device_id=dev)
        return "⏮️ Précédent."

    def set_volume(self, vol: int) -> str:
        vol = max(0, min(100, int(vol)))
        dev = self.ensure_device()
        if not dev: return "⚠️ Aucun appareil Spotify."
        self.sp.volume(volume_percent=vol, device_id=dev)
        return f"🔉 Volume {vol}%."
