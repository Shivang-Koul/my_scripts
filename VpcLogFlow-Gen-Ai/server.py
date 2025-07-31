from http.server import BaseHTTPRequestHandler, HTTPServer
import sys

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple HTTP Server</title>
</head>
<body>
    <h1>Hello from CloudAge</h1>
    <p>{content}</p>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, region, *args, **kwargs):
        self.region = region
        super().__init__(*args, **kwargs)

    def do_GET(self):
        print("path: ", self.path)
        if self.path == '/':
            message = HTML_TEMPLATE.format(content="Welcome to your server!")
        else:
            message = HTML_TEMPLATE.format(content=f"You entered path: {self.path}")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))

def run(args):
    port = 80
    region = "default"
    # Example: parsing command-line args for port and region
    if "-p" in args:
        idx = args.index("-p") + 1
        if idx < len(args):
            port = int(args[idx])
    if "-r" in args:
        region = "user-region"

    def handler(*handler_args, **handler_kwargs):
        return RequestHandler(region, *handler_args, **handler_kwargs)

    server_address = ('', port)
    httpd = HTTPServer(server_address, handler)
    print(f"Serving HTTP on port {port} (region: {region})...")
    httpd.serve_forever()

if __name__ == '__main__':
    run(sys.argv[1:])
