from Modules.chromeDriver.driver import *
from Modules.database.mySQLConnector import *
from Modules.database.mongoDBConnector import *
import datetime
import time
from dateutil.relativedelta import relativedelta
import logging
import traceback
import re


class Scraping:
    def __init__(self):
        self.driver = ChromeDriver().getDriver()

########################################################################################################################

    def getDurationInSeconds(self,duration):
        '''
            Returns given duration value in Seconds
            E.g. duration = 02:25 -----> 145 seconds
        '''
        if ':' in duration and len(duration.split(":")) < 3 and len(duration.split(":")) > 0:
            duration_s = '00:' + duration
        elif ':' in duration and len(duration.split(":")) == 3:
            duration_s = duration

        if ':' in duration and len(duration) > 0:
            duration_seconds = time.strptime(duration_s, '%H:%M:%S')
            duration_seconds = datetime.timedelta(hours=duration_seconds.tm_hour, minutes=duration_seconds.tm_min,
                                                  seconds=duration_seconds.tm_sec).seconds
            self.durationList.append(int(duration_seconds / 60))

########################################################################################################################

    def getCount(self,data):
        '''
            Returns the count in float value for given input
            E.g. count = 12K -----> 12000.0
        '''
        if type(data) == int:
            return data

        count = 0
        data = data.split(" ")[0]
        if 'K' in data:
            count = data.split('K')[0]
            count = float(count) * (10 ** 3)
        elif 'M' in data:
            count = data.split('K')[0]
            count = float(count) * (10 ** 6)
        elif data.isdigit():
            count = float(data)

        return count

########################################################################################################################

    def getUploadData(self,upload_month):
        '''
            Returns dictionary with month wise data
        '''
        months = {'1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'June', '7': 'Jul', '8': 'Aug',
                  '9': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

        if len(upload_month.split(" ")) != 3:
            upload_month = upload_month.replace(upload_month.split(" ")[0] + " ", "")
        val, unit = upload_month.split()[:2]
        upload_month = datetime.datetime.now() - relativedelta(**{unit: int(val)})
        month_i = str(upload_month.month)
        if months[month_i] in self.uploadDict:
            self.uploadDict[months[month_i]] = self.uploadDict[months[month_i]] + 1
        else:
            self.uploadDict[months[month_i]] = 1

########################################################################################################################

    def getChannelData(self,url):
        '''

        :param url: channel_link
        :return: Channel Data and List of latest 50 Videos

        Fetch Youtube channel Data from given URL using selenium

        '''
        try:
            self.durationList = []
            self.uploadDict = {}
            viewsList = []
            videoList = []
            videoMongoList = []
            videoDBList = []

            driver = self.driver
            driver.get(url + '/about')
            ChromeDriver().scrollPageEnd(driver)
            
            dp = driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/div[2]/div/div[1]/yt-img-shadow/img').get_attribute('src')

            # Changing pixel for Channel Profile Picture
            dp = re.sub('=s\d+', '=s500', dp)

            channelName = driver.find_element_by_xpath(
                '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/div[2]/div/div[1]/div/div[1]/ytd-channel-name/div/div/yt-formatted-string').text
            description = driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-channel-about-metadata-renderer/div[1]/div[1]/yt-formatted-string[2]').text
            joined = driver.find_element_by_xpath('//*[@id="right-column"]/yt-formatted-string[2]/span[2]').text
            total_views = driver.find_element_by_xpath('//*[@id="right-column"]/yt-formatted-string[3]').text
            subscribers = driver.find_element_by_xpath('//*[@id="subscriber-count"]').text

            channel_Details = {'profilePic': dp, 'name': channelName, 'description': description, 'joined_date': joined,
                               'totalViews': total_views, 'subscribers': subscribers, 'channelLink': url}
            channel_Mongo = {'channel_name': channelName, 'channel_dp': dp, 'description': description, 'joined_date': joined,
                               'total_views': total_views, 'subscribers': subscribers, 'channel_link': url}

            driver.get(url + '/videos')
            driver.maximize_window()

            idx = 1
            driver.execute_script('window.scrollBy(0, 1000);')

            for i in range(0, 50):
                if idx % 18 == 0:
                    driver.execute_script('window.scrollBy(0, 1000);')
                    time.sleep(0.5)
                    driver.execute_script('window.scrollBy(0, 1000);')

                title_xpath = '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/div[1]/div[1]/h3/a'
                img_xpath = '/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/ytd-thumbnail/a/yt-img-shadow/img'
                duration_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/ytd-thumbnail/a/div[1]/ytd-thumbnail-overlay-time-status-renderer/span'
                views_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/div[1]/div[1]/div/div[1]/div[2]/span[1]'
                uploaded_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/div[1]/div[1]/div/div[1]/div[2]/span[2]'
                link_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[' + str(
                    idx) + ']/div[1]/div[1]/div[1]/h3/a'

                video_title = driver.find_element_by_xpath(title_xpath).text
                thumbnailLink = driver.find_element_by_xpath(img_xpath).get_attribute('src')
                duration = driver.find_element_by_xpath(duration_xpath).text
                views = driver.find_element_by_xpath(views_xpath).text
                uploaded = driver.find_element_by_xpath(uploaded_xpath).text
                link = driver.find_element_by_xpath(link_xpath).get_attribute('href')


                if '/shorts/' not in link:

                    self.getDurationInSeconds(duration)

                    view_count = self.getCount(views)
                    viewsList.append(view_count)

                    videoData = {'video_title': video_title, 'thumbnailLink': thumbnailLink, 'duration': duration,
                                 'views': views, 'uploaded': uploaded, 'link': link}
                    videoMongoData = {'video_name': video_title, 'video_thumbnail': thumbnailLink, 'duration': duration,
                                 'views': views, 'uploaded': uploaded, 'video_link': link}
                    videoList.append(videoData)
                    videoMongoList.append(videoMongoData)
                    videoDBList.append((video_title,duration,views,link))

                idx += 1

            driver.close()
            avg_views = '{:,}'.format(int(sum(viewsList)/len(viewsList)))
            avg_duration = round((sum(self.durationList)/len(self.durationList)),2)

            channel_Details['avg_views'] = avg_views
            channel_Details['viewsList'] = viewsList
            channel_Details['avg_duration'] = avg_duration
            channel_Details['durationList'] = self.durationList

            # Uploading files to MySQL and MongoDB

            channelDB = (channelName,joined,subscribers,total_views,url)
            row_count = MySQLConnector().insertChannel(channelDB)
            if row_count > 0:
                print("Channel Data inserted in MySQL.....")
                logging.info("Channel Data inserted in MySQL.....")
            response = mongoDBConnector().insertChannel(channel_Mongo)
            if response is not None:
                print("Channel Data inserted in MongoDB.....")
                logging.info("Channel Data inserted in MongoDB.....")

            row_count = MySQLConnector().insertVideo(videoDBList,url)
            if row_count > 0:
                print("Video Data inserted in MySQL.....")
                logging.info("Video Data inserted in MySQL.....")
            response = mongoDBConnector().insertVideo(url,videoMongoList)
            if response is not None:
                print("Video Data inserted in MongoDB.....")
                logging.info("Video Data inserted in MongoDB.....")

            logging.info('Fetched Channel Data.... ')
            logging.info('Fetched Video Data....')

            return channel_Details, videoList

        except Exception as e:
            logging.error('Channel Page - ' + str(traceback.format_exc()))
            print('The Exception message is: ', e)
            print(traceback.format_exc())

########################################################################################################################

    def getVideoData(self, url,title,views,duration):
        '''

        :param url: video_link
        :param title: video_name
        :param views: Number of views
        :param duration: Duration of video
        :return: Number of likes,comments & List of comments

        Fetching Video Data for given Youtube video link
        '''
        try:
            commentsList = []
            cmntsDBList = []
            cmntsMongoList = []
            driver = self.driver
            driver.get(url)
            driver.maximize_window()

            ChromeDriver().scrollPageEnd(driver)

            likes = driver.find_element_by_xpath(
                '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/div[7]/div[1]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/div[1]/ytd-toggle-button-renderer[1]/a/yt-formatted-string').text
            cmnts = driver.find_element_by_xpath(
                '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-comments/ytd-item-section-renderer/div[1]/ytd-comments-header-renderer/div[1]/h2/yt-formatted-string/span[1]').text

            embed_url = url.replace('watch?v=', 'embed/')

            comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
            commentor_Name = driver.find_elements_by_xpath('//*[@id="header-author"]')

            for i in range(len(commentor_Name)):
                cmntr_Name = commentor_Name[i].text.split("\n")
                name = cmntr_Name[0]
                modified = cmntr_Name[-1]
                data = comment_elems[i].text
                cmntsData = {'name': name, 'modified': modified, 'data': data}
                cmntsMongoData = {'name': name, 'comments': data, 'commented': modified}
                cmntsDBList.append((name, modified))
                cmntsMongoList.append(cmntsMongoData)
                commentsList.append(cmntsData)

            if likes == '':
                likes = 0

            views_count = self.getCount(views)
            likes_count = self.getCount(likes)
            cmnts_count = self.getCount(cmnts)

            videoData = {'title': title, 'views': views, 'likes': likes, 'cmnts': cmnts, 'embed_url': embed_url,
                         'duration': duration, 'pieData': [int(views_count), int(likes_count), int(cmnts_count)]}
            driver.close()

            row_count = MySQLConnector().updateVideo(likes, cmnts, url)
            if row_count > 0:
                print("Data Updated in MySQL....")
                logging.info("Data Updated in MySQL....")

            row_count = MySQLConnector().insertComments(cmntsDBList, url)
            if row_count > 0:
                print("Comments Created in MySQL....")
                logging.info("Comments Created in MySQL....")

            videoMongoData = {'likes': likes, 'comments': cmnts, 'comment_details': cmntsMongoList}
            response = mongoDBConnector().updateVideo(url, videoMongoData)
            if response is not None:
                print("Video Data updated in MongoDB.....")
                logging.info("Video Data updated in MongoDB.....")

            return videoData, commentsList

        except Exception as e:
            logging.error('Video Page - ' + str(traceback.format_exc()))
            print('The Exception message is: ', e)
            print(traceback.format_exc())

########################################################################################################################

