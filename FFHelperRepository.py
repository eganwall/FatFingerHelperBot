import configparser
import pymongo
import FFHelperUtils
import datetime

class Repository:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("settings.config")

        username = config.get("Mongo", "username")
        password = config.get("Mongo", "password")

        self.logger = FFHelperUtils.LogUtility()

        self.client = pymongo.MongoClient(
            "mongodb://{}:{}@solutiongambling-shard-00-00-vcw5b.mongodb.net:27017,"
            "solutiongambling-shard-00-01-vcw5b.mongodb.net:27017,"
            "solutiongambling-shard-00-02-vcw5b.mongodb.net:27017/admin?ssl=true&replicaSet=SolutionGambling-shard-0"
            "&authSource=admin".format(username, password))

        self.db = self.client.ffhelper_db

        self.commentdb = self.db.comments

        self.logger.log_info_message("MongoDB connection initialized.")

    def INSERT_COMMENT_ID(self, id):
        comment_id = self.commentdb.insert_one({'_id' : id, 'createdAt' : datetime.datetime.now()}).inserted_id
        # self.logger.log_info_message("INSERT_COMMENT_ID returned : [ID = {}]".format(str(comment_id)))
        return comment_id

    def GET_COMMENT_BY_ID(self, id):
        comment = self.commentdb.find_one({'_id' : id})
        #print("GET_COMMENT_BY_ID returned : [comment = {}]".format(str(comment)))
        return comment

class StringConstants:
    LINK_TEMPLATE = """[Here is link number {} - Previous text "{}"]({})

"""

    REPLY_TEMPLATE = """It seems that your comment contains 1 or more links that are hard to tap for mobile users. 
I will extend those so they're easier for our sausage fingers to click!


{}

----
^Please ^PM ^[\/u\/eganwall](http://reddit.com/user/eganwall) ^with ^issues ^or ^feedback! ^| ^[Code](https://github.com/eganwall/FatFingerHelperBot) ^| ^[Delete](https://reddit.com/message/compose/?to=FatFingerHelperBot&subject=delete&message=delete%20ID_HERE)
"""