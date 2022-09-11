from flask import Flask, render_template, request, jsonify, url_for, redirect, send_file
from libraries.flask_cors import CORS, cross_origin
from Modules.utilities import util
from Modules.scrapingData import scraping
import traceback
import logging

app = Flask(__name__)
logging.basicConfig(filename='mainPy.log',level=logging.INFO)

# Route to display the home page
@app.route('/',methods=['GET','POST'])
@cross_origin()
def homePage():
    return render_template('home/search.html')

########################################################################################################################

# Route to display the channel page - POST
@app.route('/channel',methods=['GET','POST'])
@cross_origin()
def getChannel():
    if request.method == 'POST':
        try:
            channel_url = request.form['channel_url'].replace(" ", "")
            logging.info('Input URL for Youtube Channel - ' + channel_url)
            valid = util.youtubeChannel_url_validation(channel_url)
            if valid:
                logging.info('Valid Youtube Channel - '+channel_url)
                channelData,videoList = scraping.Scraping().getChannelData(channel_url)
                return render_template('home/index.html',channelData = channelData,videoList = videoList)
            else:
                logging.error('Invalid Youtube Channel - ' + channel_url)
                return render_template('home/page-404.html'), 404

        except Exception as e:
            logging.error('Channel Page - '+str(traceback.format_exc()))
            print('The Exception message is: ',e)
            print(traceback.format_exc())
            return render_template('home/page-404.html'), 404
    else:
        return redirect(url_for('homePage'))

########################################################################################################################

# Route to display the video page - POST
@app.route('/video',methods=['GET','POST'])
@cross_origin()
def getVideo():
    if request.method == 'POST':
        try:
            video_url = request.form['link'].replace(" ","")
            title = request.form['title']
            views = request.form['views']
            duration = request.form['duration'].replace('/','')
            channel = request.form['channel']
            logging.info('Fetched Video Link - ' + video_url)
            valid = util.youtubeVideo_url_validation(video_url)
            if valid:
                logging.info('Valid Youtube Video Link - ' + video_url)
                videoData,commentsList = scraping.Scraping().getVideoData(video_url,title,views,duration)
                return render_template('home/video.html',videoData = videoData,commentsList = commentsList)
            else:
                logging.info('Invalid Youtube Video Link - ' + video_url)
                return render_template('home/page-404.html'), 404

        except Exception as e:
            logging.error('Video Page - ' + str(traceback.format_exc()))
            print('The Exception message is: ',e)
            print(traceback.format_exc())
            return render_template('home/page-404.html'), 404
    else:
        return redirect(url_for('homePage'))

########################################################################################################################

# Video Downloading function - POST
@app.route("/download",methods=['GET','POST'])
def download():
    if(request.method=='POST'):
        link = request.form['url']
        file_name = request.form['title']
        logging.info("Download Details - "+link)
        try:
            if link == '':
                 logging.error("Invalid Link")
                 return render_template('home/page-500.html'), 500
            else:
                util.uploadS3Video(link,file_name)
                buffer = util.downloadVideo(link)
                return send_file(buffer, as_attachment=True, download_name=file_name+".mp4", mimetype="video/mp4")
        except Exception as e:
            logging.error('Download Page - ' + str(traceback.format_exc()))
            print('The Exception message is: ', e)
            print(traceback.format_exc())
            return render_template('home/page-500.html'), 500

########################################################################################################################

if __name__ == "__main__":
	app.run(debug=True)

