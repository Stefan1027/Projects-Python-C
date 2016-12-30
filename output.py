# -*- coding: utf-8 -*-
import sys
import re


for line in sys.stdin:
    line = line.strip() #removes whitespaces
    denominator = re.match("(.*)\:(.*)", line , re.I)
    if (denominator):
        list_denominators = denominator.group(1).split(",")
        for i in list_denominators:
            penny = i.match("(.*)p.*", i , re.I)
            if (penny):
                pennypound_denom_list.append(group(1))
                #Penny
                continue
            else:
                pound = i.match(".*([0-9]*).*", i , re.I)
                if (pound):
                    string = pound.group(1)
                    string = str(int (string) * 100) #converts pounds to penny and puts the value back into the string to be appended to the list
                    pennypound_denom_list.append(string)
                    continue
            #print "Neither a Penny or a Pound coin"
        pennypound_denom_list = reversed(sorted(pennypound_denom_list)) #Sorts the list decreasingly
        dispense_amount = int(denominator.group(2)) #Converts denominator to int for division purposes
        for i in pennypound_denom_list:
            rest = dispense_amount / int(i)
            rest = int ( rest ) #If it's a float , convert to int to make it comparable
            if ( rest > 1 ):
                dispense_amount = dispense_amount - int (i) * rest # appends current values of denominators which are being dispensed
                value_string = str(i) + "x" + str(rest)
                displayed_output.append(value_string)
                continue
            if ( rest == 1 ):
                value_string_final = str(i) + "x" + str(rest) #Value of 1 for the rest will only be accomlished if there's a case such as 150 where's 1*100+1*50 and there's a perfect rounded result. This part allows the last denomination and "x1" to be stored in the list of elements which is going to be displayed at end, after the for loop is broken
                displayed_output.append(value_string_final)
                #print "Reached end of division, breaking to go to the next step in displaying the amount of denominators to be dispensed by each one for the requested amount of coins"
                break
            if ( rest < 1 ):
                if not displayed_output :
                    #print "This amount is not able to be dispensed due to the fact that the dominations are too high" #Happens only when I have a value of coins smaller than the smallest denominator
                    break
                else:
                    #print "There's no dispensable coins for this amount"
                    continue
        if displayed_output :
            for i in displayed_output:
                print i + ","
                continue
            
                
            
            

            
                
            
            
