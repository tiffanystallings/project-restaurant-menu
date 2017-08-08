from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


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