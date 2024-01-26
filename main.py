import json
import tornado.ioloop
import tornado.web
import jinja2
import config
import psycopg2
from config import db_host, db_database, db_user, db_password
import folium
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


routes, waypoints = get_routes_and_waypoints(1)

print('Routes:')
for route in routes:
    print(f'- {route.name}')

print('Waypoints:')
for waypoint in waypoints:
    print(f'- ({waypoint.lat}, {waypoint.long})')


class RoutesHandler(tornado.web.RequestHandler):
    def get(self):
        route_name = "Hiking in the Alps"
        # Retrieve the route from the database
        route = Route.select().where(Route.name == route_name).get()

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
        m.save('map.html')

        self.render('map.html')


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
