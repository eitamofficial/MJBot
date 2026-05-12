import os
from googleapiclient.discovery import build
from mj_bot.core.config import YOUTUBE_API_KEY, MJ_OFFICIAL_CHANNEL_ID

class YouTubeManager:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.channel_id = MJ_OFFICIAL_CHANNEL_ID
        self.youtube = build('youtube', 'v3', developerKey=self.api_key) if self.api_key else None

    async def fetch_discography(self):
        if not self.youtube:
            return []

        print("📡 Récupération de la discographie MJ en cours (Plus de titres)...")
        discography = []
        
        try:
            # On récupère plus de titres en paginant ou en augmentant maxResults
            # On va faire 2 pages de 50 pour avoir 100 titres
            next_page_token = None
            for _ in range(2):
                request = self.youtube.search().list(
                    channelId=self.channel_id,
                    part="snippet",
                    maxResults=50,
                    order="viewCount",
                    type="video",
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    title = item['snippet']['title'].lower()
                    if any(x in title for x in ["official", "music video", "audio", "remastered"]):
                        if not any(x in title for x in ["cover", "tribute", "fan made", "reaction"]):
                            video_id = item['id']['videoId']
                            discography.append({
                                'id': video_id,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'title': item['snippet']['title']
                            })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            # Fallback if empty
            if not discography:
                request = self.youtube.search().list(
                    q="Michael Jackson Official Music Video",
                    part="snippet",
                    maxResults=50,
                    type="video"
                )
                response = request.execute()
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    discography.append({
                        'id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'title': item['snippet']['title']
                    })

            return discography
        except Exception as e:
            print(f"❌ Erreur YouTube API : {e}")
            return []
