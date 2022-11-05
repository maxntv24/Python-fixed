import os
import psycopg2
from flask import Flask, render_template, request, send_file, abort, flash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, current_user 

# user define
import database
from utils import *
from auth.routes import auth

# INIT 
app = Flask(__name__)
app.secret_key = "#@yGcXWZq54Z5Y*gvTvVKrU+a8p@cmxEguDM6I@g&Qx^j@"
login_manager = LoginManager()
login_manager.init_app(app)
database.init()
app.register_blueprint(auth)


# GLOBAL VARIABLES
HOST = '0.0.0.0'
PORT = '1337'
BASE_DIR = '/app'
BASE_UPLOAD_PATH = '/app/upload/'
BASE_UNZIP_PATH = '/app/upload/unzip/'
RANDOM_LENGTH = 48

# Session management
class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
	conn = psycopg2.connect(
			host='database',
			database=os.environ['POSTGRES_DB'],
			user=os.environ['POSTGRES_USER'],
			password=os.environ['POSTGRES_PASSWORD'])
	cur = conn.cursor()
	cur.execute('SELECT username FROM users WHERE username = %s;', [username])
	result = cur.fetchone()

	cur.close()
	conn.close()

	if result == None:
		return

	user = User()
	user.id = username
	return user

# Router
@app.route('/')
def indexHandler():
	if current_user.is_authenticated:
		if current_user.id == 'fl4g':
			flash('Welcom fl4g, GoOd 3XPLo1T!! ٩( ᐛ )و', 'success')
	data = database.get_crypto_info()	
	return render_template('index.html', data = data)

@app.route('/about')
def aboutHandler():
	return render_template('about.html')

@app.route('/services')
def serviceHandler():
	return render_template('services.html')

@app.route('/upload', methods = ['POST'])
def uploadHandler():
	if request.files['file']:
		file = request.files['file']
		if file.filename and allowed_file(file.filename):
			file.filename = secure_filename(file.filename)
			if not check_filename(file.filename):
				return "Oh no no no"
				
			unique_id = get_random_string(RANDOM_LENGTH)

			upload_path = path.join(BASE_UPLOAD_PATH, unique_id)
			makedirs(upload_path)
			uploaded_file = path.join(upload_path, file.filename)

			file.save(uploaded_file)
			if file.filename[-3:] == "zip":
				unzip_path = path.join(BASE_UNZIP_PATH, unique_id)
				makedirs(unzip_path)
				print(uploaded_file)
				system("unzip {0} -d {1}".format(uploaded_file, unzip_path))
				unzip_path = unzip_path.replace('/app', '')
				return "File is unzip-ed to <a href='" + unzip_path + "'>" + unzip_path + "</a>"
			uploaded_file = uploaded_file.replace('/app', '')
			return "File is uploaded: " + uploaded_file
	return "No file to be uploaded (txt and zip only)"

@app.route('/getData', methods=['GET'])
def getLog():
	name = ['auto.txt', 'ctf.txt', 'flask.txt', 'python.txt', 'stock_market.txt' ]
	if request.args.get('f') not in name:
		return ({'status': 'invalid path'},200)
	else:
		log_file = '/app/fus/data/' + request.args.get('f')
		return send_file(log_file, mimetype='text/plain', as_attachment=False)

# run script to crawl data
@app.route('/runScript', methods=['POST'])
def runScript():
	json = request.json
	msg = start(json)
	return ({'status': msg},200)

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def directory_index(req_path):
	abs_path = path.join(BASE_DIR, req_path)
	if not path.exists(abs_path):
		return abort(404)
	if path.isfile(abs_path):
		abs_path = abs_path.replace('..', '')
		return send_file(abs_path)
	files = listdir(abs_path)
	return render_template('files.html', files=files)


if __name__ == '__main__':
	app.run(HOST, PORT)
