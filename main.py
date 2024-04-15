import json
import tornado.ioloop
import tornado.web
import os
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
    lng = FloatField()
    elevation = FloatField(null=True)
    order_wp = IntegerField(constraints=[Check('order_wp > 0')])

    class Meta:
        table_name = 'waypoints'


db.connect()


def conn():
    db.create_tables([User, Route, Waypoint])
    routes = Route.select().join(Waypoint).group_by(Route.id)
    return routes


class PolylineHandler(tornado.web.RequestHandler):
    def get(self, route_id):
        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)

        m = folium.Map(location=[waypoints[0].lat, waypoints[0].lng], zoom_start=6)

        for waypoint in waypoints:
            folium.Marker([waypoint.lat, waypoint.lng]).add_to(m)

        coordinates = [[waypoint.lat, waypoint.lng] for waypoint in waypoints]

        folium.PolyLine(locations=coordinates, color='red').add_to(m)

        m.save('polyline.html')

        with open('./polyline.html', 'r') as file:
            content = file.read()

        self.write(content)


class DirectionsHandler(tornado.web.RequestHandler):
    def get(self, route_id):

        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)

        start = (waypoints[0].lat, waypoints[0].lng)
        end = (waypoints[-1].lat, waypoints[-1].lng)

        intermediate_waypoints = [(waypoint.lat, waypoint.lng) for waypoint in waypoints[1:-1]]

        url = f'http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};'

        for waypoint in intermediate_waypoints:
            url += f'{waypoint[1]},{waypoint[0]};'

        url += f'{end[1]},{end[0]}?overview=full&geometries=polyline'

        response = requests.get(url)

        polyline_data = response.json()['routes'][0]['geometry']

        coordinates = polyline.decode(polyline_data)

        m = folium.Map(location=start, zoom_start=6)

        folium.Marker(start).add_to(m)
        folium.Marker(end).add_to(m)

        for waypoint in intermediate_waypoints:
            folium.Marker(waypoint).add_to(m)

        folium.PolyLine(locations=coordinates, color='red').add_to(m)

        m.save('directions.html')

        with open('./directions.html', 'r') as file:
            content = file.read()

        self.write(content)


class RoutesHandler(tornado.web.RequestHandler):
    def get(self):
        routes = conn()
        self.render("routes.html", routes=routes)


if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/polyline/(\d+)', PolylineHandler),
        (r'/directions/(\d+)', DirectionsHandler),
        (r'/routes', RoutesHandler)
    ])
    app.listen(8080)
    print("Server started at http://localhost:8080/routes")
    tornado.ioloop.IOLoop.current().start()
