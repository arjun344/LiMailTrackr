from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.middleware.csrf import get_token
from django.http import JsonResponse


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
	print(sender_email,unique_mail_id)
	return HttpResponse(image_data, content_type="image/png")