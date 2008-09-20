from lib.arecibo import post as error 
from lib.arecibo import postaddress
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from socket import gethostname

import traceback
import sys
import time 

def post(request, status, **kw):
    exc_info = sys.exc_info() 
    url = "%s://%s%s" % (request.META["wsgi.url_scheme"],
            request.get_host(),
            request.get_full_path())
    data = {
        "account": settings.ARECIBO_PUBLIC_ACCOUNT_NUMBER,
        "url": url, 
        "ip": request.META.get('REMOTE_ADDR'),
        "traceback": "\n".join(traceback.format_tb(exc_info[2])),
        "type": exc_info[0],
        "msg": exc_info[1],
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
            tried = "\n".join(m["tried"])
            msg = "Failed to find %s, tried: \n\t%s" % (m["path"], tried)
        data["msg"] = msg
                                                                   
    # if we don't get a priority, make create one   
    if not data.get("priority"):
        if status == 500:
            data["priority"] = 1
        else: 
            data["priority"] = 5

    err = error()
    for key, value in data.items():
        err.set(key, value)
    
    try:
        if settings.ARECIBO_TRANSPORT == "smtp":
            err.transport = "smtp"
    except AttributeError:
        pass
        
    try:
        if err.transport == "smtp":
            # use djangos builtin mail 
            send_mail("Error", error._msg_body(), "arecibo@%s" % gethostname(), postaddress)
        else:                
            err.send()
    except:
        pass
        
    return data["uid"]
      