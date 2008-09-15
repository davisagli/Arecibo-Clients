from lib.arecibo import post, postaddress
from App.config import getConfiguration
from AccessControl import getSecurityManager
from ZODB.POSException import ConflictError
from clearwind.arecibo.interfaces import IAreciboConfiguration

def arecibo(context, **kw):
    qu = context.getSiteManager().queryUtility(IAreciboConfiguration, name='Arecibo_config')
    key = qu.account_number
    if not key:
        return
    req = context.REQUEST
    error = post()
    
    mail_possible = not not context.MailHost.smtp_host
    if mail_possible and qu.transport == "smtp":
        error.transport = "http"
        
    if kw.get("error_type") == 'NotFound':
        status = 404
        priority = 5
    elif kw.get("error_type") == 'Unauthorized':
        status = 403
        priority = 3        
    else:
        status = 500
        priority = 1
    
    error.set("account", key)
    error.set("priority", priority)
    error.set("user_agent", req['HTTP_USER_AGENT'])
    
    if req.get("QUERY_STRING"):
        error.set("url", "%s?%s" % (req['ACTUAL_URL'], req['QUERY_STRING']))
    else:
        error.set("url", req['ACTUAL_URL'])
    
    error.set("uid", kw.get("error_log_id"))
    error.set("ip", req.get("X_FORWARDED_FOR", req.get('REMOTE_ADDR', '')))   
    error.set("type", kw.get("error_type"))
    error.set("status", status)
    
    if status != 404:
        # lets face it the 404 tb is not useful
        error.set("traceback", kw.get("error_tb"))
    
    # i thought this might be useful
    usr = getSecurityManager().getUser()
    error.set("msg", "username: %s\nuserid: %s" % (usr.getUserName(), usr.getId()))

    if error.transport == "http":    
        try:
            error.send()
        except ConflictError:
            raise
        except:
            pass
            # should we log anything beyond what is already around here?
    elif error.transport == "smtp":
        # use the MailHost to send out which is configured by the site
        # administrator, and has more functionality than straight smtplib
        try:
            context.MailHost.send(error._msg_body())
        except ConflictError:
            raise
        except:
            pass
            # again should we log anything beyond what is already around here?