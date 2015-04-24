from __future__ import division
import config, web, re
import time, os, io
from PIL import Image

class ImageScaler:
	def parse_settings(self, settings):
		types = {
			'p': 'percentage',
			'w': 'width',
			'h': 'height'
		}
		
		s = {}
		s['type'] = types[settings[-1:]]
		s['value'] = int(settings[1:-1])
		return s
	
	def adjustimage(self):
		(width,height) = self.image.size
		
		if self.settings['type'] == 'width':
			scale = self.settings['value'] / width
			width = self.settings['value']
			height = int(height*scale)
		elif self.settings['type'] == 'height':
			scale = self.settings['value'] / height
			height = self.settings['value']
			width = int(width*scale)
		elif self.settings['type'] == 'percentage':
			scale = self.settings['value'] / 100
			height = int(height*scale)
			width = int(width*scale)
			
		self.image.thumbnail((width, height), Image.ANTIALIAS)
	
	def getdata(self):
		output = io.BytesIO()
		self.image.save(output, self.image.format)
		return output.getvalue()
	
	def __init__(self, disk_path, settings):
		self.disk_path = disk_path
		self.settings = self.parse_settings(settings)
		print self.settings
		
		self.image = Image.open(config.filedir + disk_path)
		self.adjustimage()

class View:
	def GET(self, name, ext):
		parser = re.compile(r'^([A-Za-z0-9]{6})(-[0-9]{1,4}[whp]|)$')
		
		match = parser.match(name)
		if not match:
			raise web.notfound()
		
		details = dict(id=match.group(1))
		results = config.db.query("SELECT *, unix_timestamp(last_viewed) timestamp, unix_timestamp(expires) expirestamp FROM images NATURAL JOIN settings WHERE id=$id", vars=details)
		
		if len(results) == 0:
			raise web.notfound()
			
		image = results[0]
		
		scaler = None
		if len(match.group(2)):
			scaler = ImageScaler(image.disk_path, match.group(2))
		
		image.view_count += 1
		with config.db.transaction():
			config.db.update('images', vars=details, where="id=$id", view_count=image.view_count)
		
		delete = False
		if image.view_limit is not None and image.view_count > image.view_limit:
			delete = True
		elif image.expirestamp is not None and image.expirestamp < time.time():
			delete = True
		elif image.inactive_expiry is not None and time.time() - image.timestamp > image.inactive_expiry:
			delete = True
		
		if delete:
			config.db.query("DELETE i, s FROM images i JOIN settings s ON i.token = s.token WHERE s.token=$t", vars=dict(t=image.token))
			count = config.db.query("select COUNT(*) c from images where token=$t", vars=dict(t=image.token))
			
			if count.c == 0:
				os.remove(config.filedir + image.disk_path)
			
			raise web.notfound()
		
		try:
			web.header('Content-Type', image.content_type)
				
			if scaler:
				return scaler.getdata()
			else:
				return open(config.filedir + image.disk_path, 'rb').read()
		
		except:
			raise web.notfound()
