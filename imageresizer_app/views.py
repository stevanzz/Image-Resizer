from django.shortcuts import render
from django.http import HttpResponse
import httpagentparser, requests
import PIL, redis, json
from PIL import Image
import shutil, os, time, re
import hashlib, base64

r = redis.Redis('localhost')
#r.flushall()

def redisNaming(file_name, width, height):
	if (width == "default") and (height == "default"):
		if "." in file_name:
			redis = file_name.split(".")[0]
		else:
			redis = file_name
	else:
		if "." in file_name:
			file_name = file_name.split(".")[0]
		redis = file_name + " {0}x{1}".format(width, height)
	return redis

def get_most_frequest_color(rgb_im, width, height):
	pixels = rgb_im.getcolors(width * height)
	most_frequent_pixel = pixels[0]
	for count, colour in pixels:
		if count > most_frequent_pixel[0]:
			most_frequent_pixel = (count, colour)
	return most_frequent_pixel[1]

def find_rows_with_color(pixels, width, height, bg_color):
	rows_found=[]
	for y in xrange(height):
		obj = 0
		for x in xrange(width):
			if str(pixels[x, y]) == str(bg_color):
				obj += 1
		avg = (float(obj)/float(width))
		if (avg > 0.95):
			rows_found.append(y)
	return rows_found

def crop_empty(new_file):
	path = os.path.join(os.path.dirname(__file__), "static/images/%s" %new_file)
	image = Image.open(path)
	rgb_im = image.convert('RGB')
	pixels_old = rgb_im.load()
	width, height = image.size
	# Get most frequent color
	bg_color = get_most_frequest_color(rgb_im, width, height)
	# Get list of rows to be removed
	rows_to_remove = find_rows_with_color(pixels_old, width, height, bg_color)
	# Give spaces at the top of image
	line = int(float(width)*30/100)
	try:
		for i in range(line):
			rows_to_remove.pop()
	except:
		pass
	# Create new image
	new_im = Image.new('RGB', (width, height - len(rows_to_remove)))
	pixels_new = new_im.load()
	rows_removed = 0
	# Replace object in old image to new image
	for y in range(height):
		if y not in rows_to_remove:
			for x in range(width):
				pixels_new[x, y - rows_removed] = pixels_old[x, y]
		else:
			rows_removed += 1
	new_im.save(path)

#SCALE DOWN A PICTURE WITH A BASEWIDTH
def scale_down(new_file, width, height):
	path = os.path.join(os.path.dirname(__file__), "static/images/%s" %new_file)
	img = Image.open(path)
	if width != "default":
		width = int(width)
		wpercent = (width/float(img.size[0]))
		if height != "default":
                        height = int(height)
		else:
			# if height is not specified, it resized based on the width
			height = int((float(img.size[1])*float(wpercent)))
		img = img.resize((width,height), PIL.Image.ANTIALIAS)
	if img.mode == "CMYK":
		img.convert("RGB").save(path)
	else:
		img.save(path)
			
def userAgent(user_agent):
	browser = user_agent[1]				# getting the user agent
#	browser = 'Chrome 51.0.2704.106'
        searchObj = re.search(r'(\w+).*', browser)	# regex for getting the name of the browser
        browser_name = searchObj.group(1)
	return browser_name

def setFileType(browser, url, file_name):
	file_type = None
	matchObj = re.match(r'(.*)\?(webp)', url)
	try:
		if "webp" in matchObj.group(2):
                        file_type = "WEBP"
 	except:
		# set file_type as WEBP if opened by Chrome
	        if (browser == "Chrome") or (browser == "ChromeiOS"):
	                file_type = "WEBP"
	       	# initialize file_type if there is no file_type set
	        elif "." in file_name:
	                file_type = file_name.split(".")[-1]
	                if file_type == "jpeg":
	                        file_type = "jpg"
	        # initialize file_type if file_type is not given
	        elif file_type == None:
	                file_type = "jpg"
	return file_type

def urlParser(url, user_agent, file_name):
	width = height = "default"
	url = url[3:]	# get the real url, starts from char number 3
	browser = userAgent(user_agent)
	# rename https to http to avoid error[NOT IMPORTANT]
	if re.match(r'https', url):
		url = "http"+url[5:]
	# in case the url doest not begin with "http://"
	elif not re.match(r'^http://', url):
		url = "http://"+url
	# remove unicode characters
	if isinstance(url, unicode):
		url = url.encode('ascii', errors='ignore')
	# get file_type	
	file_type = setFileType(browser, url, file_name)
	# crop background
        crop = False
        matchObj1 = re.match(r'(.*)\?cropempty=(True|False)', url)
        try:
                if "True" in matchObj1.group(2):
                        crop = True
        except:
                pass
	# regex for getting the original url and size
        matchObj = re.match(r'(.*)\?(\d+x?(\d+)?)', url)
	try:
		if "x" in matchObj.group(2):
			width, height = matchObj.group(2).split("x")
			try:
				height = int(height)
			except:
				height = "default"
		else:
			width = matchObj.group(2)
		url = matchObj.group(1)
	except:
		pass
	# get hash_name from domain name for redis purpose
	hash_name = base64.urlsafe_b64encode(hashlib.md5(url.split("/")[2]).digest())[:16]
	return url, hash_name, file_type, width, height, crop

def image(request, url):
	if request.method == "GET":
		s = request.META['HTTP_USER_AGENT']
		user_agent = httpagentparser.simple_detect(s)
		file_name = url.split("/")[-1]
		asos = url.split("/")
		try:
			if asos[2] == "images.asos-media.com":
				productid = asos[9]
				imagename, filetype = file_name.split(".")
				file_name = "{}{}.{}".format(imagename, productid, filetype)
		except:
			pass
		full_url = request.get_full_path()
		
		# check for http:// and https://
		
		fx = full_url.split("http://")
		pre = "/q/http://"
		
		if len(fx) == 1 :
			fx = full_url.split("https://")
			pre = "/q/https://"
			
		if len(fx) > 1 :
			full_url = "{}{}".format(pre, fx[-1])
		
		
		full_url, hash_name, file_type, width, height, crop = urlParser(full_url, user_agent, file_name)	# parse the url to get the data inside
		raw_name = redisNaming(file_name, width, height)
		redis_name = "{0}{1}?crop={2}.{3}".format(hash_name,raw_name,str(crop),file_type)			# redis name
		if crop:
			new_file = hash_name + '-' + raw_name + ' (cropped).' + file_type
		else:
			new_file = hash_name + '-' + raw_name + "." + file_type				# new file name
		path = os.path.join(os.path.dirname(__file__), "static/images/%s" %new_file)
		default_header = {'User-agent':'Chrome 51.0.2704.106'}
		if r.get(redis_name) != "1":
			f = requests.get(full_url, stream=True, headers=default_header)			#Download the file in current folder
			if f.status_code == 200:
				with open(new_file, 'wb') as g:
		        		f.raw.decode_content = True
		        		shutil.copyfileobj(f.raw, g)
				r.set(redis_name, "1")
				src = "/home/ubuntu/webapps/imageresizer/%s" %new_file
				shutil.move(src, path)
				if crop:
					crop_empty(new_file)	
				scale_down(new_file, width, height)
			else:
				error_json = {"error": "incorrect_url:{}".format(full_url), "status_code": `f.status_code`}
				json_data = json.dumps(error_json)
				return HttpResponse(json_data, content_type="application/json")
		image_data = open(path).read()
		return HttpResponse(image_data, content_type='image/%s' %file_type)

def nothing(request):
	if request.method == "GET":
		error_json = {"error": "incorrect_url", "detail": "missing_/q/"}
		json_data = json.dumps(error_json)
		return HttpResponse(json_data, content_type="application/json")

def homepage(request):
	if request.method == "GET":
		output = {"name": "imageresizer", "features": {"/q/": "start_process", "?widthxheight": "set_width_and_height", "?webp": "return_web_type", "?cropempty=True|False": "crop_background_color"}}
		json_data = json.dumps(output)
		return HttpResponse(json_data, content_type="application/json")
