import argparse
import time
import datetime
import datetime as dt

bad_data_value = 6999
OutFilePresent = False
from dp_funks import netrad
# For help from the command line, type either:
# python OptionalArgWNetRad.py -h
# or 
# python OptionalArgWNetRad.py --h
##################################################
# Run this file from Aptana Studio by typing:
#C:\bobs_folders\py_datapro\DataPro_Sample_Files\outputs\array_netrad.csv
#C:\bobs_folders\py_datapro\DataPro_Sample_Files\outputs\array_windspeed.csv -n 10 20
#C:\bobs_folders\py_datapro\DataPro_Sample_Files\outputs\outputfile.csv
# AND by having ${string_prompt} ${string_prompt} ${string_prompt} in the run configuration argument list 
# (Don't forget to insert a space between the two string prompts in the run configuration.)
##################################################
# Run this code as a netrad adjuster from the command line by typing:
# python OptionArgWNetRad.py 
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\array_netrad.csv
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\array_windspeed.csv -n 10 20
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\outputfile_netrad_adjusted.csv
##################################################
# Run this code as a glomming together tool from the command line by typing:
# python OptionArgWNetRad.py 
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\array_Temperature.csv
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\array_Battery.csv 
#C:\\bobs_folders\\py_datapro\\DataPro_Sample_Files\\outputs\\outputfile.csv
parser = argparse.ArgumentParser(description = 'reads first and last dates from two output files \n filename1 and filename2')
parser.add_argument("filename1", help="Directory and the first filename (This should be the raw rad file if the -netrad option is chosen)"\
                    , type =str)
parser.add_argument("filename2", help="Directory and the second filename (This should be the windspeed file if the -netrad option is chosen)"\
                    , type =str)
parser.add_argument("outputfile", help="Directory and the filename of the output file"\
                    , type =str)
parser.add_argument('--n','-n','--N','-N','--r','-r','--R','-R','--netrad','-netrad', help=" Two floating point decimals will need to follow this optional argument: \
    The first floating point value represents the multiplier for positive data values.  \
    The second floating point value represents the multiplier for negative data values. \
    Using the optional argument will cause the code  \
    to assume that filename1 is the raw radiation file and that filename2 is the windspeed file.  \
    WITHOUT this optional argument, filename1 and filename2 will just be glommed together"
    , nargs =2  , type =float)
args = parser.parse_args()
print ('%r',args)
#try:
#    print args.n[0]
#    print args.n[1]
#except:
#    pass
ProcessNetRad = False
#if args.netrad:
#    print "time to process netrad\n"
#    ProcessNetRad = True
#else:
#    print "not time to process netrad\n"
##################################################### PROCESS first file
print "File being opened is: "
print args.filename1
first_file_object = open(args.filename1,'r')
data1 = first_file_object.readlines()
first_line_file1 = data1[4]
last_line_file1 = data1[-1]
first_line_file1 = first_line_file1.rstrip()
last_line_file1 = last_line_file1.rstrip()
first_line_file1_array= first_line_file1.split(',')
last_line_file1_array= last_line_file1.split(',')

#print "\n"
#print first_line_file1_array[0]
#print "\n"
#ymd=time.strptime(first_line_file1_array[0].strip('"').split()[0],'%Y-%m-%d')[0:3]
#print "ymd: ", ymd;
#print "\n"
#hms=time.strptime(first_line_file1_array[0].strip('"').split()[1],'%H:%M:%S')[3:6]
#print "hms: ", hms
#print "\n"
YmdHmsStart1 = time.strptime(first_line_file1_array[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
YmdHmsEnd1 = time.strptime(last_line_file1_array[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
Start1 = datetime.datetime(YmdHmsStart1[0], YmdHmsStart1[1], YmdHmsStart1[2], YmdHmsStart1[3], YmdHmsStart1[4], YmdHmsStart1[5])
End1 = datetime.datetime(YmdHmsEnd1[0], YmdHmsEnd1[1], YmdHmsEnd1[2], YmdHmsEnd1[3], YmdHmsEnd1[4], YmdHmsEnd1[5])

first_date_str_file1 = first_line_file1_array[0].strip('"').split()[0].split('-')
last_date_str_file1 = last_line_file1_array[0].strip('"').split()[0].split('-')
first_time_str_file1 = first_line_file1_array[0].strip('"').split()[1].split(':')
last_time_str_file1 = last_line_file1_array[0].strip('"').split()[1].split(':')
##########################################PROCESS SECOND FILE
print "File being opened is: "
print args.filename2
second_file_object = open(args.filename2,'r')
data2 = second_file_object.readlines()
first_line_file2 = data2[4]
last_line_file2 = data2[-1]
first_line_file2 = first_line_file2.rstrip()
last_line_file2 = last_line_file2.rstrip()
first_line_file2_array= first_line_file2.split(',')
last_line_file2_array= last_line_file2.split(',')

YmdHmsStart2 = time.strptime(first_line_file2_array[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
YmdHmsEnd2 = time.strptime(last_line_file2_array[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
Start2 = datetime.datetime(YmdHmsStart2[0], YmdHmsStart2[1], YmdHmsStart2[2], YmdHmsStart2[3], YmdHmsStart2[4], YmdHmsStart2[5])
End2 = datetime.datetime(YmdHmsEnd2[0], YmdHmsEnd2[1], YmdHmsEnd2[2], YmdHmsEnd2[3], YmdHmsEnd2[4], YmdHmsEnd2[5])

first_date_str_file2 = first_line_file2_array[0].strip('"').split()[0].split('-')
last_date_str_file2 = last_line_file2_array[0].strip('"').split()[0].split('-')
first_time_str_file2 = first_line_file2_array[0].strip('"').split()[1].split(':')
last_time_str_file2 = last_line_file2_array[0].strip('"').split()[1].split(':')
##################################
#        Summarize dates of the Input files
###################################

if Start1 < Start2:
    print "first file starts before the second one\n"
    StartDateOutput = Start2
else:
    print "second file starts before or at the same time as the first one\n"
    StartDateOutput = Start1
if End1 < End2:
    print "first file ends before the second one\n"
    EndDateOutput = End1
else:
    print "second file ends before or at the same time as the first one\n"
    EndDateOutput = End2
##########################################
# Prepare input data and header info
########################################
datafile1 = data1[4:]
datafile2 = data2[4:]
if args.n:
    header1 =  'after netrad'+ '\n'
else:
    header1 =  'after glom' + '\n'
header2 = data1[1] 
header3 = data1[2] 
header4 = data1[3] 

##################################
#                  Process  outputfile.csv
#################################

DataWDatesToProcess = False
try:
    print "Outputfile is: \n"
    print args.outputfile
    outputfile_handle = open(args.outputfile,'r')
    OutFilePresent=True  ###CAUTION!!!  This assumes that if the out file is there, it has some data in it
    dataout= outputfile_handle.readlines()
    lastline_dataout = dataout[-1]
    lastline_dataout= lastline_dataout.rstrip()
    lastline_outfile_array=lastline_dataout.split(',')
    YmdHmsEndOut = time.strptime(lastline_outfile_array[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
    EndDate_OutFile= datetime.datetime(YmdHmsEndOut[0],YmdHmsEndOut[1],YmdHmsEndOut[2],YmdHmsEndOut[3],\
                                   YmdHmsEndOut[4],YmdHmsEndOut[5])
    outputfile_handle.close()
    if (EndDate_OutFile >=StartDateOutput) and \
        (EndDate_OutFile < EndDateOutput) and \
        (StartDateOutput < EndDateOutput):
        StartDateOutput = EndDate_OutFile
        print "We can consolidate the files\n"
        DataWDatesToProcess = True
    elif (StartDateOutput < EndDateOutput) and \
        (EndDate_OutFile < StartDateOutput):
        print "We can consolidate the files\n"
        DataWDatesToProcess = True
    else:
        print args.filename1 
        print "\n and \n"
        print args.filename2
        print "\n do not have new data to add to: \n"
        print args.outputfile +'\n'

    print "The output file has end date: \n"
    print EndDate_OutFile         
except:
    print "There is no outputfile.  It will therefore be created."
    outputfile_handle = open(args.outputfile,'w')
    outputfile_handle.writelines(header1)
    outputfile_handle.writelines(header2)
    outputfile_handle.writelines(header3)
    outputfile_handle.writelines(header4)
    outputfile_handle.close()
    if StartDateOutput <= EndDateOutput:
        DataWDatesToProcess = True
    else:
        print args.filename1 
        print "\n and \n"
        print args.filename2
        print "\n don't have overlapping data."
############################################SUMMARIZE

print "first file: \n"
print first_date_str_file1 + first_time_str_file1
print "\n"
print last_date_str_file1 + last_time_str_file1
print "\n"
print "second file: \n"
print first_date_str_file2 + first_time_str_file2
print "\n"
print last_date_str_file2 + last_time_str_file2


###################################################################
#             Find the starting line numbers for the individual input files
####################################################################
file1_linenum =0 
file1_linestart = 0
for line_one in datafile1:
    lineof_dataone= line_one.rstrip()
    linearray_one = line_one.split(',')
    YmdHmdline_one = time.strptime(linearray_one[0].strip('"'),'%Y-%m-%d %H:%M:%S')
    Timeline_one=datetime.datetime(YmdHmdline_one[0],YmdHmdline_one[1],YmdHmdline_one[2],\
                                   YmdHmdline_one[3],YmdHmdline_one[4],YmdHmdline_one[5])
    if Timeline_one == StartDateOutput:
        file1_linestart = file1_linenum
    else:
        pass
    file1_linenum += 1
print "Startline for file1: \n"  +  str(file1_linestart)
file2_linenum = 0 
file2_linestart = 0
for line_two in datafile2:
    lineof_datatwo= line_two.rstrip()
    linearray_two = line_two.split(',')
    YmdHmdline_two = time.strptime(linearray_two[0].strip('"'),'%Y-%m-%d %H:%M:%S')
    Timeline_two=datetime.datetime(YmdHmdline_two[0],YmdHmdline_two[1],YmdHmdline_two[2],\
                                   YmdHmdline_two[3],YmdHmdline_two[4],YmdHmdline_two[5])
    if Timeline_two == StartDateOutput:
        file2_linestart = file2_linenum
    else:
        pass
    file2_linenum += 1
print "Startline for file2: \n"  +  str(file2_linestart)  
#########################  Send data to outfile
#Send data to outfile
##################################################
if OutFilePresent:
    fileone_line = file1_linestart+1
    filetwo_line = file2_linestart+1    
else:
    fileone_line = file1_linestart
    filetwo_line = file2_linestart
n1 = dt.datetime.now()
    
TimeDiffOutput = EndDateOutput - StartDateOutput
TimeDiffOutputInSeconds = TimeDiffOutput.days *86400 +TimeDiffOutput.seconds
NumberOfLinesToProcess =  int(TimeDiffOutputInSeconds/3600)  +1
print "Number of lines to send to the output file:\n"
print NumberOfLinesToProcess
if DataWDatesToProcess:
    try:
            out_file_handle = open(args.outputfile,'a')
        
            
            while (fileone_line < NumberOfLinesToProcess):
            #create string from input files and send out to the outputfile
                currentline1 = datafile1[fileone_line].rstrip()
                currentarray1 = currentline1.split(',')
                NumArray1Columns = len(currentarray1)
                currentline2 = datafile2[filetwo_line].rstrip()
                currentarray2 = currentline2.split(',')
                NumArray2Columns = len(currentarray2)
                YmdHmdcurrentline1 = time.strptime(currentarray1[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
                #YmdHmdcurrentline2 = time.strptime(currentarray2[0].strip('"'),'%Y-%m-%d %H:%M:%S')[0:6]
                currentDate = datetime.datetime(YmdHmdcurrentline1[0],YmdHmdcurrentline1[1],YmdHmdcurrentline1[2],\
                                   YmdHmdcurrentline1[3],YmdHmdcurrentline1[4],YmdHmdcurrentline1[5])
                column_num1 = 0
                column_num2 = 0
                if args.n:
                    outstring = currentarray1[0]+',' + \
                    '%.3f' %netrad(float(currentarray1[1]),float(currentarray2[1]),\
                               float(args.n[0]),float(args.n[1]),bad_data_value)\
                               + '\n'
                else:
                    outstring = currentarray1[0]+','
                    while column_num1 < NumArray1Columns-1:
                        column_num1 +=1    
                        outstring = outstring + currentarray1[column_num1]+','
                    while column_num2 < NumArray2Columns-1:
                        column_num2 +=1
                        outstring += currentarray2[column_num2] + ','
                    outstring = outstring + '\n'
                out_file_handle.writelines(outstring)
                fileone_line =fileone_line + 1
                filetwo_line =filetwo_line + 1
            out_file_handle.close()
    except:
            print "couldn't open the outputfile"

else:
    print "There are no dates to process"
###################################################################
############     Pull DATA between StartDateOutPut and EndDateOutput 
############     from filename1 AND filename2

n2 = dt.datetime.now()
print "The elapse time is:  " + str((n2.microsecond-n1.microsecond)/1e6) + "seconds\n"

#######CLOSE FILES
first_file_object.flush()
first_file_object.close()
second_file_object.flush()
second_file_object.close()

