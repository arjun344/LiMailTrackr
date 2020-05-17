from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
import datetime
import requests
from django.http import JsonResponse
from django.shortcuts import redirect

from .database import JsonDb
from .telegramResponse import telegramResponse
from .helper import Helpers


def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html',{'csrf_token':str(csrf_token)})

def getTimeDifference(current,lastread):
	# datetime(year, month, day, hour, minute, second) 
	print(current,lastread)
	curr_d = current.split(" ")[0].split("-")
	curr_t = current.split(" ")[1].split(":")
	las_d = lastread.split(" ")[0].split("-")
	las_t = lastread.split(" ")[1].split(":")
	current = datetime.datetime(int(curr_d[0]),int(curr_d[1]),int(curr_d[2]),int(curr_t[0]),int(curr_t[1]),int(curr_t[2]))
	lastread = datetime.datetime(int(las_d[0]),int(las_d[1]),int(las_d[2]),int(las_t[0]),int(las_t[1]),int(las_t[2]))
	diff = current-lastread
	return diff.seconds

def setTrackr(request,sender_email,unique_mail_id,comments):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	db = JsonDb()
	helpers = Helpers(db,request,sender_email,unique_mail_id,comments)
	sender_email = db.getUserFromId(sender_email)
	count = db.getConfigCount(sender_email,unique_mail_id)

	if sender_email == None or count==None:
		return JsonResponse({'errorcode':'Hey This Seems its invalid url !'})

	if count != None:
		count = int(count)
		if count > 1:
			fromGoogle = helpers.verifyGoogleCache()
			if fromGoogle:
				lastread = db.getLastRead(sender_email,unique_mail_id)
				if lastread == None:
					diff = 100
				else:
					diff = getTimeDifference(timestamp,lastread)

				print(diff)

				if diff >= 5:
					status = db.updateMailReadCount(sender_email,unique_mail_id)
					if status:
						chat_id = db.getChatId(sender_email)
						tResponse = telegramResponse(request,sender_email,unique_mail_id,comments,chat_id,timestamp)
						tResponse.sendReadResponse()
						return JsonResponse({'status':'request logged as mail read'})
					else:
						return JsonResponse({'status':'something went wrong'})

				else:
					return JsonResponse({'status':'TIME_DIFF_LESS_THAN_5'})

			else:
				return JsonResponse({'status':'Hey this url is not meant to be accesed from outside !'})

		elif count == 1:
			db.updateConfigCount(sender_email,unique_mail_id)
			return JsonResponse({'status':'imageGenerated'})


	return JsonResponse({'errorcode':'Sorry Action Not Allowed'})

def setTrackrr(request):
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

		db = JsonDb()
		helper = Helpers(db,request,sender_email,unique_mail_id,comments)
		is_valid,err_code = helper.setTracker()

		if is_valid:
			user_id = db.getUniqueId(sender_email)
			chat_id = db.getChatId(sender_email)
			
			db.updateConfigCount(sender_email,unique_mail_id)
			tResponse = telegramResponse(request,sender_email,unique_mail_id,comments,chat_id,timestamp)
			tResponse.sendConfigResponse()

			return JsonResponse({'validated':'True','errorcode':str(err_code),'user_id':str(user_id)})
		else:
			return JsonResponse({'validated':'False','errorcode':str(err_code)})

	return JsonResponse({'validated':'False','errorcode':'NOT_ALLOWED'})