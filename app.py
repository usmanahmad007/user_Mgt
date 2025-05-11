from flask import Flask, request, render_template, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'secret_key'
DATA_FILE = 'users.txt'

# --------- Helper Functions ---------
def read_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)



def write_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)



def authenticate(email, password):
    users = read_users()
    user = users.get(email)
    return user and user['password'] == password

# --------- Routes ---------



@app.route('/')
def main():
    return render_template('main.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        age = request.form['age']
        password = request.form['password']

        users = read_users()
        if email in users:
            return render_template('register.html', message="User already exists.")
        users[email] = {'email': email, 'age': age, 'password': password}
        write_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if authenticate(email, password):
            session['email'] = email
            return redirect(url_for('home'))
        else:
            return render_template('login.html', message="Invalid credentials.")
    return render_template('login.html')




@app.route('/home')
def home():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    users = read_users()
    user = users.get(email)
    return render_template('home.html', user=user)




@app.route('/update', methods=['POST'])
def update():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    new_age = request.form.get('age')
    new_password = request.form.get('password')

    users = read_users()
    if new_age:
        users[email]['age'] = new_age
    if new_password:
        users[email]['password'] = new_password
    write_users(users)
    flash('User information updated successfully!')
    return redirect(url_for('home'))



@app.route('/delete', methods=['POST'])
def delete():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    users = read_users()
    users.pop(email, None)
    write_users(users)
    session.clear()
    return redirect(url_for('main'))




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

# --------- API Routes ---------




@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    email = data.get('email')
    age = data.get('age')
    password = data.get('password')

    if not email or not age or not password:
        return "Missing data", 400

    users = read_users()
    if email in users:
        return "User already exists", 400

    users[email] = {'email': email, 'age': age, 'password': password}
    write_users(users)
    return "User added successfully", 201




@app.route('/get_user/<email>', methods=['GET'])
def get_user(email):
    users = read_users()
    user = users.get(email)
    if not user:
        return "User not found", 404
    return json.dumps(user), 200




@app.route('/update_user/<email>', methods=['PUT'])
def update_user(email):
    data = request.get_json()
    new_age = data.get('age')
    new_password = data.get('password')

    users = read_users()
    user = users.get(email)
    if not user:
        return "User not found", 404

    if new_age:
        users[email]['age'] = new_age
    if new_password:
        users[email]['password'] = new_password

    write_users(users)
    return "User updated successfully", 200




@app.route('/delete_user/<email>', methods=['DELETE'])
def delete_user(email):
    users = read_users()
    if email not in users:
        return "User not found", 404

    users.pop(email, None)
    write_users(users)
    return "User deleted successfully", 200



if __name__ == '__main__':
    app.run(debug=True)
