import json
import requests
import re
import urllib

class netease(object):
    
    def __init__(self, debug=False):
        self.isDebug = debug
        self.header = {
            'Referer': 'http://music.163.com/',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
        }
        self.cookie = 'appver=2.0.2'
        self.apilyric = 'http://music.163.com/api/song/lyric'
        self.apiquery = 'http://music.163.com/api/search/get/'
        

        
    def printdbg(self, text):
        if self.isDebug == True:
            print '[DEBUG]' + str(text)
        
    def search(self, artist, title):
        s_id = []
        s_artist = []
        s_title = []
        s_album = []
        s_lyric = []
        req = requests.post(self.apiquery, data=self.get_search_params(artist, title), headers=self.header)
        #req.add_header('Content-Type', 'application/json')
        
        response = json.loads(req.text)['result']
        #self.printdbg(json.dumps(response, indent=4))
        
        #print artist, title
        try:
            for key in response['songs']:
                try:
                    #self.printdbg(key)
                    lyric = requests.get(self.apilyric + "?os=pc&id=" + str(key['id']) + "&lv=-1&kv=-1&tv=-1")
                    lyric = json.loads(lyric.text)
                    lyric = lyric['lrc']['lyric']
                    #self.printdbg(json.dumps(lyric, indent=4))
                    #self.s_id.append(key['id'])
                    s_artist.append(key['artists'][0]['name'])
                    s_title.append(key['name'])
                    s_album.append(key['album']['name'])
                    s_lyric.append(lyric)
                except:
                    pass
        except:
            pass
        
        #self.printdbg(self.s_id)
        #self.printdbg(self.s_artist)
        #self.printdbg(self.s_title)
        #self.printdbg(self.s_album)
        #self.printdbg(self.s_lyric)
        return s_lyric, s_artist, s_title, s_album
        
        
    def get_search_params(self, artist, title, limit=None, type=None, offset=None):
        if limit is None: limit = str(10)
        if type is None: type = str(1)
        if offset is None: offset = str(0)
        if isinstance(artist, unicode):
            artist = artist.encode('gb2312', 'ignore')
        else:
            artist = artist.decode('utf-8').encode('gb2312')
        if isinstance(title, unicode):
            title = title.encode('gb2312', 'ignore')
        else:
            title = artist.decode('utf-8').encode('gb2312')
        artist = artist.replace('//', '')
        title = title.replace('//', '')
        return "s=" + artist + "+" + title + "&limit=" + limit + "&type=" + type + "&offset=" + offset




















    
