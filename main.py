import json
from gmplot import gmplot
import geopy
from geopy.geocoders import Nominatim
import tornado.ioloop
import tornado.web
import jinja2
import config
import psycopg2
from config import db_host, db_database, db_user, db_password
import googlemaps
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


def get_routes_and_waypoints(user_id):
    db.connect()
    db.create_tables([User, Route, Waypoint])
    routes = Route.select().where(Route.user_id == user_id)
    waypoints = Waypoint.select().join(Route).where(Route.user_id == user_id)
    return routes, waypoints


routes, waypoints = get_routes_and_waypoints(1)

print('Routes:')
for route in routes:
    print(f'- {route.name}')

print('Waypoints:')
for waypoint in waypoints:
    print(f'- ({waypoint.lat}, {waypoint.long})')


class RoutesHandler(tornado.web.RequestHandler):
    def get(self):
        # routes, waypoints = get_routes_and_waypoints(user_id)
        # self.render('routes.html', routes=routes, waypoints=waypoints)
        self.render('index.html')


class GetRoutesAndWaypointsHandler(tornado.web.RequestHandler):
    def get(self, user_id):
        # Get routes and waypoints from the database
        routes, waypoints = get_routes_and_waypoints(user_id)

        # Prepare data to send back to the client
        data = {
            'routes': routes,
            'waypoints': waypoints
        }
        # Send data back as JSON response
        self.write(json.dumps(data))


if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', RoutesHandler),
        (r'/get-routes-and-waypoints/(?P<user_id>\d+)', GetRoutesAndWaypointsHandler)
    ])
    app.listen(8888)
    print("Server started at http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
