from __future__ import division


class Value(object):

    def __init__(self, val):
        self._val = val
        self._last_hash_key = 0 # used for each() iterator
        if (isinstance(val, list)):
            self.type = "List"
        elif (isinstance(val, dict)):
            self.type = "Hash"
        elif (val is None):
            self.type = "Undef"
        else:
            self.type = "Scalar"

    def get_obj_val(self):
        return self._val

    def set_obj_val(self, v):
        self._val = v

    # extracts a number from a SV
    # so... the SV could be a string, but we
    # try to get a number out of it
    def numerify(self):
        if (self.type == "Undef"):
            return 0
        if (self._val is None):
            return 0
        if (self.type == "Scalar" and isinstance(self._val, str)):
            f_decimal = False
            f_dash = False
            num = ""
            for c in self._val:
                if (str.isalpha(c)):
                    break
                if (c == '.'):
                    if (f_decimal):
                        break
                    else:
                        f_decimal = True
                        num += '.'
                if (c == '-'):
                    if (f_dash):
                        break
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

    def stringify(self, sep=''):
        """ Attempts to coerce 'Value' into string form"""

        if (self.type == "Undef"):
            return ""
        if (self.type == "Scalar"):
            if (str(self._val) == ""):
                return ""
            else:
                return str(self._val)
        elif (self.type == "List" or self.type == "Hash"):
            #return str(len(self._val))
            return sep.join(map(lambda x: str(x), self._val))
        else:
            return ""

    def boolify(self):
        if (self.type == "Undef"):
            return False
        if (self._val is None):
            return False
        if (self.type == "Scalar"):
            if (isinstance(self._val, str)):
                if (len(self._val) > 0):
                    return True
                else:
                    return False
            else:
                return self._val > 0
        elif (self.type == "List" or self.type == "Hash"):
            return len(self._val) > 0
        else:
            return False

    def scalar_context(self):
        """ Impose Scalar Context on this _val """
        if (self.type == "Undef"):
            return Value(None)
        if (self._val is None):
            return Value(None)
        if (self.type == "Scalar"):
            return Value(self._val)
        elif (self.type == "List"):
            return Value(len(self._val))
        elif (self.type == "Hash"):
            return Value(self._val.keys()[-1])
        else:
            return Value(None)

    def list_context(self):
        """ Impose List Context on this _val """
        if (self.type == "Undef"):
            return Value(None)
        if (self._val is None):
            return Value(None)
        if (self.type == "Scalar"):
            return Value([self._val])
        elif (self.type == "List"):
            return Value(self._val)
        elif (self.type == "Hash"):
            s = []
            for i in self._val:
                s.append(i)
                s.append(self._val[i])
            return Value(s)
        else:
            return Value(None)

    def hash_context(self):
        """Impose Hash Context on this _val"""
        if (self.type == "Undef"):
            return Value(None)
        if (self._val is None):
            return Value(None)
        if (self.type == "Scalar"):
            return Value({self._val: None})
        elif (self.type == "List"):
            return Value(self._val)
        elif (self.type == "Hash"):
            s = []
            for i in self._val:
                s.append(i)
                s.append(self._val[i])
            return Value(s)
        else:
            return Value(None)

    def _each(self):
        if (self.type == 'Hash'):
            try:
                arr = self._val.keys()
                arr.reverse()
                k = arr[self._last_hash_key]
                v = self._val[k]
                self._last_hash_key += 1
                return (Value(k), v)
            except IndexError:
                self._last_hash_key = 0 # reset it for next time
                return (Value(None), Value(None))
        else:
            raise Exception("Each arg must be a hash!")

    def __setitem__(self, key, v):
        if (self.type == "List"):
            if key >= len(self._val):
                end = key-len(self._val);
                for i in range(0, end+1):
                    self._val.append(Value(None))

            self._val[key] = v
        elif (self.type == "Hash"):
            self._val[key] = v
        elif (self.type == "Scalar"):
            if key >= len(self._val):
                end = key-len(self._val);
                for i in range(0, end+1):
                    self._val.append(Value(None))
            self._val[key] = v

    def __getitem__(self, key):
        if (self.type == "List"):
            if type(key) is slice:
                return self._val[key]
            else:
                if key >= len(self._val):
                    return Value(None)
                else:
                    return self._val[key]
        elif (self.type == "Hash"):
            if key in self._val:
                if type(self._val[key]) is Value:
                    return self._val[key]
                else:
                    return Value(self._val[key])
            else:
                return Value(None)
        else:
            return Value(None)

    def __str__(self):
        if (self.type == "Undef"):
            return ""
        elif (self.type == "Scalar"):
            return str(self._val)
        elif (self.type == "List"):
            return ",".join(map(lambda x: str(x), (self._val)))
        elif (self.type == "Hash"):
            s = "{"
            for i in self._val:
                s += str(i) + ' => ' + str(self._val[i]) + ','
            s = s.strip()
            s += '}'
            return s
        else:
            return ""

    def __int__(self):
        return int(self.numerify())

    def __float__(self):
        return self.numerify()

    def __len__(self):
        if (self.type == "Undef"):
            return Value(0)
        elif (self._val == "None"):
            return Value(0)
        elif (self.type == "Scalar" and isinstance(self._val, str)):
            return Value(len(self._val))
        elif (self.type == "List" or self.type == "Hash"):
            return Value(len(self._val))
        else:
            return Value(0)

    def __abs__(self):
        return Value(abs(self.numerify()))

    def __neg__(self):
        if (self.type == "List"):
            return -(self._val[-1].numerify())
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

    def prepend_list(self, other):
        if other.type == 'Scalar':
            return Value([other._val] + self._val)

        return Value(other._val + self._val)

    def list_concat(self, other):
        return Value(self._val + other._val)

    def str_concat(self, other):
        return Value(self.stringify() + other.stringify())

    def str_eq(self, other):
        return Value(self.stringify() == other.stringify())

    def str_ne(self, other):
        return Value(self.stringify() != other.stringify())

    def str_lt(self, other):
        return Value((self.stringify()) < (other.stringify()))

    def str_le(self, other):
        return Value((self.stringify()) <= (other.stringify()))

    def str_gt(self, other):
        return Value((self.stringify()) > (other.stringify()))

    def str_ge(self, other):
        return Value((self.stringify()) >= (other.stringify()))

    def __and__(self, other):
        return Value(self.numerify() & other.numerify())

    def __or__(self, other):
        return Value(self.numerify() | other.numerify())

    def __xor__(self, other):
        return Value(self.numerify() ^ other.numerify())

    def push(self, v):
        if (self.type == "List"):
            self._val.append(v)

    def reverse(self):
        if (self.type == "List"):
            self._val.reverse()

    def shift(self):
        if (self.type == "List"):
            val = self._val[0]
            self._val = _val[1:]
            return val
        else:
            raise Exception("shift must operate on array!")
