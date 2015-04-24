import config
import web, json
import os, time

class Update:
	def __init__(self):
		self.result = json.loads('{}')
	
	def POST(self):
		input = web.input()
		
		try:
			input.view_limit = abs(int(input.view_limit))
		except:
			input.view_limit = None
		
		try:
			input.inactive_expiry = abs(int(input.inactive_expiry))
		except:
			input.inactive_expiry = None
		
		try:
			input.expires = abs(int(input.expires))
			input.expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + input.expires))
		except:
			input.expires = None
	
		with config.db.transaction():
			config.db.update('settings', vars=input, where="token=$token", view_limit=input.view_limit, inactive_expiry=input.inactive_expiry, expires=input.expires)
		
		self.result['success'] = True
		return json.dumps(self.result)
