#!/usr/bin/env python3

import praw
import configparser
from bs4 import BeautifulSoup
import FFHelperRepository
import FFHelperUtils
from statsd import StatsClient
import time
import traceback
from prawcore.exceptions import Forbidden


username_blacklist = ['FatFingerHelperBot', 'WikiTextBot', 'DuplicatesBot', 'AutoModerator', 'MTGCardFetcher',
                      'AskScienceModerator', 'Decronym', 'OriginalPostSearcher', 'Reply-Dota-2-Reddit', 'upmo',
                      'Lapis_Mirror', 'EternalCCGFetcher', 'AlwaysPuppies', 'TSATPWTCOTTTADC', 'notist', 'NGramatical',
                      'xanalives', 'coronata', 'MarioThePumer', 'whyhahm', 'MercuryPDX', 'interrogatrix', 'Chrisfade',
                      'phiiscool', 'Mentioned_Videos', 'BlatantConservative', 'AreYouDeaf', 'Gogrammer', 'howellq',
                      'gingerkid427', 'lambda_abstraction', 'Tigertemprr', 'mdaniel', 'anisuggest', 'Roboragi', 'ChaoticNeutralCzech']

subreddit_blacklist = ['custommagic', 'sakuragakuin', 'ggwpLive', 'france', 'technology', 'parkinsons', 'TheMarketsofSidon']

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
statsd = StatsClient('localhost', 8125, prefix='MobileHelper')

# get our logger
logger = FFHelperUtils.LogUtility()

# just for fun karma tracking
redditor = reddit.redditor('FatFingerHelperBot')

while True:
    try:
        for comment in reddit.subreddit('all').stream.comments():
            log_string = ""
            log_string += "Received comment : [AUTHOR = {}] [ID = {}]\n".format(comment.author.name, comment.id)

            # don't reply to our own comments
            if comment.author.name in username_blacklist or 'bot' in comment.author.name.lower() \
                    or 'fetcher' in comment.author.name.lower() or comment.subreddit in subreddit_blacklist:
                log_string += "Skipping comment : [AUTHOR = {}] [ID = {}] [SUBREDDIT = {}]\n".format(comment.author.name, comment.id, comment.subreddit)
                logger.log_info_message(log_string)
                continue

            # if we have already replied to a comment, move along
            if repo.GET_COMMENT_BY_ID(comment.id) is not None:
                continue

            repo.INSERT_COMMENT_ID(comment.id)
            statsd.gauge('totalCommentsReceived', 1, delta=True)
            statsd.incr('commentsReceived.count')

            # get timing for our latency
            start = time.time()

            # now we can process the comment - start by parsing the html out of the body and looking for links
            soup = BeautifulSoup(comment.body_html, 'html.parser')
            links = soup.find_all('a')
            if links is not None and len(links) > 0:
                curr_reply = """"""
                links_corrected = 0
                for idx, link in enumerate(links):
                    address = link.get('href')
                    body = str(link.string)
                    if len(body) <= 3 and body.lower() != 'www' and body.lower() != 'faq' and '(' not in address and ')' not in address and address.lower().startswith('http'):
                        links_corrected += 1
                        curr_reply += constants.LINK_TEMPLATE.format(str(links_corrected), address, body)

                if len(curr_reply) > 0:
                    full_reply = constants.REPLY_TEMPLATE.format(curr_reply)
                    reply_comment = comment.reply(full_reply)

                    if reply_comment is not None:
                        log_string +="Execution successful : [ID = {}] [REPLY_BODY = {}]".format(comment.id, full_reply)
                        reply_with_delete = full_reply.replace('ID_HERE', reply_comment.id)
                        reply_comment.edit(reply_with_delete)
                        log_string += "Comment reply posted : [ID = {}] [REPLY_BODY = {}]".format(reply_comment.id, reply_comment.body)
                    else:
                        log_string += "Execution unsuccessful : [ID = {}] [REPLY_BODY = {}]".format(comment.id, full_reply)

                    dt = int((time.time() - start) * 1000)
                    statsd.timing('latency', dt)
                    statsd.gauge('totalCommentsProcessed', 1, delta=True)
                    statsd.incr('commentsProcessed.count')
                    statsd.gauge('commentKarma', redditor.comment_karma)
                    statsd.gauge('subreddits.' + comment.subreddit.display_name, 1, delta=True)

                    if len(log_string) > 0:
                        logger.log_info_message(log_string)
    except Forbidden:
        logger.log_error_message("Error 403 Forbidden : we can't access this resource!")
        statsd.incr('exception_403.count')
        pass
    except KeyboardInterrupt:
        logger.log_error_message("KeyboardInterrupt detected - exiting...")
        statsd.incr('exception_keyboardInterrupt.count')
        break
    except:
        logger.log_error_message(traceback.format_exc() + "=== END OF STACK TRACE")
        statsd.incr('exception_general.count')
        pass
