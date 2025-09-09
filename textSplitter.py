from youtube_transcript_api import NoTranscriptFound, YouTubeTranscriptApi, TranscriptsDisabled
import requests
import json
import re
from bs4 import BeautifulSoup
def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title)
class GetYoutubeVideo:
    def __init__(self,url):
        self.id= url.split('v=')[1]
        self.url = url

    def transcriptMaker(self):
        try:
            transcript_data = None
            transcript_Instance = YouTubeTranscriptApi()
            transcript_list = transcript_Instance.list(video_id=self.id)

            english_codes = ['en', 'en-US', 'en-GB', 'en-IN', 'en-CA', 'en-AU']
            
            try:
                transcript_find = transcript_list.find_manually_created_transcript(language_codes=english_codes)
                transcript_data = transcript_find.fetch()
            except NoTranscriptFound:
                try:
                    transcript_find = transcript_list.find_generated_transcript(language_codes=english_codes)
                    transcript_data = transcript_find.fetch()
                    print("Found generated English transcript")
                except NoTranscriptFound:
                    try:
                        transcript_find = transcript_list.find_transcript(language_codes=english_codes)
                        transcript_data = transcript_find.fetch()
                        print("Found translated English transcript")
                    except NoTranscriptFound:
                        try:
                            transcript_data = transcript_Instance.fetch(video_id=self.id, languages=['hi'])
                            print("Found Hindi transcript")
                        except Exception as e:
                            print(f"No transcript found in English or Hindi: {e}")
                            return None

            if transcript_data:
                title = self.getTitle()
                videoLength = self.getLengthOfVideo()
                transcriptJson = self.saveTranscript(title, transcript_data, videoLength)
                return transcriptJson
            else:
                return None

        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video {self.id}")
            return None
        except Exception as e:
            print(f"Error in transcriptMaker: {e}")
            return None
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
