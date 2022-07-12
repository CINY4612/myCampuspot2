from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
# client = MongoClient('mongodb://54.180.93.142', 27017, username="test", password="sparta")
client = MongoClient('mongodb+srv://test:sparta@cluster0.8gfz7vo.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# JWT 토큰을 만들 때 필요한 비밀문자열 / 내 서버에서만 인코딩, 디코딩 가능
SECRET_KEY = 'CAMPUSPOT'

import jwt
import datetime # 토큰 만료시간을 위한 모듈
import hashlib  # 비밀번호 암호화를 위한 모듈 (기본설치)

###### 페이지 리턴 ######
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.userdb.find_one({"email": payload['email']})
        return render_template('main.html', name=user_info["name"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/signup')
def signup():
    return render_template('signup.html')


###### 로그인 관련 ######

# [회원가입 API]
@app.route('/api/signup', methods=['POST'])
def api_signup():
    email_receive = request.form['email_give']
    password_receive =request.form['password_give']
    name_receive = request.form['name_give']
    birth_receive = request.form['birth_give']
    campus_receive = request.form['campus_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()  # 비밀번호 암호화

    db.userdb.insert_one({'email': email_receive, 'password': pw_hash, 'name': name_receive, 'birth' : birth_receive, 'campus' : campus_receive})

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})


# [로그인 API]
@app.route('/api/login', methods=['POST'])
def api_login():
    email_receive = request.form['email_give']
    password_receive =request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.userdb.find_one({'email': email_receive, 'password': pw_hash})

    # 일치하는 유저정보 찾아 JWT 토큰을 만들어 발급
    if result is not None:
        # JWT 토큰 - payload와 시크릿키가 필요
        # 시크릿키로 토큰 디코딩하여 payload값 확인
        payload = {
            'email': email_receive, # ID로 로그인 이력 확인
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)   # 만료시간(1분) 이후 에러
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)