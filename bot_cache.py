import requests
import urllib.parse
import json
import time

from PIL import Image
import io

import jumpstartdata as jsd

class BotCache:

    uniqueListCache = {}
    uniqueListCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    uniqueListFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    scryFallJSONCardCache = {}
    scryFallJSONCardCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    scryFallJSONCardFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    imageCache = {}
    imageCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    imageFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    def __init__(self):
        theVariable = 0

    #Get the list from GitHub
    def fetchGitHubList(self, jset, uniqueList):
        theListText = ""

        startTime = time.time()
        self.uniqueListFetchStats['fetchCount'] = self.uniqueListFetchStats['fetchCount'] + 1

        url = f'https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/main/etc/{urllib.parse.quote(jset)}/{urllib.parse.quote(uniqueList)}.txt'
        req = requests.get(url)

        if(req.status_code == requests.codes.ok):
            theListText = f'{req.text}'
        else:
            self.uniqueListFetchStats['fetchFailures'] = self.uniqueListFetchStats['fetchFailures'] + 1
        
        endTime = time.time()
        self.uniqueListFetchStats['timeFetching'] = self.uniqueListFetchStats['timeFetching'] + (endTime - startTime)

        return theListText

    #Get the list from GitHub or the cache
    def fetchWithCacheGitHubList(self, jset, uniqueList):
        theListText = ""

        cacheKey = f"{jset}{uniqueList}"
        if(cacheKey not in self.uniqueListCache):
            self.uniqueListCacheStats['cacheMiss'] = self.uniqueListCacheStats['cacheMiss'] + 1
            theListText = self.fetchGitHubList(jset, uniqueList)
            self.uniqueListCache[cacheKey] = theListText
        else:
            self.uniqueListCacheStats['cacheHit'] = self.uniqueListCacheStats['cacheHit'] + 1
            theListText = self.uniqueListCache[cacheKey]

        return theListText

    #Get the JSON from ScryFall (be nice with hitting this)
    def fetchScryFallCardJSON(self, jset, exactCardName):
        scryFallJSON = json.loads("{}")

        startTime = time.time()
        self.scryFallJSONCardFetchStats['fetchCount'] = self.scryFallJSONCardFetchStats['fetchCount'] + 1

        #Fixing scryfall strangness
        if(jset == "BRO" and exactCardName == "UNEARTH"):
            exactCardName = "UNEARTH-(THEME)"
        elif(jset == "J22" and exactCardName == "BLINK"):
            exactCardName = "BLINK-(FRONT-CARD)"

        url = f"https://api.scryfall.com/cards/named?exact={urllib.parse.quote(exactCardName)}&pretty=true&set={urllib.parse.quote(jsd.sets[jset]['ScryfallFrontSetCode'])}"
        req = requests.get(url)
        if(req.status_code == requests.codes.ok):
            scryFallJSON = json.loads(req.text)
        else:
            self.scryFallJSONCardFetchStats['fetchFailures'] = self.scryFallJSONCardFetchStats['fetchFailures'] + 1
            scryFallJSON = json.loads("{}")
            print(f"FAILURE - '{jset}' '{exactCardName}'\n")
        
        endTime = time.time()
        self.scryFallJSONCardFetchStats['timeFetching'] = self.scryFallJSONCardFetchStats['timeFetching'] + (endTime - startTime)

        return scryFallJSON

    #Get the card image url from scryFall or the cache
    def fetchThemeImageURLWithCacheScryfallCardJSONURL(self, jset, theme):
        theListThemeCardImageUrl = ""
        
        cacheKey = f"{jset}{theme}"

        if(cacheKey not in self.scryFallJSONCardCache):
            self.scryFallJSONCardCacheStats['cacheMiss'] = self.scryFallJSONCardCacheStats['cacheMiss'] + 1
            scryFallJSON = self.fetchScryFallCardJSON(jset, theme)
            self.scryFallJSONCardCache[cacheKey] = scryFallJSON
            theListThemeCardImageUrl = self.scryFallJSONCardCache[cacheKey]["image_uris"]["small"]
        else:
            self.scryFallJSONCardCacheStats['cacheHit'] = self.scryFallJSONCardCacheStats['cacheHit'] + 1
            theListThemeCardImageUrl = self.scryFallJSONCardCache[cacheKey]["image_uris"]["small"]

        return theListThemeCardImageUrl

    def fetchScryFallCardImage(self, jset, exactCardName):

        cardImage = Image.new('RGBA', (1, 1))

        theListThemeCardImageUrl = self.fetchThemeImageURLWithCacheScryfallCardJSONURL(jset, exactCardName)

        startTime = time.time()

        self.imageFetchStats['fetchCount'] = self.imageFetchStats['fetchCount'] + 1

        imageDataResults = requests.get(theListThemeCardImageUrl, stream=True)
        if(imageDataResults.status_code == requests.codes.ok):
            cardImage = Image.open(imageDataResults.raw)
        else:
            self.imageFetchStats['fetchFailures'] = self.imageFetchStats['fetchFailures'] + 1
            cardImage = Image.new('RGBA', (1, 1))

        endTime = time.time()

        self.imageFetchStats['timeFetching'] = self.imageFetchStats['timeFetching'] + (endTime - startTime)

        return cardImage


    #Get the card image url from scryFall or the cache
    def fetchThemeImageWithCacheScryfallCardImage(self, jset, theme):
        cardImage = Image.new('RGBA', (1, 1))
        
        cacheKey = f"{jset}{theme}"

        if(cacheKey not in self.imageCache):
            self.imageCacheStats['cacheMiss'] = self.imageCacheStats['cacheMiss'] + 1
            cardImage = self.fetchScryFallCardImage(jset, theme)
            self.imageCache[cacheKey] = cardImage
        else:
            self.imageCacheStats['cacheHit'] = self.imageCacheStats['cacheHit'] + 1
            cardImage = self.imageCache[cacheKey]

        return cardImage

    def purgeImageCache(self):
        self.imageCache = {}

    def purgeScryfallJSONCardCache(self):
        self.scryFallJSONCardCache = {}

    def __str__(self):
        return f"""Bot Cache Statistics: (hits / misses / items)
        uniqueListCache       {self.uniqueListCacheStats['cacheHit']} / {self.uniqueListCacheStats['cacheMiss']} / {len(self.uniqueListCache)}
        scryFallJSONCardCache {self.scryFallJSONCardCacheStats['cacheHit']} / {self.scryFallJSONCardCacheStats['cacheMiss']} / {len(self.scryFallJSONCardCache)}
        imageCache            {self.imageCacheStats['cacheHit']} / {self.imageCacheStats['cacheMiss']} / {len(self.imageCache)}

Bot Fetch Statistics: (fetches (failures)/ total time)
        uniqueListFetch       {self.uniqueListFetchStats['fetchCount']} ({self.uniqueListFetchStats['fetchFailures']}) / {self.uniqueListFetchStats['timeFetching']}
        scryFallJSONCardFetch {self.scryFallJSONCardFetchStats['fetchCount']} ({self.scryFallJSONCardFetchStats['fetchFailures']}) / {self.scryFallJSONCardFetchStats['timeFetching']}
        imageFetch            {self.imageFetchStats['fetchCount']} ({self.imageFetchStats['fetchFailures']}) / {self.imageFetchStats['timeFetching']}
        """