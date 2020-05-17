from tinydb import TinyDB, Query
from tinydb.operations import *
import datetime

class JsonDb:
	def __init__(self):
		self.db = TinyDB('Database/db.json')
		self.querier = Query()
		# db.insert({'email': 'karjun344@gmail.com', 'telegram_id': '1234',
		# 	'mail_unique_id_count':{'mail123':1,'mail124':1},
		# 	'mail_last_read':{'mail123':'today','mail124':'yesterday'},
		#	'mail_comment': {'mail123': "testing", 'mail124': "testing2"}})
	def checkMail(self,email_id):
		result = self.db.search(self.querier.email == str(email_id))
		if len(result) == 1:
			return True,result
		else:
			return False,None

	def getReadCount(self,sender_email,unique_mail_id):
		result = self.db.search(self.querier.email == str(sender_email))
		count = result[0]['mail_unique_id_count'][unique_mail_id]
		return count

	def getConfigCount(self,sender_email,unique_mail_id):
		try:
			result = self.db.search(self.querier.email == str(sender_email))
			count = result[0]['config_count'][unique_mail_id]
			return count
		except Exception as e:
			return None

	def updateConfigCount(self,sender_email,unique_mail_id):
		result = self.db.search(self.querier.email == str(sender_email))
		config_count = result[0]['config_count']
		config_count[unique_mail_id] = config_count[unique_mail_id] + 1
		self.db.update({'config_count':config_count},self.querier.email == str(sender_email))

	def checkUniqueId(self,sender_email,unique_mail_id):
		result = self.db.search(self.querier.email == str(sender_email))
		if str(unique_mail_id) in result[0]['mail_unique_id_count'].keys():
			return False
		else:
			return True

	def insertMail(self,sender_email,unique_mail_id,comments):
		try:
			result = self.db.search(self.querier.email == str(sender_email))

			mail_id_dict = result[0]['mail_unique_id_count']

			mail_id_dict[unique_mail_id] = 0
			self.db.update({'mail_unique_id_count':mail_id_dict},self.querier.email == str(sender_email))

			mail_last_dict = result[0]['mail_last_read']
			mail_last_dict[unique_mail_id] = {0:'0-0-0 0:0:0'}
			self.db.update({'mail_last_read':mail_last_dict},self.querier.email == str(sender_email))

			mail_comments = result[0]['mail_comment']
			mail_comments[unique_mail_id] = comments
			self.db.update({'mail_comment':mail_comments},self.querier.email == str(sender_email))

			config_count = result[0]['config_count']
			config_count[unique_mail_id] = 0
			self.db.update({'config_count':config_count},self.querier.email == str(sender_email))

			return True

		except Exception as e:

			print(e)

			return False

	def updateMailReadCount(self,sender_email,unique_mail_id):
		try:
			result = self.db.search(self.querier.email == str(sender_email))

			mail_id_dict = result[0]['mail_unique_id_count']
			mail_id_dict[unique_mail_id] = mail_id_dict[unique_mail_id] + 1
			self.db.update({'mail_unique_id_count':mail_id_dict},self.querier.email == str(sender_email))

			mail_last_dict = result[0]['mail_last_read']
			mail_last_dict[unique_mail_id][len(mail_last_dict[unique_mail_id])] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.db.update({'mail_last_read':mail_last_dict},self.querier.email == str(sender_email))

			return True

		except Exception as e:
			print(e)
			return False

	def getLastRead(self,sender_email,unique_mail_id):
		try:
			result = self.db.search(self.querier.email == str(sender_email))
			mail_last_read = result[0]['mail_last_read'][unique_mail_id]
			return mail_last_read[len(mail_last_read)-1]
		except Exception as e:
			print(e)

	def getUniqueId(self,sender_email):
		result = self.db.search(self.querier.email == str(sender_email))
		user_id = result[0]['encrypted']
		return str(user_id)

	def getChatId(self,sender_email):
		result = self.db.search(self.querier.email == str(sender_email))
		chat_id = result[0]['chat_id']
		return str(chat_id)

	def getUserFromId(self,sender_email):
		try:
			result = self.db.search(self.querier.encrypted == str(sender_email))
			email = result[0]['email']
			return str(email)
		except Exception as e:
			return None
