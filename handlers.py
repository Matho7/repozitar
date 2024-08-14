import tornado.web
from tornado.auth import GoogleOAuth2Mixin
from tornado.httpclient import AsyncHTTPClient, HTTPClientError
import datetime
import csv
import io
import polyline
from models import User, Route, Waypoint
from utils import render_template
from peewee import fn  # Pridanie importu fn

class BaseHandler(tornado.web.RequestHandler):
    def render_template(self, template_name, **kwargs):
        self.write(render_template(template_name, **kwargs))

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id:
            return None
        user = User.get(User.id == int(user_id.decode('utf-8')))
        return user


class IndexHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        self.render_template("index.html", user=user)


class GoogleLoginHandler(BaseHandler, GoogleOAuth2Mixin):
    async def get(self):
        if self.get_argument("code", False):
            user = await self.get_authenticated_user(
                redirect_uri=self.settings["google_oauth"]["redirect_uri"],
                code=self.get_argument("code"),
                client_id=self.settings["google_oauth"]["client_id"],
                client_secret=self.settings["google_oauth"]["client_secret"]
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
                # Získanie nového ID pre používateľa
                max_id = User.select(fn.MAX(User.id)).scalar()
                new_id = max_id + 1 if max_id else 1
                existing_user = User.create(id=new_id, email=email)

            self.set_secure_cookie("user", str(existing_user.id))
            self.redirect("/routes")
        else:
            self.authorize_redirect(
                redirect_uri=self.settings["google_oauth"]["redirect_uri"],
                client_id=self.settings["google_oauth"]["client_id"],
                scope=["profile", "email"],
                response_type="code",
                extra_params={"approval_prompt": "auto"}
            )


class RoutesHandler(BaseHandler):
    def get(self):

        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        # user = User.get(User.id == 1)

        routes = Route.select().where(Route.user_id == user.id)
        message = self.get_argument("message", None)
        self.render_template("routes.html", routes=routes, message=message)


class PolylineHandler(BaseHandler):
    def get(self, route_id):

        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)
        route = Route.get(Route.id == route_id)
        waypoint_list = [{"lat": wp.lat, "lng": wp.lng} for wp in waypoints]
        markers = [{"lat": wp.lat, "lng": wp.lng} for wp in waypoints]
        self.render_template("map.html", waypoints=waypoint_list, markers=markers, route_name=route.name)


class DirectionsHandler(BaseHandler):
    async def get(self, route_id):

        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        waypoints = Waypoint.select().where(Waypoint.route_id == route_id)
        route = Route.get(Route.id == route_id)

        if not waypoints:
            self.write("No waypoints found for this route.")
            return

        start = (waypoints[0].lat, waypoints[0].lng)
        end = (waypoints[-1].lat, waypoints[-1].lng)
        intermediate_waypoints = [(waypoint.lat, waypoint.lng) for waypoint in waypoints[1:-1]]

        # Build URL
        if intermediate_waypoints:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};"
            url += ";".join(f"{wp[1]},{wp[0]}" for wp in intermediate_waypoints)
            url += f";{end[1]},{end[0]}?overview=full&geometries=polyline"
        else:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=polyline"

        try:
            response = await AsyncHTTPClient().fetch(url)
            polyline_data = tornado.escape.json_decode(response.body)['routes'][0]['geometry']
            decoded_polyline = polyline.decode(polyline_data)

            waypoint_list = [{"lat": lat, "lng": lng} for lat, lng in decoded_polyline]
            markers = [{"lat": start[0], "lng": start[1]}] + \
                      [{"lat": wp[0], "lng": wp[1]} for wp in intermediate_waypoints] + \
                      [{"lat": end[0], "lng": end[1]}]

            self.render_template("map.html", waypoints=waypoint_list, markers=markers, route_name=route.name)
        except HTTPClientError as e:
            print(f"HTTP request to OSRM server failed: {e}")
            self.write("Error fetching directions from OSRM server.")


class UploadHandler(BaseHandler):
    def post(self):

        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        # user = User.get(User.id == 1)

        fileinfo = self.request.files['file'][0]
        data = fileinfo['body'].decode('utf-8')

        reader = csv.reader(io.StringIO(data), delimiter=';')
        success = True
        try:
            for row in reader:
                if len(row) < 2:
                    success = False
                    continue

                waypoints_str, route_name = row[0], row[1].strip()
                waypoints = waypoints_str.split(',')

                if len(waypoints) % 2 != 0:
                    success = False
                    continue

                max_route_id = Route.select(fn.MAX(Route.id)).scalar()
                new_route_id = max_route_id + 1 if max_route_id else 1

                new_route = Route.create(
                    id=new_route_id, user_id=user.id, name=route_name, creation_date=datetime.datetime.now())

                # Prepare list of dictionaries for bulk insertion
                waypoint_data = []
                max_waypoint_id = Waypoint.select(fn.MAX(Waypoint.id)).scalar()
                new_waypoint_id = max_waypoint_id + 1 if max_waypoint_id else 1

                for i in range(0, len(waypoints), 2):
                    lat = float(waypoints[i].strip())
                    lng = float(waypoints[i+1].strip())
                    waypoint_data.append({
                        'id': new_waypoint_id,
                        'route_id': new_route.id,
                        'lat': lat,
                        'lng': lng,
                        'order_wp': (i//2) + 1
                    })
                    new_waypoint_id += 1

                # Bulk insert the waypoint data
                Waypoint.insert_many(waypoint_data).execute()

            if success:
                self.redirect("/routes?message=Upload successful")
            else:
                self.redirect("/routes?message=Upload completed with some errors")
        except Exception as e:
            self.redirect(f"/routes?message=Upload failed: {e}")


class DeleteRouteHandler(BaseHandler):
    def get(self, route_id):
        user = self.get_current_user()
        if not user:
            self.redirect("/login")
            return

        try:
            Waypoint.delete().where(Waypoint.route_id == route_id).execute()
            Route.delete().where(Route.id == route_id).execute()
            self.redirect("/routes")
        except Exception as e:
            self.write(f"Error deleting route: {e}")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")
