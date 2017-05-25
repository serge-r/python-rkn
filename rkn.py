from base64 import b64encode, b64decode
from suds.client import Client
from argparse import ArgumentParser, FileType
import time

# Test URL
# URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl'
URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl'
# Request format
DUMPVER = '2.2'
# Max number of attempts to downloading file
MAXTRIES = 5 


def sendQuery(wsdlClient, queryFile, queryFileSing):
    '''
    Send a request to rkn
    Returns code string or None if error
    '''
    request = b64encode(queryFile.read()).decode()
    request_sign = b64encode(queryFileSing.read()).decode()

    try:
        result = wsdlClient.service.sendRequest(requestFile=request,
                                                signatureFile=request_sign,
                                                dumpFormatVersion=DUMPVER)
    except Exception as e:
        print('Error send request', e)
        return None

    if result['result'] == True:
        print(result['code'])
        return(result['code'])
    else:
        print(result['resultComment'])
        return None


def getFile(wsdlClient, codeString):
    ''' 
    Try to download file from RKN
    Returns archive or None if error
    '''
    tries = 0

    try:
        while tries < MAXTRIES:
            result = wsdlClient.service.getResult(code=codeString)

            if result['resultCode'] == 0:
                print('Wait 60 seconds: ', result['resultComment'])
                time.sleep(60)
                tries += 1
                continue

            elif result['resultCode'] == 1:
                print('Download success')
                return result['registerZipArchive']

            else:
                print("Error: ", result['resultComment'])
                return None

        print("All tries exceeded")
        return None

    except Exception as e:
        print('Some exception ', e)
        return None


def addArgs():
    '''
    Init command-line args
    '''
    parser = ArgumentParser()
    parser.add_argument("query",
                        type=FileType('rb'),
                        help="Path to query file")
    parser.add_argument("querySign",
                        type=FileType('rb'),
                        help="Query file signed with EDP")
    parser.add_argument("output",
                        help="File to save information from RKN")
    args = parser.parse_args()
    return args


def main():
    '''
    Start point
    '''
    args = addArgs()
    try:
        client = Client(URL, cache=None)

    except Exception as e:
        print("Error init the client: ", e)
        exit(1)

    code = sendQuery(client, args.query, args.querySign)

    if code:
        zipfile = getFile(client, code)

        if zipfile:
            print("Writing file ", args.output)
           try: 
                with open(args.output, 'wb') as file:
                    content = b64decode(zipfile.encode())
                    bytes = file.write(content)
                    print("File {} was writed. Size: {} KB".format(args.output, round(bytes/1048, 2)))
            except Exception as e:
                print("Error writing file", e)

    args.query.close()
    args.querySign.close()
    exit(0)


if __name__ == '__main__':
    main()
