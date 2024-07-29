import os
import tornado.web

class AuthStaticFileHandler(tornado.web.StaticFileHandler):
    def prepare(self):
        user = self.get_current_user()
        print(f"Debug: AuthStaticFileHandler user={user}, uri={self.request.uri}")  # Debug výpis
        if not user:
            self.redirect("/login")
            return super().prepare()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    @classmethod
    def get_absolute_path(cls, root, path):
        # This is necessary to override the default method and avoid errors.
        return os.path.join(root, path)
