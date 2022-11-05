import os
import uuid
import psycopg2

from hashlib import md5
from flask import render_template, url_for, flash, redirect, request, session, Blueprint
from flask_login import login_user, logout_user, UserMixin

auth = Blueprint('auth', __name__)

# connect to database
def get_db_connection():
    conn = psycopg2.connect(
            host='database',
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])
    return conn

# prevent attribute in form POST have elements in blacklist:
def is_safe(blacklist:list, attributes:list):
    for element in blacklist:
        for attribute in attributes:
            if element in attribute:
                return False
    return True

class User(UserMixin):
    pass

# Function: sign in
@auth.route('/signin',methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if is_safe([';'], [username, password]) == False:
            flash('Please don\'t hack :\'(', 'danger')
            return redirect(url_for('auth.signin'))  

        conn = get_db_connection()
        cur = conn.cursor()
        signin_check = 1
        try:
            password = md5(password.encode()).hexdigest()
            cur.execute('PREPARE login(varchar, varchar) AS SELECT * FROM users '
                        'WHERE username = $1 AND password = $2;')
            cur.execute('EXECUTE login($param_1${}$param_1$, '
                        '$param_2${}$param_2$);'.format(username, password))
            result = cur.fetchone()
            signin_check = (result != None)      
        except psycopg2.Error as e:
            print(e)
            signin_check = 0

        cur.close()
        conn.close()

        if signin_check:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('indexHandler'))

        flash('Wrong username or password. Please try again.', 'danger')
        return redirect(url_for('auth.signin'))
    return render_template('signin.html')        


# Function: sign up
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        verifycode = request.form.get('verifycode')

        if is_safe([';'], [username, password, fullname, phone, email, verifycode]) == False:
            flash('Please don\'t hack :\'(', 'danger')
            return redirect(url_for('auth.signup'))  
        
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute('SELECT id FROM verifycode WHERE code = $param_1${}$param_1$;'.format(verifycode))
            existing_code = cur.fetchone()
            if not existing_code:
                flash('Invalid verify code.', 'danger')
                return redirect(url_for('auth.signup'))

            cur.execute('SELECT username FROM users WHERE username = $param_1${}$param_1$;'.format(username))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username {} already exists.'.format(existing_user[0]), 'warning')
                return redirect(url_for('auth.signup'))
            
            password = md5(password.encode()).hexdigest()
            cur.execute('PREPARE register(varchar, varchar, varchar, varchar, varchar, int) ' 
                        'AS INSERT INTO users (username, password, fullname, phone, email, verifycode) '
                        'VALUES($1, $2, $3, $4, $5, $6);')
            cur.execute('EXECUTE register($param_1${}$param_1$, $param_2${}$param_2$, $param_3${}$param_3$,'
                        '$param_4${}$param_4$, $param_5${}$param_5$, $param_6${}$param_6$);'.format(username, 
                        password, fullname, phone, email, existing_code[0]))
            
        except psycopg2.Error as e:
            print(e)
            flash('Registration failed', 'danger')
            return redirect(url_for('auth.signup')) 

        conn.commit()
        cur.close()
        conn.close()

        flash('Registration completed', 'success')
        return redirect(url_for('auth.signup')) 
    return render_template('signup.html')

# Function: log out
@auth.route('/logout')
def logout():
    logout_user()
    return redirect( url_for('indexHandler'))

# Function: Forgot password 
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot():
	if 'login' in session:
		return redirect(url_for('/'))
	if request.method == 'POST':
		email = request.form['email']
		if ';' in email:
			flash('Please don\'t hack :\'(', 'danger')
			return redirect(url_for('auth.forgot')) 
        # Gen token
		token = str(uuid.uuid4())
		conn =  get_db_connection()
		cur = conn.cursor()
        # Check mail's exist
		cur.execute("""SELECT email FROM users WHERE email='%s'""" % email)
		result = cur.fetchone() 
		if result is not None:
			cur = conn.cursor()
            # Set token for user's account have 'that' email
			cur.execute('UPDATE users SET token=%s WHERE email=%s', [token, email])
			conn.commit()
			cur.close()
			conn.close()
            
			flash('Token already sent to your email', 'success')
			return redirect(url_for('auth.forgot'))
		else:
			flash('Email does not match', 'danger')
		conn.close()
	return render_template('forgot-password.html')


# Function: Reset password
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if 'login' in session:
		return redirect(url_for('/'))
	if request.method == 'POST':
		password = request.form['password']
		confirm_password = request.form['confirm_password']
        # Confirm password
		if password != confirm_password:
			flash('Password does not match', 'danger')
			return redirect(url_for('auth.reset_password'))

		password = md5(password.encode()).hexdigest()
		conn = get_db_connection()
		cur = conn.cursor()
        # Check mail's exist
		cur.execute('SELECT * FROM users where token=%s', [token])
		user = cur.fetchone()
  
		if user:
			cur = conn.cursor()
            # Update password for user's account have 'that' email
			cur.execute('UPDATE users SET token=NULL, password=%s WHERE token=%s', [password, token])
			conn.commit()
    
			cur.close()
			conn.close()
			flash('Your password successfully updated', 'success')
			return redirect(url_for('auth.signin'))

		else:
			flash('Your token is invalid', 'danger')
			return redirect('/')

	return render_template('reset-password.html')
