import googlemaps
from gmplot import gmplot
import geopy
from geopy.geocoders import Nominatim
import tornado.ioloop
import tornado.web
import psycopg2

import config

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class MapHandler(tornado.web.RequestHandler):
    def post(self):
        origin = self.get_argument("origin")
        destination = self.get_argument("destination")
        travel_mode = self.get_argument("travelMode")

        # Get coordinates for origin and destination
        origin_coords = self.get_coordinates(origin)
        dest_coords = self.get_coordinates(destination)

        # Render the template and pass variables
        self.render("map.html", api_key=config.api_key, originCoords=origin_coords, destCoords=dest_coords, travelMode=travel_mode)

    def get_coordinates(self, location):
        geolocator = Nominatim(user_agent="my_geocoder")
        location_info = geolocator.geocode(location)
        if location_info:
            return location_info.latitude, location_info.longitude
        else:
            # Fallback to dummy coordinates if geocoding fails
            return 37.42299, -122.143076

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/map", MapHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
