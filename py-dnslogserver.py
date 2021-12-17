#!/usr/bin/env python3
# coding=utf-8
# ******************************************************************
# DNSLog-Server: A Python-based DNSLog-server
# Author:
# L Scheibling
# ******************************************************************
# Additional Credit:
# Github Copilot
# ******************************************************************
# License:
# Distributed under the MIT License
# ******************************************************************

import os, argparse, copy, json, datetime, sys

from dnslib import RR, QTYPE
from dnslib.server import DNSServer, BaseResolver
from dnslib.dns import A

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from termcolor import cprint

cprint('[•] Python3 DNSLog Server', 'green')
cprint('[•] Provided by https://github.com/scheibling', 'yellow')
cprint('[•] Version 1.0', 'yellow')

if len(sys.argv) <= 1:
    cprint('No arguments provided, run -h for help', 'red')
    exit(0)

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dnslog-domain",
                    dest="dnslog_domain",
                    help="DNSLog domain to resolve (Required)",
                    action="store",
                    required=True)
parser.add_argument("-i", "--dnslog-ip",
                    dest="dnslog_ip",
                    help="The IP of this server for listeners (Required)",
                    action="store",
                    required=True)
parser.add_argument("-f", "--logging-folder",
                    dest="logging_folder",
                    help="Folder to store logs (Default: 'logging'-subdirectory)",
                    action="store",
                    default="logging/")

args = parser.parse_args()

# Respond with fixed requests to all DNS queries
class FixedResolver(BaseResolver):
    def __init__(self, zone, args):
        self.rrs = RR.fromZone(zone)
        self.args = args

        if (self.args.logging_folder[-1:] != '/'):
            self.args.logging_folder += '/'

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname

        # Create a log file for the requests
        if not os.path.isdir(self.args.logging_folder):
            os.makedirs(self.args.logging_folder)

        # Create a log file for the requests

        with open('%s%stxt' % (self.args.logging_folder, str(qname)), 'a') as file:
            log = {
                "dns_name": str(qname),
                "src": str(handler.client_address[0]),
                "timestamp": str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
            }
            file.write(json.dumps(log) + '\n')
        
        # Reply to the request
        for rr in self.rrs:
            a = copy.copy(rr)
            a.rname = qname
            
            # If the request is for the top DNSLog domain, reply with the IP of the server
            if (qname == '%s.' % self.args.dnslog_domain):
                reply.add_answer(RR(qname, QTYPE.A, QTYPE.A, 10, A(self.args.dnslog_ip)))
                return reply
            reply.add_answer(a)
        return reply

class DNSLogServer():
    def __init__(self, args):
        self.args = args
        cprint('[•] Initiating fixed DNS resolver for zone %s' % self.args.dnslog_domain, 'green')
        self.resolver = FixedResolver('. 60 IN A 127.1.2.3', self.args)

    def start_server(self):
        self.udp_server = DNSServer( self.resolver,
                                port=53,
                                address=self.args.dnslog_ip)
        self.udp_server.start_thread()

        self.tcp_server = DNSServer( self.resolver,
                                port=53,
                                address=self.args.dnslog_ip,
                                tcp=True)
        self.tcp_server.start_thread()

        cprint('[•] DNSLog server started on %s:53/tcp/udp' % self.args.dnslog_ip, 'green')
        
    def stop_server(self):
        self.udp_server.stop()
        self.tcp_server.stop()
        cprint('[•] DNSLog server stopped', 'green')

def CreateHandlerClass(init_args):
    class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urlparse(self.path)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            if parsed_path.query[0:17] == 'query_identifier=' and os.path.isfile('%s%s.%s.txt' % (init_args.logging_folder, parsed_path.query[17:], init_args.dnslog_domain)):       
                with open('%s%s.%s.txt' % (init_args.logging_folder, parsed_path.query[17:], init_args.dnslog_domain), 'r') as file:
                    self.wfile.write(file.read().encode('utf-8'))
            else:
                self.wfile.write("{}".encode('utf-8'))
    return CustomHTTPRequestHandler

class LogOutputServer():
    def __init__(self, args):
        self.args = args
        cprint('[•] Initiating HTTP server for %s' % self.args.dnslog_domain, 'green')
        self.handler = CreateHandlerClass(self.args)
        self.server = HTTPServer((self.args.dnslog_ip, 80), self.handler)
        
    def start_server(self):
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.server_close()
            cprint('[•] Shutting down HTTP server', 'green')

if __name__ == "__main__":
    dnslog_server = DNSLogServer(args)
    dnslog_server.start_server()

    log_output_server = LogOutputServer(args)
    log_output_server.start_server()

    cprint('[•] Shutting down DNSLog Server', 'green')
    dnslog_server.stop_server()

    cprint('[•] Exiting...', 'green')