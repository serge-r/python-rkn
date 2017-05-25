from base64 import b64encode, b64decode
from suds.client import Client
from argparse import ArgumentParser, FileType
import time

# URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequestTest/?wsdl'
URL = 'http://vigruzki.rkn.gov.ru/services/OperatorRequest/?wsdl'
DUMPVER = '2.2'


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
    except:
        print('Some exception')
        return None

    if result['result'] == True:
        print(result['code'])
        return(result['code'])
    else:
        print(result['resultComment '])
        return None


def getFile(wsdlClient, codeString):
    ''' 
    Try to download file from RKN
    Returns archive or None if error
    '''
    try:
        while True:
            result = wsdlClient.service.getResult(code=codeString)
            if result['result'] == True:
                    if result['resultCode'] == 1:

                        print("Download success")
                        return result['registerZipArchive']
                    else:
                        print(result['resultComment'])
                        return None
            else:
                print(result['resultComment'])
                time.sleep(60)
    except:
        print('Some exception')
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
    client = Client(URL, cache=None)

    code = sendQuery(client, args.query, args.querySign)

    if code:
        zipfile = getFile(client, code)

        with open(args.output, 'wb') as file:
            content = b64decode(zipfile.encode())
            bytes = file.write(content)
            print("File {} was writed. Size: {} MB".format(args.output,round(bytes/2048,2)))

    args.query.close()
    args.querySign.close()


if __name__ == '__main__':
    main()
