# Deluge Sickbeard plugin

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import collections

try:
  # Python 2.7+
  basestring
except NameError:
  # Python 3.3+
  basestring = str

_DEBUG = False

def _dbg(msg):
    if _DEBUG:
        print msg

def todict(obj, dup_ids = None):
    """
    Recursively convert a Python object graph to sequences (lists)
    and mappings (dicts) of primitives (bool, int, float, string, ...).

    Prevents infinte recursion(RuntimeError: maximum recursion depth
    exceeded). Circulair referencesare converted to None.
    """

    if None is dup_ids:
        dup_ids = []

    # Only enble for debugging; may throw asci conversion exception
    #_dbg("in: " + str(obj))

    if isinstance(obj, basestring):

        return obj

    elif isinstance(obj, dict):

        _dbg("dict: " + str(id(obj)))
        if id(obj) not in dup_ids:
            dup_ids.append(id(obj))
            d = dict((key, todict(val, dup_ids)) for key, val in obj.items())
            dup_ids.remove(id(obj))
            return d
        else:
            _dbg("Nested dict!: " + str(obj))
            return None

    elif isinstance(obj, collections.Iterable):

        _dbg("iterable: " + str(id(obj)))
        if id(obj) not in dup_ids:
            dup_ids.append(id(obj))
            d = [todict(val, dup_ids) for val in obj]
            dup_ids.remove(id(obj))
            return d
        else:
            _dbg("Nested iterable!: " + str(obj))
            return None

    elif hasattr(obj, '__dict__'):

        _dbg("__dict__: " + str(id(obj)))
        if id(obj) not in dup_ids:
            dup_ids.append(id(obj))
            d = todict(vars(obj), dup_ids)
            dup_ids.remove(id(obj))
            return d
        else:
            _dbg("Nested __dict_!: " + str(obj))
            return None

    elif hasattr(obj, '__slots__'):

        return todict(dict((name, getattr(obj, name), dup_ids) for name in getattr(obj, '__slots__')))


    return obj

def no_underscore(d):
    for key in d:
        if key.startswith("_"):
            nkey = key.replace("_", "", 1)
            d[nkey] = d[key]
            del d[key]

    return d

if __name__ == "__main__":

    class A:
        def __init__(self):
            self.a = 1
            self.b = 2
            self.c = 3
            self.d = None

    L  = [ 1, 2, 3, 4, 5, None ]
    L[5] = L

    D  = { 'a': 1, 'b': 2, 'c': 3}
    D['d'] = D

    a = A()
    a.d = a
    a.L = L
    a.D = D

    l = [a, a, a, L, L, D, D]
    _l = todict(l)

    d = { 'one': a, 'two': a, 'three': a, 'four': L, 'five': L, 'six': D, 'seven': D }
    _d = todict(d)

    l2 = [L, L, L]

    print "List: "
    print _l
    print "Dict: "
    print _d

    D = { '_a': 10, '_b': 12, 'hello': 9}
    print no_underscore(D)



