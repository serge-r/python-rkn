# Config parameters
#
# RKN Urls:
# Test URL
# URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl'
# Current URL
URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl'
# Request format
DUMPVER = '2.2'
# Max number of attempts to downloading file
MAXTRIES = 5
# Log format
LOGFORMAT = '%(asctime)s %(levelname)s %(filename)s[Line:%(lineno)d] %(message)s'
# Logging levels
LEVELS = ("DEBUG", "INFO","WARNING", "ERROR")
# Dump file name
DUMP="dump.xml"
# Whitelist file
WHITELIST="whitelist.txt"
# Result file
RESULT_FILE="out.txt"
# Output dir
# OUT_DIR=os.getcwd()
#
# SCE Paarameters
# SCE DEVICE
SCE_IP='192.168.1.1'
# SCE username and pass
SCE_USER='user'
SCE_PASS='pass'
SCE_ENABLE_PASS='cisco'
SCE_FLAVOR_ID='164'
#
FTP_IP='192.168.2.1'
