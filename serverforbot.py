import requests
import json
from tinydb import TinyDB, Query
from tinydb.operations import *

class telegram_chatbot():
	def __init__(self):
		self.token = '1224852365:AAEoDrTaMmfDqG2Ch-9owJeT31nXfKbkID4'
		self.base = "https://api.telegram.org/bot{}/".format(self.token)

	def get_updates(self,offset=None):
		url = self.base + "getUpdates"
		if offset:
			url = url+"?offset={}".format(offset+1)
		r = requests.get(url,verify=False)
		return json.loads(r.content)

	def send_message(self,msg,chat_id):
		url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(chat_id,msg)
		if msg is not None:
			requests.get(url,verify=False)

class JsonDb:
	def __init__(self):
		self.db = TinyDB('bot_api/Database/db.json')
		self.db2 = TinyDB('bot_api/Database/chat_id_mapping.json')
		self.querier = Query()
		self.querier2 = Query()
		# db.insert({'email': 'karjun344@gmail.com', 'telegram_id': '1234',
		# 	'mail_unique_id_count':{'mail123':1,'mail124':1},
		# 	'mail_last_read':{'mail123':'today','mail124':'yesterday'},
		#	'mail_comment': {'mail123': "testing", 'mail124': "testing2"}})

	def checkUserExists(self,chat_id):
		result = self.db2.search(self.querier2.chat_id == str(chat_id))
		if len(result) == 0:
			return False,None
		else:
			return True,result[0]['user_name']

	def setUserName(self,username,chat_id):
		chk,old_username = self.checkUserExists(chat_id)
		if chk:
			return False,old_username
		else:
			try:
				self.db2.insert({"user_name": username,"chat_id":str(chat_id),"encrypted":str(hash(username))})
				return True,username
			except Exception as e:
				print(e)
				return False,"error"

bot = telegram_chatbot()


def make_reply(msg,sender):
	reply = None
	db =  JsonDb()
	user_exist,user_name = db.checkUserExists(sender)
	if msg is not None:
		sent_user_name = msg.split(":")
		if len(sent_user_name) >=2:
			username = ''.join(sent_user_name[1:])
			result,name = db.setUserName(str(username),sender)
			if result:
				reply = "`Hey your username has been set to `*"+name+"*"
			else:
				if name != "error":
					reply = "`Hey seems you already have a name `*"+name+"*"
				else:
					reply = "`Hey seems there was a problem try again ! `"

		if msg == '/start':
			if user_exist:
				reply = "`Welcome Back !` *"+user_name+"*"
			else:
				reply = '''`Let's get you started ! 
Click below command to setup your account`

	*/setmeup*
				'''
		elif msg == '/setmeup':
			if user_exist:
				reply = "`Seems you are all set` *"+user_name+"*"
			else:
				reply = '''`Send me a cool` *USERNAME* `!` in below format

`user:your_username`
				'''

		else:
			reply = "`Sorry i am a baby bot,not as smart as you !`"

	return reply

update_id = None
while True:
	updates = bot.get_updates(offset=update_id)
	updates = updates["result"]
	if updates:
		for item in updates:
			update_id = item["update_id"]
			try:
				message = str(item["message"]["text"])
			except:
				message = None
			from_ = item["message"]["from"]["id"]
			reply = make_reply(message,from_)
			bot.send_message(reply, from_)