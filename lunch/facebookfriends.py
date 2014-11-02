#!/usr/bin/python3.4
from lunch import app
import requests
import pymongo
mongoclient=pymongo.MongoClient()
db=mongoclient.YoLunchMeDb
users=db.Users
sessions=db.Sessions

def get_facebook_friends(url):
	yo_names=[]
	fb_friendsdata=requests.get(url).json()
	for user in fb_friendsdata['data']:
		if users.find_one({'facebook_user_ID': user['id']}):
			yo_names.append(users.find_one({'facebook_user_ID': user['id']})['_id'])
	if 'next' in fb_friendsdata['paging']:
		yo_names.extend(get_facebook_friends(fb_friendsdata['paging']['next']))
	return yo_names

def add_facebook_friends(username):
	userdata=users.find_one({'_id': username})
	users.update(userdata, {'$set': {'facebook_friends': get_facebook_friends('https://graph.facebook.com/v2.2/me/friends?access_token={0}'.format(userdata['facebook_token']))}})
