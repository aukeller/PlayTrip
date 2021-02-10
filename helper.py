import os
from datetime import datetime

import random

import googlemaps
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Sends request to Google Maps API for trip time
def get_travel_duration(origin, destination, form):
    gmaps = googlemaps.Client(key=os.environ['API_KEY'])

    # Request directions via desired form of transportation
    now = datetime.now()
    directions_result = gmaps.directions(origin,
                                         destination,   
                                         mode=form,
                                         departure_time=now)

    
    if form == 'driving':
        duration = directions_result[0]['legs'][0]['duration_in_traffic']['value']
    else:
        duration = directions_result[0]['legs'][0]['duration']['value']

    return round(duration / 60, 2)

# Gets user's saved songs from 'Your Music' from Spotify API through spotipy
def get_liked_songs():
    # Configuration to allow API to read user's library
    scope = 'user-library-read'
    auth_manager = SpotifyOAuth(scope=scope)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    saved_tracks = sp.current_user_saved_tracks()
    
    songs = []

    # Iterates through response and appends dicts of all user's tracks with their id's and durations to songs list
    while saved_tracks:
        for i in range(len(saved_tracks['items'])):
            name = saved_tracks['items'][i]['track']['name']
            track_id = saved_tracks['items'][i]['track']['id']
            duration = round((saved_tracks['items'][i]['track']['duration_ms']) / 60000, 2)

            songs.append({'id': track_id, 'duration': duration, 'name': name})

        if saved_tracks['next']:
            saved_tracks = sp.next(saved_tracks)
        else:
            saved_tracks = None
    
    return songs

# Creates a new playlist using spotipy and adds tracks 
def create_playlist(name, songs):
    scope = 'playlist-read-private playlist-modify-public'
    auth_manager = SpotifyOAuth(scope=scope)

    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.me()

    # Creates new playlist and gets the id
    playlist = sp.user_playlist_create(user['id'], name)
    
    # Adds songs to playlist by id
    song_ids = []
    for song in songs:
        song_ids.append(song['id'])
    
    # Handles playlists longer than 100 song
    if len(song_ids) > 100:  
        while song_ids:
            sp.playlist_add_items(playlist['id'], song_ids[:100])
            song_ids = song_ids[100:]
    else:
        sp.playlist_add_items(playlist['id'], song_ids)

# Iterates through all songs randomly and creates a new list whose sum of song lengths is equal to trip time
def sort_songs(trip_duration, songs):
    sorted_songs = []
    total_song_lengths = 0

    for track in songs:
        track = random.choice(songs)
        
        # Just to ensure that no songs that are most likely intro tracks or interludes are not included
        # also no overly long songs
        if track['duration'] < 1 or track['duration'] > 7:
            continue
        else:
            # Total song lengths is equal to the trip duration, we can return
            if round(total_song_lengths + track['duration']) == trip_duration:
                sorted_songs.append(track)
                return sorted_songs
            
            # Skips if adding to list will go over trip time
            elif round(total_song_lengths + track['duration']) > trip_duration:
                continue

            # Adds song to list of songs being included in playlist
            else:
                total_song_lengths += track['duration']
                sorted_songs.append(track)
    
    return sorted_songs

