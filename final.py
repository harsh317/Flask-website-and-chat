from flask import Flask,render_template,request,redirect,url_for,session,flash
from datetime import timedelta,datetime
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
app.secret_key= "mysecret"
run_with_ngrok(app)

socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.permanent_session_lifetime = timedelta(minutes=5)
db = SQLAlchemy(app)

class users(db.Model):
    _id =  db.Column("id" , db.Integer , primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    occu = db.Column(db.String(100)) 
	
    def __init__(self,name,email,occu):
        self.name = name
        self.email = email
        self.occu = occu
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/view')
def view():

    if "user" in session:
        return render_template("view.html" , values=users.query.all())
    else:
        flash(f"You are not logged in", "info")
        return redirect(url_for("login"))
	
@app.route('/login', methods=["POST","GET"])
def login():
    if request.method == "POST":
        #session.permanent=True
        user = request.form["name"]
        session["user"] = user
	
        found_user = users.query.filter_by(name=user).first()     
	        
        if found_user:
            session["email"] = found_user.email
            session["occu"] = found_user.occu
        else:
            usr = users(user, "","")
            db.session.add(usr)
            db.session.commit()
        
        flash(f"Login in succesful!!!!", "info")
        return redirect(url_for("use"))
        
    else:
        if "user" in session:
            flash(f"Already loggied in", "info")
            return redirect(url_for("use"))
        return render_template("login.html")
	
        
       

@app.route("/user" , methods=["POST","GET"])
def use():
    email = None
    occu = None
   
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
       	    email = request.form["email"]
       	    occu = request.form["occu"]
       	    session["email"] = email
       	    session["occu"] = occu
       	    
       	    found_user = users.query.filter_by(name=user).first()       
       	    found_user.email = email
       	    found_user.occu = occu
       	    db.session.commit()
       	    flash("email and Occupation was saved")
       	else:
       	    if "occu" in session:
       	        occu = session["occu"]
       	    if "email" in session:
       	        email = session["email"]
        	    
       	return render_template("userlog.html",email=email,occu=occu)
        
    else:
       flash(f"You are not logged in", "info")
       return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"You have been logged out,{user}", "info")
    session.pop("user",None)
    session.pop("email",None)
    session.pop("occu",None)
    return render_template("login.html")
    print(users.name)
@app.route('/chat')
def sessions():
    return render_template('chat.html')
	 
def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':
   db.create_all()
   socketio.run(app,debug=True)
   
