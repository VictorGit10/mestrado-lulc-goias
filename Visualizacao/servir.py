from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
import os
import time

class RobustHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        try:
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
        except Exception:
            pass

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except Exception:
            pass

class RobustThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # Ignore socket errors caused by client disconnects
        pass

if __name__ == "__main__":
    port = 8765
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)
    print(f"Servindo {directory} em http://127.0.0.1:{port}/")

    while True:
        try:
            server = RobustThreadingHTTPServer(('127.0.0.1', port), RobustHTTPRequestHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor finalizado pelo usuário.")
            break
        except Exception as e:
            print(f"Reiniciando servidor após exceção: {e}")
            time.sleep(1)
