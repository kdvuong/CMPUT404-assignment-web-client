#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if len(buffer) == 0:
                headers, _ = self.parse_response(part.decode("utf-8"))
                status_code = self.get_status_code(headers)
                if status_code >= 300 and status_code < 400:
                    buffer.extend(part)
                    break;
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8', errors="replace")

    def GET(self, url, args=None):
        host, path, protocol, port = self.parse_url(url)

        request = f"GET {path} HTTP/{protocol}\r\nHost: {host}\r\nUser-Agent: Python/3.6\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        code, body = self.send_request(host, port, request)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, path, protocol, port = self.parse_url(url)
        request_body = self.to_qs(args)
        request = f"POST {path} HTTP/{protocol}\r\nHost: {host}\r\nUser-Agent: Python/3.6\r\nAccept: */*\r\nContent-type: application/x-www-form-urlencoded\r\nContent-Length: {len(request_body)}\r\nConnection: close\r\n\r\n{request_body}"
        code, body = self.send_request(host, port, request)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def parse_url(self, url):
        protocol, url = url.split("://")
        path = "/"
        host = url

        if url.find("/") != -1:
            url = url.split("/", 1)
            host = url[0]
            if len(url) > 1:
                path = path + url[1]
        
        port = 80
        if host.find(":") != -1:
            host, port = host.split(":")
            port = int(port)

        protocol = "2" if protocol == "https" else "1.1"

        return host, path, protocol, port

    def parse_response(self, response):
        headers, body = response.split("\r\n\r\n")
        headers = headers.split("\r\n")
        return headers, body

    def get_status_code(self, headers):
        first = headers[0].split(" ")
        return int(first[1])

    def send_request(self, host, port, request):
        self.connect(host, port)
        self.sendall(request)

        response = self.recvall(self.socket)
        headers, body = self.parse_response(response)
        code = self.get_status_code(headers)

        self.socket.close()

        return code, body

    def to_qs(self, data):
        query = []
        if isinstance(data, dict):
            for (key, val) in data.items():
                query.append(f"{key}={val}")
            return "&".join(query)
        else:
            return ""
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))