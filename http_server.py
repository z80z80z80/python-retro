#!/usr/bin/env python3

from flask import Flask, request, render_template, redirect
import socket
import sys
import logging

app = Flask(__name__)
app.debug = False

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True
app.logger.disabled = True

def send(key):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 1312)
    message = str.encode(key)
    
    # Send data
    sent = sock.sendto(message, server_address)
    sock.close()

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        key = request.form["key"]
        #print(key)
        send(key)        
    return render_template(template)

if __name__=="__main__":
    port = sys.argv[1]    
    fps = int(sys.argv[2])

    if fps == 1:
        template = "index_15fps.html"
        template = "index_20fps.html"
    else:
        template = "index_20fps.html"
    app.run(host="0.0.0.0", port=port)
