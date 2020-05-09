from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
from validate_email import validate_email
from tinydb import TinyDB, Query
from tinydb.operations import *
import datetime
import requests
from django.http import JsonResponse

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

	def updateMailReadCount(self,sender_email,unique_mail_id):
		try:
			result = self.db.search(self.querier.email == str(sender_email))

			mail_id_dict = result[0]['mail_unique_id_count']
			mail_id_dict[unique_mail_id] = mail_id_dict[unique_mail_id] + 1
			self.db.update({'mail_unique_id_count':mail_id_dict},self.querier.email == str(sender_email))

			mail_last_dict = result[0]['mail_last_read']
			mail_last_dict[unique_mail_id] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			self.db.update({'mail_last_read':mail_last_dict},self.querier.email == str(sender_email))

			return True

		except Exception as e:
			print(e)
			return True


class Helpers:
	def __init__(self,EMAIL_NOT_FOUND_ERROR=401,EMAIL_UNREGISTERED_ERROR=402,MAIL_NOT_UNIQUE_ERROR=403,OTHER_ERRORS=404):
		self.EMAIL_NOT_FOUND_ERROR = EMAIL_NOT_FOUND_ERROR
		self.EMAIL_UNREGISTERED_ERROR = EMAIL_UNREGISTERED_ERROR
		self.MAIL_NOT_UNIQUE_ERROR = MAIL_NOT_UNIQUE_ERROR
		self.OTHER_ERRORS = OTHER_ERRORS
		self.db = JsonDb()

	def verifyEmail(self,sender_email,unique_mail_id,check):
		try:
			self.is_valid = validate_email(sender_email)
			if self.is_valid:
				if self.db.checkMail(sender_email):
					if self.db.checkUniqueId(sender_email,unique_mail_id):
						return True,None
					else:
						## Because the receiver side might have opened the mail hence not feasible to show the error code
						if check == "FromSender":
							return False,self.MAIL_NOT_UNIQUE_ERROR
						else:
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

	def updatemailreadCount(self,sender_email,unique_mail_id):
		if self.db.updateMailReadCount(sender_email,unique_mail_id):
			return True,None
		else:
			return True,None


class EmailTrackr:
	def __init__(self,sender_email,unique_mail_id,comments,check):
		self.sender_email = sender_email
		self.unique_mail_id = unique_mail_id
		self.comments = comments
		self.check = check

	def checkPar(self):
		self.helper = Helpers()
		self.is_valid,self.err_code = self.helper.verifyEmail(self.sender_email,self.unique_mail_id)


	def setTracker(self):
		self.helper = Helpers()
		self.is_valid,self.err_code = self.helper.verifyEmail(self.sender_email,self.unique_mail_id,self.check)
		if self.err_code == 'receiver_request':
			self.incr,self.err_code =self.helper.updatemailreadCount(self.sender_email,self.unique_mail_id)
			return True,'receiver_request'
		if self.is_valid:
			self.insert,self.err_code = self.helper.insertEmail(self.sender_email,self.unique_mail_id,self.comments)
			if self.insert:
				return True,None
			else:
				return False,self.err_code
			return True,None
		else:
			return False,self.err_code


class headerInfo:
	def __init__(self,request):
		self.header = request.headers

	def verifyGoogleCache(self):
		try:
			self.user_agent = self.header['User-Agent']
			if 'GoogleImageProxy' in self.user_agent:
				return True
		except Exception as e:
			print(e)
			return False
	
	def getIp(self):
		try:
			self.ip_addr = self.header['X-Forwarded-For']
			return ip_addr
		except Exception as e:
			print(e)
			try:
				self.ip_addr = self.header['X-Real-Ip']
				return ip_addr
			except Exception as e:
				print(e)
				return False

# class telegramMessage:
# 	def __init__(self,email_id,mail_id,ip_addr)

def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html')

def visitor_ip_address(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def getHeader(request):
	header_data = request.headers
	return header_data

def getImage(request):
	csrf_token = get_token(request)
	ip = visitor_ip_address(request)
	headers = getHeader(request)
	token = '1224852365:AAEoDrTaMmfDqG2Ch-9owJeT31nXfKbkID4'
	base = "https://api.telegram.org/bot{}/".format(token)
	ip = str(ip)+" Accessed Your Email"
	url = base + "sendMessage?chat_id={}&text={}&parse_mode=HTML".format('578382604',ip)
	requests.get(url,verify=False)
	ip = str(headers)
	url = base + "sendMessage?chat_id={}&text={}&parse_mode=HTML".format('578382604',ip)
	requests.get(url,verify=False)
	return render(request,'indexx.html')

def setTrackr(request,sender_email,unique_mail_id,comments):
	csrf_token = get_token(request)
	check = "FromReceiver"
	print("i am here")
	sender_email = str(sender_email).lower().strip()
	unique_mail_id = str(unique_mail_id).strip().lower()
	comments = str(comments).strip().lower()
	mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments,check)
	is_valid,err_code = mailTrackr.setTracker()

	if err_code == 'receiver_request':
		image_data = getImage(request)
		return HttpResponse(image_data, content_type="image/png")

	if is_valid:
		image_data = getImage(request)
		if check == "FromSender":
			return JsonResponse({'validated':'True','errorcode':str(err_code)})
		else:
			return HttpResponse(image_data, content_type="image/png")
	else:
		if check == "FromSender":
			return JsonResponse({'validated':'False','errorcode':str(err_code)})
		else:
			image_data = open("static/img/"+str(err_code)+".PNG","rb").read()

	# if err_code == 'receiver_request':
	# 	image_data = open("static/img/401.PNG", "rb").read()

	return HttpResponse(image_data, content_type="image/png")

def setTrackrr(request):
	csrf_token = get_token(request)
	if request.is_ajax():
		request_data = request.POST
		check = request_data['check']
		print("i am here 2")
		sender_email = request_data['emailid'].lower().strip()
		unique_mail_id = request_data['mailid'].strip().lower()
		comments = request_data['comments'].strip().lower()
		mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments,check)
		is_valid,err_code = mailTrackr.setTracker()
		if is_valid:
			image_data = getImage(request)
			if check == "FromSender":
				return JsonResponse({'validated':'True','errorcode':str(err_code)})
			else:
				return HttpResponse(image_data, content_type="image/png")
		else:
			if check == "FromSender":
				return JsonResponse({'validated':'False','errorcode':str(err_code)})
			else:
				image_data = open("static/img/"+str(err_code)+".PNG","rb").read()

		return HttpResponse(image_data, content_type="image/png")