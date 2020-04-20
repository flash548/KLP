import re
import string

# builds a range for a transliteration
def build_tr_range(start, end):
    retval = ''
    if start != None and end != None:   
        if (start in string.ascii_lowercase and end in string.ascii_lowercase):
            start_index = string.ascii_lowercase.index(start)
            end_index = string.ascii_lowercase.index(end)
            retval = string.ascii_lowercase[start_index:end_index+1]
        elif (start in string.ascii_uppercase and end in string.ascii_uppercase):
            start_index = string.ascii_uppercase.index(start)
            end_index = string.ascii_uppercase.index(end)
            retval = string.ascii_uppercase[start_index:end_index+1]
        elif (start in string.digits and end in string.digits):
            start_index = string.digits.index(start)
            end_index = string.digits.index(end)
            retval = string.digits[start_index:end_index+1]
    
    if retval != '' and retval != None: return retval
    
    raise Exception("Invalid transliteration spec")
    
    
def transliteration(in_str, spec, repl):
    spec_actual = ''
    last_char = None
    i = 0
    while i < len(spec):
        if spec[i] == '-':
            spec_actual += build_tr_range(last_char, spec[i+1])
            i += 2
            last_char = None
            continue
        
        if last_char != None: spec_actual += last_char
        last_char = spec[i]
        i += 1
        
    if last_char != None: spec_actual += last_char
        
    repl_actual = ''
    last_char = None
    i = 0
    while i < len(repl):
        if repl[i] == '-':
            repl_actual += build_tr_range(last_char, repl[i+1])
            i += 2
            last_char = None
            continue
        
        if last_char != None: repl_actual += last_char
        last_char = repl[i]
        i += 1
        
    if last_char != None: repl_actual += last_char
        
    new_str = ''
    for i in in_str:
        idx = spec_actual.index(i)
        if idx > len(repl_actual)-1:
            idx = len(repl_actual)-1
        new_str += repl_actual[idx]
    return new_str
    
