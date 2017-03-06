import ssl
from string import ascii_lowercase
from random import choice
import urllib
import urllib2
import json
import time


class spotify_api(object):
    
    PORT = 4370
    DEFAULT_RETURN_ON = ['login', 'logout', 'play', 'pause', 'error', 'ap']
    ORIGIN_HEADER = {'Origin': 'https://open.spotify.com'}
    
    def __init__(self):
        self.oauth_token = self.get_oauth_token()
        self.csrf_token = self.get_csrf_token()
    

    # I had some troubles with the version of Spotify's SSL cert and Python 2.7 on Mac.
    # Did this monkey dirty patch to fix it. Your milage may vary.
    def new_wrap_socket(self, *args, **kwargs):
        kwargs['ssl_version'] = ssl.PROTOCOL_SSLv3
        return orig_wrap_socket(*args, **kwargs)

    orig_wrap_socket, ssl.wrap_socket = ssl.wrap_socket, new_wrap_socket

    def get_json(self, url, params={}, headers={}):
        if params:
            url += "?" + urllib.urlencode(params)
        request = urllib2.Request(url, headers=headers)
        return json.loads(urllib2.urlopen(request).read())


    def generate_local_hostname(self):
        """Generate a random hostname under the .spotilocal.com domain"""
        subdomain = ''.join(choice(ascii_lowercase) for x in range(10))
        return subdomain + '.spotilocal.com'


    def get_url(self, url):
        return "https://%s:%d%s" % (self.generate_local_hostname(), self.PORT, url)


    def get_version(self):
        return self.get_json(self.get_url('/service/version.json'), params={'service': 'remote'}, headers=self.ORIGIN_HEADER)


    def get_oauth_token(self):
        return self.get_json('http://open.spotify.com/token')['t']


    def get_csrf_token(self):
        # Requires Origin header to be set to generate the CSRF token.
        return self.get_json(self.get_url('/simplecsrf/token.json'), headers=self.ORIGIN_HEADER)['token']


    def _get_status(self, oauth_token, csrf_token, return_after=59, return_on=DEFAULT_RETURN_ON):
        params = {
            'oauth': oauth_token,
            'csrf': csrf_token,
            'returnafter': return_after,
            'returnon': ','.join(return_on)
        }
        return self.get_json(self.get_url('/remote/status.json'), params=params, headers=self.ORIGIN_HEADER)
    
    def get_status(self):
        status = self._get_status(self.oauth_token, self.csrf_token, 1)
        playing_position = int(status['playing_position'] * 1000)
        artist = status['track']['artist_resource']['name']
        track = status['track']['track_resource']['name']
        album = status['track']['album_resource']['name']
        isplaying = status['playing']
        return artist, track, album, playing_position, isplaying
    

    def _pause(self, oauth_token, csrf_token, pause=True):
        params = {
            'oauth': oauth_token,
            'csrf': csrf_token,
            'pause': 'true' if pause else 'false'
        }
        self.get_json(self.get_url('/remote/pause.json'), params=params, headers=self.ORIGIN_HEADER)
    
    def pause(self):
        self._pause(self.oauth_token, self.csrf_token)

    def _unpause(self, oauth_token, csrf_token):
        self._pause(oauth_token, csrf_token, pause=False)
    
    def unpause(self):
        self._unpause(self.oauth_token, self.csrf_token)

    def play(self, oauth_token, csrf_token, spotify_uri):
        params = {
            'oauth': oauth_token,
            'csrf': csrf_token,
            'uri': spotify_uri,
            'context': spotify_uri,
        }
        self.get_json(self.get_url('/remote/play.json'), params=params, headers=self.ORIGIN_HEADER)

    def open_spotify_client(self):
        return get(self.get_url('/remote/open.json'), headers=self.ORIGIN_HEADER).text

