import config, web, os
import re

class Delete:
	def GET(self, id):
		if not re.match(r'^[A-Za-z0-9]{12}$', id):
			raise web.notfound()
		
		v = dict(t=id)
		image = config.db.query("SELECT disk_path FROM images WHERE token=$t", vars=v)
		config.db.query("DELETE i, s FROM images i JOIN settings s ON i.token = s.token WHERE s.token=$t", vars=v)
		count = config.db.query("select COUNT(*) c from images where token=$t", vars=v)
		
		if count.c == 0 and len(image) >0:
			os.remove(config.filedir + image[0].disk_path)
			return config.templates.base("Image deleted.")
		else:
			raise web.notfound()