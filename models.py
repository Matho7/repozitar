from peewee import *
import config

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
    id = IntegerField(primary_key=True)
    email = CharField(unique=True)

    class Meta:
        table_name = 'users'

class Route(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(User, backref='routes')
    name = CharField()
    creation_date = DateTimeField()

    class Meta:
        table_name = 'routes'

class Waypoint(BaseModel):
    id = IntegerField(primary_key=True)
    route_id = ForeignKeyField(Route, backref='waypoints')
    lat = FloatField()
    lng = FloatField()
    order_wp = IntegerField(constraints=[Check('order_wp > 0')])

    class Meta:
        table_name = 'waypoints'

# Vytvoření tabulek v databázi
db.connect()
db.create_tables([User, Route, Waypoint])
