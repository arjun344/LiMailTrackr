from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
from validate_email import validate_email
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
			return True
		else:
			return False

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
			mail_last_dict[unique_mail_id] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.db.update({'mail_last_read':mail_last_dict},self.querier.email == str(sender_email))

			mail_comments = result[0]['mail_comment']
			mail_comments[unique_mail_id] = comments
			self.db.update({'mail_comment':mail_comments},self.querier.email == str(sender_email))

			return True

		except Exception as e:
			print(e)
			return False




class Helpers:
	def __init__(self,EMAIL_NOT_FOUND_ERROR=401,EMAIL_UNREGISTERED_ERROR=402,MAIL_NOT_UNIQUE_ERROR=403,OTHER_ERRORS=404):
		self.EMAIL_NOT_FOUND_ERROR = EMAIL_NOT_FOUND_ERROR
		self.EMAIL_UNREGISTERED_ERROR = EMAIL_UNREGISTERED_ERROR
		self.MAIL_NOT_UNIQUE_ERROR = MAIL_NOT_UNIQUE_ERROR
		self.OTHER_ERRORS = OTHER_ERRORS
		self.db = JsonDb()

	def verifyEmail(self,sender_email,unique_mail_id):
		try:
			self.is_valid = validate_email(sender_email)
			if self.is_valid:
				if self.db.checkMail(sender_email):
					if self.db.checkUniqueId(sender_email,unique_mail_id):
						return True,None
					else:
						## Because the receiver side might have opened the mail hence not feasible to show the error code
						return False,'receiver_request' 

					return True,None
				else:
					return False,self.EMAIL_UNREGISTERED_ERROR
			else:
				return False,self.EMAIL_NOT_FOUND_ERROR
		except Exception as e:
			print(e)
			return False,self.OTHER_ERRORS
	
	def insertEmail(self,sender_email,unique_mail_id,comments):
		if self.db.insertMail(sender_email,unique_mail_id,comments):
			return True,None
		else:
			return False,self.OTHER_ERRORS


class EmailTrackr:
	def __init__(self,sender_email,unique_mail_id,comments):
		self.sender_email = sender_email
		self.unique_mail_id = unique_mail_id
		self.comments = comments

	def setTracker(self):
		helper = Helpers()
		self.is_valid,self.err_code = helper.verifyEmail(self.sender_email,self.unique_mail_id)
		if self.err_code == 'receiver_request':
			return True,'receiver_request'
		if self.is_valid:
			self.insert,self.err_code = helper.insertEmail(self.sender_email,self.unique_mail_id,self.comments)
			if self.insert:
				return True,None
			else:
				return False,self.err_code
			return True,None
		else:
			return False,self.err_code



def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html')

def getImage(request):
	csrf_token = get_token(request)
	image_data = open("static/img/profile.jpg", "rb").read()
	return HttpResponse(image_data, content_type="image/png")

def setTrackr(request,sender_email,unique_mail_id,comments):
	csrf_token = get_token(request)
	sender_email = str(sender_email).lower().strip()
	unique_mail_id = str(unique_mail_id).strip().lower()
	comments = str(comments).strip().lower()
	mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments)
	is_valid,err_code = mailTrackr.setTracker()
	if is_valid:
		image_data = open("static/img/profile.jpg", "rb").read()
	else:
		print(err_code)
		image_data = open("static/img/"+str(err_code)+".PNG","rb").read()

	if err_code == 'receiver_request':
		image_data = open("static/img/profile.jpg", "rb").read()

	return HttpResponse(image_data, content_type="image/png")