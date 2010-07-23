#!/usr/bin/python -tt

"""This short program converts CR10X array data from julian to the table based date format and
normalizes the data.  In this context normalizing means a 2 column file with the first column the
Date & time and column 2 the sensor value at that time step.

Intentions are for it to expand to replace the data processing functionality that datapro had
back in the day.

Brainstormed features include logging any QAQC catches to a per sensor log file.  Tying into
the datasite system would be good, too.  Perhaps that's where the whole flexibility of python comes in,
can pass a web link like for some datasite info as we were talking about in email January 2008ish.
That would become the source data.


1) read in the key file, passed on the command line
2) open up the data file mentioned in the key file
3) read through

do directory checks and create them if they're not present (such as for the error log directory).
declare behavior for arrays that are missing the year (like a command line option maybe?)
bob@bob_workstation /work/python/py_datapro
$ python datapro.py c:\\data\\atlas\\C1-grid\\c1-met_key.py.txt
"""

import ConfigParser
import os
import sys
import dp_funks  # data_pro function library
import csv
import urllib2

VERSION = '0.1'

###################################################################################
##  Read in the site configuration file                                          ##
###################################################################################

#First we need to get the config file, or die if it hasn't been given

try:
    configFile = sys.argv[1]
except IndexError:
    print """Needs Configuration File.  Enter like this:
    $ python datapro.py c:\\data\\atlas\\C1-grid\\c1-met_key.py.txt
    """
    sys.exit(1)

# 1) initialize the config object
keyfile = ConfigParser.SafeConfigParser()
# 2) Read the config file...
# ... Returns a dictionary of the keys and values in the configuration file
readSuccess = keyfile.read([configFile])

# if there was trouble reading the file error out here
try:
    if not(readSuccess[0] == configFile):
        print "Could not read config file";
        sys.exit(1)
except IndexError:
    print "Could not read config file";
    sys.exit(1)
# print to screen the contents of this key file:
print '==============================================================='
print '       Station Name:   ', keyfile.get('main', 'station_name')
print '       logger type:    ', keyfile.get('main', 'logger_type')
print '       input file:     ', keyfile.get('main', 'input_data_file')
print '       output_dir:     ', keyfile.get('main', 'output_dir')
print '       qc_log_dir:     ', keyfile.get('main', 'qc_log_dir')
print '       error_log_dir:  ', keyfile.get('main', 'error_log_dir')
print '==============================================================='
print ' '
print ' '

###################################################################################
##  read in the data variable specific configuration file                        ##
###################################################################################

# Here is the current list of params:
# D_Element  -- data element, this is like the input location ID from the .dld/.csi that is saved out in the output to final storage section of the program
# Data_Type  -- data type here refers to the data processing mechanism / functions
# Input_Array_Pos  -- position in the data array of this data element.  This included since all this info is read in as an unordered dictionary, need to create the order so this is how I did it.
# Coef_1     -- 7 coefficients here (more than I can imagine needing at present) for use with any of the functions in Data_Type like thermistors need the 3 steinhart-hart coefficients
# Coef_2     -- soil moisture sensors need the polynomial coefficients etc.
# Coef_3     -- another use is for net radiation to include + and - params plus array_pos of the windspeed for doing the wind correction.
# Coef_4
# Coef_5
# Coef_6
# Coef_7
# Qc_Param_High --
# Qc_Param_Low
# QC_Param_Step -- step is like the max acceptable jump between time steps so,
# Output_Header_Name -- The name of the sensor, appears at the top of the output file
# Ouput_Header_Units -- The units of the data appears at the top of output file
# Output_Header_Measurement_Type -- The type of measurement: Wind Vector, Average, Sample, Totalize


try:
    csvFile = open(keyfile.get('main', 'array_based_params_key_file'), 'r' )

except Exception, e:
    print "Could not obtain station info: ", e
    sys.exit(1)

csvReader = csv.DictReader(csvFile)
siteList={}
h = 0
for row in csvReader:
    # row['StationName'] = the element in the first column
    siteList[h] = row
    h+=1
# done with the key file
csvFile.close()



###################################################################################
##  create necessary output directories  if they haven't been made before:       ##
###################################################################################
if not os.path.exists(keyfile.get('main', 'output_dir')):
    os.mkdir(keyfile.get('main', 'output_dir'))
if not os.path.exists(keyfile.get('main', 'error_log_dir')):
    os.mkdir(keyfile.get('main', 'error_log_dir'))
if not os.path.exists(keyfile.get('main', 'qc_log_dir')):
    os.mkdir(keyfile.get('main', 'qc_log_dir'))



###################################################################################
##  read through the data parameters dictionary and pull out date columns        ##
##  then do some initial date work                                               ##
###################################################################################

####################################################################################################################################################
## A list of 'Data_Type' choices:                                                                                                                 ##
## ignore = something to be ignored (not going into the output) like the array ID for example                                                     ##
## datey  = year from array based data file                                                                                                       ##
## dated  = julian day from array based data file                                                                                                 ##
## dateh  = time in 'hhmm' format                                                                                                                 ##
## tmstmp = regular date & time format (but may need reformatting)                                                                                ##
## num    = normal float                                                                                                                          ##
## therm  = thermistor... specify the coefficients in the coefficient table.                                                                      ##
## poly   = polynomial... specify the coefficients in the coefficient table.                                                                      ##
## net    = net radiation... specify in the coefficients table the windspeed column so net can be corrected if needed                             ##
## precip = Could do a totalize down the road but for present, maybe check the air temperature (column specified in the coefficients table again) ##
####################################################################################################################################################

# initialize column deals for the date functions
yearcol = -1
daycol = -1
timecol = -1
tmstmpcol = -1

for element in siteList :
    col_type =  siteList[element]
    if col_type['Data_Type'] == 'datey' :
        yearcol = col_type['Input_Array_Pos']
    elif col_type['Data_Type'] == 'dated' :
        daycol = col_type['Input_Array_Pos']
    elif col_type['Data_Type'] == 'dateh' :
        timecol = col_type['Input_Array_Pos']
    elif col_type['Data_Type'] == 'tmstmpcol' :
        tmstmpcol = col_type['Input_Array_Pos']
# type change the values we pulled form the site dictioary from string to integer
yearcol = int(yearcol)
daycol = int(daycol)
timecol = int(timecol)
tmstmcol = int(tmstmpcol)

####################################################################################
##  1) Read in the entire input data file                                         ##
##  2) Read in the last date from each output data file                           ##
####################################################################################

## okay so now all the config stuff has been read in we're ready to start the processing.
## shortly down the road this will do more than just tear through a file and dump it, it will do the honest to goodness procesing
## as each data value comes through, but not quite to that point yet.

#####################################
## Reading in the input data file  ##
#####################################

# soon check out urllib package
# http://www.python.org/doc/2.4/lib/module-urllib.html
# this would allow reading files from a url like off the http://www.uaf.edu/water/projects/near-real-time/rawdatafiles/ link.
try:
    # So, now we read in the input data file and read through it.
    input_data_file_obj = urllib2.urlopen(keyfile.get('main','input_data_file'))
    # read in the entire file
    all_input_data = input_data_file_obj.readlines()
    skipped_rows = 0

except :
    print "** couldn't open the input data file"
    sys.exit(1)
output_file = {}

##################################################
## Reading in the last date in the individual   ##
## output data files / create new output data   ##
## files and the required headers               ##
##################################################

for element in siteList :
    col_type =  siteList[element]
    d_type = col_type['Data_Type']
    # a check to see if this is a column for output
    if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmp' :
        # we have a variable that needs outputting.
        # open the file for reading and appending.
        out_file_name = keyfile.get('main', 'output_dir') + col_type['d_element'] + '.csv'

        ## Check to see if the output file exists and has data in it already:
        if os.path.exists(out_file_name) :
            try :
                output_file[ col_type['d_element']] = open( out_file_name, 'a+')
                data_lines = output_file[ col_type['d_element']].readlines()
                last_line = data_lines[-1]
                # strip off the new line.
                last_line = last_line.rstrip()
                # split the last line
                last_line_array  = last_line.split(',')

                siteList[element]['last_date'] = last_line_array[0]
            except :
                print 'problem opening %s for reading and appending' % (out_file_name)
        ## it's a new file, need to create the header and such.
        else :
            try :


                output_file[ col_type['d_element']] = open( out_file_name , 'w')
                # file doesn't exist, so need to create it and place the header at the top.
                # Line 1
                out_string = '"TOA5",' +  keyfile.get('main', 'station_name') + ',' + keyfile.get('main', 'logger_type') + os.linesep
                output_file[col_type['d_element']].writelines(out_string)
                # line 2
                out_string = '"TimeStamp",' + col_type['Output_Header_Name'] + os.linesep
                output_file[col_type['d_element']].writelines(out_string)
                # Line 3
                out_string = '"",'+ col_type['Ouput_Header_Units'] + os.linesep
                # Line 4
                output_file[col_type['d_element']].writelines(out_string)
                out_string = '"",' +  col_type['Output_Header_Measurement_Type'] + os.linesep
                output_file[col_type['d_element']].writelines(out_string)
                siteList[element]['last_date'] = -1
            except :
                print 'problem opening %s for writing' % (out_file_name)

##################################################
##  Run through the input data file             ##
##################################################
skippedlines = 0
# loop through the lines in data input file
for line in all_input_data :
    # strip new lines and whitespace off the far end of the string:
    line = line.rstrip()
    in_array = line.split(',')
    #print line
    # skip lines at the top of the input files (if present)
    if skippedlines <= int( keyfile.get('main', 'first_data_line') ) :
        #print 'array: %i and %s' % (len(in_array), keyfile.get('main', 'arrays') )
        if len(in_array) == int(keyfile.get('main', 'arrays')) :
        #            print 'array_id = %s & %i,   logger type = %s' % (keyfile.get('main', 'array_id'), in_array[0], keyfile.get('main','logger_type'))
            if keyfile.get('main','logger_type') == 'CR10X' :
                # this is a check to make sure that we're looking at a line of data rather than text like a header.
                try:
                    array_id = int(in_array[0])
                    if int(keyfile.get('main', 'array_id')) == int(in_array[0])  :

                        # for qc step check:
                        oldline = line
                        # and increment...
                        skippedlines += 1
                except:
                    # a string so do nothing
                    pass
    # okay, the lines have been skipped, into the meat of the processing.
    if skippedlines > int(keyfile.get('main', 'first_data_line')) :

        if len(in_array) == int(keyfile.get('main', 'arrays')) :

            try:
                # Here is a test to make sure the first column value is really an integer
                array_id = int(in_array[0])
    #            print 'array_id = %s & %i,   logger type = %s' % (keyfile.get('main', 'array_id'), in_array[0], keyfile.get('main','logger_type'))
                if int(keyfile.get('main', 'array_id')) == int(in_array[0]) and keyfile.get('main','logger_type') == 'CR10X' :

                    ##################
                    ## Get the date ##
                    ##################
                    # case 1: table based data
                    if not (tmstmpcol == -1) :
                         datez =in_array[tmstmpcol]
                    # case 2:  array based data with a year column
                    elif not(yearcol==-1) :
                        hhmm = in_array[timecol]
                        day = int(in_array[daycol])
                        year = int(in_array[yearcol])
                        #print 'year = %i, day = %i, time = %s' % (year, day, hhmm)
                        datez = dp_funks.juliantodate(year, day, hhmm)
                    # case 3:  array based data without a year column
                    elif yearcol == -1 and tmstmpcol == -1 :
                        # then there isn't a year column.  do some fancy stuff... later
                        # fancy stuff could be like...
                        # so each program run this column check will happen and the comparison will be
                        # today's julian date vs. the one in the data file.
                        # if today's julian data is less than the one in the data file then the data point
                        # in the data file is from the previous year.
                        # pop over to gp.py to see how the date stuff goes.
                        hhmm = in_array[timecol]
                        day = int(in_array[daycol])
                        year = dp_funks.getyear(day)
     #                   print line
     #                   print oldline
     #                   print 'year = %i, day = %i, time = %s' % (year, day, hhmm)
                        datez = dp_funks.juliantodate(year, day, hhmm)
    #                    print datez

                    # okay now datez looks like this: "2008-09-10 21:00:00"
                    # ready to move on to the rest.


                    ###########################################################
                    ## Loop through the variables for this line of data      ##
                    ###########################################################
                    for element in siteList :
                        ####################################################################
                        ## Check to see if this is an array element to process            ##
                        ####################################################################
                        d_type = siteList[element]['Data_Type']
                        if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmp' :

                            ####################################################################
                            ## Check to see if this is a new data point for the output file   ##
                            ####################################################################
                            if dp_funks.newdatacheck(datez, siteList[element]['last_date']) :
                                siteList[element]['last_date'] = datez
                                ###########################################################
                                ## Process data element and output to file               ##
                                ## dp_funks.data_process handles all data analysis,      ##
                                ## data transformation and qa/qc                         ##
                                ###########################################################
                                out_data =  dp_funks.data_process(siteList[element], \
                                                line, oldline, datez, \
                                                keyfile.get('main', 'error_log_dir'), \
                                                keyfile.get('main', 'qc_log_dir'), \
                                                keyfile.get('main', 'bad_data_val'))

                                out_string = ','.join([datez, str(out_data) + os.linesep])
                                output_file[siteList[element]['d_element']].writelines(out_string)

                    oldline = line
            except:
                # from higher up, if the column is a string then do nothing for this row of data.
                pass
###########################################################
## Close Input and Output Files                          ##
###########################################################
input_data_file_obj.close()
for element in siteList :

    # print element
    col_type =  siteList[element]
    d_type = col_type['Data_Type']
    if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmp' :
        output_file[col_type['d_element']].close





