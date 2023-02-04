from datetime import datetime
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List
from os import environ

SPOTIFY_CLIENT_ID = environ.get("client_id")
SPOTIFY_CLIENT_SECRET = environ.get("client_secret")
SPOTIFY_BASE_URL = "https://api.spotify.com/"


class PlaylistCreator:
    """Class that allows you to create Spotify playlist with songs that were popular at provided date"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

        # Auth to Spotify part
        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
                                                                        client_secret=self.client_secret,
                                                                        redirect_uri="http://localhost:8888/callback",
                                                                        scope="playlist-modify-private"))
        self.spotify_user = self.spotify_client.current_user()

    def create_playlist(self, date: str, song_and_artist: List) -> None:
        """Creates Spotify playlist and adds songs to it"""
        spotify_song_uris = []
        for song, artist in song_and_artist:
            spotify_search = self.spotify_client.search(q=f"{song} {artist}",
                                                        type="track")
            try:
                song_uri = spotify_search['tracks']['items'][0]['uri']
                print(f"{song} added to playlist")
                spotify_song_uris.append(song_uri)
            except IndexError:
                print(f"{song} doesn't exist in Spotify. Skipped.")
            # print(song, artist)
        # print(len(spotify_song_uris))
        user_id = self.spotify_user["id"]
        my_playlist = self.spotify_client.user_playlist_create(user=user_id, name=f"{date} top 100 songs",
                                                               public=False,
                                                               description=f"Billboard Hot 100 for {date}")
        print(my_playlist)
        self.spotify_client.playlist_add_items(playlist_id=my_playlist["id"],
                                               items=spotify_song_uris)


def get_100_songs(date) -> List:
    """Returns list of songs and artists"""
    response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    song_list = soup.find_all(name="h3", class_="a-no-trucate")
    artist_list = soup.find_all(name="span",
                                class_="a-no-trucate")

    edited_song_list = [song.get_text().strip() for song in song_list]
    edited_artist_list = [artist.get_text().strip() for artist in artist_list]

    return list(zip(edited_song_list, edited_artist_list))


def main():
    try:
        date_entry = input("Which date you want to make playlist of? Type the date in format YYYY-MM-DD: ")
        valid_date = datetime.strptime(date_entry, '%Y-%m-%d')
        date = datetime.strftime(valid_date, "%Y-%m-%d")
        song_and_artist_list = get_100_songs(date)

        playlist_creator = PlaylistCreator(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        # playlist_creator.create_playlist(date, song_and_artist_list)
    except ValueError:
        print("Date is invalid. Please, ensure it is in YYYY-MM-DD format")


if __name__ == '__main__':
    main()
