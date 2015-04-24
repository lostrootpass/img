import config
import web, cgi
import handlers

#web.config.debug = False
config.db = web.database(
	dbn = 'mysql',
	host = config.db_cfg['host'],
	user = config.db_cfg['user'],
	pw = config.db_cfg['password'],
	db = config.db_cfg['db']
)

web.config.db_printing = True

urls = (
    '/', 'index',
	'/upload', 'handlers.upload.Uploader',
	'/([a-zA-Z0-9]+)\.([a-zA-Z]{1,4})', 'handlers.view.View',
	'/delete/([a-zA-Z0-9]+)', 'handlers.delete.Delete',
	'/update', 'handlers.update.Update',
	'/kill', 'kill'
)
app = web.application(urls, globals())
templates = web.template.render("templates")
config.templates = templates

web.config.session_parameters['cookie_name'] = 'sess_id'
cgi.maxlen = config.image_max_size

if web.config.get('_session') is None:
	web.config._session = web.session.Session(app, web.session.DBStore(config.db, 'sessions'), initializer={'token': ''})

config.sess = web.config._session

def notfound():
	return web.notfound(templates.base("That doesn't exist.", "error"))
	
app.notfound = notfound

class kill:
	def GET(self):
		config.sess.kill()
		
		raise web.seeother('/')

class index:        
    def GET(self):
		return templates.base()

if __name__ == "__main__":
    app.run()