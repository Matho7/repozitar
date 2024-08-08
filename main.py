import tornado.ioloop
import tornado.web
import os
import config
from models import db
from handlers import IndexHandler, GoogleLoginHandler, PolylineHandler, DirectionsHandler, RoutesHandler, UploadHandler, DeleteRouteHandler, LogoutHandler
from custom_static_file_handler import AuthStaticFileHandler
from middleware import AuthMiddleware


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/login", GoogleLoginHandler),
            (r"/auth/callback", GoogleLoginHandler),
            (r"/polyline/(\d+)", PolylineHandler),
            (r"/directions/(\d+)", DirectionsHandler),
            (r"/routes", RoutesHandler),
            (r"/upload", UploadHandler),
            (r"/delete/(\d+)", DeleteRouteHandler),
            (r"/logout", LogoutHandler),
            (r'/static/(.*)', AuthStaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "templates")}),
        ]
        settings = {
            "cookie_secret": config.cookie_secret,
            "login_url": "/",
            "google_oauth": {
                "client_id": config.oauth2_client_id,
                "client_secret": config.oauth2_client_secret,
                "redirect_uri": config.oauth2_redirect_uri,
                "key": config.oauth2_client_id
            },
            "static_path": os.path.join(os.path.dirname(__file__), "templates"),
            "default_handler_class": AuthMiddleware,
        }
        super(Application, self).__init__(handlers, **settings)


if __name__ == "__main__":
    app = Application()
    app.listen(8080)
    print("Server started at http://localhost:8080/")
    tornado.ioloop.IOLoop.current().start()
