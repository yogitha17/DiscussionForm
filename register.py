import json
import mysql.connector as mysql


def checkEmail(email, config):
    db = mysql.connect(**config)
    cursor = db.cursor()
    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    data = cursor.fetchone()
    cursor.close()
    db.close()
    if data:
        return True
    else:
        return False

def registeration(data, config):
    fname = data['fname']
    lname = data['lname']
    email = data['email']
    password = data['password']
    cpassword = data['cpassword']

    if (fname == '' or lname == '' or email == '' or password == '' or cpassword == ''):
        return json.dumps({'message': 'Please fill all the fields', 'status': 'error'})
    
    elif (password != cpassword):
        return json.dumps({'message': 'Password and confirm password does not match', 'status': 'error'})
    
    # check if the email is @uwm.edu
    elif (email[email.find('@'):] != '@uwm.edu'):
        return json.dumps({'message': 'Please enter a valid UWM email', 'status': 'error'})
    
    elif (len(password) < 8):
        return json.dumps({'message': 'Password must be atleast 8 characters', 'status': 'error'})
    
    # check if the email is already registered
    elif (checkEmail(email, config)):
        return json.dumps({'message': 'Email is already registered', 'status': 'error'})
    else:
        # connect to database
        db = mysql.connect(**config)
        cursor = db.cursor()
        # insert data into database
        query = "INSERT INTO users (FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s)"
        values = (data['fname'], data['lname'], data['email'], data['password'])
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        db.close()
        return json.dumps({'message': 'Insert successful', 'status': 'success'})