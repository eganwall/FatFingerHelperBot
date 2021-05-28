#!/usr/bin/env python3

import praw
from praw.models import Message
import configparser
import FFHelperRepository
import FFHelperUtils
from statsd import StatsClient
import traceback
from prawcore.exceptions import Forbidden
import time

config = configparser.ConfigParser()
config.read("settings.config")

# create our Reddit instance
c_id = config.get("General", "client_id")
c_secret = config.get("General", "client_secret")
user = config.get("General", "plain_username")
pw = config.get("General", "password")

reddit = praw.Reddit(
    client_id = c_id,
    client_secret = c_secret,
    username = user,
    password = pw,
    user_agent = 'link helper test by /u/eganwall'
)

# initialize our MongoDB repository and constants
repo = FFHelperRepository.Repository()
constants = FFHelperRepository.StringConstants

# get our statsd client
statsd = StatsClient('localhost', 8125, prefix='MobileHelperMailMon')

# get our logger
logger = FFHelperUtils.LogUtility()

while True:
    try:
        for item in reddit.inbox.unread(limit=None):
            if isinstance(item, Message):
                body_lower = item.body.lower()
                subject_lower = item.subject.lower()
                item.mark_read()

                if body_lower.startswith('delete'):
                    logger.log_info_message("Received delete message : [BODY = {}] [AUTHOR = {}]".format(body_lower, item.author.name))
                    parts = body_lower.split(' ')
                    if len(parts) == 2:
                        comment_id = parts[1]
                        print(comment_id)
                        parent_comment = reddit.comment(id=comment_id).parent()
                        if item.author.name == 'eganwall' or (parent_comment and parent_comment.author and (parent_comment.author.name == item.author.name)):
                            comment = reddit.comment(id=comment_id)
                            comment.delete()
                            logger.log_info_message("Comment deleted : [ID = {}] [USER = {}]".format(comment_id, item.author.name))
                            statsd.gauge("commentsDeleted", 1, delta=True)
            else:
                item.mark_read()
            logger.log_info_message("Processed inbox item : [FULLNAME = {}]".format(item.fullname))

            # time.sleep(30)

    except Forbidden:
        logger.log_error_message("Error 403 Forbidden : we can't access this resource!")
        statsd.incr('exception_403.count')
        pass
    except KeyboardInterrupt:
        logger.log_error_message("KeyboardInterrupt detected - exiting...")
        statsd.incr('exception_keyboardInterrupt.count')
        break
    except Exception:
        logger.log_error_message(traceback.format_exc() + "=== END OF STACK TRACE")
        statsd.incr('exception_general.count')
        pass