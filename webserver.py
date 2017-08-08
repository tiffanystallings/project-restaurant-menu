from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class WebserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>Hello!</body></html>"
				self.wfile.write(output)
				print output
				return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)


def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print ("Web server is running on port %s" % port)
		server.serve_forever()

	except KeyboardInterrupt:
		print ("Keyboard Interrupt detected. \
			Web server shutting down."
		server.socket.close()


if __name__ == '__main__':
	main()
