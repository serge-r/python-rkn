# Config parameters
#
#
# RKN Urls:
# Test URL
# URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl'
URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl'
# Request format
DUMPVER = '2.2'
# Max number of attempts to downloading file
MAXTRIES = 5
# Log format
LOGFORMAT = '%(asctime)s %(levelname)s Line:%(lineno)d %(message)s'
# Logging levels
LEVELS = ("DEBUG", "INFO", "ERROR")
# Dump file name
DUMP="dump.xml"
# Whitelist file
WHITELIST="whitelist.txt"
#
# Result file
RESULT_FILE="out.txt"
#
#
# SCE Paarameters
#
# SCE DEVICE
SCE_IP='192.168.0.0'
#
# SCE username and pass
SCE_USER='user'
SCE_PASS='pass'
SCE_ENABLE_PASS='cisco'
#
FTP_IP='192.168.0.0'
