from gmplot import gmplot
import geopy
from geopy.geocoders import Nominatim
import tornado.ioloop
import tornado.web
import config
import psycopg2
from config import db_host, db_database, db_user, db_password
import googlemaps

# Pripojenie k databáze
conn = psycopg2.connect(
    host=db_host,
    database=db_database,
    user=db_user,
    password=db_password
)

# Vytvorenie kurzoru
cur = conn.cursor()
user_id = 1

# Získanie trasy a jej bodov pre konkrétneho používateľa
cur.execute("SELECT * FROM routes WHERE user_id = %s LIMIT 1", (user_id,))
route = cur.fetchone()
cur.execute("SELECT * FROM waypoints WHERE route_id = %s", (route[0],))
waypoints = cur.fetchall()

# Uloženie lat a long do pola
waypoints_array = []
for waypoint in waypoints:
    lat = waypoint[2]
    long = waypoint[3]
    waypoints_array.append([lat, long])

print("Waypoints array:", waypoints_array)

class MainHandler(tornado.web.RequestHandler):
    def get(self):

        self.render("index.html", waypoints_array=waypoints_array)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
