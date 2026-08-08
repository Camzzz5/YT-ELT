import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('./.env')

API_KEY = os.getenv('API_KEY')

CHANNEL_HANDLE = 'MrBeast'
maxResults = 50


def get_playlist_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        channel_items = data["items"][0]
        channel_playlistid = channel_items["contentDetails"]["relatedPlaylists"]['uploads']
        #print(channel_playlistid)
        return channel_playlistid
    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlist_id):
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_id}&key={API_KEY}'

    video_ids = []
    pageToken = None

    try:

        while True:
            url = base_url

            if pageToken:
                url += f'&pageToken={pageToken}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e



if __name__ == '__main__':
    playlist_id = get_playlist_id()
    print(get_video_ids(playlist_id))

