# -*- coding: utf-8 -*-
"""
Created on Fri Aug  8 15:53:31 2014
 
@author: awon
"""
#import requests
import json
import re
import itertools
import time, urllib
import pdb #use pdb.set_trace() to stop
 
endpoint = "http://ws.spotify.com/search/1/track.json?q="
#this is a song titled "Asterisk" to represent an * when a match is not found
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
        if self.cache.has_key(url):
            if int(time.time()) - self.cache[url][0] < max_age:
                return self.cache[url][1]
        # Retrieve and cache
        data = urllib.urlopen(url).read()
        self.cache[url] = (time.time(), data)
        return data
         
fetcher = CacheFetcher()

"""function to breakdown line of text into combinations while maintaining order
from user falsetru: http://stackoverflow.com/a/18406982 ; altered to return list.
Does not include whole line."""
def break_down(text):
    x = []
    words = text.split()
    ns = range(1, len(words)) # n = 1..(n-1)
    for n in ns: # split into 2, 3, 4, ..., n parts.
        for idxs in itertools.combinations(ns, n):
            x.append([' '.join(words[i:j]) for i, j in zip((0,) + idxs, idxs + (None,))])
    return x
              
#looks for an exact phrase-track title match within api search results. 
#Returns Spotify link if found; no match returns logical false    
def track_match(phrase):
    phrase = re.sub("[!?#$*./,-]", "", phrase)
    phrase = phrase.lower().encode("utf-8")
    track_results = sp_search(phrase)
    if len(track_results) == 0: return False
    for i in range(0, len(track_results)):
        track_results[i].title = re.sub("[!?#$*./,-]", "", track_results[i].title)
        if track_results[i].title.lower() == phrase:
            return track_results[i].link
            break
        elif i + 1 == len(track_results):
            return False
 
#search Spotify metadata API for tracks given a query string    
def sp_search(query):
    track_list = []
    #response = requests.get(endpoint, params = {"q": query})
    response = fetcher.fetch(endpoint + query, 300)
    #results = json.loads(response.text)['tracks']
    results = json.loads(response)['tracks']
    for i in range(0,len(results)): track_list.append(spotify_track(results[i]))
    return track_list
 
#given a list of words, attempt to find a match and return a playlist
def get_tracks(words):
    songs = [] #empty list to store track links
    for chunk in words:
        if track_match(chunk) != False: 
            songs.append(track_match(chunk)) #add track to playlist
        else:
            songs.append(asterisk)
    return songs
 
# take multiple lines as input, enter or keyboard interrupt to finish
# from http://stackoverflow.com/a/10426831/2727740
"""def multi_input():
    try:
        while True:
            data=raw_input("Type in a line of your poem and press <Enter>." +
            "\n" + "Press <Enter> again on a blank line when finished: ")
            if not data: break
            yield data
    except KeyboardInterrupt:
        return
 """
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
        word_chunks = []
        if " " not in i:
            playlist.append(get_tracks(poem))
        else:
            word_chunks.append(break_down(i))
            temp_list = []
            for line in word_chunks:
                for x in line:
                #for every combination in a list of combinations
                    temp_list.append(get_tracks(x))
                playlist.append(best_playlist(temp_list))
    print "Here is your playlist: "
    for x in playlist: 
        for y in x:
            print y

"""    if len(playlist) > 1:
        for x in best_playlist(playlist): print x
    else: 
        for x in playlist: print x
"""     
"""
   for i in playlist:
        for x in i:
            print x
"""
    
def best_playlist(playlists):
    filtered_playlists = []
    for i in playlists:
        if asterisk not in i: filtered_playlists.append(i)
    if len(filtered_playlists) != 0:
        filtered_playlists = sorted(filtered_playlists, key = len)
    else:
        filtered_playlists = sorted(playlists, 
                                    key = lambda x: (x.count(asterisk), len(x)))
    return filtered_playlists[0]


if __name__ == "__main__":
    poem_to_playlist()