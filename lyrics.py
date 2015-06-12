import requests
import json

MUSIXMATCH_API_URL = "http://api.musixmatch.com/ws/1.1/"
MUSIXMATCH_API_KEY = "04c02296b664ee7966ac93a8203f41a7"


def make_musixmatch_request(method, payload):
    '''
    Send GET request to MusixMatch API using request method and payload.
    Returns message body.
    '''

    payload.update({'apikey': MUSIXMATCH_API_KEY})

    url = "{}{}".format(MUSIXMATCH_API_URL, method)
    r = requests.get(url, params=payload)
    response = r.json()
    body = response['message']['body']
    return body


def get_artist_id(artist_name):
    '''
    Find artist by name and return artist_id of first result.
    '''

    payload = {
        'q_artist': artist_name
    }
    body = make_musixmatch_request('artist.search', payload)
    artist = body['artist_list'][0]['artist']
    return artist['artist_id']


def get_albums(artist_id):
    '''
    Get list of albums by artist_id.
    '''

    payload = {
        'artist_id': artist_id,
        'page_size': 100
    }

    body = make_musixmatch_request('artist.albums.get', payload)
    albums = body['album_list']
    return albums


def get_tracks(album_id):
    '''
    Get tracks by album
    '''

    payload = {
        'album_id': album_id
    }

    body = make_musixmatch_request('album.tracks.get', payload)
    tracks = body['track_list']
    return tracks


def get_lyrics(track_id):
    '''
    Get lyrics for single track
    '''

    payload = {
        'track_id': track_id
    }

    body = make_musixmatch_request('track.lyrics.get', payload)

    if len(body) < 1:
        return ""
    elif body.get('lyrics') and body['lyrics'].get('lyrics_body'):
        lyrics = body['lyrics']['lyrics_body']
    else:
        lyrics = ""

    return lyrics

