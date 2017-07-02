from lxml import etree
from urllib.parse import urlparse


FILE_NAME = 'dump.xml'

def parse(dump):
	records = []

	blocked_ips = []
	blocked_subnets = []
	blocked_domains = []
	blocked_urls = []

	parser = etree.parse(dump)
	root = parser.getroot()

	for node in root:

		records.append({  'urls':		[item.text for item in node if item.tag == 'url'], 
						  'domains': 	[item.text for item in node if item.tag == 'domain'],
						  'ips': 		[item.text for item in node if item.tag == 'ip'],
						  'subnets': 	[item.text for item in node if item.tag == 'ipSubnet']
						  })

	for record in records:

		#print("Value is: {}".format(record))
		for subnet in record['subnets']:
			blocked_subnets.append(subnet)

		for url in record['urls']:
			res = urlparse(url)
			if res.scheme == 'https' or (record['urls'] == [] and record['domains'] == []):
				# print("Domain {} will blocked by IPs {}".format(res.hostname, record['ips']))
				blocked_ips.append(record['ips'])
			elif res.scheme == 'http':
				blocked_urls.append(url)
				

	subnets_set = set(blocked_subnets)
	ip_set = set(sum(blocked_ips,[]))
	url_set = set(blocked_urls)

	print("Count all subnets: {}".format(len(subnets_set)))
	print("Count all ip's: {}".format(len(ip_set)))
	print("Count all urls: {}".format(len(url_set)))

	print("Count of all records: {}".format(len(root)))


if __name__ == '__main__':
	parse(dump=FILE_NAME)
