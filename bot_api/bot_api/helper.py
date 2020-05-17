
class Helpers:
	def __init__(self,db,request,sender_email,mail_id,comments,EMAIL_NOT_FOUND_ERROR=401,EMAIL_UNREGISTERED_ERROR=402,MAIL_NOT_UNIQUE_ERROR=403,OTHER_ERRORS=404):
		self.EMAIL_NOT_FOUND_ERROR = EMAIL_NOT_FOUND_ERROR
		self.EMAIL_UNREGISTERED_ERROR = EMAIL_UNREGISTERED_ERROR
		self.MAIL_NOT_UNIQUE_ERROR = MAIL_NOT_UNIQUE_ERROR
		self.OTHER_ERRORS = OTHER_ERRORS
		self.request = request
		self.header = request.headers
		self.db = db
		self.sender_email = sender_email
		self.mail_id = mail_id
		self.comments = comments

	def verifyGoogleCache(self):
		try:
			self.user_agent = self.header['User-Agent']
			if 'GoogleImageProxy' in self.user_agent:
				return True
			else:
				return False
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

	def verifyEmail(self):
		is_valid,result = self.db.checkMail(self.sender_email)
		if is_valid:
			return True

	def setTracker(self):
		is_valid = self.verifyEmail()
		if is_valid:
			if self.db.checkUniqueId(self.sender_email,self.mail_id):
				flag = self.db.insertMail(self.sender_email,self.mail_id,self.comments)
				if flag:
					return True,None
				else:
					return False,self.OTHER_ERRORS
			else:
				return False,self.MAIL_NOT_UNIQUE_ERROR
		else:
			return False,self.EMAIL_UNREGISTERED_ERROR


		