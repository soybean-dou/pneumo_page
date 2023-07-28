# app.py
from flask import Flask, render_template, request

#Flask 객체 인스턴스 생성
app = Flask(__name__)

@app.route('/',methods=('GET','POST')) # 접속하는 url
def index():
    if request.method == "POST":
        print(request.form.get('user'))
        user = request.form.get('user')
        return render_template('index.html',user=user)
    elif request.method == "GET":
       user="반원"
       return render_template('index.html',user=user)


if __name__=="__main__":
  app.run(debug=True)
  # host 등을 직접 지정하고 싶다면
  # app.run(host="127.0.0.1", port="5000", debug=True)