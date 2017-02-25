# -*- coding: utf-8 -*-
import requests
import json

followers_url = 'https://api.instagram.com/v1/users/%i/followed-by?count=50&access_token=%s'
followings_url = 'https://api.instagram.com/v1/users/%i/follows?count=50&access_token=%s'

def get_all_followers(user_id, token):
    followers = []
    next_url = followers_url % (int(user_id), token)
    while True:
        followers_data = requests.get(next_url)
        r = json.loads(followers_data.text)
        for u in r["data"]:
            followers.append({
                                    "username" : u["username"],
                                    #"profile_picture": u["profile_picture"],
                                    #"id": u["id"],
                                    "id" : u["id"]
                                    #"full_name": u["full_name"]
                                  })
        if 'next_url' in r['pagination']:
            # have more data
            next_url = r["pagination"]["next_url"]
        else:
            # end of data
            # print '[FUNC followers] uid: %s, count: %i' % (user_id, len(followers))
            return followers
    return False


def get_all_followings(user_id, token):
    followings = []
    next_url = followings_url % (int(user_id), token)
    while True:
        followings_data = requests.get(next_url)
        r = json.loads(followings_data.text)
        for u in r["data"]:
            followings.append({
                                    "username" : u["username"],
                                    #"profile_picture": u["profile_picture"],
                                    #"id": u["id"],
                                    "id" : u["id"]
                                    #"full_name": u["full_name"]
                                  })
        if 'next_url' in r['pagination']:
            # have more data
            next_url = r["pagination"]["next_url"]
        else:
            # end of data
            # print '[FUNC followings] uid: %s, count: %i' % (user_id, len(followings))
            return followings
    return False