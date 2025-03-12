import requests
import json
import datetime
from time import sleep

def generate_token(client_key, client_secret):
    url = 'https://open.tiktokapis.com/v2/oauth/token/'
    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache',
    }
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=token_headers, data=data)
    access_token = response.json()['access_token']

    return access_token


def generate_date_ranges(start_date, end_date):
    date_ranges = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    current_date = start_date
    
    while current_date < end_date:
        next_date = current_date + datetime.timedelta(days=30)
        if next_date > end_date:
            next_date = end_date
        date_ranges.append((current_date.strftime("%Y%m%d"), next_date.strftime("%Y%m%d")))
        current_date = next_date
        
    return date_ranges


# Chunk longer search period into no more than 30 days due to TikTok's restriction
def generate_request_params(search_query, start_date, end_date, cursor, search_id):
    date_ranges = generate_date_ranges(start_date, end_date)
    
    params_list = []
    
    for range_start, range_end in date_ranges:
        params_list.append({
            "query": {
                "and": [
                    {
                        "operation": "IN",
                        "field_name": "keyword",
                        "field_values": search_query
                    }
                ]
            },
            "max_count": 100,
            "cursor": cursor,
            "start_date": range_start,
            "end_date": range_end,
            "search_id": search_id if search_id else None
        })
    
    return params_list



def fetch_tiktok(client_key, client_secret, search_query, start_date, end_date, cursor, search_id, sleep_timer=1, max_retries=3):

    access_token = generate_token(client_key, client_secret)
    
    endpoint = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,video_description,create_time,region_code,share_count,view_count,like_count,comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text,hashtag_info_list,sticker_info_list,video_mention_list,video_label"
    headers = {
        'Content-Type': 'application/json',
        'authorization': f"Bearer {access_token}"
    }
    video_list = []
    request_number = 1

    # Generate request parameters (one per date range)
    params_list = generate_request_params(search_query, start_date, end_date, cursor, search_id)

    # Iterate over each date range separately
    for tiktok_params in params_list:
        try:
            # Send nitial request for this date range
            response = requests.post(endpoint, headers=headers, json=tiktok_params)
            if response.status_code == 200:
                print(f'Request no. {request_number} is good!')
                data = response.json()
                video_list.extend(data.get('data', {}).get('videos', []))

                # Update cursor and search_id for pagination requests
                cursor = data.get('data', {}).get('cursor', '')
                search_id = data.get('data', {}).get('search_id', '')
                has_more = data.get('data', {}).get('has_more', False)
            else:
                raise Exception(f"Initial request failed with status code {response.status_code}")

            # Pagination loop for the current date range
            while has_more:
                request_number += 1
                
                # Update the tiktok_params with new cursor and search_id before making next request
                tiktok_params["cursor"] = cursor
                tiktok_params["search_id"] = search_id

                pagination_response = requests.post(endpoint, headers=headers, json=tiktok_params)
                
                if pagination_response.status_code == 200:
                    print(f"Request no. {request_number} is good!")
                    data = pagination_response.json()
                    video_list.extend(data.get('data', {}).get('videos', []))
                    
                    # Update cursor and search_id for paginating the next page
                    cursor = data.get('data', {}).get('cursor', '')
                    search_id = data.get('data', {}).get('search_id', '')
                    has_more = data.get('data', {}).get('has_more', False)

                elif pagination_response.status_code == 500:
                    retry = 0
                    while retry < max_retries:
                        retry += 1
                        enhanced_sleep_timer = sleep_timer * (2 ** retry)
                        sleep(enhanced_sleep_timer)
                        print(f"Due to 500 error. Retrying request no. {request_number} (attempt {retry}/{max_retries})")

                        pagination_response = requests.post(endpoint, headers=headers, json=tiktok_params)

                        if pagination_response.status_code == 200:
                            print(f"Request no. {request_number} is good after retry!")
                            data = pagination_response.json()
                            video_list.extend(data.get('data', {}).get('videos', []))
                            cursor = data.get('data', {}).get('cursor', '')
                            search_id = data.get('data', {}).get('search_id', '')
                            has_more = data.get('data', {}).get('has_more', False)
                            break 
                    else:
                        print(f"Exceeded maximum retries ({max_retries}). Unable to complete request no. {request_number}.")
                        has_more = False
                else:
                    print(f"A {pagination_response.status_code} error occurred during request {request_number}: {pagination_response.text}")
                    has_more = False  
        except Exception as e:
            print(f"An error occurred: {e}")
            break  

    return video_list


if __name__ == "__main__":
    client_key = '1233211234567'
    client_secret = 'abcdedfg'
    search_query = 'search query' 
    start_date= '2023-01-1' # date format example
    end_date= '2023-12-15' # date format example
    cursor= None
    search_id=None
    video_list = fetch_tiktok(client_key, client_secret, search_query, start_date, end_date, cursor, search_id)


