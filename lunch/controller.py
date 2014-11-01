from lunch import app
from flask import redirect, request
import json
import requests

def send_yo(username, link):
	requests.post('http://api.justyo.co/yo/', data={'api_token': app.config['YO_API'], 'username': username, 'link': link})

@app.route('/')
def tsst():
	return 'Tsst!'

@app.route('/yo')
# Yo callback
def yo():
	username=request.args.get('username')
	send_yo(username, 'https://www.facebook.com/dialog/oauth?client_id={0}&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=user_friends'.format(app.config['FB_APP']))
	return 'OK'
