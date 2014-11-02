#!/usr/bin/python3.4
from lunch import app
import pymongo
from lunch.controller import mongoclient, db, Users, Sessions
import requests

def get_facebook_friends(url):
	yo_names=[]
	fb_friendsdata=requests.get(url).json()
	for user in fb_friendsdata['data']:
		yo_names.append(Users.find_one({'facebook_user_ID': user['id']})['_id'])
	if 'next' in fb_friendsdata['paging']:
		yo_names.extend(get_facebook_friends(fb_friendsdata['next']))
	return yo_names

def add_facebook_friends(username):
	userdata=Users.find_one({'_id': username})
