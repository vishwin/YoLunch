from lunch import app
from flask import request, render_template
import json
import requests

def send_yo(username, link):
	requests.post('http://api.justyo.co/yo/', data={'api_token': app.config['YO_API'], 'username': username, 'link': link})

import pymongo
mongoclient=pymongo.MongoClient()
db=mongoclient.YoLunchMeDb
users=db.Users
sessions=db.Sessions

@app.route('/')
def tsst():
	return 'Tsst!'

@app.route('/yo')
# Yo callback
def yo():
	username=request.args.get('username')
	send_yo(username, 'http://{0}/register?username={1}'.format(app.config['LOCALHOST'], username))
	return 'OK'

@app.route('/register')
def register():
	if request.args.get('code') and request.args.get('state'):
		auth=requests.get('https://graph.facebook.com/oauth/access_token', params={'client_id': app.config['FB_APP'], 'client_secret': app.config['FB_APP_SECRET'], 'code': request.args.get('code'), 'redirect_uri': 'http://' + app.config['LOCALHOST'] + '/register'})
		fb_userdata=requests.get('https://graph.facebook.com/v2.2/me', params=auth.text)
		users.insert({
			'facebook_user_ID': fb_userdata.json()['id'],
			'_id': request.args.get('state'),
			'name': fb_userdata.json()['name']
		})
		return 'OK'
	else:
		return render_template('register.html', app_id=app.config['FB_APP'], localhost=app.config['LOCALHOST'], username=request.args.get('username'))

@app.route('/<user1>/wantsToLunch/<user2>/near/<latitude>/<longitude>')
def wantsToLunch(user1, user2, latitude, longitude):
	return user1 + ' wantsToLunch ' + user2 + ' near ' + latitude + ' ' + longitude

@app.route('/<user1>/confirmsLunchWith/<user2>')
def wantsToLunch2(user1, user2):
	return user1 + ' confirmsLunchWith ' + user2

@app.route('/<user1>/lunches/<user2>')
def wantsToLunch4(user1, user2):
	return user1 + ' lunches ' + user2

#Dummy comment
@app.route('/done')
def wantsToLunch5():
	return 'done'
