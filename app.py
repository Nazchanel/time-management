from flask import Flask, render_template, request, redirect

import sqlite3

app = Flask(__name__)

logged_in_user = ""

@app.route('/', methods=['GET', 'POST'])
def login():
    global logged_in_user

    conn = sqlite3.connect('user_credentials.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        password = user_details['password']

        cursor.execute('''CREATE TABLE IF NOT EXISTS user_credentials (username TEXT NOT NULL UNIQUE, password TEXT NOT NULL);''')

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
                return redirect("/home")
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
    conn = sqlite3.connect('user_credentials.db')
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
        return render_template('home.html', username = logged_in_user)
    else:
        return render_template('login-message.html')
        

    
    

if __name__ == '__main__':
    app.run(debug=True, port=8080)
