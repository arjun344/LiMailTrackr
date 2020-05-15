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

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html',{'csrf_token':str(csrf_token)})

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

# def setTrackr(request,sender_email,unique_mail_id,comments):
# 	global timestamp
# 	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# 	csrf_token = get_token(request)
# 	check = "FromReceiver"
# 	sender_email = str(sender_email).lower().strip()
# 	unique_mail_id = str(unique_mail_id).strip().lower()
# 	comments = str(comments).strip().lower()
# 	db = JsonDb()
# 	sender_email = db.getUserFromId(sender_email)
# 	print(sender_email)
# 	mailTrackr= EmailTrackr(sender_email,unique_mail_id,comments,check)
# 	is_valid,err_code = mailTrackr.setTracker()

# 	print(is_valid,err_code)

# 	if err_code == 'receiver_request':
# 		response = telegramResponse(request,sender_email,unique_mail_id,comments)
# 		response.createReadResponse()
# 		httpresponse = HttpResponse()
# 		httpresponse['status_code'] = 200
# 		return httpresponse

# 	if is_valid:
# 		image_data = getImage(request)
# 		if check == "FromSender":
# 			return JsonResponse({'validated':'True','errorcode':str(err_code)})
# 		else:
# 			return HttpResponse(image_data, content_type="image/png")
# 	else:
# 		if check == "FromSender":
# 			return JsonResponse({'validated':'False','errorcode':str(err_code)})
# 		else:
# 			image_data = open("static/img/"+str(err_code)+".PNG","rb").read()

# 	return HttpResponse(image_data, content_type="image/png")

def setTrackrr(request):
	global timestamp
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