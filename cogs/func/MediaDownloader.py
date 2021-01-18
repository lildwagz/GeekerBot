import requests
import twitter
import os
import uuid
import json
from urllib.parse import urlparse


class MediaDownloader:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, output_dir="out/"):
        self.twitter_client = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token,
            access_token_secret=access_token_secret
        )
        self.supported_links = {
            "twitter.com": lambda x: self.twitter_link(x),
            "cdn.discordapp.com": lambda x: self.discord_link(x),
            "media.discordapp.net": lambda x: self.discord_link(x)
        }
        self.output_dir = output_dir

    def discord_link(self, link):
        filename = self.get_filename(link)
        parsed_url = urlparse(link)
        clean_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

        self.download_media(self.output_dir + filename, clean_url)
        return self.output_dir + filename

    def twitter_link(self, link):
        parsed_url = urlparse(link)
        status_id = os.path.basename(parsed_url.path)

        status = self.twitter_client.GetStatus(status_id).AsJsonString()
        media_list = json.loads(status).get("media")

        if media_list == None:
            with open(self.output_dir + "failed.txt", 'a') as f:
                f.write(link + "\n")
            return

        for media in media_list:
            type = media["type"]
            url = None

            if type == "photo":
                url = self.twitter_image(media)
            elif type == "video":
                url = self.twitter_video(media)
            else:
                print("Twitter media is not supported")
                return

            filename = self.get_filename(url)
            self.download_media(self.output_dir + filename, url)
        return self.output_dir + filename

    def get_filename(self, url):
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if filename == "unknown.png":
            file_ext = os.path.splitext(filename)[1]
            filename = str(uuid.uuid1().fields[0]) + file_ext
        return filename

    @staticmethod
    def download_media(filename, url):
        media = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in media.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return 1

    @staticmethod
    def twitter_video(video_media):
        video_variants = video_media["video_info"]["variants"]

        previous_bitrate = 0
        video_url = ""

        for video in video_variants:
            video_type = video["content_type"]
            if video_type == "application/x-mpegURL":
                continue

            current_bitrate = video["bitrate"]
            current_url = video["url"]
            if current_bitrate > previous_bitrate:
                previous_bitrate = current_bitrate
                video_url = current_url

        return video_url

    @staticmethod
    def twitter_image(image_media):
        image_url = image_media["media_url"]
        return image_url

    def download(self, url):
        uri_netloc = urlparse(url).netloc
        media = self.supported_links.get(uri_netloc)
        if media is None:
            return None
        return media(url)

    def download_from_file(self, input_file):
        with open(input_file, 'r') as f:
            lines = f.read().splitlines()
            line_count = len(lines)
            line_iter = 1

            if lines == None:
                print("Text file is empty")
                return

            for line in lines:
                self.download(line)
                print(f"Downloading media: {line_iter}/{line_count}", end="\r")
                line_iter += 1
        print("")
        return 1