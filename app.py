import os
from datetime import datetime, timedelta

import psutil
from flask import Flask, render_template, send_file, request, redirect

from threads import RepeatedTimer
from timelapse import frames_to_video

# opens the config file and gets the values
with open('config.txt', 'r') as f:
	lines = f.readlines()
	config = {}
	for line in lines:
		if line[0] == '#' or line == '\n':
			continue
		key, value = line.split('=')
		config[key] = value.strip()
	config['photos_interval'] = int(config['second_interval']) + 60 * int(config['minute_interval']) + 3600 * int(
		config['hour_interval'])

assert config["abs_path"], 'Absolute path to the images is not set in config.txt'
assert config["photos_subfolder"], 'Photos subfolder is not set in config.txt'
assert config["timelapse_subfolder"], 'Timelapse subfolder is not set in config.txt'
assert config["hour_interval"], 'Photos interval is not set in config.txt'
assert config["minute_interval"], 'Photos interval is not set in config.txt'
assert config["second_interval"], 'Photos interval is not set in config.txt'
assert config["photos_interval"], 'Photos interval failed to be calculated'
assert config["hotspot_ssid"], 'Hotspot ssid is not set in config.txt'
assert config["hotspot_password"], 'Hotspot password is not set in config.txt'


def launch_captures():
	return RepeatedTimer(float(config["photos_interval"]), capture)


def capture():
	this_picture_number = get_bigger_number() + 1
	os.system("raspistill -n -o {}/{}.jpg".format(config["abs_path"] + config["photos_subfolder"],
	                                              str(this_picture_number).zfill(4)))
	# os.system("touch {}/{}.jpg".format(config["abs_path"] + config["photos_subfolder"], str(this_picture_number).zfill(4)))
	print("captured photo {}".format(this_picture_number))


def get_bigger_number():
	# reads the folder photos and returns the filename of the file with the highest number
	# if there is no file, returns 0
	bigger_number = 0
	for file in os.listdir(config["abs_path"] + config["photos_subfolder"]):
		if file.endswith(".jpg"):
			number = int(file.split('.')[0])
			if number > bigger_number:
				bigger_number = number
	return bigger_number


class HaricotApp(Flask):
	def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
		if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
			with self.app_context():
				global rt
				rt = launch_captures()
		super(HaricotApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = HaricotApp(__name__)
app.run()

# get present time on server startup
start = datetime.now()


def get_last_modified(folder=config["abs_path"] + config["photos_subfolder"]):
	# returns the last modified file in the photos directory
	files = os.listdir(folder)
	if not files:
		return None
	files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
	return folder.split("/")[-1] + "/" + files[-1]


def get_memory_left():
	# gives the amount of storage left on the computer
	# in Gigabytes, rounded to 3 decimals
	return round(psutil.disk_usage('/').free / 1024 / 1024 / 1024, 3)


def time():
	# gets the time since the start of the program
	elapsed = datetime.now() - start
	# returns the time with the format days hours minutes seconds
	elapsed = elapsed.days * 24 * 60 * 60 + elapsed.seconds
	return str(elapsed // 60 // 60) + "h " + str(elapsed // 60 % 60) + "m " + str(elapsed % 60) + "s"


@app.route('/')
def index():
	timer = timedelta(seconds=float(config["photos_interval"])) - (datetime.now() - rt.last_exec)
	timer = timer.total_seconds()
	return render_template(
		template_name_or_list='index.html',
		timer=timer,
		timeout=str(config["photos_interval"]),
		count=len(os.listdir(config["abs_path"] + config["photos_subfolder"])),
		memory_left=get_memory_left(),
		time_elapsed=time(),
		last_modified=get_last_modified(),
		filename_template=config["photos_subfolder"][1::] + "/filename.jpg")


@app.errorhandler(404)
@app.route('/404')
def error_404(e=None):
	return render_template(template_name_or_list='404.html'), 404


@app.errorhandler(500)
@app.route('/500')
def error_500(e=None):
	return render_template(template_name_or_list='500.html'), 500


@app.route('/config-hotspot')
def config_hotspot():
	return render_template(
		template_name_or_list='config-hotspot.html',
		ssid=config["hotspot_ssid"],
		password=config["hotspot_password"])


@app.route('/config-interval', methods=['POST', 'GET'])
def config_interval():
	if request.method == 'POST':
		hour_interval = request.form.get('hour_interval')
		minute_interval = request.form.get('minute_interval')
		second_interval = request.form.get('second_interval')
		config["hour_interval"] = hour_interval
		config["minute_interval"] = minute_interval
		config["second_interval"] = second_interval
		config["photos_interval"] = int(hour_interval) * 60 * 60 + int(minute_interval) * 60 + int(second_interval)
		global rt
		rt.stop()
		rt = launch_captures()
		return redirect(request.url)
	else:
		return render_template(
			template_name_or_list='config-interval.html',
			current_hour_interval=config["hour_interval"],
			current_minute_interval=config["minute_interval"],
			current_second_interval=config["second_interval"],
		)


@app.route('/photos', methods=['POST', 'GET'])
def dir_listing():
	# Return 404 if path doesn't exist
	if not os.path.exists(config["abs_path"] + config["photos_subfolder"]):
		return render_template('404.html')

	# Check if path is a file and serve
	if os.path.isfile(config["abs_path"] + config["photos_subfolder"]):
		return send_file(config["abs_path"] + config["photos_subfolder"])

	# Show directory contents
	files = sorted(os.listdir(config["abs_path"] + config["photos_subfolder"]))
	return render_template('photos.html', files=files,
	                       amount=len(os.listdir(config["abs_path"] + config["photos_subfolder"])))


@app.route('/photos/<filename>')
def render_photo(filename):
	file_path = config["abs_path"] + config["photos_subfolder"] + "/" + filename

	# Return 404 if path doesn't exist
	if not os.path.exists(file_path) or filename == '':
		return render_template('404.html')

	# Check if path is a file and serve
	if os.path.isfile(file_path):
		return send_file(file_path)

	# Show directory contents
	files = sorted(os.listdir(file_path))
	return render_template('photos.html', files=files,
	                       amount=len(os.listdir(config["abs_path"] + config["photos_subfolder"])))


@app.route('/timelapse', methods=['POST', 'GET'])
def timelapse():
	if request.method == 'POST':
		# print all the values from the form
		filename = request.form.get('timelapse_name')
		fps = request.form.get('timelapse_fps')
		interpolation = request.form.get('timelapse_interpolation')
		frames_to_video(config["abs_path"] + config["photos_subfolder"] + "/", filename, int(fps),
		                interpolation == "on")
		return redirect(request.url)
	else:
		return render_template(
			template_name_or_list='timelapse.html',
			last_timelapse=get_last_modified(config["abs_path"] + config["timelapse_subfolder"]))


@app.route('/timelapse/<filename>')
def get_time_lapse(filename):
	return send_file(config["abs_path"] + config["timelapse_subfolder"] + "/" + filename)


@app.route('/take-picture')
def take_picture():
	# asks the canon eos 2000d to take a picture and save it in the photos
	# directory, without renaming it
	capture()
	return redirect(request.url)


@app.route('/delete_photos', methods=['POST'])
def photos_delete():
	# Asks the user for confirmation with an flash message
	# and deletes the photos directory
	if request.method == 'POST':
		print("Deleting photos...")
		os.system("rm -rf " + config["abs_path"] + config["photos_subfolder"] + "/*.jpg")
		print("Photos deleted")
	else:
		print("You should not be here...")
	return redirect("/photos")


if __name__ == '__main__':
	app.run(host='0.0.0.0')
