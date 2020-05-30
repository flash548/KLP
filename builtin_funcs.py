from Value import Value
from regexp_funcs import *
import sys
import os
import re
import time
import math

import subprocess
from subprocess import CalledProcessError
import crypt

class BuiltIns():

    @staticmethod
    def do_print(vm, fh, argv):
        sep = vm.get_variable(',', 'scalar').stringify()
        end = vm.get_variable('\\', 'scalar').stringify()
        itr = 0
        count = len(argv)-1
        if (len(argv) > 0):
            for i in range(len(argv)-1, -1, -1):
                if fh == None:
                    sys.stdout.write(argv[i].stringify())
                else:
                    if str(fh) == 'stdout':
                        sys.stdout.write(argv[i].stringify())
                    else:
                        vm.get_variable(fh, 'raw')._val.write(argv[i].stringify())
                if (itr < count and itr != ''):
                    sys.stdout.write(sep)
                    itr += 1
        else:
            # print $_
            if fh == None:
                sys.stdout.write(vm.get_variable('_', 'scalar').stringify())
            else:
                if str(fh) == 'stdout':
                    sys.stdout.write(vm.get_variable('_', 'scalar').stringify())
                elif str(fh) == 'stderr':
                    sys.stderr.write(vm.get_variable('_', 'scalar').stringify())
                else:
                    vm.get_variable(fh, 'raw')._val.write(vm.get_variable('_', 'scalar').stringify())

        if end != '':
            sys.stdout.write(end)
        vm.stack.push(Value(1))

    @staticmethod
    def do_die(vm, argv):
        if len(argv) > 0:

            if (type(argv[0] is str)):
                vm.set_variable('!', Value(argv[0]), 'scalar')
                print((argv[0]))
            else:
                vm.set_variable('!', Value(argv[0].stringify()), 'scalar')
                print((argv[0]).stringify())
        else:
            sys.stdout.write("Died")

        vm.die()

    @staticmethod
    def do_exit(vm, argv):
        code = 0
        if len(argv) > 0:
            code = argv[-1].numerify()
        sys.exit(code)

    @staticmethod
    def do_backticks(vm, cmd):
        result = None
        try:
            if vm.is_stash:
                result = vm._stash(cmd.stringify())
            elif os.name == 'nt':
                # windows
                result = subprocess.check_output(['cmd', '/c', cmd.stringify()], stderr=subprocess.STDOUT)
            elif os.name.endswith('ix'):
                # posix-ish - assume bash
                result = subprocess.check_output(['/bin/bash', '-c', cmd.stringify()], stderr=subprocess.STDOUT)
            else:
                Builtins.do_die(vm, "Died.  Unknown OS to do backticks on")

            vm.set_variable('?', Value(0), 'scalar')
        except CalledProcessError as e:
            vm.set_variable('?', Value(e.returncode), 'scalar')

        vm.stack.push(Value(result))

    @staticmethod
    def do_length(vm, argv):
        vm.stack.push(Value(len(str(argv[0]))))

    @staticmethod
    def do_join(vm, argv):
        ary = None
        joiner = None
        # perl 1 allowed any order of the args here.
        # I think the intent was so that a literal list of values
        # could be specified if the delimited was 1st arg, and 2Nd...Nth was items
        if ((type(argv[1]) is str)):
            #arg1 was bareword
            ary = argv[1]
            joiner = argv[0]
        elif (argv[-1].type == "Scalar"):
            #arg0 was Value obj but a scalar - so its a delimiter
            ary = argv[0:-1]
            joiner = argv[-1]
        else:
            BuiltIns.do_die(vm, [ "Join requires an array or list to join!" ])

        if (type(ary) is str):
            # joining an array indicated by its bareword
            tmplist = []
            ary = vm.get_variable(ary, 'list')
            if ary.type == "List":
                for i in range(len(ary)):
                    tmplist.append(str(ary[i]))
            else:
                BuiltIns.do_die(vm, [ "Join requires an array or list to join!" ])

            vm.stack.push(Value(str(joiner).join(tmplist)))
        else:
            # joining evaulated list of n-items with joiner
            new_list = []
            for i in ary:
                if (i.type == "List"):
                    new_list = i._val + new_list
                else:
                    new_list = [ i._val ] + new_list

            vm.stack.push(Value(str(joiner).join(map(lambda x: str(x), new_list))))


    @staticmethod
    def do_keys(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            key_arry = argv[0]._val.keys()
            key_arry.reverse()
            vm.stack.push(Value(key_arry))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            key_arry = v._val.keys()
            key_arry.reverse()
            vm.stack.push(Value(key_arry))

    @staticmethod
    def do_values(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            val_arry = argv[0]._val.values()
            val_arry.reverse()
            vm.stack.push(Value(val_arry))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            val_arry = v._val.values()
            val_arry.reverse()
            vm.stack.push(Value(val_arry))

    @staticmethod
    def do_each(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            pair = argv[0]._each()
            vm.stack.push(Value([pair[0], pair[1]]))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            pair = v._each()
            vm.stack.push(Value([pair[0], pair[1]]))

    @staticmethod
    def do_eval(vm, argv):
        from Lexer import Lexer
        from Parser import Parser
        from VM import VM
        error_msg = ''
        v = None
        try:
            l = Lexer(str(argv[0]))
            p = Parser(l)
            ast = p.parse()
            v = VM()

            # merge in existing scope, stack, subs, etc
            v.current_scope = vm.current_scope
            v.pgm_stack_frames = vm.pgm_stack_frames

            ast.emit(v)
            v.run()

            # merge the scopes back out again
            vm.current_scope = v.current_scope
            vm.pgm_stack_frames = v.pgm_stack_frames

        except Exception as e:
            error_msg = str(e)

        # push the return value back to the main program
        if v != None and len(v.stack) > 0:
            vm.stack.push(v.stack.pop())
        else:
            vm.stack.push(Value(None))

        # set $@ result
        vm.set_variable('@', Value(error_msg), 'scalar')

    @staticmethod
    def do_open(vm, argv):
        handle = str(argv[1])
        filename = str(argv[0])
        fp = None
        error = ''
        success = True
        try:
            if filename.startswith('>>'):
                fp = open(filename[2:], 'a')
            elif filename.startswith('>-'):
                fp = sys.stdout
            elif filename.startswith('>'):
                fp = open(filename[1:], 'w')
            elif filename.startswith('<'):
                fp = open(filename[1:], 'r')
            else:
                fp = open(filename, 'r')
        except Exception as e:
            error = str(e)
            success = False

        vm.set_variable('!', Value(error), 'scalar')
        vm.set_variable(handle, Value(fp), 'raw')
        vm.last_fh_read = handle

        # return success or failure
        vm.stack.push(Value(1) if success else Value(0))

    @staticmethod
    def do_close(vm, argv):
        handle = str(argv[0])
        fp = vm.get_variable(handle, 'raw')
        error = ''
        success = True
        try:
            fp._val.close()
        except Exception as e:
            error = str(e)
            success = False

        vm.set_variable('!', Value(error), 'scalar')
        vm.set_variable(handle, Value(fp), 'raw')
        vm.stack.push(Value(1) if success else Value(0))

    @staticmethod
    def do_eof(vm, argv):
        handle = None
        fp = None
        if len(argv) > 0:
            handle = str(argv[0])
            fp = vm.get_variable(handle, 'raw')
        else:
            fp = vm.last_fh_read

        if (fp._val.closed):
            vm.stack.push(Value(1))
            return

        pos = fp._val.tell()
        a = fp._val.readline()
        if (a == ''):
            fp._val.seek(pos)
            vm.stack.push(Value(1))
        else:
            fp._val.seek(pos)
            vm.stack.push(Value(0))

    @staticmethod
    def do_shift(vm, argv):
        v = vm.get_variable(str(argv[0]), 'list')
        elem0 = Value(None)
        if (len(v) > 1):
            elem0 = v._val[0]
            vm.set_variable(str(argv[0]), Value(v._val[1:]), 'list')
        elif (len(v) == 1):
            elem0 = v._val[0]
            vm.set_variable(str(argv[0]), Value(None), 'list')
        else:
            vm.set_variable(str(argv[0]), Value(None), 'list')
        vm.stack.push(elem0)

    @staticmethod
    def do_unshift(vm, argv):
        name = str(argv[-1])
        v = vm.get_variable(name, 'list')

        for i in range(0, len(argv)-1):
            if (argv[i]._val != None):
                v = v.prepend_list(argv[i])
                vm.set_variable(name, v, 'list')

        vm.stack.push(Value(len(v)))

    @staticmethod
    def do_index(vm, argv):
        src = str(argv[1])
        search = str(argv[0])
        pos = -1
        try:
            pos = src.index(search, 0)
        except:
            pass
        vm.stack.push(Value(pos))


    # TODO: major hack, needs fixed
    # here we have to see what format specifiers are present
    # and convert the value to something python is happy with
    # plus in order to use Python's builtin format function,
    # we have to have exactly same number fields vs items ... Python is
    # soooo picky!  This is just ugly.
    @staticmethod
    def do_sprintf(vm, argv):
        fmt_str = None
        fmt_str = argv[-1]
        if (fmt_str.type == "List"):
            fmt_str = str(argv[-1][0])
            argv = argv[-1][1:]
            argv.reverse()
        else:
            fmt_str = str(argv[-1])
            argv = argv[0:-1]
        strs = []
        for i in range(0, len(argv)):
            if (argv[i].type == "List"):
                sublist = []
                for j in argv[i]._val:
                    sublist.insert(0, j)
                for j in sublist: strs.insert(0, j)
            else:
                strs.insert(0, argv[i])

        fields = re.findall("%[0-9-.]*?([a-zA-Z])", fmt_str)
        idx = 0
        for field in fields:
            if 's' not in field:
                # anything other than string, do a numerify
                if idx >= len(strs):
                    strs.append(Value(None).numerify())
                else:
                    strs[idx] = strs[idx].numerify()
            else:
                if idx >= len(strs):
                    strs.append(Value(None).stringify())
                else:
                    strs[idx] = strs[idx].stringify()

            idx += 1

        if (len(fields) == 0):
            vm.stack.push(Value(fmt_str))
        else:
            if len(fields) < len(strs):
                strs = strs[0:len(fields)]

            vm.stack.push(Value(fmt_str % tuple(strs)))

    @staticmethod
    def do_seek(vm, argv):
        handle = str(argv[-1])
        offset = argv[-2].numerify()
        whence = 0
        if (len(argv) > 2):
            whence = argv[-3].numerify()
        fp = vm.get_variable(handle, 'raw')
        error = ''
        success = True
        try:
            fp._val.seek(offset, whence)
        except Exception as e:
            error = str(e)
            success = False

        # set errno
        vm.set_variable('!', Value(error), 'scalar')
        vm.set_variable(handle, fp, 'raw')
        vm.stack.push(Value(1) if success else Value(0))

    @staticmethod
    def do_tell(vm, argv):
        handle = None
        fp = None
        if len(argv) > 0:
            handle = str(argv[0])
            fp = vm.get_variable(handle, 'raw')
        else:
            fp = vm.last_fh_read

        pos = fp._val.tell()
        vm.stack.push(Value(pos))

    @staticmethod
    def do_crypt(vm, argv):
        word = argv[-1]
        salt = argv[-2]

        vm.stack.push(Value(crypt.crypt(str(word), str(salt))))

    @staticmethod
    def do_chop(vm, argv):
        var = None
        name = None
        if (len(argv) == 0):
            name = '_'
        else:
            name = str(argv[-1])

        var = vm.get_variable(name, 'scalar').stringify()
        if len(var) > 0:
            last_char = var[-1]
            var = var[0:-1]
            vm.set_variable(name, Value(var), 'scalar')
            vm.stack.push(Value(last_char))
        else:
            vm.stack.push(Value(None))

    @staticmethod
    def do_push(vm, argv):
        name = str(argv[-1])
        v = vm.get_variable(name, 'list')

        for i in range(0, len(argv)-1):
            if (argv[i]._val != None):
                if argv[i].type == 'Scalar':
                    v = (v._val + [ argv[i]._val ])
                else:
                    v = v._val + argv[i]._val
                vm.set_variable(name, Value(v), 'list')

        v = vm.get_variable(name, 'list')
        vm.stack.push(Value(len(v._val)))

    @staticmethod
    def do_pop(vm, argv):
        v = vm.get_variable(str(argv[0]), 'list')
        elem0 = Value(None)
        if (len(v) >= 1):
            elem0 = v._val.pop()
            vm.set_variable(str(argv[0]), v, 'list')
        else:
            vm.set_variable(str(argv[0]), Value(None), 'list')
        vm.stack.push(elem0)

    @staticmethod
    def do_sleep(vm, argv):
        if (len(argv) == 0):
            time.sleep(float('Inf'))
        else:
            time.sleep(argv[-1].numerify())

        vm.stack.push(argv[-1])

    @staticmethod
    def do_split(vm, argv):
        spec = argv[-1]
        var = argv[-2]
        if (var._val == None):
            var = vm.get_variable('_', 'scalar')

        # check if PATTERN is not really a PATTERN - but an expression
        regex_is_space = False
        if type(spec._val) != dict:
            s = spec.stringify()
            if s == ' ':
                regex_is_space = True
            spec = Value({ 'spec': spec.stringify(), 'opts': '' })

        regex = spec._val['spec']
        options = spec._val['opts']

        if regex == '':
            ret = [i for i in var.stringify()]

        # check for match of "NULL PATTERN"
        # makes "OK" for op.split test #6
        elif regex == ' *':
            ret = [i for i in var.stringify()]
            ret = ' '.join(ret).split(' ') # removes empty entries

        # makes "OK" for op.split test #5
        elif regex_is_space:
            ret = var.stringify().split()

        else:
            ret = re.split(regex, var.stringify(), parse_re_opts(vm, options))


        if (ret):
            mod_ret = []
            for i in ret:
                if i != '': mod_ret.append(i)

            vm.stack.push(Value(mod_ret))
        else:
            vm.stack.push(var)


    @staticmethod
    def do_printf(vm, fh, argv):
        BuiltIns.do_sprintf(vm, argv)
        BuiltIns.do_print(vm, fh, [ vm.stack.pop() ])

    @staticmethod
    def do_ord(vm, argv):
        vm.stack.push(Value(ord(argv[-1].stringify()[0])))

    @staticmethod
    def do_chr(vm, argv):
        try:
            val = chr(argv[-1].numerify())
            vm.stack.push(Value(val))
        except:
            vm.stack.push(Value(None))

    @staticmethod
    def do_hex(vm, argv):
        try:
            val = int((argv[-1].stringify()), 16)
            vm.stack.push(Value(val))
        except:
            vm.stack.push(Value(None))

    @staticmethod
    def do_oct(vm, argv):
        try:
            val = argv[-1].stringify()
            if val.upper().startswith("0X"):
                BuiltIns.do_hex(vm, argv)
            elif val.startswith("0"):
                val = int((argv[-1].stringify()), 8)
                vm.stack.push(Value(val))
            else:
                val = int((argv[-1].stringify()), 10)
                vm.stack.push(Value(val))
        except:
            vm.stack.push(Value(None))

    @staticmethod
    def do_int(vm, argv):
        try:
            val = int((argv[-1].numerify()))
            vm.stack.push(Value(val))
        except:
            vm.stack.push(Value(None))

    @staticmethod
    def do_time(vm, argv):
        vm.stack.push(Value(int(time.time())))

    @staticmethod
    def do_localtime(vm, argv):
        time_stamp = time.time()
        if (len(argv) > 0):
            time_stamp = argv[-1].numerify()
        parts = time.localtime(time_stamp)
        # $sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst
        parts_new = [ Value(parts.tm_sec), Value(parts.tm_min), Value(parts.tm_hour),
                    Value(parts.tm_mday), Value(parts.tm_mon), Value(parts.tm_year),
                    Value(parts.tm_wday), Value(parts.tm_yday), Value(parts.tm_isdst) ]
        vm.stack.push(Value(parts_new))

    @staticmethod
    def do_gmtime(vm, argv):
        time_stamp = time.time()
        if (len(argv) > 0):
            time_stamp = argv[-1].numerify()
        parts = time.gmtime(time_stamp)
        # $sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst
        parts_new = [ Value(parts.tm_sec), Value(parts.tm_min), Value(parts.tm_hour),
                    Value(parts.tm_mday), Value(parts.tm_mon), Value(parts.tm_year),
                    Value(parts.tm_wday), Value(parts.tm_yday), Value(parts.tm_isdst) ]
        vm.stack.push(Value(parts_new))

    @staticmethod
    def do_stat(vm, argv):
        f = None
        if (type(argv[-1]) is Value):
            f = argv[-1].stringify()
        else:
            f = vm.get_variable(argv[-1], 'raw')._val.name
        try:
            parts = os.stat(f)
            #$dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,
            #   $blksize,$blocks
            parts_new = [ Value(parts.st_dev), Value(parts.st_ino), Value(parts.st_mode),
                        Value( parts.st_nlink), Value(parts.st_uid), Value(parts.st_gid),
                        Value(parts.st_rdev), Value(parts.st_size), Value(parts.st_atime),
                        Value(parts.st_mtime), Value(parts.st_ctime), Value(parts.st_blksize),
                        Value(parts.st_blocks) ]
            vm.stack.push(Value(parts_new))
        except:
            vm.stack.push(Value(None))

    @staticmethod
    def do_substr(vm, argv):
        s = argv[-1].stringify()
        off = int(argv[-2].numerify())
        length = int(argv[-3].stringify())

        vm.stack.push(Value(s[off:length]))

    @staticmethod
    def do_exp(vm, argv):
        s = argv[-1].numerify()
        vm.stack.push(Value(math.exp(s)))

    @staticmethod
    def do_log(vm, argv):
        s = argv[-1].numerify()
        vm.stack.push(Value(math.log(s)))

    @staticmethod
    def do_sqrt(vm, argv):
        s = argv[-1].numerify()
        vm.stack.push(Value(math.sqrt(s)))

    @staticmethod
    def do_chdir(vm, argv):
        s = argv[-1].stringify()
        try:
            os.chdir(s)
            vm.stack.push(Value(1))
        except:
            vm.stack.push(Value(0))

    @staticmethod
    def do_umask(vm, argv):
        s = argv[-1].numerify()
        try:
            ret = os.umask(s)
            vm.stack.push(Value(ret))
        except:
            vm.stack.push(Value(0))

    @staticmethod
    def do_rename(vm, argv):
        old = argv[-1].stringify()
        new = argv[-2].stringify()
        try:
            os.rename(old, new)
            vm.stack.push(Value(1))
        except:
            vm.stack.push(Value(0))

    @staticmethod
    def do_unlink(vm, argv):
        count = 0
        for i in range(len(argv)-1, -1, -1):
            try:
                os.unlink(argv[i].stringify())
                count += 1
            except:
                pass
        vm.stack.push(Value(count))

    @staticmethod
    def do_link(vm, argv):
        old = argv[-1].stringify()
        new = argv[-2].stringify()
        try:
            os.link(old, new)
            vm.stack.push(Value(1))
        except:
            vm.stack.push(Value(0))

    @staticmethod
    def do_chmod(vm, argv):
        mode = argv[-1].numerify()
        argv = argv[0:-1]
        count = 0
        for i in range(len(argv)-1, -1, -1):
            try:
                os.chmod(argv[i].stringify(), mode)
                count += 1
            except:
                pass
        vm.stack.push(Value(count))
