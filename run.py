#!/usr/bin/env python3

import socket, socketserver
import sys, os, argparse
import threading

DNS_HEADER_LENGTH = 12
    
class DNSHandler(socketserver.BaseRequestHandler):
    # based on: https://github.com/pathes/fakedns
    # (c) 2014 Patryk Hes [MIT license]

    def handle(self):
        socket = self.request[1]
        data = self.request[0].strip()

        # If request doesn't even contain full header, don't respond.
        if len(data) < DNS_HEADER_LENGTH:
            return

        # Try to read questions - if they're invalid, don't respond.
        try:
            all_questions = self.dns_extract_questions(data)
        except IndexError:
            return

        # Filter only those questions, which have QTYPE=A and QCLASS=IN
        # TODO this is very limiting, remove QTYPE filter in future, handle different QTYPEs
        accepted_questions = []
        for question in all_questions:
            name = str(b'.'.join(question['name']), encoding='UTF-8')
            if ((name == "ctest.cdn.nintendo.net") and (question['qtype'] == b'\x00\x01' and question['qclass'] == b'\x00\x01')):
                accepted_questions.append(question)
            else:
                print("ATTENTION: Nintendo seems to have changed their captive portal check to:", name)
        response = (
            self.dns_response_header(data) +
            self.dns_response_questions(accepted_questions) +
            self.dns_response_answers(accepted_questions)
        )
        socket.sendto(response, self.client_address)

    def dns_extract_questions(self, data):
        """
        Extracts question section from DNS request data.
        See http://tools.ietf.org/html/rfc1035 4.1.2. Question section format.
        """
        questions = []
        # Get number of questions from header's QDCOUNT
        n = (data[4] << 8) + data[5]
        # Where we actually read in data? Start at beginning of question sections.
        pointer = DNS_HEADER_LENGTH
        # Read each question section
        for i in range(n):
            question = {
                'name': [],
                'qtype': '',
                'qclass': '',
            }
            length = data[pointer]
            # Read each label from QNAME part
            while length != 0:
                start = pointer + 1
                end = pointer + length + 1
                question['name'].append(data[start:end])
                pointer += length + 1
                length = data[pointer]
            # Read QTYPE
            question['qtype'] = data[pointer+1:pointer+3]
            # Read QCLASS
            question['qclass'] = data[pointer+3:pointer+5]
            # Move pointer 5 octets further (zero length octet, QTYPE, QNAME)
            pointer += 5
            questions.append(question)
        return questions

    def dns_response_header(self, data):
        """
        Generates DNS response header.
        See http://tools.ietf.org/html/rfc1035 4.1.1. Header section format.
        """
        header = b''
        # ID - copy it from request
        header += data[:2]
        # QR     1    response
        # OPCODE 0000 standard query
        # AA     0    not authoritative
        # TC     0    not truncated
        # RD     0    recursion not desired
        # RA     0    recursion not available
        # Z      000  unused
        # RCODE  0000 no error condition
        header += b'\x80\x00'
        # QDCOUNT - question entries count, set to QDCOUNT from request
        header += data[4:6]
        # ANCOUNT - answer records count, set to QDCOUNT from request
        header += data[4:6]
        # NSCOUNT - authority records count, set to 0
        header += b'\x00\x00'
        # ARCOUNT - additional records count, set to 0
        header += b'\x00\x00'
        return header

    def dns_response_questions(self, questions):
        """
        Generates DNS response questions.
        See http://tools.ietf.org/html/rfc1035 4.1.2. Question section format.
        """
        sections = b''
        for question in questions:
            section = b''
            for label in question['name']:
                # Length octet
                section += bytes([len(label)])
                section += label
            # Zero length octet
            section += b'\x00'
            section += question['qtype']
            section += question['qclass']
            sections += section
        return sections

    def dns_response_answers(self, questions):
        """
        Generates DNS response answers.
        See http://tools.ietf.org/html/rfc1035 4.1.3. Resource record format.
        """
        records = b''
        for question in questions:
            record = b''
            for label in question['name']:
                # Length octet
                record += bytes([len(label)])
                record += label
            # Zero length octet
            record += b'\x00'
            # TYPE - just copy QTYPE
            # TODO QTYPE values set is superset of TYPE values set, handle different QTYPEs, see RFC 1035 3.2.3.
            record += question['qtype']
            # CLASS - just copy QCLASS
            # TODO QCLASS values set is superset of CLASS values set, handle at least * QCLASS, see RFC 1035 3.2.5.
            record += question['qclass']
            # TTL - 32 bit unsigned integer. Set to 0 to inform, that response
            # should not be cached.
            record += b'\x00\x00\x00\x00'
            # RDLENGTH - 16 bit unsigned integer, length of RDATA field.
            # In case of QTYPE=A and QCLASS=IN, RDLENGTH=4.
            record += b'\x00\x04'
            # RDATA - in case of QTYPE=A and QCLASS=IN, it's IPv4 address.
            record += b''.join(map(
                lambda x: bytes([int(x)]),
                IP.split('.')
            ))
            records += record
        return records

def print_logo():
    # s/o to http://www.gamers.org/~fpv/

    if os.get_terminal_size()[0] < 78:

        logo = '''\033[1;35m
   ______ _____ _____ __   ___
   | __  \  _  |  _  |  \ /  |
   | | \ | | | | | | | . V . |
   | | / | \_/ | \_/ | |\ /| |
   | |/ / \   / \   /| | V | |
   | ' /   \_/   \_/ \_|   | |
   |__/                    \_|
        \033[0;39m'''

    else:

        logo = '''\033[1;35m
   =================     ===============     ===============   ========  ========
    \b\\\\ . . . . . . .\\\\   //. . . . . . .\\\\   //. . . . . . .\\\\  \\\\. . .\\\\// . . //
   ||. . ._____. . .|| ||. . ._____. . .|| ||. . ._____. . .|| || . . .\/ . . .||
   || . .||   ||. . || || . .||   ||. . || || . .||   ||. . || ||. . . . . . . ||
   ||. . ||   || . .|| ||. . ||   || . .|| ||. . ||   || . .|| || . | . . . . .||
   || . .||   ||. _-|| ||-_ .||   ||. . || || . .||   ||. _-|| ||-_.|\ . . . . ||
   ||. . ||   ||-'  || ||  `-||   || . .|| ||. . ||   ||-'  || ||  `|\_ . .|. .||
   || . _||   ||    || ||    ||   ||_ . || || . _||   ||    || ||   |\ `-_/| . ||
   ||_-' ||  .|/    || ||    \|.  || `-_|| ||_-' ||  .|/    || ||   | \  / |-_.||
   ||    ||_-'      || ||      `-_||    || ||    ||_-'      || ||   | \  / |  `||
   ||    `'         || ||         `'    || ||    `'         || ||   | \  / |   ||
   ||            .===' `===.         .==='.`===.         .===' /==. |  \/  |   ||
   ||         .=='   \_|-_ `===. .==='   _|_   `===. .===' _-|/   `==  \/  |   ||
   ||      .=='    _-'    `-_  `='    _-'   `-_    `='  _-'   `-_  /|  \/  |   ||
   ||   .=='    _-'          `-__\._-'         `-_./__-'         `' |. /|  |   ||
   ||.=='    _-'                                                     `' |  /==.||
   =='    _-'                                                            \/   `==
   \   _-'                                                                `-_   /
   `''                                                                      ``'
        \033[0;39m'''

    print(logo)

def run_server(server):
    try:
        server.serve_forever()
    except:
        server.shutdown()
        sys.exit(0)

def find_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("duckduckgo.com", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def parse_arg():
    parser = argparse.ArgumentParser(description='Game streaming server for Nintendo Switch', usage='python %(prog)s [options]')
    parser.add_argument('--port', dest='port', default=80, metavar='PORT', help='port of the http server (default: 80). If you don\'t want to run this with sudo, use --port 8080')
    parser.add_argument('--ap', dest='ap', metavar='INT', default=0, help='start ap with interface INT (see "ip address" to find your wifi interface, i.e. wlan0 or wlp2s0)')    
    parser.add_argument('--c', dest='c', default=10, metavar='CHAN', help='wifi channel')
    parser.add_argument('--sound', dest='sound', metavar='N', default=1, help='activate sound on the host (default: 1)')
    parser.add_argument('--fps', dest='fps', metavar='N', default=2, help='client fps (1 = 15FPS, 2 = 20FPS, default: 2)')    
    parser.add_argument('--res', dest='res', metavar='N', default=1, help='resolution (1 = low, 2 = mid, default: 1)')
    parser.add_argument('--verbose', dest='verb', metavar='N', default=0, help='show debug information (default: 0)')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    # Minimal configuration - allow to pass IP in configuration    
    args = parse_arg()
    http_port = int(args.port)
    if type(args.ap) != str:
        ap = int(args.ap)
    else:
        ap = args.ap   
    channel = int(args.c)
    fps = args.fps
    res = args.res    
    sound = int(args.sound)
    verb = int(args.verb)

    print_logo()
    print(" * Starting up, please wait...")
    if http_port == 80:
        host, dns_port = '', 53
        if not ap:
            IP = find_ip()
            server = socketserver.ThreadingUDPServer((host, dns_port), DNSHandler)
            print('\033[1;32m * Started DNS server.\033[0;39m')
            threading.Thread(target=run_server, args=[server], daemon=True).start()

        else:
            if verb:
                threading.Thread(target=os.system, args=["create_ap -n -c %s --redirect-to-localhost -w 1+2 %s MarikoDoom" % (channel, ap)], daemon=True).start()             
            else:                  
                threading.Thread(target=os.system, args=["create_ap -n -c %s --redirect-to-localhost -w 1+2 %s MarikoDoom > /dev/null" % (channel, ap)], daemon=True).start()                   
    if verb:
        threading.Thread(target=os.system, args=["python http_server.py %s %s > /dev/null" % (str(http_port), str(fps))], daemon=True).start()
    else:
        threading.Thread(target=os.system, args=["python http_server.py %s %s" % (str(http_port), str(fps))], daemon=True).start()     
    os.system("python pgtest.py")
