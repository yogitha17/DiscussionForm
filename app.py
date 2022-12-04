from flask import Flask, render_template, request, redirect, url_for
import json
import mysql.connector as mysql
from register import registeration
from flask_login import UserMixin, login_user, current_user, LoginManager, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '3ba690099520ffabb4f49adba0769cfac42be0c4!'
login_manager = LoginManager()
login_manager.init_app(app)

# database config
config = {
    'user': 'root',
    'password': 'Yogitha@2000',
    'host': 'localhost',
    'database': 'discussionFourm',
    'raise_on_warnings': True
}

class User(UserMixin):
    pass

class IndividualUser:
    def __init__(self, id = None, username = None, email = None):
        self.id = id
        self.username = username
        self.email = email
    
    @property
    def is_authenticated(self):
        conn = mysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT * FROM Users WHERE Id = %s"
        cursor.execute(query, (self.id,))
        result = cursor.fetchall()
        conn.close()
        if len(result) > 0:
            return True
        else:
            return False
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

def get_user(id):
    conn = mysql.connect(**config)
    cursor = conn.cursor()
    query = "SELECT * FROM Users WHERE Id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    conn.close()
    if len(result) > 0:
        return IndividualUser(result[0][0], result[0][1], result[0][3])
    else:
        return None

@login_manager.user_loader
def user_loader(id):
    return get_user(id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')

    elif request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        if (email == '' or password == ''):
            return json.dumps({'message': 'Please fill all the fields', 'status': 'error'})
        else:
            db = mysql.connect(**config)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            data = cursor.fetchall()
            cursor.close()
            db.close()
            if data:
                User = IndividualUser(data[0][0], data[0][1], data[0][3])
                login_user(User, remember=True)
                
                return json.dumps({'message': 'Login successful', 'status': 'success'})
            else:
                return json.dumps({'message': 'Invalid email or password', 'status': 'error'})



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        data = request.get_json()
        return registeration(data, config)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/postQuestion', methods=['GET', 'POST'])
@login_required
def postQuestion():
    if request.method == 'GET':
        return render_template('postQuestion.html')
    elif request.method == 'POST':
        data = request.get_json()
        question = data['question']
        category = data['category']
        if (question == '' or category == ''):
            return json.dumps({'message': 'Please fill all the fields', 'status': 'error'})
        else:
            db = mysql.connect(**config)
            cursor = db.cursor()
            cursor.execute("INSERT INTO Questions (Question, Category, UserId) VALUES (%s, %s, %s)", (question, category, current_user.id))
            db.commit()
            cursor.close()
            db.close()
            return json.dumps({'message': 'Question posted successfully', 'status': 'success'})


@app.route('/getQuestions', methods=['POST'])
@login_required
def getQuestions():
    data = request.get_json()
    category = data['category']
    db = mysql.connect(**config)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Questions WHERE Category = %s", (category,))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    if len(result) > 0:
        return json.dumps({'questions': result, 'status': 'success'})
    else:
        return json.dumps({'message': 'No questions', 'status': 'error'})

@app.route('/question/<int:id>', methods=['GET', 'POST'])
@login_required
def question(id):
    if request.method == 'GET':
        return render_template('question.html')
    elif request.method == 'POST':
        data = request.get_json()
        questionId = data['questionId']
        # given id is question id and retun question and replies
        db = mysql.connect(**config)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Questions WHERE QuestionId = %s", (questionId,))
        questionResult = cursor.fetchall()
        query = "SELECT * FROM Replies WHERE QuestionId = %s"
        cursor.execute(query, (questionId,))
        repliesResult = cursor.fetchall()
        cursor.close()
        db.close()
        if len(questionResult) > 0:
            return json.dumps({'question': questionResult, 'replies': repliesResult, 'status': 'success'})
        else:
            return json.dumps({'message': 'No questions', 'status': 'error'})

@app.route('/reply', methods=['POST'])
@login_required
def reply():
    data = request.get_json()
    questionId = data['questionId']
    reply = data['reply']
    if (questionId == '' or reply == ''):
        return json.dumps({'message': 'Please fill all the fields', 'status': 'error'})
    else:
        db = mysql.connect(**config)
        cursor = db.cursor()
        cursor.execute("INSERT INTO Replies (QuestionId, reply, UserId) VALUES (%s, %s, %s)", (questionId, reply, current_user.id))
        db.commit()
        cursor.close()
        db.close()
        return json.dumps({'message': 'Reply posted successfully', 'status': 'success'})
        



if __name__ == '__main__':
    app.run(debug=True)