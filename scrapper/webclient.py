
import urllib2
from json import dumps, loads
import socket

class Webclient:

    def query_server(self, endpoint, request):

        url = "https://supremedecisions.court.gov.il/Home/%s" % endpoint

        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8,he;q=0.6',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            # Identify as a browser or you shall be blocked
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

        req = urllib2.Request(url, dumps(request), headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        a = loads(the_page)
        return a["data"]

    def download_url(self, url, retries = 5):
        import time

        headers = {
            # Identify as a browser or you shall be blocked
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

        for retry in xrange(0, retries):
            req = urllib2.Request(url, None, headers)
            try:
                response = urllib2.urlopen(req)
            except (socket.error, urllib2.HTTPError), e:
                if isinstance(e, urllib2.HTTPError) and hasattr(e, "code") and e.code == 404:
                    print "404 Not found: %s" % url
                    return None
                sleeptime = 2**retry
                print "Failed %s in retry %s" % (url, retry)
                time.sleep(sleeptime)
                continue
            text = response.read()
            return text
        return None