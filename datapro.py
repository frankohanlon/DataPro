#!/usr/bin/python -tt

"""
IARC data processing project
****************************

This short program converts CR10X array data from julian to the table based date format and
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

DataPro Regular
"""

import ConfigParser
import os
import sys
import dp_funks  # data_pro function library
import csv
import urllib2

VERSION = '0.2'

therm_1_res = []
therm_1_a = []
therm_1_b = []
therm_1_c = []
therm_2_res = []
therm_2_a = []
therm_2_b = []
therm_2_c = []


processline = False

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
# Allow an alternate input data file name to be specified on the command line.
# for example, one site we need to include in the data processing has the year and month appended (specific example here):
#   (this data comes from an external ftp site)
#   Hokudai_Iwahana_01_CR1000_201206.dat
#   Hokudai_Iwahana_01_CR1000_201207.dat
# another specific case is a direct data download.  In that case the key files (both csv and txt) may be the same as the previous visit but the data file will have a different name like:
#   NFHS_Diagnostic_2012_04_03.dat
#   BJ_NorthFacing_High_Diagnostic-2012_04_27.dat

try:
    altdatafile = sys.argv[2]
except:
    # otherwise, default to ignore the alt file name
    altdatafile = 'null'
    
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
    
# Allow an alternate input data file name to be specified on the command line.
if altdatafile != 'null' :
    keyfile.set('main','input_data_file', altdatafile)

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
try:
    csvFileQClogger = open(keyfile.get('main', 'qc_log_record'), 'a' )

except:
    pass


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
if (keyfile.get('main', 'logger_type') == 'CR10X' or keyfile.get('main', 'logger_type') == 'Array') :
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
elif (keyfile.get('main', 'logger_type') == 'Table' ) :
    for element in siteList :    
        col_type = siteList[element]
        if col_type['Data_Type'] == 'tmstmpcol' :
            tmstmpcol = int(col_type['Input_Array_Pos'])

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
###############################################
## Try reading in a couple thermistor files  ##
###############################################
if keyfile.get('main','therm1') != 'null':
    try:
        therm1_fh = open(keyfile.get('main', 'therm1'), 'r')
        all_therms = therm1_fh.readlines()
        for line in all_therms[2:] :
            # strip new lines and whitespace off the far end of the string:
            line = line.rstrip()
            line_split = line.split(',')
            therm_1_res.append(float(line_split[0]))
            therm_1_a.append(float(line_split[2]))
            therm_1_b.append(float(line_split[3]))
            therm_1_c.append(float(line_split[4]))
        therm1_fh.close()
    except:
        print 'problem opening therm_1 file for reading; either set in key to null: "therm1 = null" or check the file location.'
        sys.exit(1)
if keyfile.get('main','therm2') != 'null':
    try:
        therm2_fh = open(keyfile.get('main', 'therm2'), 'r')
        all_therms = therm2_fh.readlines()
        for line in all_therms[2:] :
            # strip new lines and whitespace off the far end of the string:
            line = line.rstrip()
            line_split = line.split(',')
            therm_2_res.append(float(line_split[0]))
            therm_2_a.append(float(line_split[2]))
            therm_2_b.append(float(line_split[3]))
            therm_2_c.append(float(line_split[4]))
        therm2_fh.close()
    except:
        print 'problem opening therm_2 file for reading; either set in key to null: "therm1 = null" or check the file location.'
        sys.exit(1)

##################################################
## Reading in the last date in the individual   ##
## output data files / create new output data   ##
## files and the required headers               ##
##################################################

for element in siteList :
    col_type =  siteList[element]
    d_type = col_type['Data_Type']
    # a check to see if this is a column for output
    if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmpcol' :
        # we have a variable that needs outputting.
        # open the file for reading and appending.
        out_file_name = keyfile.get('main', 'output_dir') + col_type['d_element'] + '.csv'

        ## Check to see if the output file exists and has data in it already:
        if os.path.exists(out_file_name) :
            try :
                output_file[ col_type['d_element']] = open( out_file_name, 'r')
                data_lines = output_file[ col_type['d_element']].readlines()
                output_file[col_type['d_element']].close
                output_file[ col_type['d_element']] = open( out_file_name, 'a')
                last_line = data_lines[-1]
                # strip off the new line.
                last_line = last_line.rstrip()
                # split the last line
                last_line_array  = last_line.split(',')
                siteList[element]['last_date'] = last_line_array[0]
            except :
                print 'problem opening %s for reading and appending' % (out_file_name)
                sys.exit(1)
        ## it's a new file, need to create the header and such.
        else :
            try :


                output_file[ col_type['d_element']] = open( out_file_name , 'w')
                # file doesn't exist, so need to create it and place the header at the top.
                # Line 1
                out_string = '"TOA5",' +  keyfile.get('main', 'station_name') + ',' + keyfile.get('main', 'logger_type') + '\n'
                output_file[col_type['d_element']].writelines(out_string)
                # line 2
                out_string = '"TimeStamp",' + col_type['Output_Header_Name'] + '\n'
                output_file[col_type['d_element']].writelines(out_string)
                # Line 3
                out_string = '"",'+ col_type['Ouput_Header_Units'] + '\n'
                # Line 4
                output_file[col_type['d_element']].writelines(out_string)
                out_string = '"",' +  col_type['Output_Header_Measurement_Type'] + '\n'
                output_file[col_type['d_element']].writelines(out_string)
                siteList[element]['last_date'] = -1
            except :
                print 'problem opening %s for writing' % (out_file_name)
                sys.exit(1)

length_oldline = int(keyfile.get('main','arrays'))
oldline = ''
i = 0
while (i < length_oldline-1):
    oldline = oldline +','
    i = i +1
##################################################
##  Run through the input data file             ##
##################################################
# loop through the lines in data input file

firstLineOfData =True


for line in all_input_data :
    # strip new lines and whitespace off the far end of the string:
  
    line = line.rstrip()
    in_array = line.split(',')
    # this if statement says if the length of the line is the same as the # of arrays specified in the key file then proceed
    # with processing the potential data.
    if len(in_array) == int(keyfile.get('main', 'arrays')) :
        # okay, the # of array element match up what next?
        # well, for array based element 0 will be a number
        # and for table element 0 will have "yyyy-mm-dd hh:mm" 18 or 21 characters as a string
        arrayheadtemp = in_array[0]
        # this is a check to make sure that we're looking at the right line of data rather than text like a header.
        # this is only true the first time we hit good data.
        if firstLineOfData == True and (keyfile.get('main','logger_type') == 'CR10X' or keyfile.get('main','logger_type') == 'Array' and in_array[0].isdigit() ) :
            if  in_array[0] != 'program' :
                if int(keyfile.get('main', 'array_id')) == int(in_array[0]) :
                    oldline = line
                    firstLineOfData = False
        elif firstLineOfData == True and (oldline == '' and len(arrayheadtemp) >=19 and arrayheadtemp[1:5].isdigit() and keyfile.get('main', 'logger_type') == 'Table' ):             
                    oldline = line   
                    firstLineOfData = False
        # so... .where to break this off... I think this section will
        # need some rewriting so that array logger code coexists with the
        # table.
        # maybe set a boolean for yes/no if the array id        
        if in_array[0].isdigit() and \
                    (keyfile.get('main','logger_type') == 'CR10X' or keyfile.get('main','logger_type') == 'Array') :
            if int(keyfile.get('main', 'array_id')) == int(in_array[0]) :
                ##################
                ## Get the date ##
                ##################
                # case 1:  array based data with a year column
                if not(yearcol==-1) :
                    hhmm = in_array[timecol]
                    day = int(in_array[daycol])
                    year = int(in_array[yearcol])
                    datez = dp_funks.juliantodate(year, day, hhmm)
                    processline = True
                # case 2:  array based data without a year column
                elif yearcol == -1 :
                    # then there isn't a year column.  do some fancy stuff... later
                    # fancy stuff could be like...
                    # so each program run this column check will happen and the comparison will be
                    # today's julian date vs. the one in the data file.
                    # if today's julian data is less than the one in the data file then the data point
                    # in the data file is from the previous year.
                    # pop over to gp.py to see how the date stuff goes.
                    #print in_array
                    hhmm = in_array[timecol]
                    day = int(in_array[daycol])
                    year = dp_funks.getyear(day)
                    datez = dp_funks.juliantodate(year, day, hhmm)
                    #print hhmm, day, year, datez
                    processline = True
                else:
                    print 'processline == false'
                    processline = False
        elif len(arrayheadtemp) >=19 and arrayheadtemp[1:5].isdigit() and keyfile.get('main', 'logger_type') == 'Table' :    
            # case 2: table based data
            if not (tmstmpcol == -1) :
                ## Need to introduce a special test here to look for funky time series data like:
                ## 2011-02-01 22:00:58.5
                if (len(in_array[tmstmpcol].split('.')) == 1) :
                    datez = in_array[tmstmpcol]
                    processline = True
                else:
                    
                    processline = False
        else:
            processline = False
            # okay now datez looks like this: "2008-09-10 21:00:00"
            # ready to move on to the rest.
        ###########################################################
        ## Loop through the variables for this line of data      ##
        ###########################################################
        if processline == True :
            ###########################################################
            ## Loop through the variables for this line of data      ##
            ###########################################################

            
            bad_data_inc=0
            for element in siteList :
                ####################################################################
                ## Check to see if this is an array element to process            ##
                ####################################################################
                d_type = siteList[element]['Data_Type']
                if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmpcol' :
                    
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
                        if d_type == 'therm_1' :
                            # pass S&H stuff along with the rest.

                            out_data =  dp_funks.data_process_therm(siteList[element], \
                                        line, oldline, datez, \
                                        keyfile.get('main', 'error_log_dir'), \
                                        keyfile.get('main', 'qc_log_dir'), \
                                        therm_1_res, therm_1_a, therm_1_b, therm_1_c, \
                                        float(keyfile.get('main', 'bad_data_val')) \
                                        )


                        elif d_type == 'therm_2' :
                            # pass S&H stuff along with the rest.

                            out_data =  dp_funks.data_process_therm(siteList[element], \
                                        line, oldline, datez, \
                                        keyfile.get('main', 'error_log_dir'), \
                                        keyfile.get('main', 'qc_log_dir'), \
                                        therm_2_res, therm_2_a, therm_2_b, therm_2_c, \
                                        float( str(data_element) - float(old_data_element),) \
                                        )


                        else :
                        
                            out_data =  dp_funks.data_process(siteList[element], \
                                        line, oldline, datez, \
                                        keyfile.get('main', 'error_log_dir'), \
                                        keyfile.get('main', 'qc_log_dir'), \
                                        float(keyfile.get('main', 'bad_data_val'))\
                                        )
                        #print out_data
                        if out_data == float(keyfile.get('main','bad_data_val')):
                            bad_data_inc +=1
                        out_tempstring = '%3.2f' % (out_data)
                        out_string = ','.join([datez, str(out_tempstring) + '\n'])
                        output_file[siteList[element]['d_element']].writelines(out_string)
            bad_data_str = ','.join([datez,str(bad_data_inc)+'\n'])
            try:
                
                csvFileQClogger.writelines(bad_data_str)
            except:
                pass
            oldline = line
###########################################################
## Close Input and Output Files                          ##
###########################################################
try:
    csvFileQClogger.close()
except:
    pass
input_data_file_obj.close()
for element in siteList :

    # print element
    col_type =  siteList[element]
    d_type = col_type['Data_Type']
    if d_type != 'ignore' and d_type != 'datey' and d_type != 'dated' and d_type != 'dateh' and d_type != 'tmstmpcol' :
        output_file[col_type['d_element']].close





