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
import time
from django.shortcuts import redirect


timestamp = None

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

	def getReadCount(self,sender_email,unique_mail_id):
		result = self.db.search(self.querier.email == str(sender_email))
		count = result[0]['mail_unique_id_count'][unique_mail_id]
		return count

	def getConfigCount(self,sender_email,unique_mail_id):
		result = self.db.search(self.querier.email == str(sender_email))
		count = result[0]['config_count'][unique_mail_id]
		return count

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
			mail_last_dict[unique_mail_id] = {}
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
			return True

	def getFirstRead(self,sender_email,unique_mail_id):
		try:
			result = self.db.search(self.querier.email == str(sender_email))
			mail_last_read = result[0]['mail_last_read'][unique_mail_id]
			return mail_last_read
		except Exception as e:
			print(e)

	def getUniqueId(self,sender_email):
		result = self.db.search(self.querier.email == str(sender_email))
		user_id = result[0]['encrypted']
		return str(user_id)

	def getUserFromId(self,sender_email):
		result = self.db.search(self.querier.encrypted == str(sender_email))
		email = result[0]['email']
		return str(email)


class Helpers:
	def __init__(self,EMAIL_NOT_FOUND_ERROR=401,EMAIL_UNREGISTERED_ERROR=402,MAIL_NOT_UNIQUE_ERROR=403,OTHER_ERRORS=404):
		self.EMAIL_NOT_FOUND_ERROR = EMAIL_NOT_FOUND_ERROR
		self.EMAIL_UNREGISTERED_ERROR = EMAIL_UNREGISTERED_ERROR
		self.MAIL_NOT_UNIQUE_ERROR = MAIL_NOT_UNIQUE_ERROR
		self.OTHER_ERRORS = OTHER_ERRORS
		self.db = JsonDb()

	def verifyEmail(self,sender_email,unique_mail_id,check):
		try:
			self.is_valid = True # validate_email(sender_email)
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

class telegramResponse:
	def __init__(self,request,email_id,mail_id,comment):
		self.request = request
		self.email_id = email_id
		self.mail_id = mail_id
		self.comment = comment
		self.sender = '578382604'
		self.header = headerInfo(request)
		self.token = '1224852365:AAEoDrTaMmfDqG2Ch-9owJeT31nXfKbkID4'
		self.base = "https://api.telegram.org/bot{}/".format(self.token)
		self.helper = Helpers()
		self.db = JsonDb()

	def createReadResponse(self):
		global timestamp
		if self.header.verifyGoogleCache():
			self.count = self.db.getReadCount(self.email_id,self.mail_id)
			# if self.count == 0:
			self.incr,self.err_code =self.helper.updatemailreadCount(self.email_id,self.mail_id)
			self.body = "`Your mail with mailid:` *"+str(self.mail_id)+"*` with remark:` *"+str(self.comment)+"*` Was interacted just now @ ` *"+str(timestamp)+"*"
			self.url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(self.sender,self.body)
			requests.get(self.url,verify=False)
			
		else:
			self.count = self.db.getConfigCount(self.email_id,self.mail_id)
			if self.count == 0:
				self.db.updateConfigCount(self.email_id,self.mail_id)
				self.body = "`You have been Configured for maild_id:` "+str(self.mail_id)+" `with remark:` "+str(self.comment)
				self.url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(self.sender,self.body)
				requests.get(self.url,verify=False)

def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html',{'csrf_token':str(csrf_token)})

def getImage(request):
	csrf_token = get_token(request)
	return render(request,'indexx.html')

def getTimeDifference(current,lastread):
	# datetime(year, month, day, hour, minute, second) 
	curr_d = current.split(" ")[0].split("-")
	curr_t = current.split(" ")[1].split(":")

	las_d = lastread.split(" ")[0].split("-")
	las_t = lastread.split(" ")[1].split(":")
	current = datetime.datetime(int(curr_d[0]),int(curr_d[1]),int(curr_d[2]),int(curr_t[0]),int(curr_t[1]),int(curr_t[2]))
	lastread = datetime.datetime(int(las_d[0]),int(las_d[1]),int(las_d[2]),int(las_t[0]),int(las_t[1]),int(las_t[2]))
	diff = current-lastread
	return diff.seconds

def setTrackr(request,sender_email,unique_mail_id,comments):
	global timestamp
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	csrf_token = get_token(request)
	check = "FromReceiver"
	sender_email = str(sender_email).lower().strip()
	unique_mail_id = str(unique_mail_id).strip().lower()
	comments = str(comments).strip().lower()
	db = JsonDb()
	sender_email = db.getUserFromId(sender_email)
	print(sender_email)
	mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments,check)
	is_valid,err_code = mailTrackr.setTracker()

	print(is_valid,err_code)

	if err_code == 'receiver_request':
		response = telegramResponse(request,sender_email,unique_mail_id,comments)
		response.createReadResponse()
		httpresponse = HttpResponse()
		httpresponse['status_code'] = 200
		image_data = open("static/img/1px-1px.png","rb").read()
		return httpresponse
		
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

def setTrackrr(request):
	csrf_token = get_token(request)
	if request.is_ajax():
		request_data = request.POST
		check = request_data['check']
		sender_email = request_data['emailid'].lower().strip()

		try:
			user_id = int(sender_email)
			return JsonResponse({'validated':'False','errorcode':str(401)})
		except Exception as e:
			print(e)


		unique_mail_id = request_data['mailid'].strip().lower()
		comments = request_data['comments'].strip().lower()
		mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments,check)
		is_valid,err_code = mailTrackr.setTracker()

		if is_valid:
			# image_data = getImage(request)
			db = JsonDb()
			print("i am here")
			user_id = db.getUniqueId(sender_email)
			print(user_id)
			if check == "FromSender":
				return JsonResponse({'validated':'True','errorcode':str(err_code),'user_id':str(user_id)})
			else:
				return HttpResponse(image_data, content_type="image/png")
		else:
			if check == "FromSender":
				return JsonResponse({'validated':'False','errorcode':str(err_code)})
			else:
				image_data = open("static/img/"+str(err_code)+".PNG","rb").read()

		return HttpResponse(image_data, content_type="image/png")