from flask import Flask, render_template, request, url_for, redirect, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
#set app as a Flask instance 
app = Flask(__name__, static_url_path='',  static_folder='static')
#encryption relies on secret keys so they could be run
app.secret_key = "testing"

def db_connect(): 
    client = MongoClient("mongodb+srv://717u5:wMz8xEJib5wUZIo5@cluster0.w6o27sx.mongodb.net/?retryWrites=true&w=majority" , server_api=ServerApi('1'))
    return client

# Create admin user
def db_init():
    pw = "1n73ll1g3nc3"
    insert_user("Admin", "admin333@yahoo.com", pw)

def find_user_username(username):
    client = db_connect()
    mydb = client["admin101"]
    mycol = mydb["users"]
    x = mycol.find_one({"name": username})
    return x

def find_user_email(email):
    client = db_connect()
    mydb = client["admin101"]
    mycol = mydb["users"]
    x = mycol.find_one({"email": email}) # {"email": "", "password": {"$ne":"whatever"}}
    return x

def insert_user(name, email, password):
    client = db_connect()
    db = client["admin101"]
    users_table = db.users
    users_table.insert_one({
        "name": name,
        "email": email,
        "password": password 
    })
    
def find_user(email, password):
    client = db_connect()
    db = client["admin101"]
    users_table = db.users
    out = users_table.find_one({
        "email": email,
        "password": password 
    })

    return out

#Strating point
@app.route("/")
def index():
    return render_template('start.html')

#Register page 
@app.route("/register.html", methods=['post', 'get'])
def register():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        #if found in database showcase that it's found 
        user_found = find_user_username(user)
        email_found = find_user_email(email)
        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            #insert it in the record collection
            insert_user(user, email, password2)
            
            #find the new created account and its email
            user_data = find_user_email(email)
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('register.html')

#Login page
@app.route("/login.html", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        user = find_user(email, password)
        if user:
            session["email"] = "admin333@yahoo.com"
            return redirect(url_for('admin'))
            
        if user:
            session["email"] = email
            return redirect(url_for('logged_in'))
        else:
            message = 'Login failed!'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

#Logged_in page
@app.route('/logged_in.html')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))

#Admin page
@app.route('/admin.html')
def admin():
    if "email" in session:
        email = session["email"]
        return render_template('admin.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route("/signout.html", methods=["POST", "GET"])
def signout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('register.html')

if __name__ == "__main__":
    print("Initialising DB")
    db_init()
    app.run(debug=True, host='0.0.0.0', port=5000)
    print(f"Web server running on port 5000")