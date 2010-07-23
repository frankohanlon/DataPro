#!/usr/bin/python -tt

"""This short program does daily averages of hourly etc. data.  There are several assumptions:
1) the data is in the normalized tob05 format (header + column 0 = date, column 1 = data)
2) standard date format in column 0 that is either:
 dd/mm/yyyy hh:mm:ss (if excel has touched the data) 
 yyyy-mm-dd hh:mm:ss (if it is straight from datapro)

So what else should I know?
3) the new file name will go from: airtemp1m.csv to airtemp1m_daily.csv so, split the filename by . then at the last one add the suffix.
4) should log somewhere, perhaps in this file how many values go into making the average.



"""
import sys
import os
import csv
import urllib2


def main():
    """ Main Program Body
    """

    # Command line interface here:
    if len(sys.argv) > 1 :
        # sys.argv[0] = the name of the python program being executed.
        input_data_file = sys.argv[1]  # The Data File
    # 1) open the data files for reading / writing.
    print 'Source:  ', sys.argv[1]
    try:
        hourly_input_file = open( input_data_file , 'r')
        all_input_data = hourly_input_file.readlines()
        hourly_input_file.close()
    except:
        print 'problem opening %s for reading' % (input_data_file)
    last_date_str = []
    last_date = 0
    file_review = 0
    daily_out_file_arr = input_data_file.split('\\')
    daily_out_file_dir = '\\'.join(daily_out_file_arr[0:-1])
    daily_out_file_dir += '\\daily\\'
    daily_out_file = daily_out_file_dir + daily_out_file_arr[-1].split('.')[0] + '_daily.csv'
    if not os.path.exists(daily_out_file_dir):
        os.mkdir(daily_out_file_dir)
    ## Check to see if the output file exists and has data in it already:
    if os.path.exists(daily_out_file) :
        try :
            print 'Daily Output: ', daily_out_file
            output_file = open(daily_out_file, 'r+')
            data_lines = output_file.readlines()
            last_line = data_lines[-1]
            # strip off the new line.
            last_line = last_line.rstrip()
            # split the last line
            last_line_array  = last_line.split(',')
            last_date_str = last_line_array[0].strip('"').split()[0].split('-')
            last_date = float(last_date_str[0]) + (float(last_date_str[1]) + float(last_date_str[2])/32)/ 13 
            file_review = 1
        except :
          print 'problem opening %s for appending' % (daily_out_file)
    else:
        try :
            
            output_file = open( daily_out_file , 'w')
            # file doesn't exist, so need to create it and place the header at the top.
            output_file.writelines(all_input_data[0])
            line = all_input_data[1].rstrip()
            line = ','.join([line ,'Count' + '\n'])
            output_file.writelines(line)
            
            output_file.writelines(all_input_data[2])
            line = all_input_data[3].rstrip()
            line = ','.join([line,'Count' + '\n'])
            output_file.writelines(line)            
            last_date = -1
        except :
            print 'problem opening %s for writing' % (daily_out_file)                
        
    # oh, also need to check out the daily file for the last entry there.
    ##################################################
    ##  Run through the input data file             ##
    ##################################################
    skippedlines = 0
    curdate = 0
    cursum = 0
    cur_indx = 0
    tempnum = 0
    # loop through the lines in data input file
    for line in all_input_data[4:] :
        # strip new lines and whitespace off the far end of the string:
        line = line.rstrip()
        in_array = line.split(',')
        # if last_date == -1 then all of the data needs to be processed... starting with line 1 of the data.
        if last_date == -1 :
            # this is a complicated lookking way of 1) stripping out the quotation mark, 2) splitting the date off from the time.
            last_date_str = in_array[0].strip('"').split()[0].split('-')
            last_date = float(last_date_str[0]) + (float(last_date_str[1]) + float(last_date_str[2])/32)/ 13 
            curdate = last_date
            tempnum = float(in_array[1])
            if tempnum != -6999 :
                cursum += tempnum
                cur_indx += 1
        # okay otherwise, not a special case... carry on
        else:
            # 1) check to see if it's a new day.
            # 1a) if it's not, incorporate this data into the accumulators
            # 2) if it is a new day, output it then
            # 3) reset accumulators
            # 4) read in new data
            # 5) move to next line.
            curdate_str = in_array[0].strip('"').split()[0].split('-')
            curdate = float(curdate_str[0]) + (float(curdate_str[1]) + float(curdate_str[2])/32)/ 13 
            
            if curdate == last_date :
#                print cur_date, curdate_str    
                # same day, increment the incrementer and add the data to the sum, if it's good data
                tempnum = float(in_array[1])

                if tempnum != -6999 :                    
                    cursum += tempnum
                    cur_indx += 1                
            elif curdate > last_date :
                # new day, initialize the output stuff
                avg =0
                out_tempstring = ''
                if file_review == 0 :
                    # if there is good data this interval then average and format for outputting otherwise, output-6999
                    if cur_indx >0 :
                        avg = cursum / cur_indx
                        out_tempstring = '%3.2f' % avg
                    else:
                        out_tempstring = '-6999'                    
                    # output data
                    out_date = '-'.join(last_date_str)
                    out_string = ','.join([out_date, out_tempstring, str(cur_indx) + '\n'])
                    output_file.writelines(out_string)
                else:
                    file_review = 0
                # reset accumulators etc.
                cursum = 0
                cur_indx = 0
                last_date = curdate
                last_date_str = curdate_str
                # read in the new data:
                tempnum = float(in_array[1])
                if tempnum != -6999 :
                    cursum += tempnum
                    cur_indx += 1                
    # and done...
    output_file.close()            


###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
