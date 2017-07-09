from base64 import b64encode, b64decode
from suds.client import Client
from argparse import ArgumentParser, FileType
from parse import parse
from zipfile import ZipFile
from config import *
import sce
import logging
import time

def sendQuery(wsdlClient, queryFile, queryFileSing):
    '''
    Send a request to rkn
    Returns code string or None if error
    '''
    logger = logging.getLogger("rkn")
    request = b64encode(queryFile.read()).decode()
    request_sign = b64encode(queryFileSing.read()).decode()

    try:
        result = wsdlClient.service.sendRequest(requestFile=request,
                                                signatureFile=request_sign,
                                                dumpFormatVersion=DUMPVER)
    except Exception as e:
        logger.error('Error send request' + str(e))
        return None

    if result['result'] == True:
        logger.info("Result successfull. Result code: " + result['code'])
        return(result['code'])
    else:
        logger.error("Error: " + result['resultComment'])
        return None


def getFile(wsdlClient, codeString):
    '''
    Try to download file from RKN
    Returns archive or None if error
    '''
    tries = 0
    logger = logging.getLogger("rkn")

    try:
        while tries < MAXTRIES:
            result = wsdlClient.service.getResult(code=codeString)

            if result['resultCode'] == 0:
                logger.info('Wait 60 seconds: ' + result['resultComment'])
                time.sleep(60)
                tries += 1
                continue

            elif result['resultCode'] == 1:
                logger.info('Download success')
                logger.debug("Operator: " + result['operatorName'])
                logger.debug("INN: " + result['inn'])
                return result['registerZipArchive']

            else:
                logger.error("Error: " + result['resultComment'])
                return None

        logger.error("All tries exceeded")
        return None

    except Exception as e:
        logger.error('Some exception: ' + str(e))
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
                        help="Query file signed with DS")
    parser.add_argument("output",
                        help="File to save information from RKN")
    parser.add_argument("-l",
                        "--logfile",
                        help="File for write logs.")
    parser.add_argument("-s",
                        "--severity",
                        help="""
                        Logging severity.
                        Might be DEBUG, INFO or ERROR
                        """,
                        default="INFO")
    args = parser.parse_args()
    return args


def main():
    '''
    Start point
    '''
    # Parse args
    args = addArgs()

    if str.upper(args.severity) in LEVELS:
        level = str.upper(args.severity)
    else:
        level = "INFO"

    # Init logger
    logger = logging.getLogger("rkn")
    logger.setLevel(level)

    formatter = logging.Formatter(LOGFORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(level)
    logger.addHandler(console)

    if args.logfile:
        try:
            logFile = logging.FileHandler(args.logfile)

        except Exception as e:
            logger.warning("Cannot log to {} error is {}".format(args.logfile, e))
            logger.warning("logging to console")
        else:
            logger.addHandler(logFile)
            logFile.setFormatter(formatter)
            logFile.setLevel(level)
            logger.removeHandler(console)

    logger.info("Script started")
    # Get url and start processing
    try:
        client = Client(URL, cache=None)

    except Exception as e:
        logger.error("Error init the client: " + str(e))
        exit(1)

    code = sendQuery(client, args.query, args.querySign)

    if code:
        zipfile = getFile(client, code)

        if zipfile:
            logger.info("Writing file " + str(args.output))

            try:
                with open(args.output, 'wb') as file:
                    content = b64decode(zipfile.encode())
                    bytes = round(file.write(content)/1024, 2)
                    logger.info("File {} was writed. Size: {} KB".format(args.output, bytes))
            except Exception as e:
                logger.error("Error writing file: " + str(e))

    args.query.close()
    args.querySign.close()

    logger.info("Begin parsing")
    try:
        with ZipFile(args.output) as zipfd:
            with zipfd.open(DUMP) as dump:
                if parse(dump, WHITELIST) > 0:
                    logger.info("Dump successfull")
                    logger.info("Connecting to SCE")
                    upload = sce.upload(RESULT_FILE)
                    if upload == 0:
                        logger.error("Uploading error")
                        exit(1)
                else:
                    logger.error("Error when parsing")
                    exit(1)
    except Exception as e:
        logger.error("Error when parsing: {}".format(e))
        exit(1)

    logger.info("Script finished")
    exit(0)


if __name__ == '__main__':
    main()
