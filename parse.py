import socket
import asyncio
import time
from lxml import etree
from urllib.parse import urlparse

FILE_NAME = 'dump.xml'
temp_list = []
domains = []

async def resolve(url):
	try:
		ip = socket.gethostbyname(url)
		msg = "Host: {} address: {}".format(url, ip)
	except Exception as e:
		msg = "Cannot resolve {} error is {}".format(url, e)
	print(msg)
	return msg


async def start(urls):
	coroutines = [resolve(url) for url in urls]
	completed, pending = await asyncio.wait(coroutines)
	for item in completed:
		#print(item.result())
		pass

def main():
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
	
	testurls = ['google.com', 'ya.ru', 'lib.ru', 'vk.com']
	event_loop = asyncio.get_event_loop()

	try:
		event_loop.run_until_complete(start(domains))
	finally:
		event_loop.close()

if __name__ == '__main__':
	main()
