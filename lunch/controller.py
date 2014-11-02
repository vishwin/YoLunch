from lunch import app
from flask import request, render_template
import requests
import urllib.parse, datetime
from lunch.facebookfriends import *

import pymongo
mongoclient=pymongo.MongoClient()
db=mongoclient.YoLunchMeDb
users=db.Users
sessions=db.Sessions

from lunch.facebookfriends import *

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km 

def send_yo(username, link):
	requests.post('http://api.justyo.co/yo/', data={'api_token': app.config['YO_API'], 'username': username, 'link': link})

#Removing expired listening sessions
def cleanExpiredSessions():
	timedelta = datetime.timedelta(0, 1800)
	expiredDateTime = datetime.datetime.utcnow() - timedelta
	for expiredSession in sessions.find({"session_opened": {"$lt": expiredDateTime}}):
		sessions.remove(expiredSession)

#All the routes
@app.route('/')
def hauptseite():
	return render_template('MainPage.html')

@app.route('/yo')
# Yo callback
def yo():
	username=request.args.get('username')

	if not(users.find_one({"_id": username})):
		send_yo(username, 'http://{0}/register?username={1}'.format(app.config['LOCALHOST'], username))
	else:
		location=request.args.get('location').split(';')
		latitude=float(location[0])
		longitude=float(location[1])

		#Clean expired sessions
		cleanExpiredSessions()

		#Inserting listening session
		if not(sessions.find_one({"_id": username})):
			listeningSession = {
				"_id": username,
				"session_opened": datetime.datetime.utcnow(),
				"latitude": latitude,
				"longitude": longitude
			}
			sessions.insert(listeningSession);
		else:
			sessions.update({"_id": username}, 
				{"$set": {
					"session_opened": datetime.datetime.utcnow(),
					"latitude": latitude,
					"longitude": longitude
				}}
			)

		#Sending yo to all the friends in the listening session
		friends_to_yo = users.find_one({"_id": username}, {'_id': False, 'facebook_friends': True})['facebook_friends']
		print(friends_to_yo)
		active_friends_to_yo=[]
		for friendToYo in friends_to_yo:
			print(friendToYo)
			friendToYoData = sessions.find_one({"_id": friendToYo}, {'_id': False, 'longitude': True, 'latitude': True})
			print(friendToYoData)
			if not(not(friendToYoData)):
				distanceInKm=haversine(longitude, latitude, friendToYoData['longitude'], friendToYoData['latitude'])
				print(distanceInKm)
				if distanceInKm<1.7:
					active_friends_to_yo.append(friendToYo)

		for listeningFriendToYo in active_friends_to_yo:
			send_yo(listeningFriendToYo, 'http://{0}/{1}/wantsToLunch/{2}'.format(app.config['LOCALHOST'], username, listeningFriendToYo))
			#link = 'http://www.YoLunch.Me/yo_username/wantsToYoLunch/listeningFriedToYo'
			#
			#that site should contain 
			#yo_username wants to have a lunch with you
			#button_link = 'http://www.YoLunch.Me/listeningFriedToYo/confirmsLunchWith/yo_username'
	return 'OK'

@app.route('/register')
def register():
	if request.args.get('code') and request.args.get('state'):
		auth=requests.get('https://graph.facebook.com/oauth/access_token', params={'client_id': app.config['FB_APP'], 'client_secret': app.config['FB_APP_SECRET'], 'code': request.args.get('code'), 'redirect_uri': 'http://' + app.config['LOCALHOST'] + '/register'})
		fb_userdata=requests.get('https://graph.facebook.com/v2.2/me', params=auth.text)

		users.insert({
			'_id': request.args.get('state'), # Yo app username
			'facebook_user_ID': fb_userdata.json()['id'],
			'name': fb_userdata.json()['name'],
			'facebook_token': urllib.parse.parse_qs(auth.text)['access_token'][0],
			'facebook_expire': datetime.datetime.utcnow() + datetime.timedelta(seconds=int(urllib.parse.parse_qs(auth.text)['expires'][0])),
			'facebook_friends': None
		})
		add_facebook_friends(request.args.get('state'))
		
		# Update other friends' lists
		for friend in users.find_one({'_id': request.args.get('state')}, {'_id': False, 'facebook_friends': True})['facebook_friends']:
			friend_list=users.find_one({'_id': friend}, {'_id': False, 'facebook_friends': True})['facebook_friends']
			friend_list.append(request.args.get('state'))
			users.update({'_id': friend}, {'$set': {'facebook_friends': friend_list}})
		return 'OK'
	else:
		return render_template('register.html', app_id=app.config['FB_APP'], localhost=app.config['LOCALHOST'], username=request.args.get('username'))

#link = 'http://www.YoLunch.Me/yo_username/wantsToYoLunch/listeningFriedToYo'
#
#that site should contain 
#yo_username wants to have a lunch with you
#button_link = 'http://www.YoLunch.Me/listeningFriendToYo/confirmsLunchWith/yo_username'
@app.route('/<user1>/wantsToLunch/<user2>')
def wantsToLunch(user1, user2):
	if not(sessions.find_one({"_id": user1})) or not(sessions.find_one({"_id": user2})):
		#return 'Too late, that lunch is already taken!'
		return render_template('TooLate.html')
	else:
		user1_data = users.find_one({"_id": user1}, {'_id': False, 'facebook_user_ID': True, 'name': True})
		#return user1 + ' wantsToLunch ' + user2 + ': <a href="' 
		#+ 'http://{0}/{1}/confirmsLunchWith/{2}'.format(app.config['LOCALHOST'], user2, user1) 
		#+ '">link</a>'
		return render_template('NewLunchRequest.html', localhost=app.config['LOCALHOST'], user_name=user1_data['name'], user2=user2, user1=user1)

@app.route('/<user2>/confirmsLunchWith/<user1>')
def confirmsLunchWith(user1, user2):
	if not(sessions.find_one({"_id": user1})) or not(sessions.find_one({"_id": user2})):
		return render_template('TooLate.html')
	else:
		#Removing complete listetning session
		sessions.remove({"_id" : user1})
		sessions.remove({"_id" : user2})

		#Sending a finalizing Yo to both users

		#Yo to user1

		send_yo(user1, 'http://{0}/youLunch/{1}'.format(app.config['LOCALHOST'], user2))
		#link = 'http://www.YoLunch.Me/youLunch/user2'
		#
		#that site should contain 
		#You're having YoLunch with user2
		#button_link = 'https://www.facebook.com/messages/user2_facebook_ID'

		#Yo to user2
		#send_yo(user2, 'http://{0}/youLunch/{1}'.format(app.config['LOCALHOST'], user1))
		#link = 'http://www.YoLunch.Me/youLunch/user1'
		#
		#that site should contain 
		#You're having YoLunch with user2
		#button_link = 'https://www.facebook.com/messages/user1_facebook_ID'
		#return user1 + ' confirmsLunchWith ' + user2 + ': <a href="' 
		#+ 'http://{0}/{1}/confirmsLunchWith/{2}'.format(app.config['LOCALHOST'], user2, user1) 
		#+ '">link</a>'
		user1_data = users.find_one({"_id": user1}, {'_id': False, 'facebook_user_ID': True, 'name': True})
		#return 'Awesome! You are going to have a lunch with ' + user1_data['name'] 
		#+ '! <a href="https://www.facebook.com/messages/{0}'.format(user1_data['facebook_user_ID']) 
		#+ '">Message him on facebook!</a>'
		return render_template('ReceivedRequest.html', localhost=app.config['LOCALHOST'], user_name=user1_data['name'], user_facebook_ID = user1_data['facebook_user_ID'])

#link = 'http://www.YoLunch.Me/youLunch/user'
#
#that site should contain 
#You're having YoLunch with user
#button_link = 'https://www.facebook.com/messages/user_facebook_ID'
@app.route('/youLunch/<user>')
def youLunch(user):
	user_data = users.find_one({"_id": user}, {'_id': False, 'facebook_user_ID': True, 'name': True})
	#return 'Awesome! You are going to have a lunch with ' + user_data['name'] 
	#+ '! <a href="https://www.facebook.com/messages/{0}'.format(user_data['facebook_user_ID']) 
	#+ '">Message him on facebook!</a>'
	return render_template('ReceivedRequest.html', localhost=app.config['LOCALHOST'], user_name=user_data['name'], user_facebook_ID = user_data['facebook_user_ID'])

@app.route('/done')
def done():
	return 'done'
