import os 

configure = {
    
    'debug':True,
    
    'template_path':os.path.join(os.path.dirname(__file__), "templates"),
    
    'cookie_secret':"__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    
    "login_url": "/login",
    
    "xsrf_cookies": True,
    
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    
}