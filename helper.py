from flask import redirect, render_template, request, session
import requests
from functools import wraps

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # print("decorated_function called")
        # print("f " + str(f))
        # print("args " + str(args))
        # print("kwargs " + str(kwargs))
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    # print("f " + str(decorated_function))
    
    return decorated_function