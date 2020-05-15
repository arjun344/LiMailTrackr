import requests

class telegramResponse:
	def __init__(self,request,email_id,mail_id,comment,chat_id,timestamp):
		self.request = request
		self.email_id = email_id
		self.mail_id = mail_id
		self.comment = comment
		self.chat_id = chat_id
		self.header = request.headers
		self.token = '1224852365:AAEoDrTaMmfDqG2Ch-9owJeT31nXfKbkID4'
		self.base = "https://api.telegram.org/bot{}/".format(self.token)
		self.timestamp = timestamp

	# def createReadResponse(self):
	# 	global timestamp
	# 	if self.header.verifyGoogleCache():
	# 		self.count = self.db.getReadCount(self.email_id,self.mail_id)
	# 		# if self.count == 0:
	# 		self.incr,self.err_code =self.helper.updatemailreadCount(self.email_id,self.mail_id)
	# 		self.body = "`Your mail with mailid:` *"+str(self.mail_id)+"*` with remark:` *"+str(self.comment)+"*` Was interacted just now @ ` *"+str(timestamp)+"*"
	# 		self.url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(self.sender,self.body)
	# 		requests.get(self.url,verify=False)
			
	# 	else:
	# 		self.count = self.db.getConfigCount(self.email_id,self.mail_id)
	# 		if self.count == 0:
	# 			self.db.updateConfigCount(self.email_id,self.mail_id)
	# 			self.body = "`You have been Configured for maild_id:` "+str(self.mail_id)+" `with remark:` "+str(self.comment)
	# 			self.url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(self.sender,self.body)
	# 			requests.get(self.url,verify=False)

	def sendConfigResponse(self):
		self.body = "`You have been Configured for maild_id:` "+str(self.mail_id)+" `with remark:` "+str(self.comment)
		self.url = self.base + "sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(self.chat_id,self.body)
		requests.get(self.url,verify=False)
