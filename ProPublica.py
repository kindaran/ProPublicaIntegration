import sys
import os
import logging
from datetime import datetime
import json
import csv

import requests
import xlrd


###############################################################################
###                                 FUNCTIONS                               ###
###############################################################################
def getArgs():

    '''
        Slightly enhanced code to retrieve command line args. Will vary by script.
        Uses PRINT instead of LOGGING as log mode has not yet been established.
    '''
    args = []

    try:
        print("***RETRIEVING COMMAND LINE ARGS")
        if len(sys.argv) == 4:
            configFilePath = sys.argv[1]
            args.append(configFilePath)
            configFileName = sys.argv[2]
            args.append(configFileName)
            loggingLevel = sys.argv[3].upper()
            args.append(loggingLevel)
            print("Logging level is %s" %(loggingLevel))
            print("Config file path is %s" %(configFilePath + "/" + configFileName))
            return args
        elif len(sys.argv) == 3:
            configFilePath = sys.argv[1]
            args.append(configFilePath)
            configFileName = sys.argv[2]
            args.append(configFileName)
            loggingLevel = "INFO"
            args.append(loggingLevel)
            print("Logging level is %s" %(loggingLevel))
            print("Config file path is %s" %(configFilePath + configFileName))
            return args            
        else:
            print("Not enough arguments provided.")
            print(
                "Incorrect arguments provided\r\nRequired: <config file path> <config file name> <OPTIONAL: debug level (default INFO)")
            return None
    except Exception as e:
        msg = str(e)
        print("*****Error in getArgs. Error: %s" %(msg))
        return None
# END DEF

def getRequest(p_URL):
    '''
        Very basic HTTP GET request. Returns the raw request object
        which would need to be further manipulated to get the response text
    '''
    try:        
        logging.info("***SENDING GET REQUEST")  
        response = requests.get(p_URL)
        response.raise_for_status()              ##if non-2xx response status returned, an error is raised
        return response
    except Exception as e:
        msg = str(e)
        logging.error("*****Error in getRequest. Error: %s" %(msg))
        return None

#END DEF

def loadConfigFile(p_file):

    try:
        logging.info("***LOAD CONFIG FILE")
        file = xlrd.open_workbook(p_file)
        worksheet = file.sheet_by_name("Input")
        return worksheet
    except Exception as e:
        msg = str(e)
        logging.error("*****Error in loadConfigFile. Error: %s" % (msg))
        return None

# END DEF

def generateOutputFilename(p_filename):

    try:
        logging.info("***GENERATE FILENAME")
        # strips the raw filename out of file string
        filename = p_filename.split(".")[0].split("/")[-1]
        current_datetime = datetime.strftime(
            datetime.now(), "%Y%m%d%H%M%S")
        output_filename = filename + "_" + current_datetime + ".csv"
        logging.debug("Output filename: %s" % (output_filename))
        return output_filename
    except Exception as e:
        msg = str(e)
        logging.error(
            "*****Error in generateOutputFilename. Error: %s" % (msg))
        return None
# END DEF

def writeFile(p_filename, p_rows):

    try:
        logging.info("***WRITING TO OUTPUT FILE")
        if len(p_rows) > 0:
            output_file = p_filename
            logging.debug('Writing to file: %s' % (output_file))
            with open(output_file, 'w') as hFile:
                writer = csv.writer(hFile,quoting=csv.QUOTE_ALL)
                writer.writerows(p_rows)
            #END WITH
            logging.info('Done writing')
        else:
            logging.warning("WARNING: No data to write***")
        #END IF
    except Exception as e:
        msg = str(e)
        logging.error("*****Error in writeFile. Error: %s" %(msg))

#END DEF

###############################################################################
###                                 MAIN                                    ###
###############################################################################

def main():

    try:
       # get command line args
        args = getArgs()
        if args == None:
            print("Unable to retrieve command line arguments - ending")
            return
        # END IF
        sourceFilePath = args[0]
        sourceFileName = args[1]
        sourceFile = sourceFilePath + "/" + sourceFileName

        loggingLevel = getattr(logging, args[0].upper(), 20)
        logging.basicConfig(level=loggingLevel,format="%(levelname)s: %(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

        #load source file
        sourceSpreadsheet = loadConfigFile(sourceFile)
        if sourceSpreadsheet == None:
            logging.info("Source spreadsheet not found - exiting")
            return
        #END IF

        #retrieve variables from spreadsheet
        EINList = []
        logging.info("*****GATHER EIN VALUES")
        for cell in sourceSpreadsheet.col_slice(colx=0,start_rowx=1):
            if cell.ctype != 2:          ## this is cell type XL_CELL_NUMBER
                logging.debug("Non numeric cell found: '%s' - ending EIN processing" %(cell.value))
                break
            #END IF
            logging.debug("EIN found: %s" %(str(int(cell.value))))
            EINList.append(str(int(cell.value)))
        #END FOR
        logging.info("Found %d EINs" %(len(EINList)))

        YearList = []
        logging.info("*****GATHER YEAR VALUES")
        for cell in sourceSpreadsheet.col_slice(colx=1,start_rowx=1):
            if cell.ctype != 2:          ## this is cell type XL_CELL_NUMBER
                logging.debug("Non numeric cell found: '%s' - ending Year processing" %(cell.value))
                break
            #END IF
            logging.debug("Year found: %s" %(str(int(cell.value))))
            YearList.append(int(cell.value))
        #END FOR
        logging.info("Found %d Years" %(len(YearList)))

        HeaderVars = []
        logging.info("*****GATHER HEADER VARIABLES")
        for cell in sourceSpreadsheet.col_slice(colx=2,start_rowx=1):
            if cell.ctype != 1:          ## this is cell type XL_CELL_TEXT
                logging.debug("Non text cell found: '%s' - ending Header var processing" %(cell.value))
                break
            #END IF
            logging.debug("Header variable found: %s" %(cell.value))
            HeaderVars.append(cell.value.strip())
        #END FOR
        logging.info("Found %d Header variables" %(len(HeaderVars)))

        FilingVars = []
        logging.info("*****GATHER FILING VARIABLES")
        for cell in sourceSpreadsheet.col_slice(colx=3,start_rowx=1):
            if cell.ctype != 1:          ## this is cell type XL_CELL_TEXT
                logging.debug("Non text cell found: '%s' - ending Filing var processing" %(cell.value))
                break
            #END IF
            logging.debug("Filing variable found: %s" %(cell.value))
            FilingVars.append(cell.value.strip())
        #END FOR    
        logging.info("Found %d Filing variables" %(len(FilingVars)))   

        OutputFileHeader = []
        logging.info("*****GATHER OUTPUT FILE COLUMN NAMES")
        for cell in sourceSpreadsheet.col_slice(colx=4,start_rowx=1):
            if cell.ctype != 1:          ## this is cell type XL_CELL_TEXT
                logging.debug("Non text cell found: '%s' - ending column header processing" %(cell.value))
                break
            #END IF
            logging.debug("Column header found: %s" %(cell.value))
            OutputFileHeader.append(cell.value.strip())
        #END FOR       
        logging.info("Found %d column headers" %(len(OutputFileHeader)))

        #execute GET request
        logging.info("*****MAKE API DATA CALLS")
        data = []
        for EIN in EINList:
            logging.debug("Retrieving EIN %s" %(EIN))
            response = getRequest("https://projects.propublica.org/nonprofits/api/v2/organizations/" + EIN + ".json")
            if response == None:
                logging.info("Error in get request - try next EIN")
                continue
            #END IF
            # logging.debug("Found data \r\n %s" %(response.json()))
            data.append(json.loads(response.text))
        #END FOR


        targetData = []
        #set first row of output to column headers
        targetData.append(OutputFileHeader)

        #process response
        logging.info("*****PROCESS RESPONSE DATA")
        for institution in data:
            logging.debug("Processing EIN %s" %(institution["organization"]["ein"]))
            orgData = []
            for headerVar in HeaderVars:
                logging.debug("Header var: %s  Value: %s" %(headerVar,institution["organization"][headerVar]))
                orgData.append(str(institution["organization"][headerVar]))
            #END FOR
            for filingList in institution["filings_with_data"]:
                if filingList["tax_prd_yr"] in YearList:
                    outputRow = []
                    outputRow += orgData
                    for filingVar in FilingVars:
                        logging.debug("Filing var: %s  Value: %s" %(filingVar,filingList[filingVar]))
                        outputRow.append(str(filingList[filingVar]))
                    #END FOR
                    targetData.append(outputRow)
                #END IF
            #END FOR
        #END FOR
        logging.info("Data rows found %d" %(len(targetData)))
        logging.debug("Target data \r\n %s" %(targetData)) 

        #write data to CSV
        logging.info("*****WRITE DATA TO CSV")
        output_filename = generateOutputFilename(sourceFile)
        writeFile(output_filename,targetData)

    except Exception as e:
        msg = str(e)
        logging.error("*****Error in Main. Error: %s" % (msg))

# END DEF

###############################################################################
###                                 CODE START                              ###
###############################################################################

print('*****PROGRAM START*****')

if __name__ == "__main__":
    main()
# END IF

print('*****PROGRAM END*****')