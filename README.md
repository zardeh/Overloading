#On Code Golf and Function Decorators
###Or: Implementing Functional Pattern Matching in Python

(Full disclosure, I'm writing this at 3 AM, pardon any errors)

To start, a brief overview of function decorators, since this will delve heavily into them:

```python
def decorator(function):
    #create a closure 
    def newFunc(): #note that newFunc still has access to the function variable
        print "stuff before"
        function()
        print "stuff after"
    return newFunc

@decorator
def ello():
    print "hello world"

ello() #->

#stuff before
#hello world
#stuff after
```

That is the simplest form, if the function or decorator takes arguments, things invariably get more complicated, but that is not a huge issue for now, we really just need to understand how they work at a basic level and then do a bit of handwaving later.

So I am a new computer science student and two of my (many) passions are codegolf and abusing python, as quick look around this github will show.  Recently I stumbled across an implementation of a not-quite-quicksort algorithm in haskell:

```haskell
qsort (p:xs) = qsort [x | x<-xs, x<p] ++ [p] ++ qsort [x | x<-xs, x>=p]
```

It is reasonably straightforward in terms of what it does, and it comes straight from the [haskell wiki](http://www.haskell.org/haskellwiki/Introduction).  It uses some cool functional programming constructs though, and so the golfer in my immediately wanted to try and implement the same kind of quicksort in python and see how short I could make it.  After a few hours of work I cut it down to 101 characters (or 100 if you ignore the newline).  That's absolutely, mind-bogglingly aggravating.  Being that close to a sub-100 character solution was annoying and yet I could not make it any shorter.  At the time, my solution was

```python
#def q(a): 
#    return a if a==[] else q([y for y in a [1:] if y < a[0] ]) + [a[0]] + q([y for y in a[1:] if y >= a[0] ])

def q(a):return a if a==[]else q([y for y in a[1:]if y<a[0]])+[a[0]]+q([y for y in a[1:]if y>=a[0]])

assert q([0,3,7,5,2,9,5,3,4,12,7,99,8,126,2,17,3,24]) == [0, 2, 2, 3, 3, 3, 4, 5, 5, 7, 7, 8, 9, 12, 17, 24, 99, 126]
assert q([]) == []
```
This certainly worked and but I wanted shorter, so I started looking at other methods of doing the same things and quickly settled on argument unpacking, that is the weird *[alist] syntax where the list is unpacked into component values and submitted to a function that can then deal with them.  Ironically, as I write this up, I noticed that changing `return a if a==[]` to `return []if a==[]` removes a character, (sort of) dropping me below the 100 mark.  Thank goodness I didn't notice that before.  The result of the argument unpacking version is this

```python
#def q(*l): 
#    return [] if l==() else q(*[y for y in l [1:] if y < l[0] ]) + [l[0]] + q(*[y for y in l [1:] if y >= l[0] ])

def q(*l):return[]if l==()else q(*[y for y in l[1:]if y<l[0]])+[l[0]]+q(*[y for y in l[1:]if y>=l[0]])

assert q() == []
assert q(1) == [1]
assert q(1, 12, 7, 4, 17, 6, 5, 32, 9, 12, 1, 17, 4) == [1, 1, 4, 4, 5, 6, 7, 9, 12, 12, 17, 17, 32]
```

This one is doing almost exactly the same thing as the previous code, however its using argument unpacking and the *args ability in python to stand in for an arbitrary list of arguments.

Its at this point that I should mention that one, if you haven't noticed, I'm using python 2.7, and two, these both still look significantly more disgusting than the haskell version, mainly because of all of this list indexing, which also makes them longer.  In both cases, I had to index into the list and use 'a[0]'' as the pivot and 'a[1:]'' as the rest of the list, where as in Haskell these were abbreviated to 'p' and 'xs' respectively, significantly more concise and also easier to read.  Also, the list unpacking version is two or three characters longer than what I had before and as a result completely useless.  As a result, I decided to try something absolutely crazy

```python
def q(x,*s):return x and q(*[y for y in s if y<x]) +[x]+q(*[y for y in s if y>=x])
assert q() ==[]
```

I was duly met with an AssertionError.  That was exactly what I expected to happen considering that I was calling q with no arguments, when it quite clearly took a few.  I tabled the idea because spring break was ending and instead decided to ask one of my disgustingly knowledgeable friends if he noticed anything else that could shorted the code, since I still hadn't broken the 100 character floor.  Much like the astute among you, he almost immediately told me to change my original function to the following

```python
def q(a):return a and q([y for y in a[1:]if y<a[0]])+[a[0]]+q([y for y in a[1:]if y>=a[0]])
```

This uses a bit of trickery to great effect, and more importantly drops to you 92 characters (91 with no space).  I was, and still am, content with the function written to this length, but the seed had already been planted and I wanted to get the Haskell-esque implementation functional.  This is where we get back to decorators.

The Functional implementation would require some form of static type system, which I admit is a bit of heresy in python, but in this case I felt that the ends were worth the means.  I tried for a bit to implement my own typing system with function decorators, but couldn't do it.  The result of a bit of [google searching](https://www.google.com/#q=python+static+typing) was [this gem](http://stackoverflow.com/questions/15299878/how-to-use-python-decorators-to-check-function-arguments) that included an example implementation.  It was terrifying

```python
def accepts(*types):
    def check_accepts(f):
        assert len(types) == f.func_code.co_argcount
        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a,t)
            return f(*args, **kwds)
        new_f.func_name = f.func_name
        return new_f
    return check_accepts
```

To figure this out, not only did I need to spend 20 minutes looking at exactly what was going on and really thinking about how decorators were implemented, but I ended up drawing some pretty pictures and needing to look up what the hell 'new_f.func_name = f.func_name' and 'f.func_code.co_argcount' were, because I had never worked with function and code objects before, and that was a struggle since the documentation is aggravating, to say the least.  For anyone else, the inspect module and its docs are super useful here, as StackOverflow will inform.

So I now had an implementation of static type checking, and after rewriting the existing code a bit, mainly renaming variables and making debugging a bit easier, I had some valid code that looked reasonably good

```python 
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
```

This ran cleanly with no errors, but of course that was absolutely useless in terms of what I actually wanted which was pattern matching via method overloading and stuff like that.  Step one was pretty clear, I needed some sort of data structure for storing all of the different versions of the different functions, and after a few minutes of thought I decided that a dictionary of function names that mapped to arrays of functions would work.  Pretty soon afterwards, I realized that this was wrong, and settled on a dictionary whose keys were function names and whose values were other dictionaries whose keys were tuples of types and whose values were functions.  That's abstraction for you.  

Due to the magic of 'undo', I can actually show the exact code I had at different points, 

```python
class TypeCheck:

    def __init__(self):
        #a dict int the form {String name : Dict { Tuple (args) : Function function }}
        self.functions = {}
        pass

    def __call__(self, *types):
        def decorator(function):
            if function.func_code.func_name in self.functions:
                if types in self.functions[function.func_code.func_name]:
                    #stuff goes here

            #shenanigans
            if len(types) == function.func_code.co_argcount:
                def new_function(*args, **kwargs):
                    counter = 0
                    for (a, t) in zip(args, types):
                        if isinstance(a, t):
                            counter += 1
                        else:
                            print "you have an error, the var \"{}\" isn't of {}".format(a, str(t))
                    if counter == function.func_code.co_argcount:
                        return function(*args, **kwargs)
                new_function.func_name = function.func_name
                return new_function
            else:
                def fl(*args):
                    print "you're lists don't match"
                return fl
        return decorator
```

I was, at this point half way through the next logical step which was a maze of conditionals.  These would essentially check to see if a function with this name had been called before, if it had not, it would add the dictionary item.  Either way, it would then see what argument types were being used and once more check to see if those arguments were already in use for that function, in other words, had a function of the same name with the same types of arguments been instantiated before?  If yes, that's a problem that should throw an error, and if not, it would create the function in the dictionary.  In code this looks something like

```python
if function.func_name in self.functions:
    if types in self.functions[function.func_name]:
        function = self.functions[function.func_name][types]
    else:
        self.functions[function.func_name][types] = function
else:
    self.functions[function.func_name] = {types:function}
```

So, this still was not quite enough in terms of changes to the original version.  The 'new_function' dealt thiw zipping args and types, but in this case there would be multiple options for args and types and all but one would be wrong.  A quick look though the doc for the dictionary.'has_key' method and a few generator expressions later a reasonably efficient solution was at hand!

```python
def new_function(*args, **kwargs):
    if self.functions[function.func_name].has_key(tuple(type(arg) for arg in args)): #tipe babay!
        return self.functions[function.func_name][tuple(type(arg) for arg in args)](*args, **kwargs)
    else:
        print "you have an error, your variables aren't a valid format when you call {}".format(function)
```

Obviously I made some changes to the error reporting as well, but in essence this just finds the correct tuple of args if it exists and then calls the function with the relevant args/kwargs and if it cannot find matching types, it throws an "error."

Great!  At this point the whole thing actually works more or less (I believe, I actually lost my undo data a few edits back and so can't check what I had).  There's a big problem though, it can only deal with concrete sets of arguments.  Given a version of a function that takes (int, int) or (str, str), you're golden, but there is still no support for (int, *ints).  For reference, the code at this point was more or less

```python
class TypeCheck:

    def __init__(self):
        #a dict int the form {String name : Dict { Tuple (args) : Function function }}
        self.functions = {}

    def __call__(self, *types):
        def decorator(function):
            if function.func_name in self.functions:
                if types in self.functions[function.func_name]:
                    function = self.functions[function.func_name][types]
                else:
                    self.functions[function.func_name][types] = function
            else:
                self.functions[function.func_name] = {types:function}
            #shenanigans
            if len(types) == function.func_code.co_argcount:
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

@checker(int, int)
def add(num, numb):
    print "numbers"
    return num + numb

@checker(str, str)
def add(stri, string):
    print "strings"
    return stri + string
add(1,2)
add("yes, no", "maybe")
```

Most people would stop here.  This was a victory, this is functional, albeit limited, optional pattern matching in python, in like 20 lines.  Its a really awesome piece of code.  I'm not most people.  I wanted some way to support a *args type of syntax and get my function working.  There was an obvious first step, seeing if this worked (as an aside, the above code is fully functional and contains some debugging prints, so if you want to see some really long dictionaries made up of `"<type 'int'>"`, run the following on top of that code.  Its fun.)

```python
for i in range(100):
    @checker(tuple(int for z in range(i)))
    def summate(*args):
        return sum(args)
```

It throws an error, saying that the lists don't match, which was at the time I believe a mistake on my part, and through some further debugging work and the use of `pprint` and a lot of well spaced print statements I finally got the above block working, but felt it would be better to push it inside the "TypeCheck" class itself.  This, would be much cleaner than forcing someone to create a (weird, ugly, foreign) for loop every time they would need to use *args in a piece of code.  Its also, full disclosure, an inefficient solution, although I haven't finished fixing that yet, eventually though.  

To actually implement this in the class was a reasonably small change, by checking to see if *types contained `"args"`, which I decided should represent the use of a *args type syntax in the code block, you could then run some extra if checks and so if you don't see "args", you do exactly what we've been doing.  If, however you do see args, you do some variable gymnastics and then do exactly what we did above, run a for loop instantiating x functions with different numbers of arguments.  The whole block of code looked a bit like this

```python
if "args" not in types:
    if function.func_name in self.functions:
        if types in self.functions[function.func_name]:
            function = self.functions[function.func_name][types]
        else:
            self.functions[function.func_name][types] = function
    else:
        self.functions[function.func_name] = {types:function}
        #notice that this is exactly the same as before
else:
    for i in range(100):
        #this avoids a local variable used before assignment error
        types2 = types[:-1] + tuple(types[-2] for i in range(i))
        for i in range(100):
            if function.func_name in self.functions:
                if types2 in self.functions[function.func_name]:
                    function = self.functions[function.func_name][types2]
                else:
                    self.functions[function.func_name][types2] = function
            else:
                self.functions[function.func_name] = {types2:function}
```

As is, the code does make the (rather huge) assumption that if you have a system like `@checker(type1, type2, type3, "args")` that everything in args will be of type3.  This might not be the case and is solvable, its just not something I'm ready to do yet.  Also, as you can see, this code still does the stupid way of making every single possible instance of the class up to a bound, which in this case is hardcoded as 100.  This has the unfortunate side effect of being awfully slow, although with small numbers this isn't apparent, and it means that your *args can only hold a maximum of 100 objects, that's a reasonable downside.

My last challenge before using this therefore was to fix that and make the number of args user controllable, which was simply a matter of making the decorator take an extra argument and moving changing some list indicies.  All told, it currently looks like this, tests included:

```python
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
            #this is an important change, instead of the previous method of simply seeing if len(types) was the same as 
            #len(args), now we see if its the same length as any of the possible functions, an imperfect method but
            #one that does weed out in some cases
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
```

You might notice some things like this code being more or less in the file
```python
@checker()
def q():return ()
@checker(int, "args", 100) #args implies a *args type value, and 1000 is the expected maximum number of stargs
def q(x,*s):return x and q(*[y for y in s if y<x])+(x,)+q(*[y for y in s if y>=x])
```

Which is pretty awesome, because it means I got my line down to 83 (or 82) characters.  Now you might say that I need to count the other version of q which is called with no arguments, and I'm inclined to agree, but I completely broke the spirit of codegolf anyway when I wrote a class to remove a mediocre 11 characters from an already great piece of golfed python, so let me celebrate a bit.  Anyway, the concept is much more interesting, and there are still some things that can be done with it, like implementing a default value for the number of args, making it unnecessary, and making the code smarter by having it build versions of the function as necessary based on the number of arguments in stead of brute forcing them.  Neither of those is too difficult and would be logical next steps since, as it stands, using this for a number of args greater than 1000 or so quickly grows infeasible, with 10000 taking something like 34 seconds to run on my computer, and that's without mass pixel pushing or debugging or anything of that nature.

There are also a bunch of problems with the current implementation, it doesn't support **kwargs at all (I don't think, I haven't tested it, but it certainly won't let you typecheck them).  It also won't allow you to overwrite previous versions of a function, so your first `@checker(str, str)` of the `concate(a,b)` function will be the only one.  Those are all on my todo list for this, to be completed someday.

So thanks for slogging through all of this I hope you found it mildly entertaining and informative. If you have any suggestions feel free to let me know.  Any questions, feel free to ask them.  Also feel free to fork this or what not, though why you would want to I'm not sure, they're the ravings and results of a lunatic.  Finally, go ahead and use this as you see fit until the if/when I get a license in this repo.  Assume MIT.  Also if anyone has example of other people doing this, I would be really interested in seeing them, I looked around and didn't come across and prior implementations that allowed you the tools this gives you.
