#!/usr/bin/env python

import re
from optparse import OptionParser
import sys
import getopt
import glob, os

global current_case_type
global set_level
global string
global totallist
global process_list
global cnt
global type_one
global string_val_1
global found_signal
global foundstuff
global skip_process
global statement_string
global error_list_signal



# list of patterns compiled to increase speed of execution
if1 = re.compile(".*\s+if(.*)then.*", re.I)
if2 = re.compile(".*\s+if[\s+|\()](.*)", re.I)
if3 = re.compile("(.*)then.*", re.I)

elsif1 = re.compile("\s*elsif(.*)then.*", re.I)
elsif2 = re.compile("\s*elsif(.*)", re.I)
elsif3 = re.compile("(.*)then.*", re.I)

case1 = re.compile("\s*case(.*)is.*", re.I)
case2 = re.compile("\s*case(.*)", re.I)
case3 = re.compile("(.*)is.*", re.I)

assignment1 = re.compile(".*\<\=(.*);", re.I)
assignment2 = re.compile(".*\<\=(.*)", re.I)
assignment3 = re.compile("(.*);.*", re.I)

secondary_assignment1 = re.compile(".*\:\=(.*);", re.I)
secondary_assignment2 = re.compile(".*\:\=(.*)", re.I)
secondary_assignment3 = re.compile("(.*);.*", re.I)

event_type_patt = re.compile("(.*)\'event.*")
rising_edge_patt = re.compile(".*rising_edge\((.*)\).*")
other_things_patt = re.compile("([0-9a-zA-Z_\.\(\)]*)\'[a-zA-Z]*", re.I)

end_pattern = re.compile(".*end\s+if.*;.*", re.I)
single_line_pattern = re.compile(r'".*?"', re.I)

assertion_patt = re.compile(".*assert\s+(.*);.*", re.I)
assertion_patt1 = re.compile(".*assert(.*)", re.I)
assertion_patt2 = re.compile("(.*);.*", re.I)

assertion_pattern = re.compile(".*assert\s+(.*)report.*", re.I)
assertion_pattern1 = re.compile(".*assert(.*)", re.I)
assertion_pattern2 = re.compile("(.*)report.*", re.I)


##########################################################################################################################################
##########################################################################################################################################
error_list_signal = ""
process_list = ""
totallist=""
string = ""
list_1 = ""
list_variable = ""

set_path = ""
set_path_list = ""

try:
	opts, args = getopt.getopt(sys.argv[1:], "l:f:i:d:h:", ["level=","filelist=","file=","directory=","help="])
except:
	assert False, "Error: Option not recognised, please insert a valid option"

for opt, arg in opts:
	if opt in ("-l", "--level"):
		set_level = arg #debug_level of errors
        elif opt in ("-f", "--filelist"):
                set_path_list = arg #file path
        elif opt in ("-i", "--file"):
                set_path = arg #single_file path
        elif opt in ("-d", "--directory"):
                set_path = arg #directory path
        elif opt in ("-h", "--help"):
                print """
                         Available options :    -l integer     (Sets the debug level of upcoming errors. 1-Debug mode, 2-Errors only mode)
                                                -f file_path   (Sets the filelist path where file paths are found)
                                                -i single_file (Sets the file_path for a single file use)
                                                -d directory   (Sets the path for a directory use, the script processes this and the single_file case in the same way)
                                                -h help        (Brings up all the usable command line options)
                      """
	else:
		assert False, "Error: option not found, use the option -h to bring up all usable command line options"

if (not set_path and not set_path_list): #the default is set only if both set_path for a file/directory is not set and there's no set_path_list set as well. So the script won't do this whole thing twice.
        set_path = os.path.dirname() #sets the default file directory to be set as the folder as which the script is already into
if not set_level:
        set_level = 2 # defaulted if it's not set in the command line to 2


def file_list(set_path_list):
        """
        Functions containing the functionality of the script when we dealing with a filelist.
        If it's a filelist, it already includes all the paths we need to take care of. 
        """
        file_path_list = []
        pod = []
        f = open(set_path_list, "r")
        for line in f:
                line = line.strip()
                line = re.sub("\/\/\#\#.*","", line)
                if line:
                        file_path_list.append(line)
        return file_path_list


def get_filepaths_single_file_or_dic(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []
    if (os.path.isfile(directory)):
            file_paths.append(directory)
            return file_paths
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths



def core_functionality (totallist, list_p, sense_list, process_list, file_name):  #this is only usable for if type but the parsed lists should have a general name but the right contenent within them
    """
    Testing function within the if cases to make it more easy to add additional stuff such as new patterns
    will always require it to be smaller in terms of arhitecture.
    This specific function covers the basic functionally in detecting missing signals within the process block or missing signals which are in the sensitivity list but not in the actual process block
    It requires 3 lists to be parsed onto them, the total list of signals/inputs , the current statement type list and the sense_list. 
    """
    global found_signal, error_list_signal
    for i in totallist:
        for j in list_p:
            if (i == j):
                print_function("Found signal in the the list that is in the total list: " + str(j), 1)
                for k in sense_list:
                    if (j == k):
                        found_signal = 1
                        break
                if (found_signal == 0):
                        if  error_list_signal:
                                error_list_signal += "\n"
                        error_list_signal += "Signal/Input in the list which should be in the sense_list and it's not: " +str(j)+ " at line: " + str(cnt) + " at process named: " +str(process_list) + " at file named: " + str(file_name)
                found_signal = 0

#def assertion_checker ( )

def sense_list_checker (totallist, statement_string, sense_list, process_list, file_name):
        """
        Contains the second part of the algorithm where the sensitivity list elements
        are checked against all the statements which were found in the process
        so that we can make sure that there are no cases where there's signals
        present in the process block.
        """
        global foundstuff
        white_statement = []
        statement_string = re.sub ("\("," ", statement_string)
        statement_string = re.sub ("\)"," ", statement_string)
        statement_string = re.sub ("\+"," ", statement_string)
        statement_string = re.sub ("\-"," ", statement_string)
        statement_string = re.sub ("\:"," ", statement_string)
        statement_string = re.sub ("/"," / ",statement_string)
        statement_string = re.sub ("\&"," & ", statement_string)
        statement_string = re.sub ("\,", " , ", statement_string)
        statement_string = re.sub ("\.[\w_]*","  ",statement_string)
        statement_list = statement_string.split()
        for  i in statement_list:
                white_statement.append(i)
        p = list(set(white_statement))
        print_function(p, 1)
        unique_list_statements = list(set(p))
        print_function("This is the copied list that adds all the statements to it: " + str(unique_list_statements), 1)
        print_function(sense_list, 1)
        for i in sense_list:
                for j in unique_list_statements:
                        if (i ==j):
                                foundstuff = 0
                                break
                if (foundstuff == 1):
                        print_function("Element in the sense_list is not in the all statements list of the process: " + str(process_list) + " element " + str(i) +  " at line number: " + str(cnt)+ " in file named: " + str(file_name), 2)
                foundstuff = 1

def event_function (pattern, string, sense_list, process_list, file_name):
        """
        All of the clock related 'ticks should be matched and then the algorithm below
        should be applied for every type of assignment/case that can happen into the process block as this are the things the proces should be terminated onto.
        """
        #print_function("PRINT ME THE STRING BEFORE MATCHING 'EVENT " + str(string), 1)
        string_l = pattern.match(string)
        print_function("This is the match : " + str(string_l),1)
        #print_function("This is the current pattern : " + str(pattern),1)
        global skip_process, found_signal
        if(string_l):
                string_p = string_l.group(1).strip()
                string_p = re.sub("\("," ", string_p)
                string_p = re.sub("\)"," ", string_p)
                list1 = string_p.split()
                print_function("This is the list before skipping the process: " + str(list1), 1)
                print_function("Sequential process, skipping process", 1)
                skip_process = 1
                found_signal = 0
                found_clk = 0
                for i in sense_list:
                        for j in list1:
                                if ( i==j ):
                                        found_clk = 1
                                        continue
                if (found_clk == 0):
                        print_function("No clock in the sensitivity list at process: " + str(process_list) + " at line: " + str(cnt) + " in file: " + str(file_name), 2)
                counter = 0
                length = len(sense_list)
                print_function(sense_list,1)
                for i in sense_list: #Counter that increments each time one of these patterns match, and will continue the loop and warn when there's more matches than it's supposed to be.
                        patt = re.match (".*clock.*", i, re.I)
                        patt1 = re.match (".*clk.*", i, re.I)
                        patt2 = re.match (".*reset.*", i, re.I)
                        if (patt or patt1 or patt2):
                                counter = counter + 1
                if (counter > length): #normally counter = length
                        print_function("More elements in the sense_list than it should be in a normal sequential process at process name: " + str(process_list) + " at line number: " +str(cnt) + " at file: " + str(file_name), 2)
                print_function("Number of clocks and resets counted: " + str(counter), 1)
                counter = 0
                return 1

def string_manipulation (string):
        """
        This function contains any string manipulations done after the if/elsif/case/assignment1/assignment2 has been detected to make the splitting process easier
        """
        string = re.sub ("\("," ", string)
        string = re.sub ("\)"," ", string)
        string = re.sub ("\+"," ", string)
        string = re.sub ("\-"," ", string)
        string = re.sub ("\:"," ", string)
        string = re.sub ("/"," / ",string)
        string = re.sub ("\.[\w_]*","  ",string)
        string = re.sub ("\,", " , ", string)
        return string

def normal_case(totallist, line, sense_list, pattern, string, case_type, process_list, file_name):
        """
        Sub-block of the initial process. In this function we apply the patterns
        that needs to be matched in order to progress through the rest of the script
        """
        global statement_string
        pattern_s = pattern.match(line, re.I)
        #print_function(pattern + "DOES IT WORK or not ",1)
        print_function(string, 1)
        print_function(line, 1)
        if (pattern_s):
                endif_pattern = end_pattern.match(line, re.I)
                if endif_pattern:
                        print_function(endif_pattern, 1)
                        return 8, string, case_type
                print_function('Found statement: ' + str(case_type), 1)
                print_function("THIS IS THE ALL STATTEMENTS STRING BEFORE FUNCTION " + string, 1)
                string += pattern_s.group(1).strip()
                #print_function("String before subbing: " + string,1)
                #statement_string = re.sub("[a-zA-Z_.\(\)]*\'high", "", string) 
               # print_function("String after subbing: " + statement_string, 1)
                #print_function('This is the matched group: ' + str(string) + " " + str(pattern), 1)
                statement_string += pattern_s.group(1) + " "
                string_c = string
                print_function(string_c,1)# string that will contain all the stuff inside the that statement and is concatenated each time a pattern has matched in the first place.
                variable = event_function(event_type_patt, string, sense_list, process_list, file_name)
                if (variable == 1):
                        return 5,string,case_type #replacing continues from before to make the loop escape if it gets in here00> we need to check for this.
                variable = event_function(rising_edge_patt, string, sense_list, process_list, file_name)
                if (variable == 1):
                        return 5,string,case_type
                #vary = output_function(other_things_patt, string_c, sense_list, process_list, file_name)
                string_variable = string_manipulation(string)
                print_function(string,1)
                list_p = string_variable.split()
                print_function(list_p,1)
                core_functionality(totallist, list_p, sense_list, process_list, file_name)
                #print_function("AM I STILL IN THE RIGHT PLACE? ", 1)
                return 1 ,string, case_type
        else:
                return 0 ,string, case_type

def output_function(pattern, string, sense_list, process_list, file_name):
        """
        This function might be redudant. 
        We don't need a pattern to check for 'length or 'low or 'high or any other vhdl argument as the splitting done in the string after the initial pattern match 
        We can replace the whole thing before and after "'" with a space, and then the second part of the script will flag it if it's a mistake and it shouldn't have been used in there. 
        """
        string_exit = re.match('\'0\'', string, re.I) #if the assigmnent value, we just return that, because we don't care about it.
        if (string_exit):
                return
        string_exit2 = re.match('\'1\'', string, re.I)
        if (string_exit2):
                return
        pattern = re.finditer(pattern, string) #this way we deal with multiple patterns on one row and they are passed once and tested individually.
        for i in pattern:
                string_p_n = i.group(1).strip()
                output_function_list = string_p_n.split()
                print_function(str(output_function_list), 1)
                print_function("The output signal/input found before e.g 'high, 'low, 'range, 'length is: " + str(output_function_list) + " at line : " + str(cnt) + " in process named: " + str(process_list) + " in file: " + str(file_name), 1)
                for i in sense_list:
                        for j in output_function_list:
                                if ( i == j):
                                        print_function("This output signal/input should not be in the sense_list: " + str(j) + " at line : " + str(cnt) + " in process named: " + str(process_list) + " in file: " + str(file_name), 2)
                                        break


def case_architecture(totallist, pattern1, pattern2, pattern3, line, sense_list, return_type, case_type, process_list, file_name):
        global string_val_1, current_case_type
        if (return_type == 1):
                #print_function("DO I CHECK this lol wtf" + str(pattern1)+ str(pattern2)+str(pattern3)+ " " + str(line),1)
                single_case,string_val,current_case_type = normal_case(totallist, line, sense_list, pattern1, string, case_type, process_list, file_name)
                print_function("OR i don't " +str(single_case), 1)
                if (single_case == 5):
                        return 5
                if (single_case == 1):
                        print_function("Single line pattern match has been detected, moving on to the next line to reapply patterns", 1)
                        return 8 # finds single line and tries to match the next pattern
                if (single_case == 8):
                        return 8
                else:
                        print_function("Haven't found a match in the current line for a single case pattern, moving on to the the start of the multi-line pattern" , 1)
                        multi_case_start, string_val_1, current_case_type = normal_case(totallist, line, sense_list, pattern2, string, case_type, process_list, file_name)
                        if (multi_case_start == 5):
                                return 5
                        if (multi_case_start == 1):
                                return 2
                        if (multi_case_start == 8):
                                return 8
                        else:
                                print_function("Haven't matched either of single line or multi_line for the current pattern and moving on to the next pattern", 1)
                                return 1 # 0 is the code for returning back to the architecture in order to start parsing a new pattern case such as else if or assignment 1/2.
        elif (return_type == 2):
                print_function("Looking for the end of the current multi_line end pattern " + str(pattern3), 1)
                variable = evaluating_multi_line(totallist, current_case_type, line, sense_list, return_type, case_type, process_list, file_name, string_val_1, pattern3)
                if (variable == 1):
                        return 3
                        #found it and moves on to the next line.
                elif (variable == 2):
                        return 2
                return 2
                        #next pattern ending case
        else:
                return 1 #defaulted to be returned to 1 if something goes wrong in the function

def evaluating_multi_line(totallist, current_case_type, line, sense_list, return_type, case_type, process_list, file_name, string, pattern3):
        global string_val_1,statement_string
        if (current_case_type == case_type): 
                #current_case_type is the case when the multi-line start has occured and if we don't wanna do pattern matching storage onto the next line unless it's the pattern we want -->economical and better
                multi_case_end, test_string_multi_end, anything = normal_case(totallist, line, sense_list, pattern3, string, case_type, process_list, file_name)
                if (multi_case_end):
                        string_val_1 += test_string_multi_end
                        print_function("Does it ever return the right thing" , 1)
                        return 1
                else:
                        string_val_1 = string_val_1 + " " +line
                        statement_string = statement_string + " " +line
                        return 2
        else:
                return 2
                #continues to go to the next pattern ending until it reaches the one we need for the multi_line_string_start.
def execution_architecture (totallist, pattern1, pattern2, pattern3, sense_list, case_type, line, process_list, file_name):
        global type_one
        type_one = case_architecture (totallist, pattern1, pattern2, pattern3, line, sense_list, type_one, case_type, process_list, file_name)
        print_function("This should be 2 after it ran the first  time, is this true" + str(type_one),1)
        if (type_one == 5):
                return 5
        if (type_one == 3):
                type_one = 1
                return 8
        if (type_one == 8):
                #print_function("AM I HERE MAN" , 1)
                type_one = 1
                return 8
        if (type_one == 2):
                #set type_one = 2 and try to improve performance
                return 2 # was 8 --> if the end hasn't been found, the next time around it should only be looking for multi-line
        #if (type_one ==1): #when it finds a single case match, this return is only valid only when the single line case has been found or the end of the multiline has been found. This prevents looking for other cases inside an actual pattern which is being searched.
            #    return 8

#executes the algorithm that encapsulates the logic for going through each pattern case matching required
#the next level of architecture is to make this workable on all patterns in an efficient way
#functions that matches on any beggining and returns the values for that specific pattern start

def pattern_function(case):
        """
        This function encapsulates all the required patterns in order to find all different cases that can occur in the process
        This function has been created to make it easier to add new, unexpected patterns that could have been not covered.
        Pattern matching call-up possibilities:if,elsif,case,assignment1,assignment2.
        """
        if (case == 'if'):
                string1 = '.*\s+if(.*)then.* , .*\s+if[\s+|\()](.*) , (.*)then.*'
                string1 = re.sub("\s", "", string1)
                if_list = string1.split(",")
                return if_list[0], if_list[1], if_list[2]
        if (case == 'elsif'):
                string2 = '\s*elsif(.*)then.* , \s*elsif(.*) , (.*)then.*'
                string2 = re.sub("\s", "", string2)
                elsif_list = string2.split(",")
                return elsif_list[0], elsif_list[1], elsif_list[2]
        if (case == 'case'):
                string3 = '\s*case(.*)is.* , \s*case(.*) , (.*)is.*'
                string3 = re.sub("\s", "", string3)
                case_list = string3.split(",")
                return case_list[0], case_list[1], case_list[2]
        if (case == 'assignment1'):
                string4 = '.*\<\=(.*); , .*\<\=(.*) , (.*);.*'
                string4 = re.sub("\s", "", string4)
                assignment1_list = string4.split(",")
                return assignment1_list[0], assignment1_list[1], assignment1_list[2]
        if (case == 'assignment2'):
                string5 = '.*\:\=(.*); , .*\:\=(.*) , (.*);.*'
                string5 = re.sub("\s", "", string5)
                assignment2_list = string5.split(",")
                return assignment2_list[0], assignment2_list[1], assignment2_list[2]
        else:
                print_function("Case not recognised, please check for spelling or if there's a new pattern, please add it to the list", 2)
#haven't covered the else if case -->got an error

def print_function(error_list, severity_level):
    """
    Printing function for filtering out debug prints and warnings/errors prints
    It provides utility in debugging the code and it makes it run faster when we want it to run in such a way
    """
    if (set_level == '1' and (severity_level == 1 or severity_level == 2)):
        print error_list
    elif (set_level == '2' and severity_level == 2):
        print error_list
    else:
        return

#Level 1 = prints debug errors and error messages
#Level 2 = prints only error messages

def start_process(path):
        """
        This function will encapsulate all the parsing process in order to be called later on easier.
        In order to make this work we need to parse in one file path at a time, and we do this by using the provided string.
        This string contains all the file paths within a specific directory under specific extension
        """
        #if_case / elsif_case /case/ assignment_1_case/ assignment_2_case
        file_name = path
        # global empty string used in the functions that handle single line patterns.
        string_val_1 = ""
        string_val = ""
        signal_list=[]
        variable_list = []
        global error_list_signal 
        error_list_signal = ""
        
        port_list=[]
        string =""
        string_p =""
        string_p_n = ""

        #General parsing constants:
        found_proc = 0
        found_entity = 0
        found_port = 0
        found_sense_list = 0
        start_main_block = 0
        found_procedure = 0
        first_port = 1

        #Algorithm within process block constants:
        global found_if
        found_if=0

        #Algorithm strings required to check all elements within the sensitivity list are used in the process
        global statement_string
        statement_string = ""
      
        
        #Counter variable to determine current row we find a problem or when we need to debug
        global cnt
        cnt = 0


        global type_one
        type_one = 1
        #Variable required to be passed globally as it's row dependant and situation dependant
        
        global foundstuff
        foundstuff = 0
        #Variable required in the skip_process situation when we encounter 'event or rising_edge
        global skip_process
        skip_process = 0

        
        #Pattern declarations used:
        pattern1 = ""
        pattern2 = ""
        pattern3 = ""
        current_case_type = ""
        process_list = ""

        #Algorithm constants that are flagged when a situation occurs and are row dependant or situation dependant
        global found_signal
        found_signal = 0
        found_variable = 0
        flag_no_entity = 0
        flag_no_process = 0
        flag_only_entity = 0
        process_start = 0
        no_sense_list = 0
        wh_statement = []
        f = open(path, "r")
        for line in f:
                cnt= cnt+1;
                # Ignore comments
                line = re.sub(r'".*?"', "", line)
                #look at dealing with multi line quotes
                mobj=line.split("--",1)
                line=mobj[0]
                # Find entity
                ent = re.match('^\s*entity\s+(.*)\s+is\s*',line, re.I)
                if (ent):
                        flag_no_entity = 1
                        found_entity = 1
                        entity_name = ent.group(1).strip()
                        print_function("This is the name of the entity: " + entity_name, 1)
                if (found_entity):
                        end_entity = re.match('^\s*end entity.*',line, re.I)
                        if (end_entity):
                                found_entity = 0
                                port_list = string.split(',')
                                print_function("Port list: " + str(port_list), 1)
                                continue
                        end_entity1 = re.match('^\s*end\s+'+entity_name+'\s*;\s*', line, re.I)
                        if (end_entity1):
                                found_entity = 0
                                port_list = string.split(',')
                                print_function("Port list: "+ str(port_list), 1)
                                continue
                        if (found_port == 0):
                                # All in one line
                                port = re.match('.*port\s*\((.*)\).*',line, re.I)
                                if (port):
                                        found_port = 0
                                        string = port.group(1).strip()
                                        string = re.sub("\s", "", string)
                                        port_list = string.split(',')
                                        print_function("Port list: "+ str(port_list), 1)
                                        continue;
                                # Multiline
                                port = re.match ('.*port\s*\((.*):\s*in\s+.*', line, re.I)
                                if (port):
                                        print_function("Found port", 1)
                                        found_port = 1
                                        string = port.group(1).strip()
                                        string = re.sub("\s", "", string)
                                port = re.match('.*port\s*\((.*)',line, re.I)
                                if (port):
                                        print_function("Found port",1)
                                        found_port = 1
                                        string = port.group(1).strip()
                                        string = re.sub("\s", "", string)
                        else:
                                foo = re.match('\s*(.*):\s*in\s+.*', line, re.I)
                                if (foo):
                                        if (first_port):
                                                first_port = 0
                                                string += re.sub("\s", "", foo.group(1))
                                        else:
                                                string += "," + re.sub("\s", "", foo.group(1))
                # Find signal
                signal = re.match('.*signal\s*(.*)\:\s+.*\;.*',line, re.I)
                if (signal):
                        signal_string = signal.group(1).strip()
                        print_function(signal_string, 1)
                        list_1 = signal_string.split(",")
                        for element in list_1:
                                signal_list.append(element)
                # Find process
                if (found_proc == 0):
                        # All in one line
                        proc = re.match('(.*)process\s*\((.*)\)\s*[^,].*',line, re.I)
                        if (proc):

                                print_function("---------- Found process ", 1)
                                found_proc = 1
                                flag_no_process = 1
                                process_name = proc.group(1).strip()
                                #process_name = string_manipulation(process_name)
                                process_name = re.sub("\s", "", process_name)
                                process_list = process_name.split(',')
                                sense_string = proc.group(2).strip()
                                sense_string = re.sub("\s", "", sense_string)
                                sense_list = sense_string.split(',')
                                print_function("Sense list: " + str(sense_list), 1)
                                continue;
                        # Multiline
                        proc = re.match('(.*)process\s*\((.*)',line, re.I)
                        if (proc):
                                print_function("---------- Found process ", 1)
                                found_proc = 1
                                flag_no_process = 1
                                found_sense_list = 1
                                process_name = proc.group(1).strip()
                                #process_name = string_manipulation(process_name)
                                process_name = re.sub("\s", "", process_name)
                                process_list = process_name.split(',')
                                sense_string = proc.group(2).strip()
                                sense_string = re.sub("\s", "", sense_string)
                        # No sense list
                        else:
                            proc = re.match('(.*)process\s*is(.*)',line , re.I)
                            if (proc):
                                    no_sense_list = 1
                                    flag_no_process = 1
                                    process_name = proc.group(1).strip()
                                    #process_name = string_manipulation(process_name)
                                    process_name = re.sub("\s", "", process_name)
                                    process_list = process_name.split(',')
                                    sense_string = proc.group(2).strip()
                                    sense_string = re.sub ("\s","", sense_string)
                                    sense_list = sense_string.split(',')
                                    found_proc = 1
                                    found_sense_list = 0
                                    print_function("Found process without sensitivity list at line: " + str(cnt) + " and process name as: " + str(process_list) + " in file : " + str(file_name), 2)
                elif(skip_process):
                    proc = re.match('^\s*end process.*',line, re.I)
                    if (proc):
                        #sense_list_checker(totallist, statement_string, sense_list, process_list, file_name)
                        print_function("---------- End begin", 1)
                        error_list_signal = ""
                        statement_string = ""
                        found_proc = 0
                        skip_process = 0
                        type_one = 1
                        found_procedure = 0
                        start_main_block = 0
                        wh_statement = []
                        variable_list = []
                        for i in variable_list: #######make this run only once.
                                for j in totallist:
                                        if (i == j):
                                                print_function("There's a variable defined in this process that a signal/input as well, and it should not be allowed at line: "  + str(cnt) + " element " + i + " in process: " + str(process_list) + " in file : " + str(file_name), 2)
                                                break
                    continue
                else:
                        # Find end of sense list
                        if (found_sense_list):
                                proc = re.match('(.*)\).*',line, re.I)
                                if (proc):
                                        sense_string += re.sub("\s", "", proc.group(1));
                                        flag_only_entity = 0
                                        found_sense_list = 0
                                        sense_list = sense_string.split(',')
                                        print_function("Sense list: " + str(sense_list), 1)
                                else:
                                        sense_string += re.sub("\s", "", line)
                                        continue
                        totallist = signal_list+port_list
                        #print_function (" WHAT " + str(totallist), 2)
                        variable = re.match('.*variable\s*(.*)\:\s+.*\;.*',line, re.I)
                        if (variable):
                                variable_string = variable.group(1).strip()
                                print_function(variable_string, 1)
                                list_variable = variable_string.split(",")
                                for element in list_variable:
                                        variable_list.append(element)
                        procedure_s = re.match ('\s*procedure\s+([\w_]*).*',line, re.I)
                        if procedure_s:
                                procedure_name = procedure_s.group(1)
                                print_function("Found a procedure, going to the next line and only searching for the end procedure or end" +str(line), 1)
                                found_procedure = 1
                                continue
                        if (found_procedure == 1):
                                procedure_end = re.match('.*end\s+'+procedure_name+';.*', line, re.I)
                                if procedure_end:
                                        print_function("Found the end of the procedure, going to the next line to start parsing the cases as normal" + str(line), 1)
                                        found_procedure = 0
                                        continue
                                else:
                                        procedure_end = re.match('.*end\s+procedure\s+'+procedure_name+';.*', line, re.I)
                                        if procedure_end:
                                                print_function("Found the end of the procedure, going to the next line to start parsing the cases as normal" +str(line), 1)
                                                found_procedure = 0
                                                continue
                        if (found_procedure == 0):
                                proc = re.match('^\s*begin.*',line, re.I)
                                if (proc):
                                        start_main_block = 1
                                        print_function("---------- Found begin " + str(line), 1)
                                        continue
                                if (start_main_block):
                                #execution of algorithm within the process block.
                                #this set of functions runs through all the possible cases before going back to the next_line, this whole function (top_level_architecture has to be called when main block has been reached)
                                #Global variable required in one of the architectures in the process function
                                        totallist = signal_list+port_list
                                        sense_list_c = sense_list
                                        sense_list2 =[]
                                        for i in sense_list:
                                                a = re.sub("\.[\w_]*", "", i)
                                                #print "before " +a
                                                a = re.sub("\([0-9a-zA-Z_]*\)","", i)
                                                #print "after " + a
                                                sense_list2.append(a)
                                        sense_list = sense_list2
                                        line = re.sub ("&"," & ", line)
                                        for  i in sense_list:
                                                wh_statement.append(i)
                                        q = list(set(wh_statement))
                                        sense_list = list(set(q))
                                        print_function("This is the sense_list : " + str(sense_list),1)
                                        print_function("This is the signal list: " + str(signal_list), 1)
                                        #if case

                                        #pattern1_1, pattern1_2, pattern1_3 = pattern_function('if')
                                        case_type = 'If case'
                                        #print_function(pattern1_1 + line, 1)
                                        #retrivies all the patterns we need to use further in the function
                                        variable = execution_architecture (totallist, if1, if2, if3, sense_list, case_type, line, process_list, file_name)
                                        print_function("Is this executed " + " " + str(variable),1)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                print_function("am i going to the next line", 1)
                                                type_one = 1
                                                continue

                                        #elsif case
                                        #pattern2_1, pattern2_2, pattern2_3 = pattern_function('elsif')
                                        case_type = 'Elsif case'
                                        variable = execution_architecture (totallist, elsif1, elsif2, elsif3, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                               # print_function("am i goiasdasdasdasdasdasdasdang to the next line", 1)
                                                type_one = 1
                                                continue

                                        #case type pattern
                                        #pattern3_1, pattern3_2, pattern3_3 = pattern_function('case')
                                        case_type = 'Case type'
                                        variable = execution_architecture (totallist, case1, case2, case3, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                print_function("am i going to asdasdthe next line", 1)
                                                type_one = 1
                                                continue

                                        #assignment_1 case
                                        #pattern4_1, pattern4_2, pattern4_3 = pattern_function('assignment1')
                                        case_type = '<= case'
                                        variable = execution_architecture (totallist, assignment1, assignment2, assignment3, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                print_function("am i going to thesdasdasd next line", 1)
                                                continue

                                        #assignment_2 case
                                        #pattern5_1, pattern5_2, pattern5_3 = pattern_function('assignment2')
                                        case_type = ':= case'
                                        variable = execution_architecture (totallist, secondary_assignment1, secondary_assignment2, secondary_assignment3, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                print_function("am i going to the next linedasdasd", 1)
                                                type_one = 1
                                                continue
                                        case_type = 'assertion'
                                        variable = execution_architecture (totallist, assertion_patt, assertion_patt1, assertion_patt2, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                type_one = 1
                                                continue
                                        case_type = 'assertion_type_two'
                                        variable = execution_architecture (totallist, assertion_pattern, assertion_pattern1, assertion_pattern2, sense_list, case_type, line, process_list, file_name)
                                        if (variable == 5):
                                                continue
                                        if (variable == 8):
                                                type_one = 1
                                                continue
                                        proc = re.match('^\s*end process.*',line, re.I)
                                        if (proc):
                                                if error_list_signal:
                                                        print_function(error_list_signal, 2)
                                                        error_list_signal = ""
                                                sense_list_checker(totallist, statement_string, sense_list, process_list, file_name)
                                                statement_string = ""
                                                print_function("---------- End begin ", 1)
                                                found_proc = 0
                                                type_one = 1
                                                found_procedure = 0
                                                start_main_block = 0
                                                wh_statement = []
                                                for i in variable_list: #######make this run only once.
                                                        for j in totallist:
                                                                if (i == j):
                                                                        print_function("There's a variable defined in this process that a signal/input as well, and it should not be allowed at line: "  + str(cnt) + " element " + i + " in process: " + str(process_list) + " in file : " + str(file_name), 2)
                                                                        break
                                                variable_list = []
                                        print_function("NEW line.",1)
        if (flag_no_entity == 0):
                print_function("No entity in this file: " + str(file_name), 1)
                flag_no_entity = 1
        if (flag_no_process == 0):
                print_function("No process found in this file: " + str(file_name), 1)
                flag_no_process = 1
        f.close()


if set_path_list: #if there's a path_list set we start the function that opens the file and gets all the paths we need to star the process onto.
        testing_value = file_list(set_path_list)
        print_function(testing_value, 1)
        for one_man in testing_value:
                print_function("This is the current file used from the filelist : " + str(one_man), 1)
                start_process(one_man)

if set_path: #if set_path is not null, as this only happens when we want to run the script on a specific file/folder and not one a filelist.
        full_file_paths = get_filepaths_single_file_or_dic(set_path)
        print_function(full_file_paths, 1)
        print_function(set_level, 1)
        for two_man in full_file_paths:
                print_function(two_man,2)
                if two_man.endswith(".vhd"):
                        print_function("This is the current used file in process : " + str(two_man), 1)
                        start_process(two_man)
##/user/sti/stefan.ilie_linux_CONFIG/powervr/hwvideo/quartz/DEV/QUARTZ_V2/quartz/src/test/
        






