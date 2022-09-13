import mysql.connector as conn

class MySQLConnector:

    def getCursor(self):
        try:
            self.mydb = conn.connect(host="database-1.cleqdbolhsqb.us-west-2.rds.amazonaws.com",
                    user = "user", passwd = "password", db="youtube_scrapper")
            cursor = self.mydb.cursor()
            return cursor
        except Exception as e:
            print(e)

########################################################################################################################

    def insertComments(self,cmntsList,url):
        try:
            cursor = self.getCursor()
            create_commentors = "create table if not exists commentors" \
                           "(comment_id INT AUTO_INCREMENT PRIMARY KEY," \
                           "commentor_name VARCHAR(255)," \
                           "commented_date VARCHAR(255)," \
                            "video_id INT," \
                           "FOREIGN KEY (video_id) REFERENCES videos(video_id))"
            cursor.execute(create_commentors)
            print('Commentors Table created...')

            video_id = self.getVideoId(cursor,url)

            for cmntsData in cmntsList:
                name = cmntsData[0]
                commented_on = cmntsData[1]
                insert_commentor = "INSERT IGNORE INTO commentors " \
                                   "(commentor_name, video_id) " \
                                   "VALUES (%s, %s)"
                cursor.execute(insert_commentor, (name, video_id))

                update_commentor = "UPDATE commentors SET commented_date = %s WHERE video_id = %s"
                cursor.execute(update_commentor, (commented_on, video_id))
            self.mydb.commit()
            row_count = cursor.rowcount
            cursor.close()
            return row_count

        except Exception as e:
            print(e)

########################################################################################################################

    def insertChannel(self,channelDetails):
        try:
            cursor = self.getCursor()
            create_channel = "create table if not exists channel" \
                           "(channel_id INT AUTO_INCREMENT PRIMARY KEY," \
                           "channel_name VARCHAR(255)," \
                           "joined_date VARCHAR(255)," \
                            "subscribers VARCHAR(255)," \
                            "total_views VARCHAR(255)," \
                           "channel_link VARCHAR(255) UNIQUE)"
            cursor.execute(create_channel)
            print('Channel Table created...')

            insert_channel = "INSERT IGNORE INTO channel " \
                             "(channel_name, joined_date, subscribers, total_views, channel_link) " \
                             "VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_channel,channelDetails)
            self.mydb.commit()
            row_count = cursor.rowcount
            cursor.close()
            return row_count

        except Exception as e:
            print(e)

########################################################################################################################

    def insertVideo(self,videoList,channel_link):
        try:
            cursor = self.getCursor()
            create_channel = "create table if not exists videos" \
                           "(video_id INT AUTO_INCREMENT PRIMARY KEY," \
                           "video_name VARCHAR(255)," \
                           "duration VARCHAR(255)," \
                           "likes VARCHAR(255)," \
                           "comments VARCHAR(255)," \
                           "views VARCHAR(255)," \
                           "download_link VARCHAR(255)," \
                           "video_link VARCHAR(255) UNIQUE," \
                           "channel_id INT," \
                           "FOREIGN KEY (channel_id) REFERENCES channel(channel_id))"
            cursor.execute(create_channel)
            print('Video Table created...')

            channel_id = self.getChannelId(cursor,channel_link)

            for videoData in videoList:
                videoData = videoData + (channel_id,)
                insert_video = "INSERT IGNORE INTO videos " \
                               "(video_name, duration, views, video_link, channel_id) " \
                               "VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_video,videoData)

            self.mydb.commit()
            row_count = cursor.rowcount
            cursor.close()
            return  row_count

        except Exception as e:
            print(e)

########################################################################################################################

    def updateVideo(self,likes,cmnts,url):
        cursor = self.getCursor()
        path = 's3://kuttralanathan/youtube_scrapper/videos/<video_name>.mp4'
        update_query = "UPDATE videos SET likes = %s WHERE video_link = %s"
        cursor.execute(update_query,(likes,url))
        update_query = "UPDATE videos SET comments = %s WHERE video_link = %s"
        cursor.execute(update_query, (cmnts, url))
        update_query = "UPDATE videos SET download_link = %s WHERE video_link = %s"
        cursor.execute(update_query, (path, url))
        self.mydb.commit()
        row_count = cursor.rowcount
        cursor.close()
        return row_count

########################################################################################################################

    def getChannelId(self,cursor,url):
        query = "select channel_id from channel where channel_link = '"+url+"'"
        cursor.execute(query)
        return cursor.fetchone()[0]

########################################################################################################################

    def getVideoId(self,cursor,url):
        query = "select video_id from videos where video_link = '"+url+"'"
        cursor.execute(query)
        return cursor.fetchone()[0]

########################################################################################################################
