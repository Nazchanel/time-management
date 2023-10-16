from flask import Flask, render_template, request, redirect, url_for

import sqlite3

app = Flask(__name__)

tasks = []

logged_in_user = ""

def get_tasks_for_username(username):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    cursor.execute("SELECT task_name FROM tasks WHERE username=?", (username,))

    tasks = cursor.fetchall()
    connection.close()

    task_names = [task[0] for task in tasks]

    return task_names

@app.route('/', methods=['GET', 'POST'])
def login():
    global logged_in_user

    if request.method == "GET" and logged_in_user != "":
        logged_in_user = ""
        print("\nUser Logged Out!\n")    

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        password = user_details['password']

        cursor.execute('''CREATE TABLE IF NOT EXISTS user_credentials (username TEXT NOT NULL UNIQUE, password TEXT NOT NULL);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (username TEXT NOT NULL, task_name TEXT NOT NULL, UNIQUE(username, task_name));''')
        
        # Execute the query with placeholders
        cursor.execute("SELECT * FROM user_credentials WHERE username = ?", (username,))

        # Fetch the result
        result = cursor.fetchone()

        # Check if the result is not empty (i.e., username exists)
        if result:
            # Check if the password matches
            if result[1] == password:  # Assuming the password column is the second column (index 1)
                logged_in_user = username
                print(f"Logged in user set: {logged_in_user}")
                return redirect(url_for('home'))
            else:
                message = "Invalid password. Please try again."
                
                print(message)
                return render_template('login.html', message = message)
        else:
            message = "User does not exist. Please signup."

            print(message)

            return render_template('login.html', message = message)

    conn.close()

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Create the user_credentials table with a unique constraint on the username column
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_credentials (username TEXT NOT NULL UNIQUE, password TEXT NOT NULL);''')

    new_user_schema = '''
        INSERT INTO user_credentials(username, password)
        VALUES (?, ?);
    '''
    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        password = user_details['password']

        try:
            cursor.execute(new_user_schema, (username, password))
            conn.commit()  # Commit the changes to the database

            message = "Signup Success!"

            print("Saved to database")

            return render_template('signup.html', message = message)

        except sqlite3.IntegrityError:
            message = "Username is not available"

            print("Duplicate entry. Try again.")

            print(message)

            return render_template('signup.html', message = message)

    conn.close()  # Close the connection to the database
    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    print(f"Logged in user: {logged_in_user}")

    if logged_in_user != '':
        tasks_for_username = get_tasks_for_username(logged_in_user)
        return render_template('home.html', username=logged_in_user, tasks=tasks_for_username)
    else:
        return render_template('login-message.html')

@app.route('/tasks')
def task_addition():
    print(f"\nLogged in User when entering tasks:{logged_in_user}\n")
    
    if request.method == 'GET' and logged_in_user != "":
        return render_template('task-addition.html', tasks=tasks)
    else:
        return render_template('login-message.html')


@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form.get('task')
    tasks.append(task)
    return redirect(url_for('task_addition'))

@app.route('/remove_task/<task>', methods=['POST'])
def remove_task(task):
    tasks.remove(task)
    return redirect(url_for('task_addition'))

@app.route('/save-tasks')
def task_save():
    global tasks

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (username TEXT NOT NULL, task_name TEXT NOT NULL, UNIQUE(username, task_name));''')

    # SQL save

    # Prepare the INSERT statement
    new_user_schema = '''
        INSERT INTO tasks(username, task_name)
        VALUES (?, ?);
    '''
    for i in tasks:
        cursor.execute(new_user_schema, (logged_in_user, i))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(tasks)
    
    # Clears Tasks after saving them to database
    tasks = []

    return redirect(url_for('home'))
   
if __name__ == '__main__':
    app.run(debug=True)
