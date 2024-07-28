import tornado.ioloop
import tornado.web
import os
import config
from models import db
from handlers import IndexHandler, GoogleLoginHandler, PolylineHandler, DirectionsHandler, RoutesHandler, UploadHandler, DeleteRouteHandler, LogoutHandler, SimulateHandler


if __name__ == '__main__':
    settings = {
        "cookie_secret": config.cookie_secret,
        "login_url": "/login",
        "google_oauth": {
            "client_id": config.oauth2_client_id,
            "client_secret": config.oauth2_client_secret,
            "redirect_uri": config.oauth2_redirect_uri,
            "key": config.oauth2_client_id  # Pridanie `key` do google_oauth nastavení
        },
        "static_path": os.path.join(os.path.dirname(__file__), "templates")
    }

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/login', GoogleLoginHandler),
        (r'/auth/callback', GoogleLoginHandler),
        (r'/polyline/(\d+)', PolylineHandler),
        (r'/directions/(\d+)', DirectionsHandler),
        (r'/routes', RoutesHandler),
        (r'/upload', UploadHandler),  # Pridanie novej cesty
        (r'/delete/(\d+)', DeleteRouteHandler),  # Pridanie cesty pre vymazanie
        (r'/logout', LogoutHandler),  # Pridanie cesty pre odhlásenie
        (r'/simulate', SimulateHandler),  # Pridanie cesty pre simuláciu
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    ], **settings)
    app.listen(8080)
    print("Server started at http://localhost:8080/")
    tornado.ioloop.IOLoop.current().start()
