from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
 
app.secret_key = '3ba690099520ffabb4f49adba0769cfac42be0c4!'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yogitha@2000'
app.config['MYSQL_DB'] = 'discussionFourm'
 
mysql = MySQL(app)

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

@app.route('/', methods=['GET', 'POST'])
def login():
     msg = ''
     if request.method == 'POST' and 'username' in request.form and 'passname' in request.form:
        # Create variables for easy access
        username = request.form['username']
        passname = request.form['passname']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND passname = %s', (username, passname,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
     return render_template('index.html', msg='')

@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'passname' in request.form and 'email' in request.form and 'fname' in request.form and 'lname' in request.form:
        # Create variables for easy access
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        password = request.form['passname']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not fname or not lname:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (fname,lname,email, username, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/home', methods = ['GET','POST'])
def comment():
    message = ''
    if request.method == 'POST' and 'category' in request.form and 'comments' in request.form and 'loggedin' in session:
        # Create variables for easy access
        category = request.form['category']
        comments = request.form['comments']
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        uid = account['id']
        name = account['username']
        if(category==0):
            message = "Please select a category"
        elif not comments:
            message = "Post field cannot be empty"
        else:
            cursor.execute('INSERT INTO post VALUES (NULL, %s, %s, %s, %s)', (uid,name,category,comments))
            mysql.connection.commit()
            message = 'You have posted successfully!!'
        # Show the profile page with account info
    # User is not loggedin redirect to login page
    return render_template('home.html', message=message,account=account)

@app.route('/userpost', methods = ['GET','POST'])
def userpost():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where id = %s', (session['id'],))
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('userpost.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/allpost', methods = ['GET'])
def allpost():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post')
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('allpost.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/house', methods = ['GET','POST'])
def house():
    # Check if user is loggedin
    if request.method == 'POST' and 'Housing' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        Housing = request.form['Housing']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where category = %s', (Housing,))
        account = cursor.fetchall()
        cursor.execute('SELECT * FROM reply where category = %s', (Housing,))
        rhouse = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('house.html', account=account, rhouse=rhouse)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/visa', methods = ['GET','POST'])
def visa():
    # Check if user is loggedin
    if request.method == 'POST' and 'Visa' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        Visa = request.form['Visa']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where category = %s', (Visa,))
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('visa.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/travel', methods = ['GET','POST'])
def travel():
    # Check if user is loggedin
    if request.method == 'POST' and 'Travel' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        Travel = request.form['Travel']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where category = %s', (Travel,))
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('travel.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/courses', methods = ['GET','POST'])
def courses():
    # Check if user is loggedin
    if request.method == 'POST' and 'Courses' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        Courses = request.form['Courses']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where category = %s', (Courses,))
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('courses.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/others', methods = ['GET','POST'])
def others():
    # Check if user is loggedin
    if request.method == 'POST' and 'Others' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        Others = request.form['Others']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post where category = %s', (Others,))
        account = cursor.fetchall()    
        # Show the profile page with account info
        return render_template('others.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
		
@app.route('/postupdate', methods = ['GET','POST'])
def postupdate():
    succ = ''
    # Check if user is loggedin
    if request.method == 'POST' and 'postid' in request.form and 'comments' in request.form and 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        postid = request.form['postid']
        comments = request.form['comments']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('update post SET comments=%s where postid=%s',(comments,postid,))
        account = cursor.fetchall() 
        mysql.connection.commit()   
        succ = "Your post is been updated successfully!!!"
        return render_template('postupdate.html', succ=succ, account=account)
        # Show the profile page with account info
    # User is not loggedin redirect to login page
    
@app.route('/replyhouse', methods = ['GET','POST'])
def replyhouse():
    message = ''
    if request.method == 'POST' and 'postid' in request.form and 'comments' in request.form and 'loggedin' in session:
        # Create variables for easy access
        postid = request.form['postid']
        comments = request.form['comments']
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        uid = account['id']
        name = account['username']
        cursor.execute('SELECT * FROM post where postid = %s', (postid,))
        preply = cursor.fetchone()
        pcategory = preply['category']
        cursor.execute('INSERT INTO reply VALUES (NULL, %s, %s, %s, %s, %s)', (postid,uid,name,pcategory,comments))
        mysql.connection.commit()
        message = 'You have replied successfully!!'
        # Show the profile page with account info
    # User is not loggedin redirect to login page
    return render_template('replyhouse.html', message=message,account=account)


        
if __name__ == "__main__":
    app.run()