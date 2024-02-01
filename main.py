import json
import tornado.ioloop
import tornado.web
import os
import jinja2
import config
import psycopg2
from config import db_host, db_database, db_user, db_password
import folium
import requests
import polyline
from peewee import *

db_host = config.db_host
db_database = config.db_database
db_user = config.db_user
db_password = config.db_password

db = PostgresqlDatabase(
    database=db_database,
    user=db_user,
    password=db_password,
    host=db_host,
    port=5432
)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        table_name = 'users'


class Route(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User, backref='routes')
    name = CharField()
    creation_date = DateTimeField()

    class Meta:
        table_name = 'routes'


class Waypoint(BaseModel):
    id = AutoField()
    route_id = ForeignKeyField(Route, backref='waypoints')
    lat = FloatField()
    long = FloatField()
    elevation = FloatField(null=True)
    order_wp = IntegerField(constraints=[Check('order_wp > 0')])

    class Meta:
        table_name = 'waypoints'


db.connect()
db.create_tables([User, Route, Waypoint])


def get_routes_and_waypoints(user_id):
    routes = Route.select().where(Route.user_id == user_id)
    waypoints = Waypoint.select().join(Route).where(Route.user_id == user_id)
    return routes, waypoints


class PolylineHandler(tornado.web.RequestHandler):
    def get(self):

        route_id = self.get_argument('route_id')

        route = Route.select().where(Route.id == route_id).get()

        # Retrieve the waypoints for the route
        waypoints = Waypoint.select().where(Waypoint.route_id == route.id)

        # Create a map object
        m = folium.Map(location=[waypoints[0].lat, waypoints[0].long], zoom_start=13)

        # Add markers to the map
        for waypoint in waypoints:
            folium.Marker([waypoint.lat, waypoint.long]).add_to(m)

        # Create a list of coordinates for the polyline
        coordinates = [[waypoint.lat, waypoint.long] for waypoint in waypoints]

        # Create a polyline object and add it to the map
        folium.PolyLine(locations=coordinates, color='red').add_to(m)

        # Display the map
        m.save('polyline.html')

        self.render('polyline.html')


class DirectionsHandler(tornado.web.RequestHandler):
    def get(self):

        # Get the route id from the request
        route_id = self.get_argument('route_id')

        # Retrieve the route from the database
        route = Route.select().where(Route.id == route_id).get()

        # Retrieve the waypoints for the route
        waypoints = Waypoint.select().where(Waypoint.route_id == route.id)

        # Define the start and end coordinates
        start = (waypoints[0].lat, waypoints[0].long)
        end = (waypoints[-1].lat, waypoints[-1].long)

        # Define the intermediate waypoints
        intermediate_waypoints = [(waypoint.lat, waypoint.long) for waypoint in waypoints[1:-1]]

        # Define the OSRM API URL
        url = f'http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};'

        for waypoint in intermediate_waypoints:
            url += f'{waypoint[1]},{waypoint[0]};'

        url += f'{end[1]},{end[0]}?overview=full&geometries=polyline'

        # Send a GET request to the API
        response = requests.get(url)

        # Extract the encoded polyline from the response
        polyline_data = response.json()['routes'][0]['geometry']

        # Decode the polyline into a list of coordinates
        coordinates = polyline.decode(polyline_data)

        # Create a map object
        m = folium.Map(location=start, zoom_start=13)

        # Add markers to the map
        folium.Marker(start).add_to(m)
        folium.Marker(end).add_to(m)

        for waypoint in intermediate_waypoints:
            folium.Marker(waypoint).add_to(m)

        # Create a polyline object and add it to the map
        folium.PolyLine(locations=coordinates, color='red').add_to(m)

        # Display the map
        m.save('osrm.html')

        self.render('osrm.html')


class RoutesHandler(tornado.web.RequestHandler):
    def get(self):
        # Retrieve routes with waypoints from the database
        routes = Route.select().join(Waypoint).group_by(Route.id)

        # Render the HTML table
        self.render("routes.html", routes=routes)


if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/polyline', PolylineHandler),
        (r'/directions', DirectionsHandler),
        (r'/routes', RoutesHandler)
    ])
    app.listen(8888)
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
