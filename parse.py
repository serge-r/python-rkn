from lxml import etree
from urllib.parse import urlparse, quote
from openpyxl import load_workbook
import logging
import sys
import config

def getWhitelist(wlfile):
	logger = logging.getLogger("rkn")
	whitelist = []

	try:
		wb = load_workbook(wlfile)
		wblist = wb.active
	except Exception as e:
		logger.warning("Cannot get info from whitelist file {}: {}".format(wlfile, e))
		return []
	# Get only values from column B
	cells = wblist['B'][1:]
	# Encode and crop wildcard(*.)
	for cell in cells:
		domain = cell.value.encode('idna')
		if domain.startswith(b'*.'):
			domain = domain[2:]
		whitelist.append(domain.decode())
	logger.info("Whitelist loaded successfull. Domain counts: {}".format(len(whitelist)))
	wb.close()
	return whitelist


def parse(dumpfile = config.DUMP):
	logger = logging.getLogger("rkn")
	records = []
	blocked_ips = []
	blocked_subnets = []
	blocked_domains = []
	blocked_urls = []

	try:
		parser = etree.parse(dumpfile)
		root = parser.getroot()
	except Exception as e:
		logger.info("Cannot parse file: {}".format(e))
		return 0

	whitelist = getWhitelist(config.WHITELIST)

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
			if domain.endswith('.'):
				domain = domain[:-1]
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
				domain = res.hostname.encode('idna').decode()
				if domain.endswith('.'):
					domain = domain[:-1]
				# Check whitelist
				if domain in whitelist:
					break
				if res.query == '':
					url = domain + quote(res.path)[:256]
				else:
					url = domain + quote(res.path)[:256] + '?' + quote(res.query)[:256]
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

	logger.info("Count all subnets: {}".format(len(subnets_set)))
	logger.info("Count all ip's: {}".format(len(ip_set)))
	logger.info("Count all urls: {}".format(len(url_set)))
	logger.info("Count all domains: {}".format(len(domains_set)))
	logger.info("Count of all records: {}".format(len(root)))

	try:
		with open(config.FTP_PATH + "/" + config.RESULT_FILE, 'w') as fd:
		 	# Write domains
		 	for domain in domains_set:
		 		fd.write(domain + "\n")

		 	for ip in ip_set:
		 		fd.write(ip + "\n")

		 	for url in url_set:
		 		fd.write(url + "\n")
	except Exception as e:
		logger.error("Cannot write output file: {}".format(e))
		return 0
	return len(root)

if __name__ == '__main__':
	# Init logger
	logger = logging.getLogger("rkn")
	logger.setLevel("INFO")
	formatter = logging.Formatter(config.LOGFORMAT)
	console = logging.StreamHandler()
	console.setFormatter(formatter)
	logger.addHandler(console)
	# Parse
	if len(sys.argv) > 1:
		parse(dumpfile=sys.argv[1])
	else:
		print("Usage: " + sys.argv[0] + " filename")