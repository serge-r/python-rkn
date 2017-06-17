import socket
import time
from lxml import etree
from urllib.parse import urlparse

FILE_NAME = 'dump.xml'
temp_list = []
domains = []

parser = etree.parse(FILE_NAME)
root = parser.getroot()

for node in root:
	temp_dict = {}

	for element in node:
		temp_dict[element.tag] = element.text

	temp_list.append(temp_dict)

del(temp_dict)

for item in temp_list:
	res = urlparse(item.get('url','fail'))
	if res.scheme == 'https':
		domains.append(res.hostname)
		#print(item.get('url'))

for item in set(domains):
	try:
		ip = socket.gethostbyname(item)
		print(item,ip)
	except Exception as e:
		print ("Cannot resolve {} error: {}".format(item,e))
	#time.sleep(1)

#print(len(domains))