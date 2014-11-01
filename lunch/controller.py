from lunch import app
from flask import request, render_template
import json
import requests
import pymongo

def send_yo(username, link):
	requests.post('http://api.justyo.co/yo/', data={'api_token': app.config['YO_API'], 'username': username, 'link': link})

@app.route('/')
def tsst():
	return 'Tsst!'

@app.route('/yo')
# Yo callback
def yo():
	username=request.args.get('username')
	send_yo(username, 'http://{0}/register'.format(app.config['LOCALHOST']))
	return 'OK'

@app.route('/register')
def register():
	if request.args.get('code'):
		auth=requests.get('https://graph.facebook.com/oauth/access_token?client_id={0}&redirect_uri=http://{1}/register&client_secret={2}&code={3}'.format(app.config['FB_APP'], app.config['LOCALHOST'], app.config['FB_APP_SECRET'], request.args.get('code')))
		return auth.text
	else:
		return render_template('register.html', app_id=app.config['FB_APP'], localhost=app.config['LOCALHOST'])

@app.route('/<user1>/wantsToLunch/<user2>/near/<latitude>/<longitude>')
def wantsToLunch():
	return user1 + ' wantsToLunch ' + user2 + ' near ' + latitude + ' ' + longitude

@app.route('/<user1>/confirmsLunchWith/<user2>')
def wantsToLunch2():
	return user1 + ' confirmsLunchWith ' + user2

@app.route('/<user1>/lunches/<user2>')
def wantsToLunch4(user1, user2):
	return user1 + ' lunches ' + user2

#Dummy comment
@app.route('/done')
def wantsToLunch5():
	return 'done'
