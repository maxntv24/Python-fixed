import re
import urllib
import requests
import subprocess
from os import path, makedirs, system, listdir, popen
from string import ascii_lowercase
from random import choice


HOME = path.dirname(path.realpath(__file__))
ALLOWED_EXTENSIONS = ['txt', 'zip']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.')[-1].lower() in ALLOWED_EXTENSIONS

def get_random_string(length):
    letters = ascii_lowercase
    result_str = ''.join(choice(letters) for i in range(length))
    return result_str

def check_filename(filename):
	pattern = re.compile(r'[^a-zA-Z0-9\.-]+')
	return (not pattern.findall(filename))

def check_script_dup(scripts, command_log, json):
	try:
		### fix rce
		script_parent_dir = scripts + '/' + json['dir']
		if not check_filename(json['dir']):
				return "Oh no no no"
		script_path = script_parent_dir + '/' + json['name']
		if not check_filename(json['name']):
				return "Oh no no no"
	except:
		return "missing dir and name"
	if path.exists(script_path):
		return "duplicate script"
	else:
		if not path.exists(script_parent_dir):
			makedirs(script_parent_dir)
		return download_script(script_path, command_log, json)

def download_script(script_path, command_log, json):
	try:
		script_link = json['url']
	except:
		return "missing url"
	# don't trust anyone
	if (urllib.parse.urlparse(script_link).netloc == "localhost:1337"):
		result = requests.get(script_link)
		with open(script_path, 'wb') as f:
			f.write(result.content)
			run_script(script_path, command_log)
	else:
		return "invalid script link"

def run_script(script_path, command_log):
	lf = open(command_log, 'wb+')
	print('comand',command_log)
	command = subprocess.Popen(['bash','-c', script_path], stderr=lf, stdout=lf, universal_newlines=True)
	return "Run successfully"

def start(json):
	scripts = HOME + '/scripts' 
	log = HOME + '/logs' 
	if not path.exists(scripts):
		makedirs(scripts)
	if not path.exists(log):
		makedirs(log)
	try:
		command_log = log + '/' + json['command_log'] + '.txt' 
	except:
		return "missing command_log"
	msg = check_script_dup(scripts, command_log, json)
	return msg
	
def remove_symlink(path):
	list_sl = popen("symlinks -rv "+path).read()
	list_sl = list_sl.split(chr(10)) 
	array_sl = [] 
	list_slname = []
	for i in list_sl: 
		array_sl.append(i.split()) 
	for i in range(len(array_sl) - 1): 
		list_slname.append(array_sl[i][1]) 
	print(list_slname) 
	for i in list_slname: 
		system("rm " + i)
	return len(list_slname)