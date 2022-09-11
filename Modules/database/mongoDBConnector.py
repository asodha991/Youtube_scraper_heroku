import pymongo
import certifi
ca = certifi.where()

class mongoDBConnector:

    def getCollection(self):
        try:
            client = pymongo.MongoClient(
                "mongodb+srv://kuttral99:kuttralanathan@cluster0.f6s4s.mongodb.net/?retryWrites=true&w=majority&connect=false",
                tlsCAFile=ca)
            db = client['youtube_scrapper']
            collection = db['youtube_channels']
            return collection
        except Exception as e:
            print("Error in getting collection - MongoDB")
            print(e)

########################################################################################################################

    def insertChannel(self,channelData):
        try:
            collection = self.getCollection()
            key = {'channel_link': channelData['channel_link']}
            value = {'$set': channelData}
            response = collection.update_one(key, value, upsert=True)
            return response
        except Exception as e:
            print("Error in inserting channel - MongoDB")
            print(e)

########################################################################################################################

    def insertVideo(self,channel_link,videoLists):
        try:
            collection = self.getCollection()
            key = {'channel_link': channel_link}
            value = {'$set': {'videos' : videoLists}}
            response = collection.update_one(key, value)
            return response
        except Exception as e:
            print("Error in inserting video - MongoDB")
            print(e)

########################################################################################################################

    def updateVideo(self,video_link,videoData):
        try:
            collection = self.getCollection()
            path = 's3://kuttralanathan/youtube_scrapper/videos/<video_name>.mp4'
            key = {'videos.video_link': video_link}
            value = {'$set': {'videos.$.download_link' : path,'videos.$.likes' : videoData['likes'],'videos.$.comments':videoData['comments'],'videos.$.comment_details':videoData['comment_details']}}
            response = collection.update_one(key, value)
            return response
        except Exception as e:
            print("Error in updating video - MongoDB")
            print(e)