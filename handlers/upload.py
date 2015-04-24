import config
import web, json
import string, random
import hashlib

class Uploader:
	def __init__(self):
		self.result = json.loads('{}')
	
	def gen_name(self):
		found = True
		newname = ''
		while found:
			newname = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
			found = config.db.query("SELECT COUNT(*) c FROM images WHERE id=$id", vars=dict(id=newname)).c > 0
		
		return newname
		
	def gen_token(self):
		found = True
		token = ''
		while found:
			token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))
			found = config.db.query("SELECT COUNT(*) c FROM images WHERE token=$t", vars=dict(t=token)).c > 0
		
		return token
	
	def GET(self):
		raise web.seeother('/')
		
	def POST(self):
		try:
			data = web.input(uploader={})
		except ValueError:
			self.result['success'] = False
			self.result['error'] = 'File too large. Max size is {0}KB.'.format(config.image_max_size/1024)
			return json.dumps(self.result)
		
		
		ext = data.uploader.filename.split('.')[-1]
		
		newname = self.gen_name()
		disk_path = newname + '.' + ext
		
		filedata = data.uploader.file.read()
		hasher = hashlib.md5()
		hasher.update(filedata)
		digest = hasher.hexdigest()
		
		results = config.db.query("SELECT disk_path FROM images WHERE img_hash=$digest LIMIT 1", vars=dict(digest=digest))
		
		if len(results) > 0:
			disk_path = results[0].disk_path
		else:
			with open(config.filedir + disk_path, 'wb') as f:
				f.write(filedata)
		
		token = self.gen_token()
		config.sess.token = token
		
		with config.db.transaction():
			config.db.insert('settings', token=token, inactive_expiry=config.inactive_expiry)
			config.db.insert('images', token=token, id=newname, disk_path=disk_path, content_type=data.uploader.type, upload_ip=web.ctx.ip, img_hash=digest)
		
		self.result['success'] = True
		self.result['id'] = newname
		self.result['url'] = '{0}{1}.{2}'.format(config.host, newname, ext)
		self.result['token'] = token
		self.result['delete_url'] = '{0}delete/{1}'.format(config.host, token)
		return json.dumps(self.result)
