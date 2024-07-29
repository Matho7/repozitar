from tornado.web import RequestHandler

class AuthMiddleware(RequestHandler):
    def prepare(self):
        user = self.get_current_user()
        if not user and self.request.uri not in ["/", "/login", "/auth/callback"]:
            self.redirect("/")
            return

    def get_current_user(self):
        return self.get_secure_cookie("user")
