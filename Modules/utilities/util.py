from pytube import YouTube
from io import BytesIO
import re
import boto3
import base64

def getS3Client():
    client = boto3.client('s3',
                          aws_access_key_id='AKIA5WH7MOAWR5PMGNF2',
                          aws_secret_access_key='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')
    return client

########################################################################################################################

def uploadS3Video(link,file_name):
    client = getS3Client()
    buffer = downloadVideo(link)
    bucket = 'kuttralanathan'
    client.upload_fileobj(buffer, bucket, 'youtube_scrapper/videos/' + file_name + '.mp4')
########################################################################################################################

def youtubeChannel_url_validation(url):
    youtube_regex = 'https?:\/\/(www\.)?youtube\.com\/(channel\/UC[\w-]{21}[AQgw]|(c\/|user\/)?[\w-]+)'
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match
    return youtube_regex_match

########################################################################################################################

def youtubeVideo_url_validation(url):
    youtube_regex = '^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match
    return youtube_regex_match

########################################################################################################################

def downloadVideo(link):
    buffer = BytesIO()
    yt = YouTube(link)
    ys = yt.streams.get_lowest_resolution()
    ys.stream_to_buffer(buffer)
    buffer.seek(0)
    return buffer