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
    data = {
        "account": settings.ARECIBO_PUBLIC_ACCOUNT_NUMBER,
        "url": request.get_full_path(),
        "ip": request.META.get('REMOTE_ADDR'),
        "traceback": "\n".join(traceback.format_tb(exc_info[2])),
        "type": exc_info[0],
        "msg": exc_info[1],
        "status": status,
        "uid": time.time(),
        "user_agent": request.META.get('HTTP_USER_AGENT'),     
    }

    data.update(kw)
    if not data.get("priority"):
        if isinstance(status, HttpResponse):
            status = status.status_code
        elif isinstance(status, Exception):
            status = 404
            
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
        
    return kw["uid"]
      