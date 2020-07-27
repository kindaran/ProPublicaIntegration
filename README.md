# ProPublica API Integration
This is a Python project I created based on a job posting on UpWork. Never heard back from the client but I have pretty much come up with an initial solution based on the requirements they posted and making some assumptions.

**NOTE: this code represents a specific point in time in my ongoing learning of Python. Certain code usage or patterns don't necessarily represent how I might code today.**

# Background
The requirements were as follows:
1) retrieve data from an API at ProPublica.org (https://www.propublica.org/datastore/api/nonprofit-explorer-api). The desired data was specific IRS filings by large educational institutions like Yale and Harvard
2) make use of an Excel spreadsheet that contains information about what data to retrieve from the API and also a sample layout of the output
3) create a CSV output file of the data

The project was a fixed cost of $30US and a duration of "less than a week". I came up with a solution in about that duration and about half that time in effort. Given the cost, fancy was not the focus. Something that works and ideally doesn't blow up was.

# Major Functions
The application performs the following major functions.

## Commandline Parameters
The following commandline parameters can be used:
1) path to the Excel config file - could be relative or absolute but absolute would be safest. Do not end with a slash
2) source file name including extension
3) optional parameter to set logging level. Has to be a valid debug level like DEBUG or INFO, etc. Of course, would document that for the client but much of the time I dont expect this to be used.

## Obtaining Config Parameters from an Excel Spreadsheet
The first major functionality is to use an Excel spreadsheet as a type of data-driven interface. The spreadsheet will provide the following parameter data:
1) distinct institution IDs. This ID is the unique key used as part of the API call
2) one or more filing years. This data is applied as a type of filter against the filings_with_data portion of the response. If the year of the filing matches one of the years in this column then use the data else skip to next filing.
3) "master" organization keys (the JSON response includes two dictionaries: organization and filings_with_data. Organization is "master" data while filings... has 1 or more years)
3) filings details keys
4) column headings for the CSV output - in the desired order. The order of items 3 and 4 have to match this same order

Each of the above are contained in a column. Using the XLRD library, it's pretty easy to traverse a column until there are no entries in the column. Each of the columns is loaded into a list.

## Make API Calls
Traversing the unique institution ID list, make GET requests from ProPublica. No authentication is required. Each response is loaded into a list.

## Process JSON Responses and Build an Output Dataset
As mentioned above, the response structure includes one dictionary of organization data (master) and a filings structure that contains one or more years of data. The CSV output will be a denormalized combination of both with the organization data repeating. Therefore, for each insitution, the organization data is read once and retained.

Next the filing data needs to be looped through. On each loop, a data row is built by 1) seeding the row with organization data and 2) appending the current filing year data. The combined row is then pushed onto a separate targetData list object.

Taking a step back, the first row pushed onto targetData is actually the column headers as provided in the Excel spreadsheet.

## Write Data to CSV
The first thing that happens is to generate what should be a unique output file name. This is done by taking the config file file name and appending the current YYYYMMDDHHMISS onto the file name. 

Next is to make use of the CSV library and csv.writer.writerows() to convert rows to comma delimited and write them out to a file.

## Conclusion
The script makes use of logging to stdout. By default, logging will be INFO level providing milestones as the script is processed. As indicated above, a command line parameter can be provided to change the logging level (generally to DEBUG to help troubleshoot a problem or for development).

For $30USD, I didnt get into too much commenting. It's also not overly complex (but that in itself does not preclude some basic commenting). There is the odd place that I add comments to clarify why I did something.

