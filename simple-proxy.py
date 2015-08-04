# -*- coding: utf-8 -*-

# Please install BeautifulSoup first:
#   easy_install-2.7 beautifulsoup4

import SocketServer
import SimpleHTTPServer
import urllib
import urlparse
import StringIO
import gzip
import re
import bs4
import signal
import sys
import argparse
import webbrowser


class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print '  get ->', self.path

        # check for change domain
        url = self.path
        pos = url.find('@')
        if pos > 0:
            pos_end = pos + 1 + url[pos + 1:].find('@')
            new_domain = url[pos + 1: pos_end]

            if new_domain:
                set_domain_name(new_domain)
                url = url[: pos] + url[pos_end + 1:]
                self.path = url
                print '[*] Domain changed to', new_domain, '!'

        # create url for request
        self.domain = get_domain_name()
        local_url = list(urlparse.urlsplit(self.path))
        local_url[0] = 'http' if not local_url[0] else local_url[0]
        local_url[1] = self.domain
        domain_url = urlparse.urlunsplit(local_url)

        # response to get
        response = urllib.urlopen(domain_url)

        # check if response gziped
        if response.info().get('Content-Encoding') == 'gzip':
            buffer = StringIO.StringIO(response.read())
            unzipped = gzip.GzipFile(fileobj=buffer)
            data = unzipped.read()
        else:
            data = response.read()

        # check if data
        if 'text/html' in response.info().get('Content-Type'):
            data_changed = False

            soup = bs4.BeautifulSoup(data, 'html.parser')
            body = soup.body
            if body:
                print '    this is html data'

                # change all urls to proxy
                for child in body.descendants:
                    if child.name == 'a':
                        if child.get('href'):
                            href = list(urlparse.urlsplit(child['href']))
                            # change href only for chosen domain
                            if href[1] == self.domain:
                                href[1] = self.host + ':' + str(self.port)
                                child['href'] = urlparse.urlunsplit(href)
                            else:  # store new domain
                                new_domain = href[1]
                                href[1] = self.host + ':' + str(self.port)
                                child['href'] = urlparse.urlunsplit(href)
                                child['href'] += '@' + new_domain + '@'

                # replace html text
                for child in body.findAll(text=True):
                    # we don't need change scripts
                    if child.parent.name == 'script':
                        continue

                    text = unicode(child)
                    query = ((r'\b(\w{' + str(self.length) + r'})\b').
                             decode('utf-8'))
                    regexp = re.compile(query, re.UNICODE)
                    sub_str = (r'\1 ' + self.chars).decode('utf-8')
                    text = regexp.sub(sub_str, text)
                    child.replace_with(text)
                    data_changed = True

                if data_changed:
                    data = str(soup)

        # send headers
        self.send_response(200)
        self.send_header('content-type', response.info().get('content-type'))
        self.end_headers()

        self.wfile.write(data)
        # self.wfile.close()

    def do_POST(self):
        print 'post ->', self.path


def set_domain_name(domain):
    f = open('simple-proxy-domain.name', 'w')
    f.write(domain)
    f.close()


def get_domain_name():
    f = open('simple-proxy-domain.name', 'r')
    domain = f.read()
    f.close()
    return domain


def sigint_handler(signal, frame):
    print '\n[*] Shutting down ...'
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description='Simple proxy server with python.\n'
        'Adds characters to words with specified length.')
    parser.add_argument('-p', '--port', type=int, default=1234,
                        help='Proxy port')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Proxy host')
    parser.add_argument('-d', '--domain', type=str, default='habrahabr.ru',
                        help='Domain name')
    parser.add_argument('-l', '--length', type=int, default=6,
                        help='Add chars to words with specified length')
    parser.add_argument('-c', '--chars', type=str, default='™',
                        help='Chars to add after words with specified length')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, sigint_handler)

    set_domain_name(args.domain)
    Proxy.length = args.length
    Proxy.chars = args.chars
    Proxy.host = args.host
    Proxy.port = args.port

    httpd = SocketServer.ForkingTCPServer((args.host, args.port), Proxy)
    print '[*] Starting for', args.domain, 'at', \
        '{0}:{1}'.format(args.host, args.port), '...'

    webbrowser.open('http://{0}:{1}'.format(args.host, args.port))
    httpd.serve_forever()

if __name__ == '__main__':
    main()
