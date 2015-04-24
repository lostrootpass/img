import config, web, re
import time, os
from PIL import Image

class View:
	def GET(self, name, ext):
		if not re.match(r'^[A-Za-z0-9]{6}$', name):
			raise web.notfound()
		
		details = dict(id=name)
		results = config.db.query("SELECT *, unix_timestamp(last_viewed) timestamp, unix_timestamp(expires) expirestamp FROM images NATURAL JOIN settings WHERE id=$id", vars=details)
		
		if len(results) == 0:
			raise web.notfound()
			
		image = results[0]
		
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
			return open(config.filedir + image.disk_path, 'rb').read()
		
		except:
			raise web.notfound()
