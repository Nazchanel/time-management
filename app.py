from flask import Flask, render_template, request, redirect, url_for
from copy import deepcopy
import sqlite3

app = Flask(__name__)

tasks = []
priorities = []

logged_in_user = ""

def get_tasks_for_username(username):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    cursor.execute("SELECT task_name FROM tasks WHERE username=?", (username,))

    tasks = cursor.fetchall()
    connection.close()

    task_names = [task[0] for task in tasks]

    return task_names

def get_priority_for_username(username):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    cursor.execute("SELECT priority FROM tasks WHERE username=?", (username,))

    tasks = cursor.fetchall()
    connection.close()

    task_names = [task[0] for task in tasks]

    return task_names

def send_notification(message):
    notification.notify(
        title="To-Do Reminder",
        message=message,
        app_name='Time Management App',
        timeout=4  # Notification will stay for 10 seconds
    )

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
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (username TEXT NOT NULL, task_name TEXT NOT NULL, priority INTEGER NOT NULL, UNIQUE(username, task_name));''')
        
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
        priorities_for_username = get_priority_for_username(logged_in_user)

        tasks_and_priorities = list(zip(tasks_for_username, priorities_for_username))
        tasks_and_priorities.sort(key=lambda x: x[1], reverse=True)
        
        
        return render_template('home.html', username=logged_in_user, tasks_and_priorities=tasks_and_priorities)
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
    global priorities
    global tasks

    importance = request.form.get('Priority')
    
    importance_value = None

    if importance == 'EI':
        importance_value = 1
    elif importance == 'I':
        importance_value = 0
    else:
        importance_value = -1
        
    tasks.append(request.form.get('task'))
    priorities.append(importance_value)
    
    return redirect(url_for('task_addition'))

@app.route('/remove_task/<task>', methods=['POST'])
def remove_task(task):
    tasks.remove(task)
    return redirect(url_for('task_addition'))

@app.route('/save-tasks')
def task_save():
    global tasks
    global priorities

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (username TEXT NOT NULL, task_name TEXT NOT NULL, priority INTEGER NOT NULL, UNIQUE(username, task_name));''')

    # SQL save

    # Prepare the INSERT statement
    new_task_schema = '''
        INSERT INTO tasks(username, task_name, priority)
        VALUES (?, ?, ?);
    '''
    for i in range(len(tasks)):
        cursor.execute(new_task_schema, (logged_in_user, tasks[i], priorities[i]))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Clears Tasks after saving them to database
    tasks = []
    priorities = []
    return redirect(url_for('home'))

@app.route('/remove-tasks', methods=['GET', 'POST'])
def remove_tasks():
    if logged_in_user != '':
        return render_template('task-removal.html', string_list=get_tasks_for_username(logged_in_user))
    else:
        return render_template('login-message.html')

@app.route('/delete', methods=['POST'])
def delete():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Get the string to delete from the form
    string_to_delete = request.form['string_to_delete']
    string_list = get_tasks_for_username(logged_in_user)

    if string_to_delete in string_list:
        
        # Execute the delete query
        cursor.execute("DELETE FROM tasks WHERE username=? AND task_name=?", (logged_in_user, string_to_delete))

        # Commit the changes
        conn.commit()

        # Close the connection
        conn.close()
    return redirect(url_for('remove_tasks'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
