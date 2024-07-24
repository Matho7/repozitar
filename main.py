import tornado.ioloop
import tornado.web
import os
import requests
import polyline
import config
from peewee import *
from tornado.auth import GoogleOAuth2Mixin
from tornado.httpclient import AsyncHTTPClient, HTTPClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Připojení k databázi
db = PostgresqlDatabase(
    database=config.db_database,
    user=config.db_user,
    password=config.db_password,
    host=config.db_host,
    port=5432
)


# Definice modelů
class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    email = CharField(unique=True)
    password = CharField(null=True)

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


# Vytvoření tabulek v databázi
db.connect()
db.create_tables([User, Route, Waypoint])

# Nastavenie Jinja2 prostredia
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(['html', 'xml'])
)


def render_template(template_name, **kwargs):
    template = env.get_template(template_name)
    return template.render(kwargs)


class BaseHandler(tornado.web.RequestHandler):
    def render_template(self, template_name, **kwargs):
        self.write(render_template(template_name, **kwargs))


class IndexHandler(BaseHandler):
    def get(self):
        self.render_template("index.html")


class GoogleLoginHandler(BaseHandler, GoogleOAuth2Mixin):
    async def get(self):
        if self.get_argument("code", False):
            user = await self.get_authenticated_user(
                redirect_uri=self.settings["google_oauth"]["redirect_uri"],
                code=self.get_argument("code")
            )
            if user is None:
                print("Error: user is None")
                self.write("Authentication failed")
                return
            access_token = user["access_token"]

            http_client = AsyncHTTPClient()
            response = await http_client.fetch(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={access_token}"
            )
            user_info = tornado.escape.json_decode(response.body)
            email = user_info["email"]

            try:
                existing_user = User.get(User.email == email)
            except User.DoesNotExist:
                existing_user = User.create(email=email)

            self.set_secure_cookie("user", str(existing_user.id))
            self.redirect("/routes")
        else:
            await self.authorize_redirect(
                redirect_uri=self.settings["google_oauth"]["redirect_uri"],
                client_id=self.settings["google_oauth"]["client_id"],
                scope=["profile", "email"],
                response_type="code",
                extra_params={"approval_prompt": "auto"}
            )


class RoutesHandler(BaseHandler):
    def get(self):
        user_id = 1
        """
        user_id = self.get_secure_cookie("user")
        if not user_id:
            self.redirect("/login")
            return
        
        user_id = int(user_id.decode('utf-8'))
        """
        routes = Route.select().where(Route.user_id == user_id)
        self.render_template("routes.html", routes=routes)


class PolylineHandler(BaseHandler):
    def get(self, route_id):
        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)
        waypoint_list = [{"lat": wp.lat, "lng": wp.lng} for wp in waypoints]
        self.render_template("map.html", waypoints=waypoint_list)


class DirectionsHandler(BaseHandler):
    async def get(self, route_id):
        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)

        if not waypoints:
            self.write("No waypoints found for this route.")
            return

        start = (waypoints[0].lat, waypoints[0].lng)
        end = (waypoints[-1].lat, waypoints[-1].lng)
        intermediate_waypoints = [(waypoint.lat, waypoint.lng) for waypoint in waypoints[1:-1]]

        # Debug: Print waypoints
        print(f"Start: {start}")
        print(f"End: {end}")
        print(f"Intermediate waypoints: {intermediate_waypoints}")

        # Build URL
        if intermediate_waypoints:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};"
            url += ";".join(f"{wp[1]},{wp[0]}" for wp in intermediate_waypoints)
            url += f";{end[1]},{end[0]}?overview=full&geometries=polyline"
        else:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=polyline"

        # Debug: Print URL
        print(f"OSRM Request URL: {url}")

        try:
            response = await AsyncHTTPClient().fetch(url)
            polyline_data = tornado.escape.json_decode(response.body)['routes'][0]['geometry']
            decoded_polyline = polyline.decode(polyline_data)

            waypoint_list = [{"lat": lat, "lng": lng} for lat, lng in decoded_polyline]
            self.render_template("map.html", waypoints=waypoint_list)
        except HTTPClientError as e:
            print(f"HTTP request to OSRM server failed: {e}")
            self.write("Error fetching directions from OSRM server.")


if __name__ == '__main__':
    settings = {
        "cookie_secret": config.cookie_secret,
        "login_url": "/login",
        "google_oauth": {
            "client_id": config.oauth2_client_id,
            "client_secret": config.oauth2_client_secret,
            "redirect_uri": config.oauth2_redirect_uri
        }
    }

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/login', GoogleLoginHandler),
        (r'/auth/callback', GoogleLoginHandler),
        (r'/polyline/(\d+)', PolylineHandler),
        (r'/directions/(\d+)', DirectionsHandler),
        (r'/routes', RoutesHandler)
    ], **settings)
    app.listen(8080)
    print("Server started at http://localhost:8080/")
    tornado.ioloop.IOLoop.current().start()
