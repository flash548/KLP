from Value import Value
import sys

class BuiltIns():

    @staticmethod
    def do_print(vm, argv):
        sys.stdout.write((argv[0]).stringify())
        vm.stack.push(Value(1))
        
    @staticmethod
    def do_length(vm, argv):
        vm.stack.push(Value(len(str(argv[0]))))
        
    @staticmethod
    def do_join(vm, argv):
        ary = argv[0]
        joiner = argv[1]
        tmplist = []            
        for i in range(len(ary)):
            tmplist.append(str(ary[i]))
        
        vm.stack.push(Value(str(joiner).join(tmplist)))
        
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
        
        
        