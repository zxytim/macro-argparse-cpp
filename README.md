macro-argparse-cpp
===================

Programs need command line arguments. I cherish the time when *argparse* module
in python make my life easier dealing with command line arguments, but sometimes
god needs us coding in c++ instead.

There are plenty of command line argument parser in the c/c++ world, such as:
+ GNU Getopt (http://www.gnu.org/software/libc/manual/html_node/Getopt.html)
+ Templatized C++ Command Line Parser Library http://tclap.sourceforge.net/
+ gflags (https://code.google.com/p/gflags/)
+ The Lean Mean C++ Option Parser (http://optionparser.sourceforge.net/)
+ ...

However, they are either too syntacticly ugly, too many zombie features that confusing,
or casting types anywhere and brining in too much concept and overhead that
complicates everything.

So I start design and write a command line parsing library myself. The command
line parser is defined using C macros, hence has 'macro' in the name.


Design goal
===========
+ keep code concise and informative
+ no explicit type casting
+ write less code
+ header files only

Requirements
============
a decent c++ compiler with c++11 support

Setup
=====
run *make* and you'll get two header files in *include*, namely:
+ macro-argparse-plain.hh
+ macro-argparse-jquery.hh
copy them along with all other header files in *include* to your project,
and include one of the above file. The difference between the two files
will be explained after.

HOW TO USE?
===========
Example:
```cpp
#include "macro-argparse-plain.hh"

DEF_ARGUMENT_CLASS(
	Argument,
	std::string,	name,		"zxytim",	OPTIONAL, OPT_SLH(-n, --name, "who to say"),
	std::string,	content,	"Bonjour",	OPTIONAL, OPT_SH(-c, "what to say"),
	int,			times,		1,			REQUIRED, OPT_LH(--times, "say how many times?"),
	bool,			decorate,	false,		OPTIONAL, OPT_SLWVH(-d, --decorate, true, "decoreate the output")
	);

int main(int argc, char *argv[]) {
	Argument args;
	if (!args.parse_args(argc, argv))
		return 1;
	if (args.decorate)
		std::cout << "==================" << std::endl;
	for (int i = 0; i < args.times; i ++)
		std::cout << args.content << " " << args.name << "!" << std::endl;
	if (args.decorate)
		std::cout << "==================" << std::endl;

	return 0;
}
```

results:
```
Error: `--times' required but not specified.
Usage: ./simple --times INT:TIMES [-c STRING:CONTENT] [-d] [-n STRING:NAME]
Options:
  --times INT:TIMES say how many times?
  -c STRING:CONTENT what to say
  -d, --decorate    decoreate the output
  -n, --name STRING:NAME who to say
```
more examples in *example* directory, use *make test* to compile them.


Define a class
--------------

Format of defining an argument class:
```
	DEF_ARGUMENT_CLASS(ArgumentClassName, [<type, name, default_val, presence, option>, ...])
```
where
+ presence is one of OPTIONAL or REQUIRED
+ option should be a call to macro OPT_<SPECIFIER>.


OPT_SPECIFIER format
--------------------

```
	OPT_SPECIFIER([<SHORT and/or LONG>, <SWITCH_TO_VAL>, <HELP>])
```
where SPECIFIER is a permutation of subsets of 'SLWH', defining the behavior of certain option:
+ S: SHORT
+ L: LONG
+ W: SWITCH_TO
+ H: HELP
subject to the contraint that there at least one of S or L should present.
The order parameters of OPT_SPECIFIER the same as order of charaters in in SPECIFIER.

for example: OPT_SLH denotes that there are three paramters: short option, long
option and help message. So OPT_SLH should be invoked like:

	OPT_SLH(-l, --long-option, "this is help message")

some more examples:

	OPT_LWH(--long-option, "witch_to_value", "this is help message")
	OPT_HL("this is help message", --long-option)
	OPT_L(--long-option)

Parse Arguments
-----------
call
```cpp
	args.parse_args(argc, argv);
```
or use initializer
```cpp
	Argument args(argc, argv);
```
and you are set.

Argument Accessing Style
------------------------
There are two argument accessing style. One is 'plain', in which arguments are
stored as a public member variable of the class:
```cpp
	std::cout << args.alpha << std::endl;
	args.beta = "hello";
```
and the other one is 'jquery', which borrows the idea of how jquery handles
getters and setters: a member function with no paramter is getter, and
a member function with a parameter acts as setter, and return the class instance,
so that you can call setters in a chain::
```
	std::cout << args.alpha() << std::endl;
	args.beta("hello").alpha(10).alpha("10").pi(3.1415926);
```

Furthermore, a generic setter *set* accessing arguments by string is also provided:
```cpp
	args.set("alpha", 10).set("alpha", "11");
```

Note that, a fallback is that  all names that the class originally used can not be
used again as arguments.


Type Cast
---------
As you can see, when you set the value to a argument, you can almost give
any reasonable type and we'll do the type convertion automatically for you.


Useful Helper Functions
-----------------------
+ print_help(std::ostream &&os, std::string const &prog_name): print the help message to *os*
+ dump(std::ostream &&os), dump(std::string const &path): dump parameters
+ load(std::istream &&os), load(std::string const &path): load parameters
+ std::vector<OptionInfo> get_option_info() const: retrieve option definitions


Development
===========
The project is undergo its fast prototyping phase. Source code
is not well-organized nor well-documented at this stage.

Any advice or question on the design or implementation techniques is warmly welcomed.
