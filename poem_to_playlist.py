#!/usr/binpython
# -*- coding: utf-8 -*-

"""
Created on Fri Aug  8 15:53:31 2014

Have the user enter in text and return a list of Spotify links to tracks whose titles best match
the entered text. As seen here: http://spotifypoetry.tumblr.com/ 

This is the first version of the solution I made. I made an arbitrary sequence of numbers, which is 
the order that get_tracks attempts find a match. E.g., in sequence (4, 3, 5, 6, 2, 1), the function 
will look for a match for the first 4 words of the text, then if no match is found attempt the first 3
words, and so forth. This favors middle to longer track titles over single-word matches.
It's quicker and dirtier than the second, but seemed to do the job reasonably well. 
@author: awon
"""
import json
import re
import time, urllib
# import pdb #debugger put pdb.set_trace() where i want to stop

endpoint = "http://ws.spotify.com/search/1/track.json?q=" # spotify metadata api 

class SpotifyTrack(dict):
    """ Class object to store results from api calls to dicts """
    def __init__(self, dict):
        self.artist = dict["artists"][0]["name"].encode("utf-8") 
        self.title = dict["name"].encode("utf-8")
        self.album = dict["album"]["name"].encode("utf-8")
        self.link = "http://open.spotify.com/track/" + dict['href'].encode('utf-8')[14:]
    def __repr__(self):
        return self.title + " by " + self.artist # human friendly way to see objects

class CacheFetcher:
    """ in memory cache that I found on the yahoo developer site:
        https://developer.yahoo.com/python/python-caching.html """
    def __init__(self):
        self.cache = {}
    def fetch(self, url, max_age=0):
    	""" Takes requests and stores in an memory cache for signaled time """	
        if self.cache.has_key(url):
            if int(time.time()) - self.cache[url][0] < max_age:
                return self.cache[url][1]
        # Retrieve and cache
        data = urllib.urlopen(url).read()
        self.cache[url] = (time.time(), data)
        return data
        
fetcher = CacheFetcher() # variable to call cache functions

def track_match(phrase):
    """ Find a track with a title that is an exact match for a phrase """
    phrase = re.sub("[!?#$*./,-:@&%]", "", phrase) # remove special characters to match titles
    phrase = phrase.lower().encode("utf-8") # make lower case and translate unicode
    track_results = sp_search(phrase) 
    if len(track_results) == 0: return False # false if no results
    for i in range(0, len(track_results)):
        track_results[i].title = re.sub("[!?#$*./,-:@&%]", "", track_results[i].title)
        if track_results[i].title.lower() == phrase:
            return track_results[i] # return a track of first exact match found
            break
        elif i + 1 == len(track_results):
            return False

def sp_search(query):
    """ search Spotify metadata API for tracks given a query string """
    track_list = [] # empty list to store tracks
    response = fetcher.fetch(endpoint + query, 300) # use cache
    results = json.loads(response)['tracks']
    for i in range(0,len(results)): 
        track_list.append(SpotifyTrack(results[i])) # store tracks in list
    return track_list

def get_tracks(words):
    """ Given a list of words or phrases attempt to find an exact match and
        and return a playlist as list """
    songs = [] # list to store tracks
    # This is an arbitrary sequence of word combinations to avoid single word track names
    seq = [4, 3, 5, 6, 2, 1]
    while len(words) > 0:
        for i in seq:
            phrase = " ".join(words[:i])
            # add matches to songs list
            if track_match(phrase) != False: 
                songs.append(track_match(phrase))
                for word in words[:i]:
                    words.remove(word) # remove words in title from word list
                break
            elif i == 1:
                if len(songs) == 0:
                    songs.append(asterisk) # add "Asterisk" if no match for the first word
                    words.remove(words[0])
                elif songs[-1] == asterisk: # if last song added was "Asterisk" don't add again
                    words.remove(words[0])
                    break
                else:
                    songs.append(asterisk)
                    words.remove(words[0])
            else:
                pass
    return songs

def multi_input(max_lines=10):
    """ Take multiple lines as input, enter or keyboard interrupt to finish
        from http://stackoverflow.com/a/10426831/2727740. Edited to take iterable
        string to change instructions. """
    prompts = ["Type in the first line of your poem and press Enter: "]
    for i in (range(0, max_lines)): prompts.append("Type another line or just press Enter: ") 
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
        Spotify links to play tracks. """
    playlist = [] # list to store tracks
    print "Generating playlist..."
    for i in poem:
        playlist.append(get_tracks(i.split()))
    print "Here is your playlist:"
    for i in playlist:
        for x in i:
            print x.link

asterisk = track_match("asterisk") # track to represent * for non matches

if __name__ == "__main__":
    poem = list(multi_input())
    poem_to_playlist()
