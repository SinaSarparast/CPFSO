'''
copied from previous data project - common/net.py
'''

# fixes for Python 2.6 / SSL / urllib2 issue
# https://github.com/calmh/unifi-api/blob/master/unifi/controller.py

# designed to fix the following exception
# URLError: <urlopen error [Errno 1] _ssl.c:504: error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>

try:
    # Ugly hack to force SSLv3 and avoid
    # urllib2.URLError: <urlopen error [Errno 1] _ssl.c:504:
    # error:14077438:SSL routines:SSL23_GET_SERVER_HELLO:tlsv1 alert internal error>
    import _ssl
    _ssl.PROTOCOL_SSLv23 = _ssl.PROTOCOL_TLSv1
except:
    pass

try:
    # Updated for python certificate validation
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass


from _socket import gaierror

#python 2 to 3 conversion

from io import StringIO
from io import BytesIO
#import exceptions
import gzip
#import httplib
import logging
import socket
import sys
import time
import unittest
import urllib

#from urllib2 import HTTPError, URLError
import http.cookiejar as cookielib
#python 2 to 3 conversion
import urllib.request as urllib2
#import urlparse
import urllib.parse as urlparse
import zlib
from bs4 import BeautifulSoup, element
from dateandtime import dateparse
#import common.basicURLexpander
#import longurl
#import requests



# URL query parameters to strip (just used for tracking purposes)
bad_query_keys = ('utm_campaign', 'utm_source', 'utm_content', 'utm_term', 'utm_id', 'utm_medium', 'utm_hp_ref')
bad_query_pairs = ( ('CMP', ('share_btn_tw', 'twt_gu', 'Share_AndroidApp_Gmail')), ('ocid', ('socialflow_twitter',)) )


# default max URL expansion values
DEFAULT_MAX_URL_EXPAND_ATTEMPTS = 5
DEFAULT_MAX_HTTP_HEAD_ATTEMPTS = 3



endurls = set()

class NonFatalNetException(Exception):
    pass

class NotModified(Exception):
    pass


def strip_query_string_tracking(query):
    # strip tracking query strings
    query_strings = urlparse.parse_qsl(query, True)
    kept_query_strings = []

    for query_key, query_value in query_strings:
        if query_key not in bad_query_keys:
            bad_query_pair = False
            for bad_query_key, bad_query_values in bad_query_pairs:
                bad_query_pair = (query_key == bad_query_key) and (query_value in bad_query_values)
                if bad_query_pair:
                    break
            if not bad_query_pair:
                k = query_key.encode('utf-8') if isinstance(query_key, unicode) else query_key
                v = query_value.encode('utf-8') if isinstance(query_value, unicode) else query_value
                kept_query_strings.append( (k, v) )

    return kept_query_strings


def split_and_strip_url(url):
    # strip Google Analytics, etc tracking from query string and return URL split in to its parts
    parsed_url = urlparse.urlsplit(url)

    url_scheme = parsed_url.scheme.lower()
    url_netloc= parsed_url.netloc.lower()
    url_path = parsed_url.path
    url_query = parsed_url.query
    url_fragment = parsed_url.fragment

    kept_query_strings = strip_query_string_tracking(url_query)

    # rebuild url
    return (url_scheme, url_netloc, url_path, urllib.urlencode(kept_query_strings, True), url_fragment)


def strip_url_tracking(url):
    (url_scheme, url_netloc, url_path, query_string, url_fragment) = split_and_strip_url(url)
    return urlparse.urlunsplit( (url_scheme, url_netloc, url_path, query_string, url_fragment) )


def build_url_path(expanded_url_path, expanded_query_string, expanded_url_fragment):
    # rebiuld a url path from path and optional query string and fragment
    url_path = expanded_url_path

    if expanded_query_string is not None and expanded_query_string != '':
        url_path += '?' + expanded_query_string

    if expanded_url_fragment is not None and expanded_url_fragment != '':
        url_path += '#' + expanded_url_fragment

    return url_path


def get_net_loc(url):
    parsed_url = urlparse.urlsplit(url)
    return parsed_url.netloc.lower()




#opener = request.build_opener(HTTP10Handler)
#print(opener.open('http://stackoverflow.com/q/13656757').read()[:100])

#failedurls = set()

connectedhosts = {}
cookiejar = cookielib.CookieJar()

class HeadRequest(urllib2.Request):
    def get_method(self):
        return 'HEAD'

def geturlcontents(link, attempt = 10, justifnewer=None, waitsecs = 0, timeout = 15, referer="http://www.google.com"):
    if attempt < 0:
        return None
    time.sleep(waitsecs)
    attempt -= 1
    try:
        #if link in failedurls:
        #    raise NonFatalNetException("Already failed at fetching "+link)
        if link.startswith("//"):
            link = "http:"+link
        parsed = urlparse.urlparse(link)
        resource = parsed.path
        if parsed.query != "":
            resource += "?" + parsed.query
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar), urllib2.HTTPSHandler()) # HTTPSHandler(debuglevel=1)
        opener.addheaders = getrequestheaders(referer=referer)
        opener.add_handler(urllib2.HTTPErrorProcessor())
        opener.add_handler(urllib2.HTTPRedirectHandler())
        if justifnewer is not None:
            try:
                headresponse = opener.open(HeadRequest(link), timeout = timeout)
                lm = dateparse(headresponse.info().getheader('Last-Modified'))
                if lm < justifnewer:
                    raise NotModified("not modified")
            except NotModified as n:
                raise n
            except Exception as e:
                pass
        response = opener.open(link, timeout = timeout)
        if response.getcode()/100 == 3 and response.info().getheader('Location'):
            return geturlcontents(response.info().getheader('Location'), attempt=attempt, waitsecs=5, timeout = timeout, referer=link)
        if not response.getcode() == 200:
            raise NonFatalNetException("Response not 200")
        possiblycompressed = response.read()
        link = response.url
        if response.info().get('content-encoding', '') == 'deflate':
            possiblycompressed = zlib.decompressobj(-zlib.MAX_WBITS).decompress(possiblycompressed)
        if response.info().get('content-encoding', '') == 'gzip':
            data = BytesIO(possiblycompressed)
            gzipper = gzip.GzipFile(fileobj=data)
            possiblycompressed = gzipper.read()
        if len(possiblycompressed) < 20000 and "http-equiv" in possiblycompressed and "URL" in possiblycompressed.upper():
            redirecturl = meta_redirect(possiblycompressed)
            if redirecturl is not None:
                return geturlcontents(redirecturl, attempt=attempt, waitsecs=5, referer=link)
        return (possiblycompressed, link)
    except NonFatalNetException as g:
        logging.debug("NonFatalNetException")
        logging.exception(g)
        raise g
    except socket.gaierror as f:
        logging.debug("socket error")
        logging.exception(f)
        raise f
    except socket.timeout as e:
        logging.warn("timeout error")
        # logging.exception(e)
        raise e
    except ssl.SSLError as e:
        if ('timeout' in e.message.lower()) or ('timed out' in e.message.lower()):
            logging.warn("timeout error")
        else:
            logging.debug("SSL error")
            logging.exception(e)
        # logging.exception(e)
        raise e
    except ValueError as e:
        if 'unknown url type' in e.message.lower():
            logging.warn("unknown URL type")
        else:
            logging.debug("ValueError")
            logging.exception(e)
        # logging.exception(e)
        raise e
    except urllib2.HTTPError as e:
        if e.code == 401:
            logging.warn("HTTP Error 401 - not authorised")
        elif e.code == 404:
            logging.warn("HTTP Error 404 - not found")
        elif e.code == 500:
            logging.warn("HTTP Error 500 - internal server error")
        elif e.code == 502:
            logging.warn("HTTP Error 502 - bad gateway")
        elif e.code == 503:
            logging.warn("HTTP Error 503 - service unavailable")
        else:
            logging.warn("HTTP Error")
            logging.exception(e)
        raise e
    except urllib2.URLError as e:
        logging.warn("URL Error %s" % e.reason)
        raise e
    except urllib.error.HTTPError as e:
        logging.warn("HTTP Error %s" % e.code)
        raise e
    except IOError as e:
        logging.warn("IOError %s, %s" % (e.errno, e.strerror))
        raise e
    except Exception as e:
        #failedurls.add(link)
        logging.warn("Failed to fetch "+link)
        logging.exception(e)
        raise e

def meta_redirect(content):
    soup  = BeautifulSoup(content, "lxml")
    #print soup
    result=soup.find(name=["meta","META","Meta"],attrs={"http-equiv":["Refresh", "REFRESH", "refresh"]})
    if result:
        wait,text=result["content"].split(";")
        if int(wait) > 5:
            return None
        if text.lower().startswith("url="):
            url=text[4:]
            return url
    return None

def get_request_header(referer = None):
    a= {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.8',
       'Accept-Encoding': 'gzip, deflate, sdch',
       'Accept-Language': 'en-US,en;q=0.8',
       'Cache-Control':'no-cache',
       'Connection': 'keep-alive'}
    if referer is not None:
        a['Referer']= referer
    a['Pragma']= 'no-cache'
    a['User-Agent']='Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36'
    return a

def getrequestheaders(referer = None):
    a = []
    a.append(('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'))
    a.append(('Accept-Charset', 'ISO-8859-1,utf-8;q=0.8'))
    a.append(('Accept-Encoding', 'gzip, deflate, sdch'))
    a.append(('Accept-Language', 'en-US,en;q=0.8'))
    a.append(('Cache-Control', 'no-cache'))
    a.append(('Connection', 'keep-alive'))
    if referer is not None:
        a.append(('Referer',referer))
    a.append(('Pragma', 'no-cache'))
    a.append(('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.28 Safari/537.36'))
    return a

def getExternalIP():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(('google.com', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip

def significanturl(url):
    #print url
    s = urlparse.urlsplit(removebadqueryparams(url))
    r = s[0]+"://"+s[1]+s[2]
    if s[3] is not None and s[3].strip() != "":
        r += "?"+s[3]
    #print r
    return r

badqueryparams = set(["utm","hash","share","cmp","fsrc","feedtype","feedname","ocid","source","ito","ns_"])
def removebadqueryparams(utmlink):
    up = urlparse.urlsplit(utmlink)
    d={}
    for n, v in urlparse.parse_qs(up.query).iteritems():
        isgood = True
        for qp in badqueryparams:
            if n.lower().startswith(qp):
                isgood = False
                break
        if isgood:
            d[n] = v
    return urlparse.urlunsplit([up.scheme, up.netloc, up.path, urllib.urlencode(d, doseq=True), ''])






