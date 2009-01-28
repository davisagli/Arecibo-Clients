from lib.arecibo import post as error 
from lib.arecibo import postaddress
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from socket import gethostname

import traceback
import sys
import time 

ignores = ["/robots.txt", "/favicon.ico"]

def post(request, status, **kw):
    # first off, these items can just be ignored, we 
    # really don't care about them too much
    if request.path in ignores:
        return
    
    exc_info = sys.exc_info()
    items = ['HOME', 'HTTP_ACCEPT', 'HTTP_ACCEPT_ENCODING', \
             'HTTP_ACCEPT_LANGUAGE', 'HTTP_CONNECTION', 'HTTP_HOST', 'LANG', \
             'PATH_INFO', 'QUERY_STRING', 'REQUEST_METHOD', 'SCRIPT_NAME', \
             'SERVER_NAME', 'SERVER_PORT', 'SERVER_PROTOCOL', 'SERVER_SOFTWARE']
    data = [ "%s: %s" % (k, request.META[k]) for k in items if request.META.get(k)]
            
    # build out data to send to Arecibo
    # some fields (like timestamp)
    # are automatically added
    data = {
        "account": settings.ARECIBO_PUBLIC_ACCOUNT_NUMBER,
        "url": request.build_absolute_uri(), 
        "ip": request.META.get('REMOTE_ADDR'),
        "traceback": "\n".join(traceback.format_tb(exc_info[2])),
        "username": request.user.username, # this will be "" for Anonymous
        "request": "\n".join(data),
        "type": str(exc_info[0].__name__),
        "msg": str(exc_info[1]),
        "status": status,
        "uid": time.time(),
        "user_agent": request.META.get('HTTP_USER_AGENT'),     
    }

    data.update(kw)
    
    # a 404 has some specific formatting of the error that
    # can be useful
    if status == 404:
        msg = ""
        for m in exc_info[1]:
            if isinstance(m, dict):
                tried = "\n".join(m["tried"])
                msg = "Failed to find %s, tried: \n%s" % (m["path"], tried)
            else:
                msg += m
        data["msg"] = msg
                                                                   
    # if we don't get a priority, lets create one   
    if not data.get("priority"):
        if status == 500:
            data["priority"] = 1
        else: 
            data["priority"] = 5

    # populate my arecibo object
    err = error()
    for key, value in data.items():
        err.set(key, value)
    
    # try to see if ARECIBO_TRANSPORT is defined
    try:
        if settings.ARECIBO_TRANSPORT == "smtp":
            err.transport = "smtp"
    except AttributeError:
        pass
        
    try:
        if err.transport == "smtp":
            # use Djangos builtin mail 
            send_mail("Error", 
                error._msg_body(), 
                "arecibo@%s" % gethostname(),  
                postaddress)
        else:                
            err.send()
    except:
        # ideally we'd log this out here, but
        # there isn't a built in log for Django
        pass
        
    return data["uid"]
      
