import re, os

#remove spaces
def del_spaces():
	path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/mongodb-ori.json")
	newpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file1.json")
	with open(newpath, "wt") as fout:
		with open(path, "rt") as fin:
			for line in fin:
				matchObj1 = re.search('"price": "([\d\.]+)"', line)
				price = discount_price = 0
				if matchObj1:
					price = matchObj1.group(1)
					result1 = '"price": %s'%price
					line = re.sub('"price": "([\d\.]+)"', result1, line)
				matchObj2 = re.search('"discount_price": "([\d\.]+)"', line)
                                if matchObj2:
                                        discount_price = matchObj2.group(1)	
					result2 = '"discount_price": %s'%discount_price
					line = re.sub('"discount_price": "([\d\.]+)"', result2, line)
				new_line = line.lstrip()
				new_line = new_line.rstrip()
				fout.write(new_line)
	fin.close()
	fout.close()

#make new line every doc
def add_line():
	path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file1.json")
	newpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file2.json")
	with open(newpath, "wt") as fout:
		with open(path, "rt") as fin:
			for line in fin:
				new_line = re.sub(r'}}{', '}}\n{', line)
				fout.write(new_line)
	fin.close()
	fout.close()

#add index id with UniqueKey in elasticsearch syntax
def add_header():
	path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file2.json")
	newpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file3.json")
	with open(newpath, "wt") as fout:
		with open(path, "rt") as fin:
			for line in fin:
				new_line = re.sub(',"_id":.*"}', '', line)
				matchObj = re.search('"UniqueKey": "([\w\d\/]+)"', new_line)
				if matchObj:
					asosid = matchObj.group(1)
					head = '{"index":{"_index":"mongo", "_type":"json", "_id":"%s"}}\n' %asosid
					fout.write(head)
					fout.write(new_line)
				else:
					head = '{"index":{"_index":"mongo", "_type":"json"}}\n'
					fout.write(head)
					fout.write(new_line)
	fin.close()
	fout.close()

#add suggestion
def add_suggestion_field():
	path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/file3.json")
	newpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/mongodb-formatted.json")
	with open(newpath, "wt") as fout:
		with open(path, "rt") as fin:
			i = 0
			for line in fin:
				i += 1
				if i % 2 == 0:
					try:
						s1 = re.search('"name": "([\w\s]+)"', line)
						if s1:
							name = s1.group(1)
						s2 = re.search('"Type": "([\w\s]+)"', line)
						if s2:
							asostype = s2.group(1)
						s3 = re.search('"Brand": "([\S\s]+)","Content"', line)
						if s3:
							brand = s3.group(1)
						suggestion = '},"all_suggestion":{"input":["%s", "%s", "%s"]},'%(name, asostype, brand)
						name_suggestion = '"name_suggestion":{"input":["%s"]},'%(name)
						type_suggestion = '"type_suggestion":{"input":["%s"]},'%(asostype)
						brand_suggestion = '"brand_suggestion":{"input":["%s"]}}'%(brand)
						sub = '{}{}{}{}'.format(suggestion, name_suggestion, type_suggestion, brand_suggestion)
						new_line = re.sub(r'}}', sub, line)
					except:
						new_line = line
					fout.write(new_line)
				else:
					new_line = line
					fout.write(new_line)
	fin.close()
	fout.close()

#split into smaller files
def split():
	path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files/mongodb-formatted.json")
	fin = open(path, "rt")
	home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	for j in range (1, 11):
		exec ('newpath%s = os.path.join(home, "files/mongodb-formatted%s.json")'%(j, j))
		exec ('fout%s = open(newpath%s, "wt")'%(j , j))
	i = 0
	for line in fin:
		if i == 20:
			i = 0
		i += 1
		if i <= 2:
			fout1.write(line)
		elif i <= 4:
			fout2.write(line)
		elif i <= 6:
			fout3.write(line)
		elif i <= 8:
			fout4.write(line)
		elif i <= 10:
			fout5.write(line)
		elif i <= 12:
                        fout6.write(line)
		elif i <= 14:
                        fout7.write(line)
		elif i <= 16:
                        fout8.write(line)
		elif i <= 18:
                        fout9.write(line)
		elif i <= 20:
                        fout10.write(line)
	fin.close()
	for k in range (1, 11):
		exec ('fout%s.close()'%k)

def format_file():
	print "Deleting spaces.."
	del_spaces()
	print "Adding new line.."
	add_line()
	print "Adding header.."
	add_header()
	print "Adding new suggestion field.."
	add_suggestion_field()
	print "Splitting into smaller files"
	split()
