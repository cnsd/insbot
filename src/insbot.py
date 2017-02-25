# -*- coding: utf-8 -*-

import requests
import random
import time
import datetime
import json
import sys
import os

from follow_related_calls import get_all_followers, get_all_followings

class InsBot:
    url = 'https://www.instagram.com/'
    url_tag = 'https://www.instagram.com/explore/tags/'
    url_likes = 'https://www.instagram.com/web/likes/%s/like/'
    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'
    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'
    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
    url_user_detail = 'https://www.instagram.com/%s/?__a=1'

    user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
    accept_language = 'en-US,en;q=0.8,en-US;q=0.6,en;q=0.4'

    like_counter = 0
    follow_counter = 0
    unfollow_counter = 0
    bot_follow_list = []
    unwanted_username_list = []

    # Log setting.
    logs_dir = "logs"

    # Other.
    user_id = 0
    media_by_tag = 0
    login_status = False


    # User follows data
    start_followers_list = []
    start_following_list = []

    # Tracking
    start_follower_count = 0
    liked_media_list = []


    # Timing
    next_iteration = {"Like": 0, "Follow": 0, "Unfollow": 0, "Comments": 0}

    def __init__(self, login, password,
                 like_per_day=1000,
                 media_max_like=50,
                 media_min_like=0,
                 follow_per_day=0,
                 follow_time=5 * 60 * 60,
                 unfollow_per_day=0,
                 comments_per_day=0,
                 tag_list=['cat', 'dog'],
                 max_like_for_one_tag=5,
                 unfollow_break_min=15,
                 unfollow_break_max=30,
                 log_to_file=False,
                 clear_after_iter=False,
                 token='',
                 proxy='',
                 unwanted_username_list=[]):

        # Bot start
        self.time_in_day = 24 * 60 * 60
        self.bot_start = datetime.datetime.now()


      ### ======|Preferences|======
       ## --- Timing preferences
        #       - Unfollows:
        self.unfollow_break_min = unfollow_break_min
        self.unfollow_break_max = unfollow_break_max
        self.unfollow_per_day = unfollow_per_day
        if self.unfollow_per_day != 0:
            self.unfollow_delay = self.time_in_day / self.unfollow_per_day

        #       - Follows
        self.follow_time = follow_time
        self.follow_per_day = follow_per_day
        if self.follow_per_day != 0:
            self.follow_delay = self.time_in_day / self.follow_per_day

        #       - Likes
        self.like_per_day = like_per_day
        if self.like_per_day != 0:
            self.like_delay = self.time_in_day / self.like_per_day
        
       ## --- Likes preferences
        #       - Min likes a media should have:
        self.media_min_like = media_min_like

        #       - Max likes a media should have:
        self.media_max_like = media_max_like

        #       - Tag list:
        self.tag_list = tag_list
        
        #       - Max likes for a tag:
        self.max_like_for_one_tag = max_like_for_one_tag

       ## --- Logging
        #       - Should log to file? True/False.
        self.log_to_file = log_to_file

       ## --- Bot Main Settings
        #       - Access token, get it from Instagram API or Ink361:
        self.token = token

        #       - Clear cmd window after iteration (True/False):
        self.clear_after_iter = clear_after_iter

        #       - Instagram Username:
        self.user_login = login.lower()

        #       - Instagram Password:
        self.user_password = password

        #       - If a user contains anything in this list, the bot wont follow him.
        self.unwanted_username_list = unwanted_username_list

       ## --- Bot fetched data:
        #       - List of medias in the randomly selected tag, Changes on every iteration.
        self.media_by_tag = []

       ## --- Starting up
        #       - Start print:
        now_time = datetime.datetime.now()
        log_string = 'Instabot started at: %s' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.write_log(log_string)

        #       - Printing Bot settings:
        self.write_log('Tag list: %s' % str(tag_list))
        self.write_log('Max Likes: %i' % like_per_day)
        self.write_log('Max Follows: %i' % follow_per_day)
        self.write_log('Max Unfollows: %i' % unfollow_per_day)

       ## --- Connectivity
        #       - Instagram session:
        self.s = requests.Session()
        
        #       - Proxy settings (Optional):
        if proxy!="":
            proxies = {
              'http': 'http://'+proxy,
              'https': 'http://'+proxy,
            }
            self.s.proxies.update(proxies)

        #       - Login to the account:
        self.login()

       ## --- Counters/Tracking
        #       - Followers count at the beggining of the run
        self.start_follower_count = self.get_user_follower_count(self.user_login)

        #       - Lists of people who follow you and people you follow
        self.start_followers_list = get_all_followers(self.user_id, self.token) # People follows you
        self.start_following_list = get_all_followings(self.user_id, self.token) # People you follow








# ''' ========== USER RELATED FUNCTIONS ========== '''

    def get_user_follower_count(self, user):
        user_id_url = self.url_user_detail % (user)
        info = self.s.get(user_id_url)
        all_data = json.loads(info.text)
        follower_count = all_data['user']['followed_by']['count']
        return follower_count
    
    def get_user_following_count(self, user):
        user_id_url = self.url_user_detail % (user)
        info = self.s.get(user_id_url)
        all_data = json.loads(info.text)
        following_count = all_data['user']['follows']['count']
        return following_count

    def get_user_id_by_login(self, user_name):
        url_info = self.url_user_detail % (user_name)
        info = self.s.get(url_info)
        all_data = json.loads(info.text)
        id_user = all_data['user']['id']
        return id_user

    def login(self):
        log_string = 'Trying to login as %s...' % (self.user_login)
        self.write_log(log_string)
        self.s.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                               'ig_vw': '1920', 'csrftoken': '',
                               's_network': '', 'ds_user_id': ''})
        self.login_post = {'username': self.user_login,
                           'password': self.user_password}
        self.s.headers.update({'Accept-Encoding': 'gzip, deflate',
                               'Accept-Language': self.accept_language,
                               'Connection': 'keep-alive',
                               'Content-Length': '0',
                               'Host': 'www.instagram.com',
                               'Origin': 'https://www.instagram.com',
                               'Referer': 'https://www.instagram.com/',
                               'User-Agent': self.user_agent,
                               'X-Instagram-AJAX': '1',
                               'X-Requested-With': 'XMLHttpRequest'})
        r = self.s.get(self.url)
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5 * random.random())
        login = self.s.post(self.url_login, data=self.login_post,
                            allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.s.get('https://www.instagram.com/')
            finder = r.text.find(self.user_login)
            if finder != -1:
                self.user_id = self.get_user_id_by_login(self.user_login)
                self.login_status = True
                log_string = 'Logged in as %s successfully!' % (self.user_login)
                self.write_log(log_string)
            else:
                self.login_status = False
                self.write_log('Login error! Could not login using ID:%s;Password:%s;' % (self.user_login, self.user_password))
        else:
            self.write_log('Login error! Connection error!')

    def logout(self):
        now_time = datetime.datetime.now()
        log_string = 'Logout: likes - %i, follow - %i, unfollow - %i' % \
                     (self.like_counter, self.follow_counter,
                      self.unfollow_counter)
        self.write_log(log_string)
        work_time = datetime.datetime.now() - self.bot_start
        log_string = 'Bot work time: %s' % (work_time)
        self.write_log(log_string)

        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            logout = self.s.post(self.url_logout, data=logout_post)
            self.write_log("Logout success!")
            self.login_status = False
        except:
            self.write_log("Logout error!")








# ''' ========== LIKE RELATED FUNCTIONS ========== '''

    def get_media_id_by_tag(self, tag):
        """ Get media ID set, by your hashtag """

        if (self.login_status):
            log_string = "Get media id by tag: %s" % (tag)
            self.write_log(log_string)
            if self.login_status == 1:
                url_tag = '%s%s%s' % (self.url_tag, tag, '/')
                try:
                    r = self.s.get(url_tag)
                    text = r.text

                    finder_text_start = ('<script type="text/javascript">'
                                         'window._sharedData = ')
                    finder_text_start_len = len(finder_text_start) - 1
                    finder_text_end = ';</script>'

                    all_data_start = text.find(finder_text_start)
                    all_data_end = text.find(finder_text_end, all_data_start + 1)
                    json_str = text[(all_data_start + finder_text_start_len + 1) \
                        : all_data_end]
                    all_data = json.loads(json_str)

                    self.media_by_tag = list(all_data['entry_data']['TagPage'][0] \
                                                 ['tag']['media']['nodes'])
                except:
                    self.media_by_tag = []
                    self.write_log("Except on get_media_id_by_tag.")
            else:
                return 0

    def like(self, media_id):
        """ Send http request to like media by ID """
        if (self.login_status):
            url_likes = self.url_likes % (media_id)
            try:
                like = self.s.post(url_likes)
                if like.status_code == 200:
                    last_liked_media_id = media_id
                    self.like_counter += 1
                    log_string = "Liked %s (No.%i)" % (media_id, self.like_counter)
                    self.write_log(log_string)
                else:
                    log_string = "Status code != 200, Sleeping 5 mins to avoid ban."
                    self.write_log(log_string)
                    time.sleep(300)
            except:
                self.write_log("Except on like function.")
                like = 0
            return like
        return False

    def like_random_media_from_tag(self):
        '''     ==like_random_media_from_tag(self)==
                
                Like random media by media_by_tag list 
                and the like function above.
                this function chooses a random post in
                the randomly selected tag and likes it
                .

        '''
        if self.media_by_tag != 0:
            random_media = random.choice(self.media_by_tag)
            if random_media['id'] not in self.liked_media_list:
                random_media_likes = random_media['likes']['count']
                if ((random_media_likes >= self.media_min_like) and (random_media_likes <= self.media_max_like)):
                    if (random_media['owner']['id'] == self.user_id):
                        log_string = 'This media is yours.'
                        self.write_log(log_string)
                        return False

                    try:
                        caption = random_media['caption'].encode('ascii',errors='ignore')
                        if sys.version_info[0] == 3: # Check if you're using Python3.x or Python2.x because of unicode.
                            tags = {str.lower((tag.decode('ASCII')).strip('#')) for tag in caption.split() if
                                    (tag.decode('ASCII')).startswith("#")}
                        else:
                            tags = {unicode.lower((tag.decode('ASCII')).strip('#')) for tag in caption.split() if
                                    (tag.decode('ASCII')).startswith("#")}
                    except:
                        self.write_log("No caption - No like (Avoiding giving likes to spam photos)")
                        return False

                    log_string = "Trying to like media: %s" % random_media['id']
                    self.write_log(log_string)
                    like = self.like(random_media['id'])
                    self.liked_media_list.append(random_media['id'])
                    return True
        else:
            log_string = 'No media found on this tag.'
            self.write_log(log_string)
        return False








# ''' ========== FOLLOW RELATED FUNCTIONS ========== '''

    def follow(self, user_id):
        """ Send http request to follow """
        if (self.login_status):
            url_follow = self.url_follow % (user_id)
            try:
                follow = self.s.post(url_follow)
                if follow.status_code == 200:
                    self.follow_counter += 1
                    log_string = "Followed: %s #%i." % (user_id, self.follow_counter)
                    self.write_log(log_string)
                return follow
            except:
                self.write_log("Except on follow function.")
        return False

    def unfollow(self, user_id):
        """ Send http request to unfollow """
        if (self.login_status):
            url_unfollow = self.url_unfollow % (user_id)
            try:
                unfollow = self.s.post(url_unfollow)
                if unfollow.status_code == 200:
                    self.unfollow_counter += 1
                    log_string = "Unfollow: %s #%i." % (user_id, self.unfollow_counter)
                    self.write_log(log_string)
                else:
                    log_string = "Status code != 200, Sleeping 5 mins to avoid ban."
                    self.write_log(log_string)
                    time.sleep(300)
                return unfollow
            except:
                self.write_log("Except on unfollow function.")
        return False


    def unfollow_non_followers(self):
        if time.time() > self.next_iteration["Unfollow"] and self.unfollow_per_day != 0 and (len(self.start_following_list) > len(self.start_followers_list)):
            user_pointer = random.choice(self.start_following_list)
            uid = user_pointer['id']
            uname = user_pointer['username']
            if user_pointer in self.start_followers_list:
                self.write_log('%s(%s) is following you. Aborting unfollow.' % (uname, uid))
            else:
                self.write_log('Trying to unfollow %s(%s).' % (uname, uid))
                self.unfollow(int(uid))
                self.start_following_list.remove(user_pointer)
                self.next_iteration["Unfollow"] = time.time() + self.add_time(self.unfollow_delay)








# ''' ========== MAIN BOT FUNCTIONS ========== '''

    def run_bot_run(self, shuffle=False):
        while True:
            if len(self.media_by_tag) == 0:
                self.get_media_id_by_tag(random.choice(self.tag_list))
                self.this_tag_like_count = 0
                self.max_tag_like_count = random.randint(1, self.max_like_for_one_tag)

            if shuffle:
                if (random.randint(0, 100) > 30 and random.randint(0, 100) < 60):
                    self.main_follow_func()
                    self.main_like_func()
                    self.unfollow_non_followers()
                elif (random.randint(0, 100) > 60 and random.randint(0, 100) < 100):
                    self.unfollow_non_followers()
                    self.main_like_func()
                else:
                    self.unfollow_non_followers()
                    self.main_follow_func()
                    self.main_like_func()
            else:
                self.main_like_func()
                self.main_follow_func()
                self.unfollow_non_followers()

            cur_follower_count = self.get_user_follower_count(self.user_login)
            cur_following_count = self.get_user_following_count(self.user_login)

            print('========================\n\
Current time: %s\n\
You have %s Followers.\n\
You follow %s instagram users.\n\
During this run you have gained %s followers.\n\
\n\
\n\
Bot Counters and Pointers:\n\
- Likes made: %s/%s\n\
- People followed: %s/%s\n\
- People unfollowed: %s/%s\n\
\n\
The bot has been running for %s\n\
========================' % (datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                                cur_follower_count,
                                cur_following_count,
                                str(int(cur_follower_count) - int(self.start_follower_count)),
                                self.like_counter,
                                self.like_per_day,
                                self.follow_counter,
                                self.follow_per_day,
                                self.unfollow_counter,
                                self.unfollow_per_day,
                                str(datetime.datetime.now() - self.bot_start)
                            )
)
            random_sleep_time = random.randint(15, 30)
            time.sleep(random_sleep_time)
            if (random.randint(0, 100) > random.randint(0, 100)):
                time.sleep(random.randint(1, 5))
            if self.clear_after_iter:
                os.system('cls')

    def main_like_func(self):
        if time.time() > self.next_iteration["Like"] and self.like_per_day != 0 \
                and len(self.media_by_tag) > 0:
            if self.like_random_media_from_tag():
                self.next_iteration["Like"] = time.time() + \
                                              self.add_time(self.like_delay)
                self.this_tag_like_count += 1
                if self.this_tag_like_count >= self.max_tag_like_count:
                    self.media_by_tag = [0]

    def main_follow_func(self):
        if time.time() > self.next_iteration["Follow"] and \
                        self.follow_per_day != 0 and len(self.media_by_tag) > 0:
            if self.media_by_tag[0]["owner"]["id"] == self.user_id:
                self.write_log("Can't follow myself")
                return
            log_string = "Trying to follow: %s" % (self.media_by_tag[0]["owner"]["id"])
            self.write_log(log_string)

            if self.follow(self.media_by_tag[0]["owner"]["id"]) != False:
                self.bot_follow_list.append([self.media_by_tag[0]["owner"]["id"],
                                             time.time()])
                self.next_iteration["Follow"] = time.time() + \
                                                self.add_time(self.follow_delay)

    def add_time(self, time):
        """ Make some random for next iteration"""
        return time * 0.9 + time * 0.2 * random.random()








# ''' ========== LOGGING ========== '''

    def write_log(self, log_text):
        """ Write log by print() and maybe to file as well """

        if self.log_to_file:
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)

            now_time = datetime.datetime.now()
            self.log_full_path = '%s/%s_%s.log' % (self.logs_dir,
                                                  self.user_login,
                                                  now_time.strftime("%d%m%Y"))
            log_format = '%s\t\t%s\t\t%s\n'
            try:
                with open(os.path.normpath(self.log_full_path), 'a') as logfile:
                    logfile.write(log_format % (now_time, self.user_login, log_text))
                print(log_text)
            except UnicodeEncodeError:
                print("Your text has a unicode error.")
        else:
            try:
                print(log_text)
            except UnicodeEncodeError:
                print("Your text has a unicode error.")
