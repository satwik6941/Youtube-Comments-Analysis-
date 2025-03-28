from googleapiclient.discovery import build
import csv
import os 

API_KEY = 'YOUR_YOUTUBE_API_KEY'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_details(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    snippet = response['items'][0]['snippet']
    title = snippet['title'].lower()
    description = snippet['description'].lower()
    channel_name = snippet['channelTitle']

    keywords = ["iphone", "samsung", "pixel", "oneplus", "redmi", "vivo", "oppo",
                "realme", "moto", "asus", "sony", "nokia", "nothing", "xiaomi"]

    phone_name = next((word.capitalize() for word in keywords if word in title or word in description), "Unknown Device")

    print(f"Detected phone in video: {phone_name}")
    return phone_name, channel_name

def get_total_comments(video_id):
    response = youtube.videos().list(
        part='statistics',
        id=video_id
    ).execute()
    return int(response['items'][0]['statistics'].get('commentCount', 0))

def get_comments(video_id, max_comments):
    comments = []
    next_page_token = None
    count = 0  

    while count < max_comments:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText',
            maxResults=min(100, max_comments - count),
            pageToken=next_page_token
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append(comment['textDisplay'])
            count += 1
            if count >= max_comments:
                break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

def save_to_csv(phone_name, channel_name, comments, filename='comments.csv'):
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Phone which is being reviewed', 'Channel Name', 'Comment'])

        for comment in comments:
            writer.writerow([phone_name, channel_name, comment])

if __name__ == "__main__":
    while True:
        video_id = input("Enter YouTube Video ID (or type 'done' to exit): ").strip()

        if video_id.lower() == "done":
            print("Exiting... All comments saved to 'comments.csv'.")
            break

        try:
            phone_name, channel_name = get_video_details(video_id)
            print(f"Video Title suggests it's about: {phone_name}")
            print(f"Channel Name: {channel_name}")

            correct_phone_name = input(f"Is the detected phone name '{phone_name}' correct? (yes/no): ").strip().lower()
            if correct_phone_name == 'no':
                phone_name = input("Please enter the correct phone name: ").strip()

            total_comments = get_total_comments(video_id)
            print(f"Total comments on the video: {total_comments}")

            num_comments = int(input(f"Enter the number of comments to download (max {total_comments}): "))

            num_comments = min(num_comments, total_comments)

            comments = get_comments(video_id, num_comments)
            save_to_csv(phone_name, channel_name, comments)

            print(f"Downloaded {len(comments)} comments successfully for video ID: {video_id}\n")

        except Exception as e:
            print(f"Error: {e}\nPlease check the video ID and try again.")