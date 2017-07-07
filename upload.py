from config import *
import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname=SCE_IP, username=SCE_USER, password=SCE_PASS, look_for_keys=False, allow_agent=False)

ssh = client.invoke_shell()

ssh.send("enable\n")
ssh.send(SCE_ENABLE_PASS + '\n')
time.sleep(1)

ssh.send("del out.txt\n")
time.sleep(1)

ssh.send("copy-passive ftp://{}/out.txt out.txt\n".format(FTP_IP))
time.sleep(1)

ssh.send("conf\n")
time.sleep(1)

ssh.send("interface line 0\n")
time.sleep(1)

ssh.send("sce-url-database clear-all\n")
time.sleep(120)

ssh.send("sce-url-database import cleartext-file out.txt flavor-id 164\n\n")
time.sleep(120)

ssh.send("exit\n")
time.sleep(1)

ssh.send("exit\n")
time.sleep(1)

ssh.send("wr\n")
time.sleep(10)

result = ssh.recv(5000)
print(result)
