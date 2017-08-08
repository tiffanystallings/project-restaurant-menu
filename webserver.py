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
				for restaurant in restaurants:
					output += "<div class = 'restaurant'><h2>%s</h2></div>" % restaurant.name
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


	def do_POST(self):
		try:
			self.send_response(301)
			self.end_headers()

			ctype, pdict = cgi.parse_header(
				self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('message')

			output = ""
			output += "<html><body>"
			output += "<h2>Okay, how about this:</h2>"
			output += "<h1>%s</h1>" % messagecontent[0]
			output += "<form method='POST' enctype='multipart/form-data'\
				action='/hello'><h2>What would you like me to say?</h2>\
				<input name='message' type='text'><input type='submit'\
				value='Submit'></form>"
			output += "</body></html>"

			self.wfile.write(output)
			print output

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
