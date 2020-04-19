

class DataStack():

    def __init__(self, max_size=100):
        self._stack = []
        self._maxsize = max_size
        
    def push(self, obj):
        self._stack.append(obj)
        if len(self._stack) > self._maxsize:
            self._stack = self._stack[1:] # dont let the stack exceed maxsize
    
    def __len__(self):
        return len(self._stack)
        
    def __getitem__(self, i):
        return self._stack[i]
        
    def pop(self):
        return self._stack.pop()