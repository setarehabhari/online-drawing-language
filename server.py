import json
import os
import shutil
from multiprocessing import Process
from http.server import BaseHTTPRequestHandler, HTTPServer

from core_server import job_create
from shared import data as sdata
import uuid


class Response:
    body = None
    status_code = 200
    content_type = 'application/json'

    def __init__(self, body):
        self.body = body


class Router:
    def route(self, path: str, type: str, body=None):
        if path.startswith('/job/') and type == 'post':
            id = uuid.uuid4().hex
            p = Process(target=job_create, args=(body, id))
            sdata.process_map[id] = p
            p.start()
            return Response({"id": id})

        if path.startswith('/job/') and type == 'get':

            job_id = path.split('/')[2]
            process = sdata.process_map.get(job_id)

            if process is None:
                return Response({
                    "status": "notfound",
                    "file_name": ""
                })
            if process.is_alive():
                return Response({
                    "status": "running",
                    "file_name": ""
                })
            if not process.is_alive():
                return Response({
                    "status": "done",
                    "file_name": job_id
                })


class MYHandler(BaseHTTPRequestHandler):
    router = Router()

    def do_GET(self):
        if self.path.startswith('/media/'):
            FILEPATH = self.path.split('/')[2] + '.jpeg'
            with open(FILEPATH, 'rb') as f:
                self.send_response(200)
                self.send_header("Content-Type", 'application/octet-stream')
                self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(os.path.basename(FILEPATH)))
                fs = os.fstat(f.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
                return

        r = self.router.route(self.path, 'get')

        self.send_response(r.status_code)
        self.send_header('Content-type', r.content_type)
        self.end_headers()
        self.wfile.write(json.dumps(r.body).encode())
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))
        r = self.router.route(self.path, 'post', body)

        self.send_response(r.status_code)
        self.send_header('Content-type', r.content_type)
        self.end_headers()
        self.wfile.write(json.dumps(r.body).encode())
        return


if __name__ == '__main__':
    try:
        server = HTTPServer(('', 8080), MYHandler)
        print('Started httpserver on port ', 8080)

        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()
