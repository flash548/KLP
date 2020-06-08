###############################################################################
#
# Filename: regexp_funcs.py 
#
# Description: These are all the regex backing functions 
#
# Revision History:
#   1-Jun-20: Initial Documentation/Release
#
###############################################################################

import re
import string
from Value import *

def parse_re_opts(vm, opts):

    opts_str = 0

    if vm.get_variable('*', 'scalar')._val:
        opts_str |= re.M

    if opts == None or opts == '':
        return opts_str

    if re.search('i', opts):
        opts_str |= re.I

    if re.search('x', opts):
        opts_str |= re.X

    return opts_str

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

def do_trans_op(vm, name, index_expr, spec, invert):
    v = None
    idx = None
    cxt = None
    if name != None:
        if (index_expr == True):
            idx = vm.stack.pop()
            if type(idx._val) is str:
                cxt = 'hash'
                v = vm.get_variable(name, 'hash')
                v = v[str(idx)].scalar_context()
            else:
                cxt = 'list'
                v = vm.get_variable(name, 'list')
                v = v[int(idx)].scalar_context()
        else:
            cxt = 'scalar'
            v = vm.get_variable(name, 'scalar').scalar_context()
    else:
        vm.get_variable('_', 'scalar') # get the $_ var

    trans_spec = spec._val['spec']
    repl_spec = spec._val['repl']

    # interpolate it
    vm.perform_interpolated_push(repl_spec)
    repl_spec = vm.stack.pop().stringify()

    ret = transliteration(v.stringify(), trans_spec, repl_spec)

    if (index_expr == True):
        if cxt == 'list':
            v[idx] = Value(ret)
            vm.set_variable(name, v, 'list')
        else:
            v[idx] = Value(ret)
            vm.set_variable(name, v, 'hash')
    else:
        vm.set_variable(name, Value(ret), 'scalar')

    if (bool(ret) ^ invert):
        vm.stack.push(Value(1))
    else:
        vm.stack.push(Value(0))

def do_subs_op(vm, name, index_expr, spec, invert):
    var = None
    v = None
    idx = None
    cxt = None
    if name != None:
        if (index_expr == True):
            idx = vm.stack.pop()
            if type(idx._val) is str:
                cxt = 'hash'
                var = vm.get_variable(name, 'hash')
                v = var[str(idx)].scalar_context()
            else:
                cxt = 'list'
                var = vm.get_variable(name, 'list')
                v = var[int(idx)].scalar_context()
        else:
            cxt = 'scalar'
            v = vm.get_variable(name, 'scalar').scalar_context()
    else:
        name = '_'
        v = vm.get_variable('_', 'scalar') # get the $_ var

    regex = spec._val['spec']
    repl = spec._val['repl']

    # interpolate it
    vm.perform_interpolated_push(regex)
    regex = vm.stack.pop().stringify()

    options = spec._val['opts']
    re_obj = re.compile(regex, parse_re_opts(vm, options))
    ret = re_obj.search(v.stringify())

    # populate $1 thru $10
    for i in range(10):
        vm.set_variable(str(i+1), Value(None), 'scalar')
    if ret and ret.lastindex:
        for i in range(0, ret.lastindex):
            vm.set_variable(str(i+1), Value(ret.group(i+1)), 'scalar')

    if ((bool(ret) ^ invert) and ret.group(0) != ''):
        # interpolate it -- but only if the subs spec isn't delimited by " ' "
        # which is a Perl 1 thing, definitely not in Perl5
        if (spec._val['separator'] != "'"):
            vm.perform_interpolated_push(repl)
            repl = vm.stack.pop().stringify()

        mod_string = None
        num_repls = None
        if ('g' in options):
            mod_string, num_repls = re_obj.subn(repl, v.stringify(), 0)
        else:
            mod_string, num_repls = re_obj.subn(repl, v.stringify(), 1)

        if (index_expr == True):
            if cxt == 'list':
                var[int(idx)] = Value(mod_string)
                vm.set_variable(name, var, 'list')
            else:
                var[str(idx)] = Value(mod_string)
                vm.set_variable(name, var, 'hash')
        else:
            vm.set_variable(name, Value(mod_string), 'scalar')

        vm.stack.push(Value(num_repls))
    else:
        vm.stack.push(Value(0))

def do_match_op(vm, name, index_expr, spec, invert):
    v = None
    if name != None:
        if (index_expr == True):
            idx = vm.stack.pop()
            if type(idx._val) is str:
                v = vm.get_variable(name, 'hash')
                v = v[str(idx)].scalar_context()
            else:
                v = vm.get_variable(name, 'list')
                v = v[int(idx)].scalar_context()
        else:
            v = vm.get_variable(name, 'scalar').scalar_context()
    else:
        vm.get_variable('_', 'scalar') # get the $_ var

    regex = spec._val['spec']
    options = spec._val['opts']
    ret = re.search(regex, v.stringify(), parse_re_opts(vm, options))
    for i in range(10):
        vm.set_variable(str(i+1), Value(None), 'scalar')
    vm.set_variable('+', Value(None), 'scalar')
    if ret and ret.lastindex:
        for i in range(0, ret.lastindex):
            vm.set_variable(str(i+1), Value(ret.group(i+1)), 'scalar')
            vm.set_variable('+', Value(ret.group(i+1)), 'scalar')

    if (bool(ret) ^ invert):
        vm.stack.push(Value(1))
    else:
        vm.stack.push(Value(0))
