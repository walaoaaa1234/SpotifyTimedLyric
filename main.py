from api.netease import netease
from spotify_api.spotify_api import spotify_api
import threading
import time
import re
import operator
import os
import tkinter
import codecs



artist_now = ''
track_now = ''
lyric = ''
playing_position = 0
isplaying = False
starttime = 0
artists = ''
songnames = ''

def cls():
    os.system('cls')  # on windows

def lrc2dict(lrc):
    lrc_dict = {}
    remove = lambda x: x.strip('[|]')
    for line in lrc.split('\n'):
        time_stamps = re.findall(r'\[[^\]]+\]', line)
        if time_stamps:
            # 截取歌词
            lyric = line
            for tplus in time_stamps:
                lyric = lyric.replace(tplus, '')
            # 解析时间
            for tplus in time_stamps:
                t = remove(tplus)
                tag_flag = t.split(':')[0]
                # 跳过: [ar: 逃跑计划]
                if not tag_flag.isdigit():
                    continue
                # 时间累加
                time_lrc = int(tag_flag) * 60000
                time_lrc += int(t.split(':')[1].split('.')[0]) * 1000
                time_lrc += int(t.split(':')[1].split('.')[1])
                lrc_dict[time_lrc] = lyric
    lrc_dict = sorted(lrc_dict.items(), key=operator.itemgetter(0))
    return lrc_dict

def show_lyric():
    #global lyric, playing_position, starttime, timenow, isplaying, text, artists, songnames
    global timenow, playing_position, text
    oldline = ''
    while True:
        time.sleep(0.05)
        if lyric != '':
            count = 0
            timenow = int(round(time.time() * 1000))
            playing_position = timenow - starttime
            #print isplaying
            while (count < len(lyric) - 1):
                if (playing_position < lyric[count+1][0] and playing_position > lyric[count][0]):
                    newline = lyric[count][1]
                    if oldline != newline:
                        #cls()
                        #print oldline
                        #print newline
                        text.delete('1.0', tkinter.END)
                        text.insert('1.0', artist_now + ' - ' + track_now + '\n' + lyric[count-1][1] + '\n> ' + lyric[count][1] + '\n' + lyric[count+1][1])
                        oldline = newline
                count += 1

def mstomin(timems):
    x = timems / 1000
    seconds = x % 60
    x /= 60
    minutes = x % 60
    x /= 60
    hours = x % 24
    return ("%d:%d:%d" % (hours, minutes, seconds))

def search_lrc_file(artist, track):
    #artist = fix_encoding(artist)
    #track = fix_encoding(track)
    try:
        f = codecs.open('lyrics/' + artist + ' - ' + track + '.lrc', "r", encoding='utf-8')
        data = f.read()
        f.close()
    except IOError:
        return ''
    return data

def write_lrc_file(artist, track, data):
    #artist = fix_encoding(artist)
    #track = fix_encoding(track)
    #data = fix_encoding(data)
    try:
        f = codecs.open('lyrics/' + artist + ' - ' + track + '.lrc', "w", encoding='utf-8')
        f.write(data)
        f.close()
    except IOError:
        pass
    
def fix_encoding(text):
    if isinstance(text, unicode):
        text = text.encode('gb2312', 'ignore')
    else:
        text = text.decode('utf-8').encode('gb2312')
    return text
    
def change_title():
    global top
    top.title(artist_now + ' - ' + track_now)
    
def status_checker():
    global artist_now, track_now, lyric, playing_position, starttime, timenow, isplaying, artists, songnames, top
    while True:
        time.sleep(0.1)
        artist, track, album, playing_position, isplaying = spotify_api.get_status()
        timenow = int(round(time.time() * 1000))
        starttime = timenow - playing_position
        #print isplaying
        if (artist_now != artist or track_now != track):
            #print 'change'
            print artist, track
            artist_now = artist
            track_now = track
            top.after(50, change_title)
            lyric = search_lrc_file(artist, track)
            if lyric == '':
                print 'Searching'
                lyrics, artists, songnames, albums = netease.search(artist, track)
                if len(lyrics) > 1:
                    print 'Found lyric'
                    lyric = lyrics[0]
                    write_lrc_file(artist, track, lyric)
                    lyric = lrc2dict(lyric)
                else:
                    print 'not found'
            else:
                print 'found lrc file'
                lyric = lrc2dict(lyric)
            

if __name__ == '__main__':
    spotify_api = spotify_api()
    netease = netease()
    
    top = tkinter.Tk()
    top.title('Spotify Lyric')
    text = tkinter.Text(top, height=4, width=60, font=('Comic Sans MS',15))
    text.insert('1.0', "\nHello World!")
    text.pack()

    
    t_status = threading.Thread(target=status_checker)
    t_status.start()
    t_lyric = threading.Thread(target=show_lyric)
    t_lyric.start()
    
    
    top.mainloop()
    
