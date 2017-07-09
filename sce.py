from config import *
from os import path
import paramiko
import logging
import sys
import time


def upload(filename=RESULT_FILE, 
			sce=SCE_IP,
			username=SCE_USER,
			password=SCE_PASS,
			enable_pass = SCE_ENABLE_PASS, 
			ftp=FTP_IP,
			flavor=SCE_FLAVOR_ID
			):
	logger = logging.getLogger("rkn")

	filename = path.basename(filename)
	
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		client.connect(hostname=sce,
					   username=username,
					   password=password,
					   look_for_keys=False, 
					   allow_agent=False)
	except Exception as e:
		logger.error("Cannot connect to SCE: {}: {}".format(sce, e))
		return 0

	ssh = client.invoke_shell()

	ssh.send("enable\n")
	ssh.send(enable_pass + "\n")
	time.sleep(1)

	ssh.send("del " + filename + "\n")
	time.sleep(1)

	ssh.send("copy-passive ftp://" + ftp + "/" + filename + " " + filename + "\n")
	time.sleep(1)

	ssh.send("conf\n")
	time.sleep(1)

	ssh.send("interface line 0\n")
	time.sleep(1)

	ssh.send("sce-url-database clear-all\n")
	time.sleep(120)

	ssh.send("sce-url-database import cleartext-file" + filename + "flavor-id" + flavor + "\n\n")
	time.sleep(120)

	ssh.send("exit\n")
	time.sleep(1)

	ssh.send("exit\n")
	time.sleep(1)

	ssh.send("wr\n")
	time.sleep(10)

	result = ssh.recv(5000)
	print(result)
	return result


if __name__ == '__main__':
	# Init logger
	logger = logging.getLogger("rkn")
	logger.setLevel("INFO")
	formatter = logging.Formatter(LOGFORMAT)
	console = logging.StreamHandler()
	console.setFormatter(formatter)
	logger.addHandler(console)
	# Upload
	if len(sys.argv) > 1:
		filename = sys.argv[1]
		upload(filename)
	else:
		print("Usage: " + sys.argv[0] + " filename")
