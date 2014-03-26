import pprint

#Lets have some fun.
#You know what decorators are, they look like this:

def decorator(function):
    def inner_function(*args, **kwargs):
        print args, kwargs
        x = function(*args, **kwargs)
        return x
    return inner_function

@decorator
def func(thing):
    print(thing)

func("thing")
print("--------------------------------------------------------------------------------------------------")
#-----------------------------------------------------------------------------------------------

#thats pretty simple.
#now step two is a decorator that can take arguments, the code looks like this


def check(*types):
    def decorator(f):
        #shenanigans to check function arglength vs. decorator arglength
        if len(types) == f.func_code.co_argcount:
            def new_f(*args, **kwds):
                counter = 0
                for (a, t) in zip(args, types):
                    if isinstance(a, t):
                        counter += 1
                    else:
                        print "you have an error, the var \"{}\" isn't of {}".format(a, str(t))
                        raise TypeError("")
                if counter == f.func_code.co_argcount:
                    return f(*args, **kwds)
            new_f.func_name = f.func_name
            return new_f
        else:
            def fl(*args):
                print "your list of types and list of args don't match"
            return fl
    return decorator

@check(str, int)
def hai(thing, thang):
    print thing

hai("hello world", 8)
hai("hi", 8)
print("--------------------------------------------------------------------------------------------------")

#-----------------------------------------------------------------------------------------------

class TypeCheck:

    def __init__(self):
        #a dict int the form {String name : Dict { Tuple (args) : Function function }}
        self.functions = {}

    def __call__(self, *types):
        def decorator(function):
            if "args" not in types:
                if function.func_name in self.functions:
                    if types in self.functions[function.func_name]:
                        function = self.functions[function.func_name][types]
                    else:
                        self.functions[function.func_name][types] = function
                else:
                    self.functions[function.func_name] = {types:function}
            else:
                for i in range(types[-1]):
                    types2 = types[:-2] + tuple(types[-3] for i in range(i))
                    for i in range(100):
                        if function.func_name in self.functions:
                            if types2 in self.functions[function.func_name]:
                                function = self.functions[function.func_name][types2]
                            else:
                                self.functions[function.func_name][types2] = function
                        else:
                            self.functions[function.func_name] = {types2:function}

            #shenanigans
            if len(types) in set(len(x) for x in self.functions[function.func_name].keys()):
                #print set(len(x) for x in self.functions[function.func_name].keys())
                #print self.functions
                def new_function(*args, **kwargs):
                    if self.functions[function.func_name].has_key(tuple(type(arg) for arg in args)): #tipe babay!
                        return self.functions[function.func_name][tuple(type(arg) for arg in args)](*args, **kwargs)
                    else:
                        print "you have an error, your variables aren't a valid format when you call {}".format(function)
                        
                new_function.func_name = function.func_name
                return new_function
            else:
                def fl(*args):
                    print self.functions[function.func_name]
                    print tuple(type(arg) for arg in args)
                    print args
                    print "you're lists don't match"
                return fl
        return decorator

checker = TypeCheck()
@checker(str)
def test(name):
    print "name"
    print name

@checker(int)
def test(number):
    print "number!"
    print number

@checker(int, int)
def add(num1, num2):
    print "darp"
    return num1 + num2

@checker(int, int)
def add(num, num2):
    return num + num2

@checker(int, "args", 15)
def test2(x, *s):
    return x and test2(*[y for y in s if y<x])+(x,)+test2(*[y for y in s if y>=x])

@checker()
def test2():
    return ()

test2(1)
print test2(7, 3, 9, 4, 6, 12, 37, 19, 2, 14, 66)

test(21)
test("help me")

print add(2, 3)


#THIS IS BEAUTIFUL OH MY GOD!
@checker(int, "args", 100) #args implies a *args type value, and 1000 is the expected maximum stargs
def q(x, *s):return x and q(*[y for y in s if y<x])+(x,)+q(*[y for y in s if y>=x])

@checker()
def q():
    return ()

print q(2, 7, 8, 9, 3, 6, 4, 1)
