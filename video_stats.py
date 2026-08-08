import requests
import json
from dotenv import load_dotenv
import os
from datetime import date
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


def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for video_id in range(0,len(video_id_list), batch_size):
            # print('#########')
            # print(video_id)
            # print(batch_size)
            # print('#########')
            yield video_id_list[video_id: video_id + batch_size]

    try:

        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ','.join(batch)

            url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}'

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):

                print(item)


                # break
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']



                video_data = {
                    'video_id':video_id,
                    'title': snippet['title'],
                    'publishedAt':snippet['publishedAt'],
                    'duration':contentDetails['duration'],
                    'viewCount':statistics.get('viewCount', None),
                    'likeCount':statistics.get('likeCount', None),
                    'commentCount':statistics.get('commentCount', None)
                }

                extracted_data.append(video_data)

        return extracted_data
    
    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    filepath = f'./data/YT_data_{date.today()}.json'
    with open(filepath, 'w', encoding = 'utf-8') as json_outfile:
        json.dump(extracted_data, json_outfile, indent = 4, ensure_ascii = False)


if __name__ == '__main__':
    playlist_id = get_playlist_id()
    #print(playlist_id)
    video_ids = get_video_ids(playlist_id)
    #print(video_ids)
    video_data = extract_video_data(video_ids)
    # print('&&&&&&&&&&&&&&&&')
    # print(video_data)
    # print('&&&&&&&&&&&&&&&&')
    save_to_json(video_data)

