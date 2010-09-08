#!/usr/bin/python -tt

"""
This short program takes daily /  hourly data from multiple files and puts it all together into a single file.  
Handy for making the yearly products or also for making like the whiplash curve.

What I want it to do:
1) read in a key file I guess (.csv) & the name of the output file
2) process the key file ala datapro.py or gp.py
3) important columns in this file:
   + file name 
   + position in the output file of this data file
   + header information tob5 style for this new column

DataPro Utilities Regular
"""
import sys
import os
import csv
import urllib2
import ConfigParser
import numpy as N

def main():
    """ Main Program Body
    """
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

    ###################################################################################
    ##  read in the data variable specific configuration file                        ##
    ###################################################################################
    try:
        csvFile = open(keyfile.get('main', 'glom_params_key_file'), 'r' )
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
    ##  create necessary error & qc log directories  if they haven't been made before:       ##
    ###################################################################################
    if not os.path.exists(keyfile.get('main', 'error_log_dir')):
        os.mkdir(keyfile.get('main', 'error_log_dir'))
    if not os.path.exists(keyfile.get('main', 'qc_log_dir')):
        os.mkdir(keyfile.get('main', 'qc_log_dir'))

    # add to the key file some glom specific params.  have a glom prefix.
    # I'm thinking: 
    # the csv components should be like:
    # 1) data element
    # 2) order in the output data file
    # 3) header information lines 1 - 3 (data element specific)
    # 4) File Name & absolute location
    # in the key file
    # 1) Output filename & directory
    # 2) Interval e.g. 2009, all
    # 3) error & qc log information

    # so, after the key file has been read in and so has the parameter csv what next?
    # + read in each file... check
    # + load columns 0 and 1 into a big array (be specific so it doesn't matter if it is one column or two) 
    # + move to the next file and do the same
    # + once all of the files are loaded into memory then ... check
    # + make sure that each is represented at every time step.
    # + date-time module for time step comparisons.
    pre_glom_data = {} 
    header_line_1 = ''
    header_line_2 = []
    header_line_3 = []
    header_line_4 = []
    header_line_2 = [''] * (len(siteList)+1)
    header_line_3 = [''] * (len(siteList)+1)
    header_line_4 = [''] * (len(siteList)+1)
    header_line_2[0] = '"TimeStamp"'
    
    for element in siteList :
        col_type =  siteList[element]
        in_file_name = col_type['File_Loc']
        ## Check to see if the input file exists
        if os.path.exists(in_file_name) :
            try :
                # open current data file, read in the file ignoring the header and
                # then splitting the file into a 2D array by time and the first two data elements
                # (hourly data should have 2 data elements, daily data should have 3 data elements)
                in_file_handle = open( in_file_name, 'r')                
                data = in_file_handle.readlines()
                header_line_1 = data[0].split(',')[0] + '\n'
                input_array = []
                in_file_handle.close()
                for line in data[4:] :
                    line = line.rstrip()
                    input_array.append(line.split(',')[0:2])
                # finally, drop the 2D array into a dict
                pre_glom_data[ int(col_type['Output_Array_Pos'])] = input_array
                # also, the header stuff...
                header_line_2[int(col_type['Output_Array_Pos'])] = col_type['Output_Header_Line_2']
                header_line_3[int(col_type['Output_Array_Pos'])] = col_type['Output_Header_Line_3']
                header_line_4[int(col_type['Output_Array_Pos'])] = col_type['Output_Header_Line_4']
            except :
                print 'problem opening %s for reading.' % (in_file_name)

    # Now all the data has been read in.  On to the glomming.
    # need to think this through some more.
    # I could maybe for starters declare '0' as the complete record.
    # then, pattern search for the time/date stamp in column 0 of the matrix.
    # when it's found then append the data value element to that array... that is the best I have at the moment.
    # surely there's a better way though.

    # jessie suggests converting dates to time in seconds and using that... I think that may be a promising route
    # and it will also make it easier to cover discrete periods like 2009 or last 90 days etc.

    # initializations:
    junk = []
    junk = [''] * (len(pre_glom_data) + 1 )
    longjunk = []
#    print header_line_2
#    print header_line_3
#    print header_line_4
    glom_data = pre_glom_data[1]
    for data_vector in glom_data :
        junk[0] = data_vector[0]
        longjunk.extend(junk)
    # now the date is in column 0 time to get the individual data bits into the main part.
    for index in pre_glom_data :
        interval = pre_glom_data[index]
        for stuff in interval :
            try:
                longjunk[longjunk.index(stuff[0]) + index ] = stuff[1]
            except:
                #longjunk[longjunk.index(stuff[0]) + index ] = 6999
                print 'error'
    # now that all of the data is into the proper spot... put the list into the right dimensions using numpy
    columns = len(pre_glom_data) + 1
    rows = len(longjunk) / columns
    shape = (rows, columns)
    n_array = N.array(longjunk)
    n_array = n_array.reshape(shape)
    final_glom = n_array.tolist()
    # finally, export complete with headers.
    try:
        out_file_handle = open(keyfile.get('main', 'output_data_file'), 'w')        
        out_file_handle.writelines(header_line_1)
        out_string = ','.join(header_line_2) + '\n'
        out_file_handle.writelines(out_string)
        out_string = ','.join(header_line_3) + '\n'
        out_file_handle.writelines(out_string)
        out_string = ','.join(header_line_4) + '\n'
        out_file_handle.writelines(out_string)
        for line in final_glom :
            out_string = ','.join(line) + '\n'
            out_file_handle.writelines(out_string)
    except:    
        print 'error opening %s for writing' % (keyfile.get('main', 'output_data_file'))

###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
