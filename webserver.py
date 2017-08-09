from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


ENGINE = create_engine('sqlite:///restaurantmenu.db')
DBSESSION = sessionmaker(bind = ENGINE)
SESSION = DBSESSION()

class WebserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				restaurants = SESSION.query(Restaurant).all()

				output = ""
				output += "<html><body>"
				output += "<h1>My Favorite Restaurants</h1>"
				output += "<p><a href='/restaurants/new'>Add a Restaurant</a></p>"
				for restaurant in restaurants:
					output += "<div class = 'restaurant'>"
					output += "<h2>%s</h2>" % restaurant.name
					output += "<a href='#'>Edit</a>"
					output += "<br>"
					output += "<a href='#'>Delete</a>"
					output += "</div>" 
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h1>Add New Restaurant</h1>"
				output += "<form method='POST' enctype='multipart/form-data'>"
				output += "<h2>Restaurant Name:</h2>"
				output += "<input name='restaurant' type='text'>"
				output += "<input type='submit' value='Add'>"
				output += "</form>"
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


	def do_POST(self):
		try:
			if self.path.endswith('/restaurants/new'):
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				restaurant_name = fields.get('restaurant')

				restaurant = Restaurant(name=restaurant_name[0])
				SESSION.add(restaurant)
				SESSION.commit()

				self.send_response(301)
				self.send_header('Location', '../restaurants')
				self.end_headers()

				print("Restaurant added!")
				return

		except:
			pass


def main():
	try:
		port = 8080
		server = HTTPServer(('', port), WebserverHandler)
		print ("Web server is running on port %s" % port)
		server.serve_forever()

	except KeyboardInterrupt:
		print ("Keyboard Interrupt detected. \
			Web server shutting down.")
		server.socket.close()


if __name__ == '__main__':
	main()
