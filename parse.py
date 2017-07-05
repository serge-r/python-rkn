from lxml import etree
from urllib.parse import urlparse

FILE_NAME = 'dump.xml'
WHITELIST = 'whitelist.txt'


def parse(dump):
	records = []
	blocked_ips = []
	blocked_subnets = []
	blocked_domains = []
	blocked_urls = []
	whitelist = []

	parser = etree.parse(dump)
	root = parser.getroot()

	# Get whitelist content
	with open(WHITELIST, 'r') as fd:
		# for line in fd:
			# whitelist.append(line)
		whitelist = fd.read()
		whitelist = whitelist.split('\n')

	print(whitelist)

	# Govnocode start
	for node in root:
		records.append({'urls':	[item.text for item in node if item.tag == 'url'], 
						'domains': [item.text for item in node if item.tag == 'domain'],
						'ips':  [item.text for item in node if item.tag == 'ip'],
						'subnets': [item.text for item in node if item.tag == 'ipSubnet']
						})

	for record in records:
		# Determine subnets
		for subnet in record['subnets']:
			blocked_subnets.append(subnet)

		# Determine domains - to compare it with url
		for domain in record['domains']:
			temp_domains = []
			if record['urls'] == []:
				if domain not in whitelist:
					domain = domain.encode('idna')
					temp_domains.append(domain.decode())

		# Determine urls and encode to puhhycode
		for url in record['urls']:
			res = urlparse(url)

			if res.scheme == 'https':
				for ip in record['ips']:
					blocked_ips.append(ip)

			elif res.scheme == 'http':
				domain = res.netloc.encode('idna').decode()
				# Check whitelist
				if domain in whitelist:
					break
				if res.query == '':
					url = domain + ':' + res.path + '*'
				else:
					url = domain + ':' + res.path + '?' + res.query + '*'
				blocked_urls.append(url)

			# Determine domains and compare it with url
			if domain in temp_domains:
				temp_domains.remove(domain)

		# Fill blocked domain list
		blocked_domains += temp_domains

		# Determine ips
		for ip in record['ips']:
			if record['urls'] == [] and record['domains'] == []:
				blocked_ips.append(ip)

	# Only uniq items
	subnets_set = set(blocked_subnets)
	ip_set = set(blocked_ips)
	url_set = set(blocked_urls)
	domains_set = set(blocked_domains)

	print("Count all subnets: {}".format(len(subnets_set)))
	print("Count all ip's: {}".format(len(ip_set)))
	print("Count all urls: {}".format(len(url_set)))
	print("Count all domains: {}".format(len(domains_set)))
	print("Count of all records: {}".format(len(root)))

	with open("result.txt", 'w') as fd:
	 	fd.write("*:")

	 	# Write domains
	 	for domain in domains_set:
	 		fd.write(domain + ":*\n")

	 	for ip in ip_set:
	 		fd.write(ip + ":*\n")

	 	for url in url_set:
	 		fd.write(url + "\n")

if __name__ == '__main__':
	parse(dump=FILE_NAME)
