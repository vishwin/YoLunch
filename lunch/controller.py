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
	return render_template('register.html', app_id=app.config['FB_APP'])
