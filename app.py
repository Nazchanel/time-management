from flask import Flask, render_template, request, redirect, url_for
from copy import deepcopy
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import os
import time
from threading import Thread
from plyer import notification

# If modifying these scopes, delete the file token.json.
# Google Calender API Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

tasks = []
priorities = []

logged_in_user = ""

# Global variables for remaining time
remaining_hours = 0
remaining_minutes = 0
remaining_seconds = 0

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

def get_calendar_service():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def format_datetime(datetime_str):
    # Parse the datetime string
    datetime_obj = datetime.datetime.fromisoformat(datetime_str)
    
    # Format the date as "Month Day"
    formatted_date = datetime_obj.strftime('%B %d')
    
    # Format the time in a more human-readable format
    formatted_time = datetime_obj.strftime('%I:%M %p')
    
    return f"{formatted_date} ({formatted_time})"

def get_today_events():
    service = get_calendar_service()
    now = datetime.datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Format start and end times in ISO format
    start_of_day_iso = start_of_day.isoformat() + 'Z'
    end_of_day_iso = end_of_day.isoformat() + 'Z'
    
    events_result = service.events().list(calendarId='primary', timeMin=start_of_day_iso, timeMax=end_of_day_iso,
                                          maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def send_notification(message):
    notification.notify(
        title="To-Do Reminder",
        message=message,
        app_name='Time Management App',
        timeout=4  # Notification will stay for 10 seconds
    )

# If the user has inputted a time
inputted = False
def countdown(h, m, s):
    global remaining_hours, remaining_minutes, remaining_seconds

    # Set global variables
    remaining_hours = h
    remaining_minutes = m
    remaining_seconds = s

    # Calculate the total number of seconds
    total_seconds = h * 3600 + m * 60 + s

    # While loop that checks if total_seconds reaches zero
    # If not zero, decrement total time by one second
    while total_seconds > 0:
        # Update global variables
        remaining_hours = total_seconds // 3600
        remaining_minutes = (total_seconds % 3600) // 60
        remaining_seconds = total_seconds % 60

        # Delays the program one second
        time.sleep(1)

        # Reduces total time by one second
        total_seconds -= 1

@app.route('/timer')
def timer_set():
    return render_template('timer-set.html')

@app.route('/start_timer', methods=['POST'])
def start_timer():
    global inputted
    if request.method == 'POST':
        # Get inputs from the form
        h = int(request.form['hours'])
        m = int(request.form['minutes'])
        s = int(request.form['seconds'])

        inputted = True

        # Create a thread for the countdown function
        countdown_thread = Thread(target=countdown, args=(h, m, s))
        countdown_thread.start()

    return render_template('timer.html')

@app.route('/get_remaining_time')
def get_remaining_time():
    global remaining_hours, remaining_minutes, remaining_seconds, inputted
    print(f"\n\nInputted Value: {inputted}\n\n")

    print(remaining_seconds)

    if remaining_seconds == 1 and inputted:
        send_notification("TIMER DONE")
        inputted = False
    return {
        'hours': remaining_hours,
        'minutes': remaining_minutes,
        'seconds': remaining_seconds
    }

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

        events = get_today_events()
        events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
        
        for event in events:
            event['start']['formatted'] = format_datetime(event['start'].get('dateTime', event['start'].get('date')))
        
        return render_template('home.html', username= logged_in_user, tasks_and_priorities= tasks_and_priorities, events= events)
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
        try:
            cursor.execute(new_task_schema, (logged_in_user, tasks[i], priorities[i]))
        except sqlite3.IntegrityError:
            return redirect(url_for("task_save"))
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


# Deprecated Code for testing and modification of the Google Calendar API

# @app.route('/google-cal')
# def list_events():
#     events = get_today_events()
#     events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
#     for event in events:
#         event['start']['formatted'] = format_datetime(event['start'].get('dateTime', event['start'].get('date')))
#     return render_template('events.html', events=events)

# 404 error page (invalid url)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
