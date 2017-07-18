from django.http import HttpResponse
import requests, re, json, datetime, os
from pymongo import MongoClient
from bson import BSON
from bson import json_util
from formatting import format_file
from elasticsearch import Elasticsearch
import threading, time, redis, subprocess

r = redis.Redis('localhost')

def get_mongo_data():
	try:
		print "Getting latest 2 days data from staging mongodb.."
		client = MongoClient('mongodb://shopprapp.io/')
		db = client.shoppr_backend_db
		year = int(time.strftime("%Y", time.localtime(time.time())))
		month = int(time.strftime("%m", time.localtime(time.time())))
		date = int(time.strftime("%d", time.localtime(time.time()))) - 2
		records = db.Crawler_productdescriptionregion.find({"UpdateDateTime": {"$gte": datetime.datetime(year,month,date)}})
		path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/mongodb-ori.json")
		fout = open(path, "wt")
		for doc in records:
			doc = json.dumps(doc, sort_keys=True, indent=4, default=json_util.default)
			fout.write("%s\n" %doc)
		fout.close()
		format_file()
		path1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file1.json")
		path2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file2.json")
		path3 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file3.json")
		os.remove(path1)
		os.remove(path2)
		os.remove(path3)
		return True
	except:
		print "Failed getting data"
		return False
	
def bulk_index():
	es = Elasticsearch()
	check = get_mongo_data()
	if check:
		try:
			home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))			
			for i in range(1, 11):
				exec ('path%s = os.path.join(home, "files/mongodb-formatted%s.json")'%(i,i))
				bulk_body = ''
				print "bulk indexing file %s" %i
				exec ("a = path%s" %i)
				with open(a, "rt") as fin:
					for line in fin:
						bulk_body += str(line)
				fin.close()
				es.bulk(body=bulk_body, request_timeout=3000)
				time.sleep(10)
			print "Bulk index success"
			return True
		except:
			print "Not enough memory when requesting bulk indexing"
			return False
	else:
		return False

def find_outdated_data():
	es = Elasticsearch()
	es_id = []
	date = (int(time.time()) - 172800)*1000
	query = {
		"fields": "_id",
		"query": {
			"range": {
				"UpdateDateTime.$date": {
					"lte":  date
				}
			}
		},
		"size":  1000
	}
	res = es.search(index="mongo", doc_type="json", scroll="2m", body=query)
	sid = res['_scroll_id']
	while len(res['hits']['hits']) > 0:
		res = es.scroll(scroll_id = sid, scroll = '2m')
                sid = res['_scroll_id']
		for doc in res['hits']['hits']:
			es_id.append(doc['_id'])
	return es_id

def del_index():
	try:
		es = Elasticsearch()
		es_id = find_outdated_data()
		for item in es_id:
			res = es.delete(index="mongo", doc_type="json", id=item)
		print "Deleting outdated data success"
		return True
	except:
		print "Deleting outdated data failed"
		return False

def url_parser(url):
	matchObj1 = re.search('q=([\w]+)', url)
	if matchObj1:
		text = str(matchObj1.group(1))
	else:
		text = ""
	matchObj2 = re.search('&size=([\d]+)', url)
	if matchObj2:
		size = int(matchObj2.group(1))
	else:
		size = 5
	matchObj3 = re.search('&cat=([\w]+)', url)
	if matchObj3:
		cat = str(matchObj3.group(1))
	else:
		cat = "all"
	matchObj4 = re.search('&from=([\d]+)', url)
        if matchObj4:
                start = int(matchObj4.group(1))
        else:
                start = 0	
	return text, size, cat, start

def category(text, size, cat, start):
	if "name" in cat:
		query = {"suggestion":{"text":text,"completion":{"size":size,"field" : "name_suggestion","from":start}}}
		json_req = json.dumps(query)
	elif "brand" in cat:
		query = {"suggestion":{"text":text,"completion":{"size":size,"field" : "brand_suggestion","from":start}}}
		json_req = json.dumps(query)
	elif "type" in cat:
		query = {"suggestion":{"text":text,"completion":{"size":size,"field" : "type_suggestion","from":start}}}
		json_req = json.dumps(query)
	else:
		query = {"suggestion":{"text":text,"completion":{"size":size,"field" : "all_suggestion","from":start}}}
		json_req = json.dumps(query)
	return json_req

def suggester(request, url):
	if request.method == "GET":
		text, size, cat, start = url_parser(url)
		json_req = category(text, size, cat, start)
		d = requests.get('http://localhost:9200/mongo/_suggest', data=json_req)
		return HttpResponse(d.text)

def sort_parser(url):
	matchObj1 = re.search('q=([\w]+)', url)
        if matchObj1:
                field = str(matchObj1.group(1))
        else:
                field = "price"
	matchObj2 = re.search('&order=(asc|desc)', url)
        if matchObj2:
                order = str(matchObj2.group(1))
        else:
                order = "desc"
	matchObj3 = re.search('&size=([\d]+)', url)
        if matchObj3:
                size = int(matchObj3.group(1))
        else:
                size = 100
	matchObj4 = re.search('&scroll_id=(.*)', url)
        if matchObj4:
                scroll_id = str(matchObj4.group(1))
        else:
                scroll_id = ""
	matchObj5 = re.search('&from=([\d]+)', url)
        if matchObj5:
                start = str(matchObj5.group(1))
        else:
                start = "-1"
	if field == "updatetime":
		field = "UpdateDateTime.$date"
	elif field == "price":
		field = "Content.price"
	elif field == "createtime":
		field = "CreatedOn.$date"	
	return field, order, size, scroll_id, start

def sort(request, url):
	if request.method == "GET":
		es = Elasticsearch()
		field, order, size, sid, start = sort_parser(url)
		if start == "-1":
			index = 0
		else:
			index = int(start)
		if field == "discount":
			query = {
			"fields": ["Content.brand", "Content.currency", "Content.discount_currency", "Content.discount_price", "Content.images", "Content.name", "Content.price", "OnlineRetailerName"], 
			"query": {
				"match_all": {}
			}, 
			"sort": {
				"_script": {
					"type": "number",
					"script" : {        
						"inline": "dis_pct=(1 - (doc['Content.discount_price'].value/doc['Content.price'].value))*100; if (dis_pct == 100) {dis_pct = 0}; return dis_pct"
	      				},
					"order" : order
				}
			}, 
			"size": size,
			"from": index
			}
		else:
			query = {
	                "fields": ["Content.brand", "Content.currency", "Content.discount_currency", "Content.discount_price", "Content.images", "Content.name", "Content.price", "OnlineRetailerName"],
	                "query": {
	                        "match_all": {}
	                },
	                "sort": {
				field : {
					"order" : order
				}
	                },
	                "size": size,
			"from": index
	                }
		if sid != "":
			try:
				res = es.scroll(scroll_id = sid, scroll = '5m', request_timeout=60)
				if len(res['hits']['hits']) <= 0:
					query = {"result": 0, "status": "max index", "reason": "end of scroll"}
					output = json.dumps(res)
					return HttpResponse(output)			
			except:
				error_json = {"status_code": 404, "error": "scroll id has expired"}
        	                output = json.dumps(error_json)
	        	        return HttpResponse(output)
		else:
			if start == "-1":
				res = es.search(index="mongo", doc_type="json",scroll="5m", body=query, request_timeout=60)
			else:
				res = es.search(index="mongo", doc_type="json", body=query, request_timeout=60)	
		try:
			output = json.dumps(res)
		except:
			error_json = {"status_code": 408, "error": "request timeout"}
			output = json.dumps(error_json)
		return HttpResponse(output)

class thread_handler():
	def update_thread(self):
		if (float(r.get("update_index")) + float(10000.0)) < time.time():
			threadLock.acquire()
			print "Clearing Elasticsearch cache"
			d = requests.post('http://localhost:9200/mongo/_cache/clear')
			print d.text
			print "Clearing OS cache"
			subprocess.call("sudo sh -c 'free && sync && echo 3 > /proc/sys/vm/drop_caches && free'", shell=True)
			print "Updating Elasticsearch"
			r.set("update_index", float(time.time()))
			check = bulk_index()
                        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs/update.txt")
                        threadlog = open(path, 'a')
                        now = datetime.datetime.now()
                        threadtime = str(now.strftime("%b %d, %Y %H:%M"))
                        if check:
                                threadlog.write("%s\n" %threadtime)
                                threadlog.write("Updating Elasticsearch success\n")
                                threadlog.write("------------------------------------------\n")
                        else:
                                threadlog.write("%s\n" %threadtime)
                                threadlog.write("Updating Elasticsearch failed\n")
                                threadlog.write("------------------------------------------\n")
                        threadlog.close()
			threadLock.release()
	def delete_thread(self):
		if (float(r.get("delete_index")) + float(10000.0)) < time.time():
			threadLock.acquire()
			print "Deleting Elasticsearch"
			r.set("delete_index", float(time.time()))
			check = del_index()
			path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs/delete.txt")
                        threadlog = open(path, 'a')
                        now = datetime.datetime.now()
                        threadtime = str(now.strftime("%b %d, %Y %H:%M"))
                        if check:
                                threadlog.write("%s\n" %threadtime)
                                threadlog.write("Deleting Elasticsearch success\n")
                                threadlog.write("------------------------------------------\n")
                        else:
                                threadlog.write("%s\n" %threadtime)
                                threadlog.write("Deleting Elasticsearch failed\n")
                                threadlog.write("------------------------------------------\n")
                        threadlog.close()
                        threadLock.release()

class update_thread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while 1:
			handler = thread_handler()
			handler.update_thread()
			handler.delete_thread()
			time.sleep(21600)

threadLock = threading.Lock()
r.set("update_index", 0.0)
r.set("delete_index", 0.0)
thread = update_thread()
thread.start()

