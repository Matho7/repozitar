import tornado.ioloop
import tornado.web
import psycopg2
import config

# Request handler that interacts with the database
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            self.render("index.html", api_key=config.api_key)
        except Exception as e:
            self.write("Error: {}".format(str(e)))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server is running at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
