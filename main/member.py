from main import *
from flask import Blueprint


blueprint =  Blueprint("member",__name__,url_prefix="/member") #블루프린트이름,모듈이름,url



#회원가입
@blueprint.route("/join", methods=["GET", "POST"])
def member_join():
    if request.method == "GET":
        return render_template("join.html")
    else:
        name = request.form.get("name", type=str)
        email = request.form.get("email", type=str)
        password = request.form.get("password", type=str)
        repassword = request.form.get("repassword", type=str)

        if name is None or email is None or password is None or repassword is None:
            flash("입력되지 않은 값이 있습니다.")
            return render_template("join.html", title="회원가입")
        
        if password != repassword:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template("join.html",title="회원가입")

        members = mongo.db.member
        cnt = members.find({"email":email}).count()
        if cnt > 0 : #같은이메일값이 하나라도 있으면
            flash("중복된 이메일 주소입니다.")
            return render_template("join.html", title="회원가입")
        
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        members = mongo.db.members
        post = {
            "name": name,
            "email": email,
            "password": password,
            "joindate": current_utc_time,
            "logintime": "",
            "logincount": 0,
        }
        
        x = members.insert_one(post)
        return redirect(url_for("member.member_login", title="회원가입"))



#로그인
@blueprint.route("/login", methods=["GET", "POST"])
def member_login():
    if request.method == "GET":
        next_url = request.args.get("next_url",type=str)
        if next_url is not None:
            return render_template("login.html",next_url = next_url, title="회원로그인")
        else:
            return render_template("login.html", title="회원로그인")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        next_url = request.form.get("next_url")

        members = mongo.db.members
        data = members.find_one({"email": email})

        if data is None:
            flash("회원정보가 없습니다.")
            return redirect(url_for("member.member_login",title="회원가입"))
        else:
            if data.get("password") == password:
                session["email"] = email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                session.permanent = True

                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect(url_for("board.lists"))
            else:
                flash("비밀번호가 일치하지 않습니다.")
                return redirect(url_for("member.member_login", title="회원 로그인"))



#로그아웃
@blueprint.route("/logout")
def member_logout():
    try:
        del session["name"]
        del session["id"]
        del session["email"]
    except:
        pass
    return redirect(url_for('member.member_login'))