import tornado.ioloop
import tornado.web
import psycopg2
from config import db_host, db_database, db_user, db_password

# Request handler that interacts with the database
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            # Establish a connection to the database
            connection = psycopg2.connect(
                host=db_host,
                database=db_database,
                user=db_user,
                password=db_password
            )

            # Create a cursor to execute SQL queries
            cursor = connection.cursor()

            # Example query: Select all rows from a table named 'example_table'
            cursor.execute("SELECT * FROM users")

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close the cursor and the database connection
            cursor.close()
            connection.close()

            # Output the results to the web page
            self.write("Database query results:<br>")
            for row in rows:
                self.write(str(row) + "<br>")

        except Exception as e:
            # Handle database connection or query errors
            self.write(f"Error: {e}")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
