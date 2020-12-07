from functools import wraps
from main import session,redirect,url_for,request

#login deco
def login_required(func):
    @wraps(func)
    def decorated_function(*args,**kwargs):
        if session.get('id') is None or session.get('id') == "":
            return redirect(url_for("member.member_login", next_url = request.url))
        return func(*args, **kwargs)
    return decorated_function 
    #request.url 은 현재접속된 page
    '''설정이유 = 로그인하지 않은상태에서 로그인자만 접속할 수 페이지에 접속하면 
        로그인페이지로 넘어가게된다. 그래서 로그인을 하면 아까전에 접근했던 페이지로
        바로 넘어가게 해준다.'''