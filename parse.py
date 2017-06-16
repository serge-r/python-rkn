import re
from lxml import etree

FILE_NAME = 'dump.xml'
temp_list = []

protocol_re = re.compile("https:\/\/(.)*")
domain_re = re.compile("(([\w\.]+)\.(\w)+)")

parser = etree.parse(FILE_NAME)
root = parser.getroot()

for node in root:
	temp_dict = {}

	for element in node:
		temp_dict[element.tag] = element.text

	temp_list.append(temp_dict)

for item in temp_list:
	if protocol_re.match(item.get('url',"fail")):
		url = item.get('url',"fail")
		result = domain_re.match(url)
		if result:
			print(result.group())