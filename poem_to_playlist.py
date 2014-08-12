#!/usr/binpython
# -*- coding: utf-8 -*-

"""
Created on Fri Aug  8 15:53:31 2014
Decribe Here!!!!!!!!
@author: awon
"""
import json
import re
import time, urllib
import pdb #debugger put pdb.set_trace() where i want to stop

# comment above
endpoint = "http://ws.spotify.com/search/1/track.json"  # two spaces if here

# this is a song titled "Asterisk" to represent a * when a match is not found
asterisk = "http://open.spotify.com/track/0me7sTN3zvz9MyZNN2hSr8"

#class for json objects returned from api calls
class spotify_track(dict):
    def __init__(self, dict):
        self.artist = dict["artists"][0]["name"].encode("utf-8")
        self.title = dict["name"].encode("utf-8")
        self.album = dict["album"]["name"].encode("utf-8")
        self.link = "http://open.spotify.com/track/" + dict['href'].encode('utf-8')[14:]
    def __repr__(self):
        return self.title + " by " + self.artist #human friendly way to see objects

#in memory cache storage fetcher via https://developer.yahoo.com/python/python-caching.html
class CacheFetcher:
    def __init__(self):
        self.cache = {}
    def fetch(self, url, max_age=0):
    	""" Enter description here """	
        if self.cache.has_key(url):
            if int(time.time()) - self.cache[url][0] < max_age:
                return self.cache[url][1]
        # Retrieve and cache
        data = urllib.urlopen(url).read()
        self.cache[url] = (time.time(), data)
        return data
        
fetcher = CacheFetcher()

#looks for an exact phrase-track title match within api search results. 
#Returns Spotify link if found; no match returns logical false    
def track_match(phrase):
    track_results = sp_search(phrase)
    if len(track_results) == 0: return False
    for i in range(0, len(track_results)):
        track_results[i].title = re.sub("[!?#$*./,]", "", track_results[i].title)
        phrase = re.sub("[!?#$*./,]", "", phrase)
        if track_results[i].title.lower() == phrase.lower():
            return track_results[i].link
            break
        elif i + 1 == len(track_results):
            return False

#search Spotify metadata API for tracks given a query string    
# rationale here
def sp_search(query):
	"""Return list of tracks from Spotify API from query string"""
    track_list = []
    #response = requests.get(endpoint, params = {"q": query})
    response = fetcher.fetch(endpoint + "?q=" + query, 90)
    #results = json.loads(response.text)['tracks']
    results = json.loads(response)['tracks']
    for i in range(0,len(results)): track_list.append(spotify_track(results[i])) # Does this make sense? if no explain
    return track_list

#given a list of words, attempt to find a match and return a playlist
def get_tracks(words):
    songs = [] #empty list to store track links
    seq = [4, 3, 5, 6, 2, 1] # arbitrary order of word combinations to try
    while len(words) > 0:
        for i in seq:
            phrase = " ".join(words[:i])
            if track_match(phrase) != False: 
                songs.append(track_match(phrase)) #add track to playlist
                for word in words[:i]:
                    words.remove(word) #remove words in title from word list
                break
            elif i == 1:
                if len(songs) == 0:
                    songs.append(asterisk)
                    words.remove(words[0])
                elif songs[-1] == asterisk:
                    words.remove(words[0])
                    break
                else:
                    songs.append(asterisk)
                    words.remove(words[0])
            else:
                pass
    return songs

# take multiple lines as input, enter or keyboard interrupt to finish
# from http://stackoverflow.com/a/10426831/2727740
def multi_input():
    x = ["Type in the first line of your poem and press Enter: "]
    for i in (range(1, 24)): x.append("Type another line or just press Enter. ") 
    x.append("Limit reached. Please press enter.")
    i = iter(x)
    try:
        while True:
            data=raw_input(i.next())
            if not data: break
            yield data
    except KeyboardInterrupt:
        return
  

def poem_to_playlist():
    poem = list(multi_input())
    playlist = []
    for i in poem:
        playlist.append(get_tracks(i.split()))
    print "Here is your playlist:"
    for i in playlist:
        for x in i:
            print x

if __name__ == "__main__":
    poem_to_playlist()
