from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL, MySQLdb
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for,flash,session
import yaml
import MySQLdb.cursors  # Importing DictCursor
import os
import pymysql.cursors
import yaml
from datetime import datetime
from flask_bcrypt import Bcrypt 
# Step 1: Create the Flask app instance first
app = Flask(__name__)

# Initialize Bcrypt with your Flask application object
bcrypt = Bcrypt(app)

# Step 2: Load database configuration from a YAML file
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)

# Configure the application with database settings
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_PORT'] = db.get('mysql_port', 3306)

# Set a secret key from environment or default to 'default_secret_key'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Step 3: Initialize MySQL with the configured app
mysql = MySQL(app)
def get_username_from_session():
    return session.get('username')
def get_usernid_from_session():
    return session.get('user_id')
@app.route('/')
def index():
    # Check if user is logged in
    if 'username' in session:
        return redirect(url_for('user_profile', username=session['username']))
    else:
        return redirect(url_for('login'))
@app.route('/catalog')
def catalog():
    try:
        # Using the connection from flask_mysqldb
        cur = mysql.connection.cursor()
        # Fetch books from the database
        sql = "SELECT BookID, Title, ImageURL FROM Books"
        cur.execute(sql)
        books = cur.fetchall()  # Fetch all books
        cur.close()  # Close the cursor
    finally:
        print("Connection Established and sending data to Home Page")
    
    return render_template('home.html', books=books)  # Pass books as plural variable


@app.context_processor
def inject_user():
    return {'get_username_from_session': get_username_from_session}

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out.', 'info')
    # Redirect to the login page or home page
    return redirect(url_for('login'))
@app.route('/book/<int:book_id>')
def book_details(book_id):
    cursor = mysql.connection.cursor()
    try:
        # Prepare SQL query to fetch book details along with associated data
        sql = """
        SELECT 
            B.BookTitle, B.AuthorName, B.PublisherName, B.PublicationDate, B.Description, B.AverageRating, BR.UserRating, B.GenreName, B.ImageURL
        FROM 
            BookDetailsPageView B LEFT JOIN BookDetailsWithLatestRating BR ON B.BookID = BR.BookID
        WHERE 
            B.BookID = %s
        """
        cursor.execute(sql, (book_id,))
        book = cursor.fetchone()  # Fetch a single book
        
        # Fetch reviews
        review_sql = "SELECT ReviewContent FROM Reviews WHERE BookID = %s;"
        cursor.execute(review_sql, (book_id,))
        reviews = cursor.fetchall()  # Fetch all reviews for the book

    finally:
        cursor.close()  # Ensure the cursor is closed after operation
        print("Book details fetched successfully.")

    return render_template('book_details.html', book=book, reviews=reviews,book_id=book_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        email = userDetails['email']
        password = userDetails['password']  
        bio=userDetails['bio']

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        print("I NEED THIS:\n", hashed_password)

        cur = mysql.connection.cursor()
        # Check if the username or email already exists
        cur.execute("SELECT * FROM Users WHERE username = %s", [username])
        if cur.fetchone():
            cur.close()
            return render_template('register.html', error="Username already taken. Please choose another one.")

        cur.execute("SELECT * FROM Users WHERE email = %s", [email])
        if cur.fetchone():
            cur.close()
            return render_template('register.html', error="Email already registered. Please use another email or log in.")

        # If both the username and email are unique, proceed with registration
        cur.execute("INSERT INTO Users(username, email, password,bio) VALUES(%s, %s, %s,%s)", (username, email, hashed_password,bio))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        password = userDetails['password']  # This should be hashed and checked against a hash in a real app
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM Users WHERE username = %s", (username,))
        if resultValue > 0:
            user = cur.fetchone()
            print(user)
            cur.close()
            # Get Database stored DB
            if bcrypt.check_password_hash(user[3], password):  # This is a placeholder; in reality you'd use password hashing
                session['username'] = username
                session['user_id'] = user[0]
                return redirect(url_for('user_profile', username=username))
            else:
                # Incorrect password
                error = 'Incorrect username or password'
        else:
            # Username not found
            error = 'Incorrect username or password'
        cur.close()
    else:
        error = None

    return render_template('login.html', error=error)

@app.route('/followers/<username>')
def view_followers(username,message=None):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT UserID FROM Users WHERE Username = %s", [username])
    user = cur.fetchone()

    # Followers
    cur.execute("""
        SELECT Users.UserID, Users.Username
        FROM Followers
        JOIN Users ON Followers.FollowerID = Users.UserID
        WHERE Followers.FollowingID = %s
    """, [user['UserID']])
    followers = cur.fetchall()

    # Followings
    cur.execute("""
        SELECT Users.UserID, Users.Username
        FROM Followers
        JOIN Users ON Followers.FollowingID = Users.UserID
        WHERE Followers.FollowerID = %s
    """, [user['UserID']])
    followings = cur.fetchall()
    cur.close()

    return render_template('followers.html', username=username, followers=followers, followings=followings,message=message)

@app.route('/delete_book/<int:book_id>/<list_type>', methods=['POST'])
def delete_book(book_id, list_type):
    # Map list_type to actual table names
    table_mapping = {
        'currently_reading': 'UserCurrentlyReading',
        'to_read': 'UserBooksToRead',
        'read': 'UserBooksRead'
    }

    # Get the actual table name from the mapping
    table_name = table_mapping.get(list_type)
    if not table_name:
        flash("Invalid book list type specified.", "error")
        return redirect(url_for('user_profile', username=get_username_from_session()))

    # Continue with deletion using the correct table name
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT UserID FROM Users WHERE Username = %s", [get_username_from_session()])
    user = cur.fetchone()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('login'))

    user_id = user['UserID']

    # Execute deletion with the correct table name
    cur.execute(f"DELETE FROM {table_name} WHERE UserID = %s AND BookID = %s", (user_id, book_id))
    mysql.connection.commit()
    cur.close()

    flash('Book removed successfully!', 'success')
    return redirect(url_for('user_profile', username=get_username_from_session()))

@app.route('/profile/<username>')
def user_profile(username):
    if not username:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Initialize all variables to ensure they are defined
    profile_details = None
    
    # Fetch user profile details including reading lists and follower counts
    cur.execute("SELECT * FROM UserProfileView WHERE Username = %s", [username])
    profile_details = cur.fetchone()
    currently_reading = []
    read = []
    to_read = []
    follower_count = 0
    following_count = 0

    if profile_details:
        user_id = profile_details['UserID']
        follower_count = profile_details['FollowerCount']
        following_count = profile_details['FollowingCount']
                # Update follower and following counts
        cur.execute("""
            UPDATE Users
            SET FollowerCount = (SELECT COUNT(*) FROM Followers WHERE FollowingID = %s),
                FollowingCount = (SELECT COUNT(*) FROM Followers WHERE FollowerID = %s)
            WHERE UserID = %s
        """, (user_id, user_id, user_id))
        mysql.connection.commit()
        # Fetch currently reading books
        cur.execute("""
            SELECT Books.BookID, Books.Title, UserCurrentlyReading.StartDate
            FROM UserCurrentlyReading
            JOIN Books ON UserCurrentlyReading.BookID = Books.BookID
            WHERE UserCurrentlyReading.UserID = %s
        """, [user_id])
        currently_reading = cur.fetchall()

        # Fetch books read
        cur.execute("""
            SELECT Books.BookID, Books.Title, UserBooksRead.DateAdded
            FROM UserBooksRead
            JOIN Books ON UserBooksRead.BookID = Books.BookID
            WHERE UserBooksRead.UserID = %s
        """, [user_id])
        read = cur.fetchall()

        # Fetch books to read
        cur.execute("""
            SELECT Books.BookID, Books.Title, UserBooksToRead.DateAdded
            FROM UserBooksToRead
            JOIN Books ON UserBooksToRead.BookID = Books.BookID
            WHERE UserBooksToRead.UserID = %s
        """, [user_id])
        to_read = cur.fetchall()

    cur.close()
    
    # Pass all lists, follower, and following counts to the template
    return render_template('user_profile.html', 
                           profile=profile_details, 
                           currently_reading=currently_reading, 
                           read=read, 
                           to_read=to_read,
                           follower_count=follower_count,
                           following_count=following_count,
                           username=username)

@app.route('/add-follower-by-username', methods=['POST'])
def add_follower_by_username():
    session_username = get_username_from_session()
    if not session_username:
        flash("You must be logged in to follow someone.", "error")
        return redirect(url_for('login'))

    following_username = request.form.get('following_username')

    # Prevent users from following themselves
    if session_username == following_username:
        flash("You cannot follow yourself.", "error")
        return redirect(url_for('view_followers', username=session_username))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch session user's ID
    cur.execute("SELECT UserID FROM Users WHERE Username = %s", [session_username])
    session_user = cur.fetchone()

    # Fetch following user's ID
    cur.execute("SELECT UserID FROM Users WHERE Username = %s", [following_username])
    following_user = cur.fetchone()

    if session_user and following_user:
        # Check if the following relationship already exists
        cur.execute("SELECT * FROM Followers WHERE FollowerID = %s AND FollowingID = %s",
                    (session_user['UserID'], following_user['UserID']))
        existing_follow = cur.fetchone()

        # If not, create the following relationship
        if not existing_follow:
            cur.execute("INSERT INTO Followers (FollowerID, FollowingID, DateFollowed) VALUES (%s, %s, CURDATE())",
                        (session_user['UserID'], following_user['UserID']))
            mysql.connection.commit()
            flash("You are now following {}.".format(following_username), "success")
        else:
            flash("You are already following {}.".format(following_username), "info")

    cur.close()

    # Redirect to the followers page of the current session user
    return redirect(url_for('view_followers', username=session_username))
@app.route('/wantread', methods=['POST'])
def wantread():
    user_id = get_usernid_from_session()  # Assuming this is a hardcoded user ID for demonstration
    data = request.json
    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO UserBooksToRead (UserID, BookID, DateAdded) VALUES (%s, %s, NOW())"
        cur.execute(sql, (user_id, data.get("id")))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data added to UserBooksToRead'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/readit', methods=['POST'])
def readit():
    user_id = get_usernid_from_session()
    data = request.json
    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO UserBooksRead (UserID, BookID, DateAdded) VALUES (%s, %s, NOW())"
        cur.execute(sql, (user_id, data.get("id")))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data added to UserBooksRead'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/currentread', methods=['POST'])
def currentread():
    user_id = get_usernid_from_session()
    data = request.json
    try:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO UserCurrentlyReading (UserID, BookID, StartDate) VALUES (%s, %s, NOW())"
        cur.execute(sql, (user_id, data.get("id")))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Data added to UserCurrentlyReading'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reviewsContent', methods=['POST'])
def reviewsContent():
    data = request.json
    book_id = data.get("id")
    try:
        cur = mysql.connection.cursor()
        sql = "SELECT ReviewContent FROM Reviews WHERE BookID = %s;"
        cur.execute(sql, [book_id])
        rows = cur.fetchall()
        comments = [row[0] for row in rows]
        cur.close()
        print(comments)  # Print comments to debug
        return jsonify({'dataReviews': {'comments': comments}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/addComment', methods=['POST'])
def addComment():
    # Your code to get the user ID goes here
    user_id = get_usernid_from_session()
    print(user_id)
    # Now retrieve the form data
    book_id = request.form.get('book_id')
    new_comment = request.form.get('newComment')
    print(new_comment,book_id)
    if user_id and book_id and new_comment:
        try:
            cur = mysql.connection.cursor()
            sql = "INSERT INTO Reviews (UserID, BookID, ReviewContent, ReviewDate) VALUES (%s, %s, %s, NOW())"
            cur.execute(sql, (user_id, book_id, new_comment))
            mysql.connection.commit()
            flash('Comment added successfully', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Failed to add comment: {e}', 'error')
        finally:
            cur.close()
    else:
        flash('Missing information for adding a comment.', 'error')
    
    return redirect(request.referrer)

@app.route('/userrating', methods=['POST'])
def userrating():
    user_id = get_usernid_from_session()
    book_id = request.form.get('book_id')
    user_rating = request.form.get('user_rating')
    print(user_rating," | ",book_id," | ",user_id)
    if user_id and book_id and user_rating:
        try:
            user_rating = float(user_rating)
            if not (0 <= user_rating <= 5):
                raise ValueError("Rating must be between 0 and 5.")
            cur = mysql.connection.cursor()
            sql = "INSERT INTO Ratings (UserID, BookID, Rating, RatingDate) VALUES (%s, %s, %s, NOW())"
            cur.execute(sql, (user_id, book_id, user_rating))
            mysql.connection.commit()
            flash('Rating added successfully', 'success')
        except ValueError as ve:
            flash(f'Invalid rating value: {ve}', 'error')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Failed to add rating: {e}', 'error')
        finally:
            cur.close()
    else:
        flash('Missing information for adding a rating.', 'error')

    return redirect(request.referrer)


@app.route('/updateuserrating', methods=['POST'])
def updateuserrating():
    user_id = get_usernid_from_session()
    data = request.get_json()
    book_id =data['id']
    user_rating = data['userRate']
    print(user_rating," | ",book_id," | ",user_id)
    try:
        user_rating = float(user_rating)
        # if not (0 <= user_rating <= 5):
        #     raise ValueError("Rating must be between 0 and 5.")
        cur = mysql.connection.cursor()
        sql = "SELECT Rating FROM Ratings WHERE UserID = %s AND BookID = %s"
        cur.execute(sql, (user_id, book_id))
        existing_rating = cur.fetchone()
        if existing_rating:
            # Update rating
            sql = "UPDATE Ratings SET Rating = %s WHERE UserID = %s AND BookID = %s"
            cur.execute(sql, (user_rating, user_id, book_id))
            mysql.connection.commit()
            flash('Rating updated successfully', 'success')
        else:
            # Insert new rating
            sql = "INSERT INTO Ratings (UserID, BookID, Rating) VALUES (%s, %s, %s)"
            cur.execute(sql, (user_id, book_id, user_rating))
            mysql.connection.commit()
            flash('Rating added successfully', 'success')
    except ValueError as ve:
        flash(f'Invalid rating value: {ve}', 'error')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Failed to add/update rating: {e}', 'error')
    finally:
        cur.close()

    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(debug=True)
