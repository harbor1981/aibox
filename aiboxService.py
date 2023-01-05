from flask import Flask, redirect, url_for, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      print(1)
      user = request.form['nm']
      return redirect(url_for('success',name = user))
   else:
      print(2)
      user = request.args.get('nm')
      return redirect(url_for('success',name = user))

@app.route('/push',methods = ['GET'])
def push():
      url = request.args.get('url')
      url2 = 'rtsp://192.168.1.5:8554/ds-test'
      print(url)
      return url2


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)