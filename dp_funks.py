#!/usr/bin/python -tt

"""This module provides initial function support for datapro.py.
Functions:
DataPro/dp_funks.py
juliantodate (yearz, jdayz, hhmm)
    arg 0 = year
    arg 1 = julian_day
    arg 2 = Time (hhmm format)
    Return = date string in T05 format,  "2008-09-06 17:00:00"

data_process (data_point_dict, line, oldline, thedate, error_dir, bad_data_val=6999)
    arg 0 = siteList dictionary list element
    arg 1 = current line of data from input file
    arg 2 = previous line of data from input file
    arg 3 = the current date (for qa/qc)
    arg 4 = qaqc directory
    arg 5 = bad data value  (default is 6999 but could be changed by specifying in the key file)
    Return = properly formatted string of processed data

qc_check(data_element, qc_high, qc_low, qc_step, bad_data_val)
    arg 0 = the data element from the input data file
    arg 1 = the previous time step data element from the input data file
    arg 2 = the current month for the monthly qc thresholds.
    arg 3 = the high qc threshold; default is 0, can either pass one value or twelve semi-colon separated values
    arg 4 = the low qc threshold; default is 0, can either pass one value or twelve semi-colon separated values
    arg 5 = the between time steps max increment; default is 0, can either pass one value or twelve semi-colon separated values
    arg 6 = the bad data value code; default is 6999
    Return = data value that has had some qa/qc

thermistor(data_element, coef_A, coef_B, coef_C, bad_data_val)
    arg 0 = the data element from the input data file
    arg 1 = the steinhart-hart equation coeficcient A
    arg 2 = the steinhart-hart equation coeficcient B
    arg 3 = the steinhart-hart equation coeficcient C
    arg 4 = bad data value (in case there are errors)
    Return = temperature in degrees Celsius.

poly(data_element, coef_0, coef_1, coef_2, coef_3, coef_4, coef_5, coef_6, bad_data_val)
    arg 0 = the data element from the input data file
    arg 1 = 0th order coefficient (coef_0  * data_element ^ 0)
    arg 2 = 1st order coefficient (coef_1  * data_element ^ 1)
    arg 3 = 2nd order coefficient (coef_2  * data_element ^ 2)
    arg 4 = 3rd order coefficient (coef_3  * data_element ^ 3)
    arg 5 = 4th order coefficient (coef_4  * data_element ^ 4)
    arg 6 = 5th order coefficient (coef_5  * data_element ^ 5)
    arg 7 = 6th order coefficient (coef_6  * data_element ^ 6)
    arg 8 = bad data value (in case of error)
    Return = result from the polynomial

flux(data_element, posical, negacal, bad_data_val)
    arg 0 = the data element from the input data file
    arg 1 = multiplier for a positive data element value (posical * data_element)
    arg 2 = multiplier for a negative data element value (negacal * data_element)
    arg 3 = bad data value (in case of error)
    Return = if (data_element >= 0) then: (posical * data_element) else: (negacal * data_element)
    
rt_sensor(data_element, val_a, val_b, val_c, bad_data_val)
   arg 0 = the data element from the input data file
   arg 1 = a divsor
   arg 2 = an offset
   arg 3 = a multiplier
   arg 4 = bad data value (in case or error)
   Return = ( ( data_element / val_a ) + val_b ) / val_c
   
getyear(jday)
    arg 0 = the julian day from the input file
    Return = the year value the julian day comes from.  Choices are this year and last year.  
             This function addresses data that comes from arrays without a year column.

"""


def juliantodate(yearz, jdayz, hhmm):
    """take a julian day plus time and return a regular date
    arg 0 = year
    arg 1 = julian day
    arg 2 = time (hhmm format)
    Return = Date that looks like:  "2008-09-06 17:00:00"
    """
    # first up do the time.
    hourz = ''
    minutez = ''
    dayz = ''
    monthz = ''
    if len(hhmm) == 4 :
        hourz = hhmm[:2]
        minutez =hhmm[2:]
    elif len(hhmm) == 3 :
        hourz = '0' + hhmm[:1]
        minutez = hhmm[1:]
    elif len(hhmm) == 2 :
        hourz = '00'
        minutez = hhmm
    elif len(hhmm) == 1 :
        hourz = '00'
        minutez = '0' + hhmm

    if int(hourz) == 24 :
        hourz = '00'
        jdayz +=1

    # next up calculate the day and month.
    if int(yearz) % 4 == 0 :
        # leapyear
        leap = 1
    else :
        leap = 0

    if int(jdayz) >= 1 and int(jdayz) <=31 :
        dayz = int(jdayz)
        monthz = '01'
    elif int(jdayz) >= 32 and int(jdayz) <=59 + leap :
        dayz = int(jdayz) - 31
        monthz = '02'
    elif int(jdayz) >= 60 + leap and int(jdayz) <=90 + leap :
        dayz = int(jdayz) - 59 - leap
        monthz = '03'
    elif int(jdayz) >= 91 + leap and int(jdayz) <=120 + leap :
        dayz = int(jdayz) - 90 - leap
        monthz = '04'
    elif int(jdayz) >= 121 + leap and int(jdayz) <=151 + leap :
        dayz = int(jdayz) - 120 - leap
        monthz = '05'
    elif int(jdayz) >= 152 + leap and int(jdayz) <=181 + leap :
        dayz = int(jdayz) - 151 - leap
        monthz = '06'
    elif int(jdayz) >= 182 + leap and int(jdayz) <=212 + leap :
        dayz = int(jdayz) - 181 - leap
        monthz = '07'
    elif int(jdayz) >= 213 + leap and int(jdayz) <=243 + leap :
        dayz = int(jdayz) - 212 - leap
        monthz = '08'
    elif int(jdayz) >= 244 + leap and int(jdayz) <=273 + leap :
        dayz = int(jdayz) - 243 - leap
        monthz = '09'
    elif int(jdayz) >= 274 + leap and int(jdayz) <=304 + leap :
        dayz = int(jdayz) - 273 - leap
        monthz = '10'
    elif int(jdayz) >= 305 + leap and int(jdayz) <=334 + leap :
        dayz = int(jdayz) - 304 - leap
        monthz = '11'
    elif int(jdayz) >= 335 + leap and int(jdayz) <=367 :
        if leap==0 and int(jdayz)==366 :
            yearz +=1
            dayz = 1
            monthz = '01'
        elif leap == 1 and int(jdayz)==367 :
            yearz +=1
            dayz = 1
            monthz = '01'
        else:
            dayz = int(jdayz) - 334 - leap
            monthz = '12'
    if monthz =='' :
        print str(yearz), str(jdayz), str(hhmm), str(leap)
    # okay so now we've got all that wrapped.
    # "2008-09-06 17:00:00"
    if dayz >=10 :
        juldate = '"' + str(yearz) + '-' + str(monthz) + '-' + str(dayz) + ' ' + hourz + ':' + minutez + ':00"'
    else:
        juldate = '"' + str(yearz) + '-' + str(monthz) + '-0' + str(dayz) + ' ' + hourz + ':' + minutez + ':00"'
    return (juldate)



def data_process(data_point_dict, line, oldline, thedate, error_dir, qc_dir, bad_data_val=6999) :

    """ the following function data_process handles all data processing (or passes it off to other functions) and then returns either a processed value or nothing.
    data_process (6 Input Arguments)
    arg 0 = siteList dictionary list element
    arg 1 = current line of data from input file
    arg 2 = previous line of data from input file
    arg 3 = the current date (for qa/qc)
    arg 4 = qaqc directory
    arg 5 = bad data value
    Return = processed data

out_data =  dp_funks.data_process(siteList[element], \
                line, oldline, datez, \
                keyfile.get('main', 'error_log_dir'), \
                keyfile.get('main', 'qc_log_dir'), \
                keyfile.get('main', 'bad_data_val'))


    a sample data_point_dict --
    'd_element' : 'airtemp1m'
    {
      'Data_Type' : 'num'
      'Input_Array_Pos' : '5'
      'Coef_1' : '0'
      'Coef_2' : '0'
      'Coef_3' : '0'
      'Coef_4' : '0'
      'Coef_5' : '0'
      'Coef_6' : '0'
      'Coef_7' : '0'
      'Qc_Param_High' : '0'
      'Qc_Param_Low' : '0'
      'QC_Param_Step' : '0'
      'Output_Header_Line_2' : 'AirTemp1m'
      'Output_Header_Line_3' : 'deg C'
      'Output_Header_Line_4' : 'Avg'
    }
    """
    # current data types for processing:
    # num    = normal float
    # therm  = thermistor... specify the coefficients in the coefficient table.
    # poly   = polynomial... specify the coefficients in the coefficient table.
    # net    = net radiation... specify in the coefficients table the windspeed column so net can be corrected if needed
    # precip = Could do a totalize down the road but for present, maybe check the air temperature (column specified in the coefficients table again)
    
    old_line_str = oldline.split(',')
    line_str = line.split(',')
    ###  Okay, before ramping up... need to account for "NAN" of Table based loggers right here.
    temp_de = line_str[ int( data_point_dict[ 'Input_Array_Pos' ] ) ]
    temp_ode = old_line_str[ int( data_point_dict[ 'Input_Array_Pos' ] ) ] 
    # .isdigit() was failing testing the whole floating point number so now we're just looking at the last character / digit.
    if temp_de[-1].isdigit() :
        data_element = float( temp_de )
    else :
        data_element = float(bad_data_val)
        
    if len(temp_ode)>1:
        if temp_ode[-1].isdigit() :
            old_data_element = float( temp_ode)
        else :
            old_data_element = float(bad_data_val)
    else:
        old_data_element = float(bad_data_val)

    if data_point_dict['Data_Type'] == 'num' or data_point_dict['Data_Type'] == 'net' or data_point_dict['Data_Type'] == 'precip':
        # process as a number, no number crunching to do.
        processed_value = qc_check(data_element, \
                        old_data_element,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )

    elif data_point_dict['Data_Type'] == 'therm' :
        processed_value = thermistor(data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        bad_data_val)
        old_processed_value = thermistor(old_data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        float(bad_data_val))
        processed_value = qc_check(processed_value, \
                        old_processed_value,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )
                          
    elif data_point_dict['Data_Type'] == 'thermF' :
        processed_value = thermistor(data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        bad_data_val)
        old_processed_value = thermistor(old_data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        float(bad_data_val))
        processed_value = qc_check(processed_value, \
                        old_processed_value,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )
        if processed_value != float(bad_data_val) :
            processed_value = processed_value * 9 / 5 + 32

    elif data_point_dict['Data_Type'] == 'poly' :
        processed_value = poly(data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        float(data_point_dict['Coef_5']), \
                        float(data_point_dict['Coef_6']), \
                        float(data_point_dict['Coef_7']), \
                        bad_data_val)
        old_processed_value = poly(old_data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        float(data_point_dict['Coef_4']), \
                        float(data_point_dict['Coef_5']), \
                        float(data_point_dict['Coef_6']), \
                        float(data_point_dict['Coef_7']), \
                        bad_data_val)
        processed_value = qc_check(processed_value, \
                        old_processed_value,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )
    elif data_point_dict['Data_Type'] == 'flux' :
        processed_value = flux(data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        bad_data_val)
        old_processed_value = flux(old_data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        bad_data_val)
        processed_value = qc_check(processed_value, \
                        old_processed_value,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )
    elif data_point_dict['Data_Type'] == 'rt_sensor' :

        processed_value = rt_sensor(data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        bad_data_val)
        old_processed_value = rt_sensor(old_data_element, \
                        float(data_point_dict['Coef_1']), \
                        float(data_point_dict['Coef_2']), \
                        float(data_point_dict['Coef_3']), \
                        bad_data_val)
        processed_value = qc_check(processed_value, \
                        old_processed_value,  \
                        thedate, \
                        qc_dir, \
                        data_point_dict['d_element'], \
                        data_point_dict['Qc_Param_High'], \
                        data_point_dict['Qc_Param_Low'], \
                        data_point_dict['QC_Param_Step'], \
                        float(bad_data_val) )                  
    else:
        processed_value = bad_data_val
    return (processed_value)
    
def data_process_therm (data_point_dict, line, oldline, thedate, error_dir, qc_dir, res_array, sh_a, sh_b, sh_c, bad_data_val=6999) :
    """ this function handles all data processing (or passes it off to other functions) and then returns either a processed value or nothing.
    data_process (6 Input Arguments)
    arg 0 = siteList dictionary list element
    arg 1 = current line of data from input file
    arg 2 = previous line of data from input file
    arg 3 = the current date (for qa/qc)
    arg 4 = qaqc directory
    arg 5 = bad data value
    arg 6 = resistance array for therm
    arg 7 = steinhart-hart A coefficient
    arg 8 = steinhart-hart B coefficient
    arg 9 = steinhart-hart C coefficient
    Return = processed data

    out_data =  dp_funks.data_process(siteList[element], \
                    line, oldline, datez, \
                    keyfile.get('main', 'error_log_dir'), \
                    keyfile.get('main', 'qc_log_dir'), \
                    keyfile.get('main', 'bad_data_val'), \
                    therm_1_res, therm_1_a, therm_1_b, therm_1_c \
                    )


        a sample data_point_dict --
        'd_element' : 'airtemp1m'
        {
          'Data_Type' : 'num'
          'Input_Array_Pos' : '5'
          'Coef_1' : '0'
          'Coef_2' : '0'
          'Coef_3' : '0'
          'Coef_4' : '0'
          'Coef_5' : '0'
          'Coef_6' : '0'
          'Coef_7' : '0'
          'Qc_Param_High' : '0'
          'Qc_Param_Low' : '0'
          'QC_Param_Step' : '0'
          'Output_Header_Line_2' : 'AirTemp1m'
          'Output_Header_Line_3' : 'deg C'
          'Output_Header_Line_4' : 'Avg'
        }
        """

    # current data types for processing:
    # num    = normal float
    # therm  = thermistor... specify the coefficients in the coefficient table.
    # poly   = polynomial... specify the coefficients in the coefficient table.
    # net    = net radiation... specify in the coefficients table the windspeed column so net can be corrected if needed
    # precip = Could do a totalize down the road but for present, maybe check the air temperature (column specified in the coefficients table again)
    old_line_str = oldline.split(',')
    line_str = line.split(',')
    data_element = float( line_str[ int( data_point_dict[ 'Input_Array_Pos' ] ) ] )
    old_data_element = float( old_line_str[ int( data_point_dict[ 'Input_Array_Pos' ] ) ] )
    ### pull out correct s&h coefficients.
    reslim = False  # denotes we've found the index to be in
    dataset = len(res_array)  # length of thermistor list
    diff = int(dataset / 2)  # temporary index for tracking location in thermistor list
    samp = diff
    runs = 0
    while reslim != True :
        # initialize resistor comparison value
        runs += 1
        diff = int(diff / 2) + 1
        # compare resistance being passed to the list of resistances
        if (1000 * data_element) < res_array[samp] :
            # check to see if the resistance incoming is within 1 of the current position in the array
            if (1000 * data_element) > res_array[samp +1] :
                reslim = True
            else:
                # do another iteration.
                samp +=  diff
        else:
            if (1000 * data_element) < res_array[samp - 1] :
                reslim = True
            else :
                samp -= diff
        if runs >100 :
            reslim = True
    de_a = sh_a[samp]
    de_b = sh_b[samp]
    de_c = sh_c[samp]
    diff = int(dataset / 2)  # temporary index for tracking location in thermistor list
    samp = diff
    runs = 0
    while reslim != True :
        # initialize resistor comparison value
        runs += 1
        diff = int(diff / 2) + 1
        # compare resistance being passed to the list of resistances
        if (1000 * old_data_element) < res_array[samp] :
            # check to see if the resistance incoming is within 1 of the current position in the array
            if (1000 * old_data_element) > res_array[samp +1] :
                reslim = True
            else:
                # do another iteration.
                samp +=  diff
        else:
            print runs, samp
            if (1000 * old_data_element) < res_array[samp - 1] :
                reslim = True
            else :
                samp -= diff
        if runs >96 :
            reslim = True
    ode_a = sh_a[samp]
    ode_b = sh_b[samp]
    ode_c = sh_c[samp]


    processed_value = thermistor(data_element, \
                           de_a, \
                           de_b, \
                           de_c, \
                           float(data_point_dict['Coef_4']), \
                           bad_data_val)
    old_processed_value = thermistor(old_data_element, \
                           ode_a, \
                           ode_b, \
                           ode_c, \
                           float(data_point_dict['Coef_4']), \
                           float(bad_data_val))
    processed_value = qc_check(processed_value, \
                      old_processed_value,  \
                      thedate, \
                      qc_dir, \
                      data_point_dict['d_element'], \
                      data_point_dict['Qc_Param_High'], \
                      data_point_dict['Qc_Param_Low'], \
                      data_point_dict['QC_Param_Step'], \
                      float(bad_data_val) )
    return (processed_value)



def qc_check(data_element, old_data_element, thedate, qc_dir, data_name, qc_high=0, qc_low=0, qc_step=0, bad_data_val=6999) :
    """The qc_check function does some initial qc-ing.
    Longterm could also add a moving average comparison comparing the data to a like a 1 day average or something.
    Something to think about anyway.
    Input arguments are:
    arg 0 = the data element from the input data file
    arg 1 = the previous time step data element from the input data file
    arg 2 = the current date (from input file) for the monthly qc thresholds and logging qaqc actions to a file.
    arg 3 = qc_dir
    arg 4 = data_name
    arg 5 = the high qc threshold; default is 0, can either pass one value or twelve semi-colon separated values
    arg 6 = the low qc threshold; default is 0, can either pass one value or twelve semi-colon separated values
    arg 7 = the between time steps max increment; default is 0, can either pass one value or twelve semi-colon separated values
    arg 8 = the bad data value code; default is 6999
    Return = data value that has had some qa/qc
    """
    import os
    
    ###############################
    ## figure the current month  ##
    ###############################
    curmonth = int(thedate[6 : 8])

    #################################
    ## default case: data is fine  ##
    #################################
    processed_value = float(data_element)
    #print '%s  value:   %f  qc_high:  %s   qc_low:  %s  qc_step:  %s' % (data_name, processed_value, qc_high, qc_low, qc_step)
    #######################################################
    ## In case of monthly arrays, split the qc params    ##
    #######################################################
    qc_high_list = qc_high.split(';')
    qc_low_list = qc_low.split(';')
    qc_step_list = qc_step.split(';')
    bad_param = ''
    bad_value_present = False
    
    if processed_value == float(bad_data_val) :
   #     print 'bad default value %s     %s' % (thedate, data_name)
        ###############################################
        ## If data is bad at logger mark it as such  ##
        ###############################################
        #bad_param_list = [thedate, 'bad at logger','default', str(data_element) + '\n' ]
        bad_param = ','.join([bad_param, thedate, 'bad at logger','default', str(data_element) + '\n' ])
        bad_value_present=True
        
    else:
        ##################################
        ## Check the High Threshold     ##
        ##################################
        if len(qc_high_list) == 12 :
            if float(qc_high_list[curmonth - 1]) != 0 :
                if processed_value > float(qc_high_list[curmonth - 1]) :
              #      print 'above high:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_high', str(qc_high_list[curmonth - 1]), str(data_element) + '\n']
                    bad_param = ','.join([bad_param, thedate, 'qc_high_violation ', 'limit = ' + str(qc_high_list[curmonth - 1]),'RawDataValue '+ str(data_element) , '' ])
                    bad_value_present=True
        else :
            # check to see if it's is above the high threshold, qc_high = 0 means no qc checking.
            if float(qc_high) != 0 :
                if processed_value > float(qc_high) :
               #     print 'above high:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_high', str(qc_high), str(data_element) + '\n']
                    bad_param = ','.join([bad_param, thedate, 'qc_high_violation', 'limit = ' + str(qc_high), 'RawDataValue ' + str(data_element) , ''] )
                    bad_value_present=True
    
        #################################
        ## Check the Low Threshold     ##
        #################################
        if len(qc_low_list) == 12 :
            if qc_low_list[curmonth - 1] != 0 :
                if processed_value < float(qc_low_list[curmonth - 1]) :
                  #  print 'below low:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_low', str(qc_low_list[curmonth - 1]), str(data_element)+ '\n' ]
                    bad_param = ','.join([bad_param, thedate, 'qc_low_violation', 'limit = ' + str(qc_low_list[curmonth - 1]),'RawDataValue ' + str(data_element), '' ])
                    bad_value_present=True
        else :
            if float(qc_low) != 0 :
                if processed_value < float(qc_low) :
                #    print 'below low:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_low', str(qc_low), str(data_element)+ '\n']
                    bad_param = ','.join([bad_param, thedate, 'qc_low_violation', 'limit = ' + str(qc_low), 'RawDataValue '+ str(data_element), ''] )
                    bad_value_present=True
        ######################################
        ## Check the time step threshold    ##
        ######################################
        if len(qc_step_list) == 12 :
            if float(qc_step_list[curmonth - 1]) != 0 :
                if abs(processed_value - float(old_data_element)) > float(qc_step_list[curmonth - 1]) and old_data_element != bad_data_val :
              #      print 'step error:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_step', str(qc_step_list[curmonth - 1]), str(data_element) + '\n' ]
                    bad_param = ','.join([bad_param, thedate, 'qc_step error', 'MaxStepDiff '+str(qc_step_list[curmonth - 1]), 'diff '+ str(processed_value - float(old_data_element)),'RawDataValue '+ str(data_element)  ] )
                    bad_value_present=True
        else :
            if float(qc_step) != 0 :
                if abs(data_element - float(old_data_element)) > float(qc_step)  and old_data_element != bad_data_val :
                #    print 'step error:   %f' % (data_element)
                    #processed_value = bad_data_val
                    #bad_param_list = [thedate, 'qc_step', str(qc_step), str(data_element) + '\n']
                    bad_param = ','.join([bad_param, thedate, 'qc_step error', 'MaxStepDiff '+str(qc_step), 'diff '+ str(data_element - float(old_data_element)),'RawDataValue '+ str(data_element)] )
                    bad_value_present=True
           
    ###############################
    ## log qaqc process to file  ##
    ###############################
    if bad_value_present:
        processed_value = bad_data_val
    if bad_value_present :
        bad_param = ''.join([bad_param,'\n'])
        bad_param = bad_param.lstrip(',')
        qa_filename = qc_dir.rstrip() + data_name.rstrip() + '_qaqc_log.csv'
        if os.path.exists(qa_filename) :
                try :
                #    print 'bad data:   %s' % (bad_param)
                    qc_list =[]
                    qc_list.append(bad_param)
                    qa_file = open( qa_filename, 'a')
                    qa_file.writelines(qc_list)
                    qa_file.close
                except :
                    print 'problem opening %s for appending' % (qa_filename)
        ## it's a new file, need to create the header and such.
        else :
            try :
               # print 'bad data:   %s' % (bad_param)
                qc_list =[]
                qc_list.append(bad_param)
                qa_file = open( qa_filename , 'w')
                qa_file.writelines(qc_list)
                qa_file.close
            except :
                print 'problem opening %s for writing' % (qa_filename)

    #############################
    ## Return processed value  ##END of QC_CHECK
    #############################
    return (processed_value)  # end of qc_check
#######################################################################################################################
def thermistor(resistance, a, b, c, offset, bad_data_val) :
    """This function converts resistance (in k-ohms) and returns temperature in degrees Celsius
    Input arguments are:
    arg 0 = the data element from the input data file
    arg 1 = the steinhart-hart equation coeficcient A
    arg 2 = the steinhart-hart equation coeficcient B
    arg 3 = the steinhart-hart equation coeficcient C
    arg 4 = bad data value (in case there are errors)
    Return = temperature in degrees Celsius.
    """
    import math

    if abs(resistance) < 6999 and resistance > 0 :
        resistance *= 1000
        tempvalue = (1 / (a + b * math.log(resistance) + c * math.log(resistance) ** 3) - 273.15) + offset
    else :
        tempvalue = bad_data_val

    return (tempvalue)

def poly(data_element, coef_0, coef_1, coef_2, coef_3, coef_4, coef_5, coef_6, bad_data_val) :
    """This function applies a polynomial, up to 6th order, to the data element.
    Common candidates for this function would include soil moisture or pressure transducers
    Input arguments are:
    arg 0 = the data element from the input data file
    arg 1 = 0th order coefficient (coef_0  * data_element ^ 0)
    arg 2 = 1st order coefficient (coef_1  * data_element ^ 1)
    arg 3 = 2nd order coefficient (coef_2  * data_element ^ 2)
    arg 4 = 3rd order coefficient (coef_3  * data_element ^ 3)
    arg 5 = 4th order coefficient (coef_4  * data_element ^ 4)
    arg 6 = 5th order coefficient (coef_5  * data_element ^ 5)
    arg 7 = 6th order coefficient (coef_6  * data_element ^ 6)
    arg 8 = bad data value (in case of error)
    Return = result from the polynomial
    """
    if abs(data_element) < 6999 :
        processed_value = coef_0 + coef_1 * data_element + coef_2 * data_element ** 2 + \
            coef_3 * data_element ** 3 + coef_4 * data_element ** 4 + \
            coef_5 * data_element ** 5 + coef_6 * data_element ** 6
    else :
        processed_value = bad_data_val

    return (processed_value)

def flux(data_element, posical, negacal, bad_data_val) :
    """This function applies a simple 1st order linearization to the data element depending on if the signal is positive or negative.
        Input arguments are:
    arg 0 = the data element from the input data file
    arg 1 = multiplier for a positive data element value (posical  * data_element ^ 1)
    arg 2 = multiplier for a negative data element value (negacal  * data_element ^ 1)
    arg 3 = bad data value (in case of error)
    Return = result from the polynomial
    """
    if abs(data_element) < 6999 :
        if data_element >= 0 :
            processed_value = posical * data_element
        else:
            processed_value = negacal * data_element
    else :
        processed_value = bad_data_val
    return (processed_value)

def rt_sensor(data_element, val_a, val_b, val_c, bad_data_val) :
    """This function applies a calibration, of what kind and to what kind of sensor I'm not sure but the format is:
    processed value = ( ( data_element / val_a ) + val_b ) / val_c
    this is a function Hiroki requested.  For his sensors val_a is 1000 so it may first be a milliVolts to Volts conversion or something like that.
    arg 0 = the data element from the input data file
    arg 1 = a divisor
    arg 2 = an offset
    arg 3 = a multiplier
    arg 4 = bad data value (in case of error)
    Return = result from the polynomial
    """
    if abs(data_element) < 6999 :
        processed_value = ( ( data_element / val_a ) + val_b ) / val_c
    else :
        processed_value = bad_data_val
    return (processed_value)

def getyear(jday) :
    """This function estimates the year for array based loggers that don't have a year column.
    The significant catch is the year choice is the current year or the previous year.  So,
    if you intend to use this program to go through several years of data it would be good to add a year column.
    The primary use of this function is to catch the change when the data goes from December 31 to
    January 1.
    Input arguments are:
    arg 0 = the julian day of the data point
    Return = the year of that data: this year or last year
    """
    import time
    (curyear, curmon, curday, curhour, curmin, cursec, curwday, curjday) = time.localtime()[0:8]
    if jday > curjday :
        theyear = int(curyear) - 1
    else :
        theyear = curyear

    return (theyear)


def newdatacheck(current_input_date, latest_output_file_date)  :
    """This function takes two dates: the date on the current line being process and the last date entered into the output file.
    The two dates are compared and if the current date is more recent than the date in the output file then this data should be processed
    so return true.
    arg 1 = current date on the line being processed from the input file
    arg 2 = last date there is data for in the output file (output file is read earlier in the program)
    Return = a boolean.  True = process this data; False = do nothing this time step
    """
    import datetime
    import time

 #   print current_input_date
 #   print latest_output_file_date
    if latest_output_file_date == -1 or latest_output_file_date == '""':
        returnval = 1   # true
    else:
       # for comparison strip the quotation marks if present.
       if current_input_date[0] == '"' :
           current_input_date = current_input_date[1:-1]
       if latest_output_file_date[0] == '"' :
           latest_output_file_date = latest_output_file_date[1:-1]

       if len(latest_output_file_date) == 15 or len(latest_output_file_date) == 14 :
           # this format for data that has been opened and then saved from excel... lame
           (oYr, oMo, oDay, oHr, oMin, oSec) = time.strptime(latest_output_file_date, '%m/%d/%Y %H:%M')[0:6]
       else :
           (oYr, oMo, oDay, oHr, oMin, oSec) = time.strptime(latest_output_file_date, '%Y-%m-%d %H:%M:%S')[0:6]
       (iYr, iMo, iDay, iHr, iMin, iSec) = time.strptime(current_input_date, '%Y-%m-%d %H:%M:%S')[0:6]

       input_reading = datetime.datetime(iYr, iMo, iDay, iHr, iMin, iSec)
       output_reading = datetime.datetime(oYr, oMo, oDay, oHr, oMin, oSec + 1)
       if input_reading < output_reading :
           returnval = 0  #false
       else:
           returnval = 1  #true

    return (returnval)

















