# -*- coding: utf-8 -*-
# Copyright ClearWind Consulting Ltd., 2008
# Under the BSD License, see LICENSE.TXT
from httplib import HTTPConnection
has_https = False
try:
    from httplib import HTTPSConnection
    has_https = True
except ImportError:
    pass
    
from urllib import urlencode
from urlparse import urlparse
from socket import gethostname, getdefaulttimeout, setdefaulttimeout
from email.Utils import formatdate

import smtplib
import simplejson

posturl = "http://www.areciboapp.com/v/1/"
postaddress = "arecibo@clearwind.ca"
url = urlparse(posturl)

keys = ["account", "ip", "priority", "uid", 
    "type", "msg", "traceback", "user_agent", 
    "url", "status", "server", "timestamp",
    "request", "username"]
    
required = [ "account", ]

class post:
    def __init__(self):
        self._data = {}
        self.transport = "http"
        self.smtp_server = "localhost"
        self.smtp_from = "noreply@clearwind.ca"
        self.set("server", gethostname())
        self.set("timestamp", formatdate())
        
    # public
    def set(self, key, value):
        """ Sets the variable named key, with the value """
        if key not in keys:
            raise ValueError, "Unknown value: %s" % key
        self._data[key] = value

    def send(self):
        """ Sends the data to the arecibo server """
        for x in required:
            assert self._data.get(x), "The key %s is required" % x

        self._send()

    # private
    def _data_encoded(self):
        data = {}
        for k in keys:
            if self._data.get(k):
                data[k] = self._data.get(k)
        return urlencode(data)

    def _send(self):
        key = self.transport.lower()
        assert key in ["http", "smtp", "https"]
        if key in ["http", "https"]:
            self._send_http()
        elif key == "smtp":
            self._send_smtp()
    
    def _msg_body(self):
        body = simplejson.dumps(self._data)
        msg = "From: %s\r\nTo: %s\r\n\r\n%s" % (self.smtp_from, postaddress, body)
        return msg
            
    def _send_smtp(self):
        msg = self._msg_body()
        s = smtplib.SMTP(self.smtp_server)
        s.sendmail(self.smtp_from, postaddress, msg)
        s.quit()
    
    def _send_http(self):
        if self.transport == "https" and has_https:
            h = HTTPSConnection(url[1])
        else:
            h = HTTPConnection(url[1])
        headers = {
            "Content-type": 'application/x-www-form-urlencoded; charset="utf-8"',
            "Accept": "text/plain"}
        data = self._data_encoded()
        oldtimeout = getdefaulttimeout()
        try:
            setdefaulttimeout(10)
            h.request("POST", url[2], data, headers)

            reply = h.getresponse()
            if reply.status != 200:
                raise ValueError, "%s (%s)" % (reply.read(), reply.status)
        finally:                                            
            setdefaulttimeout(oldtimeout)
            
if __name__=='__main__':
    new = post()
    #new.transport = "https"
    new.set("account", "YOUR KEY HERE")
    new.set("priority", 4)
    new.set("user_agent", "Mozilla/5.0 (Macintosh; U; Intel Mac OS X...")
    new.set("url", "http://badapp.org/-\ufffdwe-cant-lose")
    new.set("uid", "123124123123")
    new.set("ip", "127.0.0.1")    
    new.set("type", "Test from python")
    new.set("status", "403")
    new.set("server", "Test Script") 
    new.set("request", """This is the bit that goes in the request""")
    new.set("username", "Jimbob")
    new.set("msg", """
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut 
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit 
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
culpa qui officia deserunt mollit anim id est laborum
""")
    new.set("traceback", """Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: integer division or modulo by zero  df
""")
    new.send()
