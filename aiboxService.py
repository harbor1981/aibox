from flask import Flask, redirect, url_for, request, render_template
import FlaskTest
app = Flask(__name__)
out_port= 9600
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

def getReturnURL(out_port):
    return_url="rtsp://192.168.1.6:%d/ds-test"%(out_port)
    return return_url

@app.route('/push',methods = ['GET'])
def push():
      inputURL = request.args.get('url')
      print("inputUrl="+inputURL)
      global out_port
      returnURL="rtsp://192.168.1.6:%d/aibox"%(out_port)
      print("returnURL=%s"%(returnURL))
      out_port = out_port + 1
      return (returnURL)


if __name__ == '__main__':

    app.run(host="0.0.0.0",port=5000)

    print("come on ")