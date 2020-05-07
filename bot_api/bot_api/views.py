from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
from django.http import JsonResponse
from validate_email import validate_email

def index(request):
	csrf_token = get_token(request)
	return render(request,'index.html')

def getImage(request):
	csrf_token = get_token(request)
	image_data = open("static/img/profile.jpg", "rb").read()
	return HttpResponse(image_data, content_type="image/png")

def setTrackr(request,sender_email,unique_mail_id):
	csrf_token = get_token(request)
	image_data = open("static/img/profile.jpg", "rb").read()
	print(verifyEmail(sender_email))
	return HttpResponse(image_data, content_type="image/png")

def verifyEmail(sender_email):
	is_valid = validate_email(str(sender_email).lower().strip())
	return is_valid