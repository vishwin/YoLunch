#imports
from pymongo import MongoClient
import datetime

#connect db
client = MongoClient('172.26.12.59', 27017)
db = client.YoLunchMeDb

users = db.Users
sessions = db.Sessions


#does user exist
exists = True
if not(users.find_one({"_id": yo_username})):
	exists = False


#putting user into db
friends_to_yo = [] #this list should contain the yo_usernames
#here comes the fun FB part
user = {
	"facebook_user_ID": facebook_user_ID,
	"_id": yo_username,
	"name": name,
	"friends_to_yo": friends_to_yo
}
users.insert(user)


#updating the list of the friends_to_yo
friends_to_yo = [] #this list should contain the yo_usernames
#here comes the fun FB part
users.update({"_id": yo_username}, 
	{"$set": {"friends_to_yo": friends_to_yo}})


#Removing expired listening sessions
def cleanExpiredSessions():
	timedelta = datetime.timedelta(0, 1800)
	expiredDateTime = datetime.datetime.utcnow() - timedelta
	for expiredSession in sessions.find({"session_opened": {"$lt": expiredDateTime}}):
		sessions.remove(expiredSession)


#On receive an registered user first Yo command

cleanExpiredSessions()
#Inserting listening session
if not(sessions.find_one({"_id": yo_username})):
	listeningSession = {
		"_id": yo_username,
		"session_opened": datetime.datetime.utcnow()
	}
	sessions.insert(listeningSession);
else:
	sessions.update({"_id": yo_username}, {"$set": {"session_opened": datetime.datetime.utcnow()}})

#Sending yo to all the friends in the listetning session
friends_to_yo = users.find_one({"_id": yo_username}, {'_id': False, 'friends_to_yo': True})['friends_to_yo']
active_friends_to_yo = list(friends_to_yo)
for friendToYo in friends_to_yo:
	#location criterium as well
	if not(sessions.find_one({"_id": friendToYo})):
		active_friends_to_yo.remove(friendToYo)

for listeningFriendToYo in active_friends_to_yo:
	#link = 'http://www.YoLunch.Me/yo_username/wantsToYoLunch/listeningFriedToYo'
	#
	#that site should contain 
	#yo_username wants to have a lunch with you
	#button_link = 'http://www.YoLunch.Me/listeningFriedToYo/confirmsLunchWith/yo_username/lat/lon'
	#warning: we need js to extract geolocation data here
	#hopefully it will work: http://www.w3schools.com/html/html5_geolocation.asp


#On receive a confirmation of lunch, i.e. a call to link
#http://www.YoLunch.Me/user1/confirmsLunchWith/user2

#Removing complete listetning session
sessions.remove({"_id" : user1})
sessions.remove({"_id" : user2})

#Sending a finalizing Yo to both users

#Yo to user1
user2_facebook_ID = users.find_one({"_id": user2}, {'_id': False, 'facebook_user_ID': True})['facebook_user_ID']
#link = 'http://www.YoLunch.Me/user1/lunches/user2'
#
#that site should contain 
#You're having YoLunch with user2
#button_link = 'https://www.facebook.com/messages/user2_facebook_ID'

#Yo to user2
user1_facebook_ID = users.find_one({"_id": user1}, {'_id': False, 'facebook_user_ID': True})['facebook_user_ID']
#link = 'http://www.YoLunch.Me/user2/lunches/user1'
#
#that site should contain 
#You're having YoLunch with user2
#button_link = 'https://www.facebook.com/messages/user1_facebook_ID'
