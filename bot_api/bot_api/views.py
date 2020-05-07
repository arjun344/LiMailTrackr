from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
from validate_email import validate_email
from tinydb import TinyDB, Query

class Helpers:
	def __init__(self,EMAIL_NOT_FOUND_ERROR=401,EMAIL_UNREGISTERED_ERROR=402,MAIL_NOT_UNIQUE_ERROR=403,OTHER_ERRORS=404):
		self.EMAIL_NOT_FOUND_ERROR = EMAIL_NOT_FOUND_ERROR
		self.EMAIL_UNREGISTERED_ERROR = EMAIL_UNREGISTERED_ERROR
		self.MAIL_NOT_UNIQUE_ERROR = MAIL_NOT_UNIQUE_ERROR
		self.OTHER_ERRORS = OTHER_ERRORS

	def verifyEmail(self,sender_email):
		try:
			self.is_valid = validate_email(str(sender_email).lower().strip())
			if self.is_valid:
				return True,None
			else:
				return False,self.EMAIL_NOT_FOUND_ERROR
		except:
			return False,self.OTHER_ERRORS


class EmailTrackr:
	def __init__(self,sender_email,unique_mail_id,comments):
		self.sender_email = sender_email
		self.unique_mail_id = unique_mail_id
		self.comments = comments

	def setTracker(self):
		helper = Helpers()
		self.is_valid,self.err_code = helper.verifyEmail(self.sender_email)
		if self.is_valid:
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
	mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments)
	is_valid,err_code = mailTrackr.setTracker()
	if is_valid:
		image_data = open("static/img/profile.jpg", "rb").read()
	else:
		print(err_code)
		image_data = open("static/img/"+str(err_code)+".PNG","rb").read()
	return HttpResponse(image_data, content_type="image/png")