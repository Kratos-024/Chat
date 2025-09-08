from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import requests
import json
import re
from bs4 import BeautifulSoup
def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title)
class GetYoutubeVideo:
    def __init__(self,video_id):
        self.id= video_id
        self.url = f'https://www.youtube.com/watch?v={self.id}'
        
    def transcriptMaker(self):
        ytt_api = YouTubeTranscriptApi()
        transcripts = ytt_api.fetch(self.id)
        title = self.getTitle()
        videoLength=self.getLengthOfVideo()
        print("videoLength",videoLength)
        transcriptJson = self.saveTranscript(title,transcripts,videoLength)
        return transcriptJson
    def getTitle(self):
        try:
            response = requests.get(self.url)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find('meta', property='og:title')
            video_title = title_tag['content'] if title_tag else 'Title not found'

            return video_title
        except Exception as e:
                print(e)
    def getLengthOfVideo(self):
        try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tag = soup.find('script', text=re.compile('ytInitialPlayerResponse'))
                if not script_tag:
                    return None
                json_text = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*\});', script_tag.string)
                if not json_text:
                    return None

                data = json.loads(json_text.group(1))
                length_seconds = data.get('videoDetails', {}).get('lengthSeconds')
                return int(length_seconds) if length_seconds else None
        except Exception as e:
            print(e)
    def saveTranscript(self, title, transcripts,videoLength):
        try:
            transcriptJson = []

            for transcript in transcripts:
                transcriptJson.append({
                    "start": transcript.start,
                    "end": transcript.duration,
                    "text": transcript.text
                })
            title = sanitize_filename(title)
          
            return {"title": title,"videoLength":videoLength ,"transcripts": transcriptJson}

        except Exception as e:
            print(e)
