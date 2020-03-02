from __future__ import division

class Value(object):

    def __init__(self, val):
        self._val = val
        if (type(val) is list): self.type = "List"
        elif (type(val) is dict): self.type = "Hash"
        elif (val == None): self.type = "Undef"
        else: self.type = "Scalar"

    def get_obj_val(self):
        return self._val

    def set_obj_val(self, v):
        self._val = v
    
    # extracts a number from a SV
    # so... the SV could be a string, but we 
    # try to get a number out of it
    def numerify(self):
        if (self.type == "Undef"): return 0
        if (self._val == None): return 0
        if (self.type == "Scalar" and type(self._val) is str):
            f_decimal = False
            f_dash = False
            num = ""
            for c in self._val:
                if (str.isalpha(c)): break
                if (c == '.'):
                    if (f_decimal): break
                    else:
                        f_decimal = True
                        num += '.'
                if (c == '-'):
                    if (f_dash): break
                    else:
                        f_dash = True
                        num += '-'
                if (str.isdigit(c)):
                    num += c
            
            if (f_decimal):
                return float(num)
            else: 
                if (len(num) == 0):
                    return 0
                else:
                    return int(num)
                
        elif (self.type == "List" or self.type == "Hash"):
            return len(self._val)
        else:
            return self._val

    def stringify(self):
        if (self.type == "Undef"): return ""
        if (self._val == None): return "0"
        if (self.type == "Scalar"):
            if (str(self._val) == ""): return "0"
            else: return str(self._val)
        elif (self.type == "List" or self.type == "Hash"):
            return str(len(self._val))
        else:
            return ""
            
    def boolify(self):
        if (self.type == "Undef"): return False
        if (self._val == None): return False
        if (self.type == "Scalar"):
            if (type(self._val) is str):
                if (len(self._val) > 0): return True
                else: return False
            else:
                return self._val > 0
        elif (self.type == "List" or self.type == "Hash"):
            return len(self._val) > 0
        else:
            return False
            
    def __getitem__(self, key):
        if (self.type == "List"):
            if key > len(self._val):
                return Value(None)
            else:
                return Value(self._val[key])
        else:
            return Value(None)
    
    def __str__(self):
        return self.stringify()
        
    def __int__(self):
        return int(self.numerify())
        
    def __float__(self):
        return numerify()
        
    def __len__(self):
        if (self.type == "Undef"):
            return 0
        elif (self._val == "None"):
            return 0
        elif (self.type == "Scalar" and type(self._val) is str):
            return len(self._val)
        elif (self.type == "List" or self.type == "Hash"):
            return len(self._val)
        else:
            return 0

    def __abs__(self):
        return Value(abs(self.numerify()))
        
    def __neg__(self):
        if (self.type == "List"): return -(self._val[-1].numerify())
        return Value(-self.numerify())
        
    def __pos__(self):
        return Value(+self.numerify())
        
    def __invert__(self):
        return Value(~self.numerify())

    def __add__(self, other):
        return Value(self.numerify() + other.numerify())
        
    def __sub__(self, other):
        return Value(self.numerify() - other.numerify())
        
    def __mul__(self, other):
        return Value(self.numerify() * other.numerify())
        
    def __div__(self, other):
        return Value(self.numerify() / other.numerify())
        
    def __pow__(self, other):
        return Value(self.numerify() ** other.numerify())
        
    def __lshift__(self, other):
        return Value(int(self.numerify()) << int(other.numerify()))
        
    def __rshift__(self, other):
        return Value(int(self.numerify()) >> int(other.numerify()))
    
    def __lt__(self, other):
        return Value(self.numerify() < other.numerify())
        
    def __le__(self, other):
        return Value(self.numerify() <= other.numerify())
        
    def __eq__(self, other):
        return Value(self.numerify() == other.numerify())
        
    def __ne__(self, other):
        return Value(self.numerify() != other.numerify())
        
    def __gt__(self, other):
        return Value(self.numerify() > other.numerify())
        
    def __ge__(self, other):
        return Value(self.numerify() >= other.numerify())
                
    def str_concat(self, other):
        return Value(self.stringify() + other.stringify())
        
    def str_eq(self, other):
        return Value(self.stringify() == other.stringify())
        
    def str_lt(self, other):
        return Value(len(self.stringify()) < len(other.stringify()))
        
    def str_le(self, other):
        return Value(len(self.stringify()) <= len(other.stringify()))
        
    def str_gt(self, other):
        return Value(len(self.stringify()) > len(other.stringify()))
        
    def str_ge(self, other):
        return Value(len(self.stringify()) >= len(other.stringify()))
