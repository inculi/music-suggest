import requests
import requests.auth
import sys
import os
from os.path import expanduser

# Access token for the reddit API
bearer = ''

# API key
key = ''

# Client name for the reddit API
client = "musicsuggest/0.1 by jay911144"

# An array of the songs for easy iteration
songs = []

# Download path
path = '/media/Plex/musicsuggest/'

# Get the API key from the user folder
def getKey():
    global key
    home = expanduser("~")
    f = open(home + '/key.txt')
    key = f.read()
    f.close()

# Get the token from the reddit API
def getToken():
    global key
    global bearer
    global client
    client_auth = requests.auth.HTTPBasicAuth('on6UGYQopYR99A', key)
    post_data = {"grant_type": "password", "username": "iwasnttrainedforthis", "password": "ishouldhavebeen"}
    headers = {"User-Agent": client}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    try:
        bearer = response.json()['access_token']
    except KeyError:
        print 'Invalid key. Please make sure there are no spaces or extra lines in the key file'
        exit()

def makeRequest():
    global bearer
    global client
    global songs

    # Reddit API authentication
    headers = {"Authorization": "bearer " + bearer, "User-Agent": client}

    # Download the subreddit that is requested
    response = requests.get("https://oauth.reddit.com/r/" + sys.argv[1], headers=headers)
    raw = response.json()

    # Currently I only have it set to do Youtube. It could VERY easily do soundcloud and other websites, except maybe Spotify
    for item in raw['data']['children']:
        if 'youtube.com' in item['data']['domain'] or 'youtu.be' in item['data']['domain']:
            songs.append(item['data'])

# Download the songs in the songs list
def downloadSongs(songs):
    for item in songs:
        # Most if not all song posts in the listentothis subreddit and the music subreddit have a dash in the name seperating
        # the artist and the song title. Plex cannot get the metadata for the songs without enoug information (such as just the song title and artist),
        # but it will work if the song is in a folder with the artist or band name as the folder name.
        try:
            # If there are not two dashes in the title, there is only going to be one. Sometimes there are two. I don''t know why.
            if not '--' in item['title']:
                artist = item['title'].split('-')[0].lower()
                #This part handles the second dash if there is one.
                if item['title'][0] == '-':
                    artist = item['title'].split('-')[1].lower()
            #If there are two dashes, just get the title.
            else:
                artist = item['title'].split('--')[0].lower()
        # If for some reason people are retarded and don't follow the formatting rules, then we can't get the artist. If this is
        # the case, set the artist name to Unknown Artist.
        except:
            print 'Unable to find artist name'
            artist = 'Unknown Artist'
        # This is where the magic of music-suggest will happen. Every post that I have seen has the genre of the song in brackets
        # at the end of the post title. The only thing I am currently doing with that is making sure that the songs I am downlading
        # are not country or rap, because I hate them.
        if not 'rap' in item['title'].split('[')[1].replace(']', ' ').lower() and not 'country' in item['title'].split('[')[1].replace(']', ' ').lower():
            os.system('youtube-dl -f 140 \"' + item['url'] + '\"  --output \"' + path + artist.rstrip() + '/%(title)s.%(ext)s\"')

getKey()
getToken()
makeRequest()
downloadSongs(songs)
