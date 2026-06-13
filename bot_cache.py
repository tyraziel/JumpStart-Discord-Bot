import requests
import urllib.parse
import json
import time

from PIL import Image
import io

import jumpstartdata as jsd

REQUEST_HEADERS = {
    'User-Agent': 'JumpStart-Discord-Bot/1.0.5 (Discord bot; https://github.com/tyraziel/JumpStart-Discord-Bot)'
}

class BotCache:

    uniqueListCache = {}
    uniqueListCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    uniqueListFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    deckJSONCache = {}
    deckJSONCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    deckJSONFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    masterDeckJSON = None
    masterDeckJSONStats = {'loaded': False, 'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

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
        req = requests.get(url, headers=REQUEST_HEADERS)

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

    #Get the master combined deck JSON from GitHub
    def fetchMasterDeckJSON(self):
        masterJSON = {}

        startTime = time.time()
        self.masterDeckJSONStats['fetchCount'] = self.masterDeckJSONStats['fetchCount'] + 1

        url = 'https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/refs/heads/main/etc/jumpstart-decks-combined.json'
        req = requests.get(url, headers=REQUEST_HEADERS)

        if(req.status_code == requests.codes.ok):
            masterJSON = json.loads(req.text)
            self.masterDeckJSONStats['loaded'] = True
        else:
            self.masterDeckJSONStats['fetchFailures'] = self.masterDeckJSONStats['fetchFailures'] + 1
            masterJSON = {}

        endTime = time.time()
        self.masterDeckJSONStats['timeFetching'] = self.masterDeckJSONStats['timeFetching'] + (endTime - startTime)

        return masterJSON

    #Get the deck JSON from GitHub
    def fetchGitHubDeckJSON(self, jset, uniqueList):
        deckJSON = {}

        startTime = time.time()
        self.deckJSONFetchStats['fetchCount'] = self.deckJSONFetchStats['fetchCount'] + 1

        url = f'https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/main/etc/{urllib.parse.quote(jset)}/{urllib.parse.quote(uniqueList)}.json'
        req = requests.get(url, headers=REQUEST_HEADERS)

        if(req.status_code == requests.codes.ok):
            deckJSON = json.loads(req.text)
        else:
            self.deckJSONFetchStats['fetchFailures'] = self.deckJSONFetchStats['fetchFailures'] + 1
            deckJSON = {}

        endTime = time.time()
        self.deckJSONFetchStats['timeFetching'] = self.deckJSONFetchStats['timeFetching'] + (endTime - startTime)

        return deckJSON

    #Get the deck JSON from GitHub or the cache
    def fetchWithCacheGitHubDeckJSON(self, jset, uniqueList):
        deckJSON = {}

        # Try master deck JSON first (load once, use forever)
        if self.masterDeckJSON is None:
            self.masterDeckJSON = self.fetchMasterDeckJSON()

        # Check if deck exists in master JSON
        masterKey = f"{jset}:{uniqueList}"
        if self.masterDeckJSON and 'decks' in self.masterDeckJSON and masterKey in self.masterDeckJSON['decks']:
            self.deckJSONCacheStats['cacheHit'] = self.deckJSONCacheStats['cacheHit'] + 1
            return self.masterDeckJSON['decks'][masterKey]

        # Fallback to individual deck JSON with caching
        cacheKey = f"{jset}{uniqueList}"
        if(cacheKey not in self.deckJSONCache):
            self.deckJSONCacheStats['cacheMiss'] = self.deckJSONCacheStats['cacheMiss'] + 1
            deckJSON = self.fetchGitHubDeckJSON(jset, uniqueList)
            self.deckJSONCache[cacheKey] = deckJSON
        else:
            self.deckJSONCacheStats['cacheHit'] = self.deckJSONCacheStats['cacheHit'] + 1
            deckJSON = self.deckJSONCache[cacheKey]

        return deckJSON

    #Get the JSON from ScryFall (be nice with hitting this)
    def fetchScryFallCardJSON(self, jset, exactCardName):
        scryFallJSON = json.loads("{}")

        startTime = time.time()
        self.scryFallJSONCardFetchStats['fetchCount'] = self.scryFallJSONCardFetchStats['fetchCount'] + 1

        #Fixing scryfall strangeness
        if(jset == "BRO" and exactCardName == "UNEARTH"):
            exactCardName = "UNEARTH-(THEME)"
        elif(jset == "J25" and exactCardName == "N'ER-DO-WELLS"):
            exactCardName = "NEER-DO-WELLS"

        # Cards that need collector number lookup due to naming conflicts on Scryfall
        if jset == "MSB" and exactCardName == "TUTORIAL (CAPTAIN AMERICA)":
            url = "https://api.scryfall.com/cards/fmsc/2"
        elif jset == "MSB" and exactCardName == "TUTORIAL (IRON MAN)":
            url = "https://api.scryfall.com/cards/fmsc/7"
        elif jset == "MSH" and exactCardName == "BLINK":
            url = "https://api.scryfall.com/cards/fmsc/23"
        else:
            url = f"https://api.scryfall.com/cards/named?exact={urllib.parse.quote(exactCardName)}&pretty=true&set={urllib.parse.quote(jsd.sets[jset]['ScryfallFrontSetCode'])}"
        req = requests.get(url, headers=REQUEST_HEADERS)
        if(req.status_code == requests.codes.ok):
            scryFallJSON = json.loads(req.text)
        else:
            self.scryFallJSONCardFetchStats['fetchFailures'] = self.scryFallJSONCardFetchStats['fetchFailures'] + 1
            scryFallJSON = json.loads("{}")
            print(f"FAILURE - '{jset}' '{exactCardName}'\n")
        
        endTime = time.time()
        self.scryFallJSONCardFetchStats['timeFetching'] = self.scryFallJSONCardFetchStats['timeFetching'] + (endTime - startTime)

        return scryFallJSON

    def _extractImageUri(self, scryFallJSON):
        if 'image_uris' in scryFallJSON:
            return scryFallJSON['image_uris']['small']
        if 'card_faces' in scryFallJSON and scryFallJSON['card_faces']:
            face = scryFallJSON['card_faces'][0]
            if 'image_uris' in face:
                return face['image_uris']['small']
        return ''

    #Get the card image url from scryFall or the cache
    def fetchThemeImageURLWithCacheScryfallCardJSONURL(self, jset, theme):
        theListThemeCardImageUrl = ""

        cacheKey = f"{jset}{theme}"

        if(cacheKey not in self.scryFallJSONCardCache):
            self.scryFallJSONCardCacheStats['cacheMiss'] = self.scryFallJSONCardCacheStats['cacheMiss'] + 1
            scryFallJSON = self.fetchScryFallCardJSON(jset, theme)
            if scryFallJSON:
                self.scryFallJSONCardCache[cacheKey] = scryFallJSON
            theListThemeCardImageUrl = self._extractImageUri(scryFallJSON)
        else:
            self.scryFallJSONCardCacheStats['cacheHit'] = self.scryFallJSONCardCacheStats['cacheHit'] + 1
            theListThemeCardImageUrl = self._extractImageUri(self.scryFallJSONCardCache[cacheKey])

        return theListThemeCardImageUrl

    def fetchScryFallCardImage(self, jset, exactCardName):

        cardImage = Image.new('RGBA', (1, 1))

        theListThemeCardImageUrl = self.fetchThemeImageURLWithCacheScryfallCardJSONURL(jset, exactCardName)

        if not theListThemeCardImageUrl:
            return cardImage

        startTime = time.time()

        self.imageFetchStats['fetchCount'] = self.imageFetchStats['fetchCount'] + 1

        imageDataResults = requests.get(theListThemeCardImageUrl, headers=REQUEST_HEADERS, stream=True)
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

    def purgeListCache(self):
        self.uniqueListCache = {}

    def purgeDeckJSONCache(self):
        self.deckJSONCache = {}

    def purgeMasterDeckJSON(self):
        self.masterDeckJSON = None
        self.masterDeckJSONStats['loaded'] = False

    def __str__(self):
        masterDeckCount = len(self.masterDeckJSON.get('decks', {})) if self.masterDeckJSON else 0
        masterLoaded = "✓" if self.masterDeckJSONStats['loaded'] else "✗"

        return f"""Bot Cache Statistics: (hits / misses / items)
        uniqueListCache       {self.uniqueListCacheStats['cacheHit']} / {self.uniqueListCacheStats['cacheMiss']} / {len(self.uniqueListCache)}
        deckJSONCache         {self.deckJSONCacheStats['cacheHit']} / {self.deckJSONCacheStats['cacheMiss']} / {len(self.deckJSONCache)}
        masterDeckJSON        {masterLoaded} Loaded / {masterDeckCount} decks
        scryFallJSONCardCache {self.scryFallJSONCardCacheStats['cacheHit']} / {self.scryFallJSONCardCacheStats['cacheMiss']} / {len(self.scryFallJSONCardCache)}
        imageCache            {self.imageCacheStats['cacheHit']} / {self.imageCacheStats['cacheMiss']} / {len(self.imageCache)}

Bot Fetch Statistics: (fetches (failures)/ total time)
        uniqueListFetch       {self.uniqueListFetchStats['fetchCount']} ({self.uniqueListFetchStats['fetchFailures']}) / {self.uniqueListFetchStats['timeFetching']}
        deckJSONFetch         {self.deckJSONFetchStats['fetchCount']} ({self.deckJSONFetchStats['fetchFailures']}) / {self.deckJSONFetchStats['timeFetching']}
        masterDeckJSONFetch   {self.masterDeckJSONStats['fetchCount']} ({self.masterDeckJSONStats['fetchFailures']}) / {self.masterDeckJSONStats['timeFetching']}
        scryFallJSONCardFetch {self.scryFallJSONCardFetchStats['fetchCount']} ({self.scryFallJSONCardFetchStats['fetchFailures']}) / {self.scryFallJSONCardFetchStats['timeFetching']}
        imageFetch            {self.imageFetchStats['fetchCount']} ({self.imageFetchStats['fetchFailures']}) / {self.imageFetchStats['timeFetching']}
        """
