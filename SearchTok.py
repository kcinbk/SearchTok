import requests 
import json
from time import sleep


def fetch_tiktok(access_token, search_query, start_date, end_date, cursor, search_id, sleep_timer, max_retries):
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    headers = {
        'Content-Type': 'application/json',
        'authorization': "Bearer "+ access_token
    }
    video_list = []
    i = 1
    # send initial request
    response = requests.post(endpoint, headers=headers, json=tiktok_params(search_query, start_date, end_date, cursor, search_id))
    # check intial request
    try:
        if response.status_code==200:
            print(f'Request no. {i} is good!')
            data = response.json()
            video_list.extend(data.get('data', {}).get('videos', []))
            cursor = data.get('data').get('cursor', '')
            search_id = data.get('data').get('search_id', '')
            has_more = data.get('data').get('has_more', False)
        else:
            print(f"A {response.status_code} error occurred during the initial request: {response.text}")
            raise Exception(f"Initial request failed with status code {response.status_code}")
        # Prerpare the subsequent requests
        while has_more == True:
            i +=1
            retry= 0
            print(f"Cursor for reqeust no.{i} will be {cursor}")
            print(f"Sleeping {sleep_timer} seconds before the sending out request no.{i}")
            sleep(sleep_timer)
            response = requests.post(endpoint, headers=headers, json=tiktok_params(search_query, start_date, end_date, cursor, search_id))
            print('Starting fetching again')
            if response.status_code==200:
                print('Request no.{i} request is good!')
                data = response.json()
                video_list.extend(data.get('data', {}).get('videos', []))
                cursor = data.get('data').get('cursor', '')
                search_id = data.get('data').get('search_id', '')
                has_more = data.get('data').get('has_more', False)
            elif response.status_code==500:
                while retry <= max_retries:
                    retry +=1
                    sleep_timer = sleep_timer * retry
                    print(f"Sleeping {sleep_timer} seconds due to 500 error.")
                    sleep(sleep_timer)
                    response = requests.post(endpoint, headers=headers, json=tiktok_params(search_query, start_date, end_date, cursor, search_id))
                    print(f'Retrying request no.{i} again')
                    if response.status_code==200:
                        print('Request no.{i} is good!')
                        data = response.json()
                        video_list.extend(data.get('data', {}).get('videos', []))
                        cursor = data.get('data').get('cursor', '')
                        search_id = data.get('data').get('search_id', '')
                        has_more = data.get('data').get('has_more', False)
                        break
                    else:
                        print(f"Exceeded maximum retries ({max_retries}). Unable to complete request no. {i}.")
            else:
                print(f"A {response.status_code} error has occur during sending request {i} due to {response.text}")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    return video_list