# -*- coding: utf-8 -*-
"""
Created on Fri Aug  8 15:53:31 2014
Take in text, find matching song titles and return a playlist with spotify links
@author: awon
"""
import json
import re
import itertools
import time, urllib
import pdb # debugger: use pdb.set_trace() to stop
 
endpoint = "http://ws.spotify.com/search/1/track.json?q=" # spotify metadata api 

#this is a song titled "Asterisk" to represent an * when a match is not found
asterisk = "http://open.spotify.com/track/0me7sTN3zvz9MyZNN2hSr8"
 
class SpotifyTrack(dict):
    """ Class object to store results from api calls to dicts """
    def __init__(self, dict):
        self.artist = dict["artists"][0]["name"].encode("utf-8") 
        self.title = dict["name"].encode("utf-8")
        self.album = dict["album"]["name"].encode("utf-8")
        self.link = "http://open.spotify.com/track/" + dict['href'].encode('utf-8')[14:]
    def __repr__(self):
        return self.title + " by " + self.artist # human friendly way to see objects
 
#in memory cache storage fetcher via https://developer.yahoo.com/python/python-caching.html
class CacheFetcher:
    """ in memory cache that I found on the yahoo developer site:
        https://developer.yahoo.com/python/python-caching.html """
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
         
fetcher = CacheFetcher() # variable to call cache functions

def break_down(text):
    """ Breaks down line of text into all possible combinations while maintaining order.
        From user falsetru: http://stackoverflow.com/a/18406982 ; altered to return list.
        Does not include full line as a combination. """
    combos = [] # empty list to store track combinations
    words = text.split()
    ns = range(1, len(words)) # n = 1..(n-1)
    for n in ns: # split into 2, 3, 4, ..., n parts.
        for idxs in itertools.combinations(ns, n):
            combos.append([' '.join(words[i:j]) for i, j in zip((0,) + idxs, idxs + (None,))])
    return combos
              
def track_match(phrase):
    " Find a track with a title that is an exact match for a phrase "
    phrase = re.sub("[!?#$*./,-]", "", phrase) # remove special characters to match titles
    phrase = phrase.lower().encode("utf-8") # make lower case and translate unicode
    track_results = sp_search(phrase) 
    if len(track_results) == 0: return False # false if no results
    for i in range(0, len(track_results)):
        track_results[i].title = re.sub("[!?#$*./,-]", "", track_results[i].title)
        if track_results[i].title.lower() == phrase:
            return track_results[i] # return a track of first exact match found
            break
        elif i + 1 == len(track_results):
            return False
 
def sp_search(query):
    " search Spotify metadata API for tracks given a query string "
    track_list = [] # empty list to store tracks
    response = fetcher.fetch(endpoint + query, 300) # use cache
    results = json.loads(response)['tracks']
    for i in range(0,len(results)): 
        track_list.append(SpotifyTrack(results[i])) # store tracks in list
    return track_list
 
#given a list of words, attempt to find a match and return a playlist
def get_tracks(words):
    """ Given a word, phrase or phrases attempt to find an exact match and
        and return a playlist as list """
    songs = [] # empty list to store track links
    for chunk in words:
        if track_match(chunk) != False: 
            songs.append(track_match(chunk)) # add track to playlist
        else:
            songs.append(asterisk) # add "Asterisk" song in place of no match
    return songs

def multi_input():
    """ Take multiple lines as input, enter or keyboard interrupt to finish
        from http://stackoverflow.com/a/10426831/2727740. Edited to take iterable
        string to change instructions. """
    prompts = ["Type in the first line of your poem and press Enter: "]
    for i in (range(1, 24)): prompts.append("Type another line or just press Enter. ") 
    prompts.append("Limit reached. Please press enter.")
    i = iter(prompts)
    try:
        while True:
            data=raw_input(i.next())
            if not data: break
            yield data
    except KeyboardInterrupt:
        return
  
def poem_to_playlist():
    """ Callable function to start prompt for poem input. Returns list of 
        Spotify links to play tracks """
    poem = list(multi_input()) # store input into variable
    playlist = [] # empty list to store tracks
    for i in poem:
        word_chunks = [] # var to store combinations for a line
        if " " not in i: # check to see if line is a single word
            playlist.append(get_tracks(poem))
        else:
            word_chunks.append(break_down(i))
            temp_list = [] # list to store
            for line in word_chunks:
                for phrases in line:
                    temp_list.append(get_tracks(phrases))
                playlist.append(best_playlist(temp_list))
    print "Here is your playlist: "
    for lists in playlist: 
        for line in lists:
            print line

def best_playlist(playlists):
    """ Take a list of playlists and reorder them so that those without the "Asterisk" song
        or with the fewest occurences is on top, then the lists with the fewest songs on 
        top. This is to prioritize better matches. Main issue to address highly rated playlists
        with low "Asterisk" occurences but matches with short song titles. """
    filtered_playlists = [] # list to store reordered list of playlists
    for i in playlists:
        if asterisk not in i: filtered_playlists.append(i)
    if len(filtered_playlists) != 0:
        filtered_playlists = sorted(filtered_playlists, key = len)
    else:
        filtered_playlists = sorted(playlists, 
                                    key = lambda x: (x.count(asterisk), len(x)))
    return filtered_playlists[0] #return first in list, which should be top rated match


if __name__ == "__main__":
    poem_to_playlist()