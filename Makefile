

all: include/macro-argparse-jquery.hh include/macro-argparse-plain.hh

include/macro-argparse-jquery.hh: gen_argument_class_def.py
	./gen_argument_class_def.py -s jquery > include/macro-argparse-jquery.hh

include/macro-argparse-plain.hh: gen_argument_class_def.py
	./gen_argument_class_def.py -s plain > include/macro-argparse-plain.hh

test: include/macro-argparse-plain.hh include/macro-argparse-jquery.hh example/simple.cpp example/argument_def_test.cpp
	g++ example/simple.cpp -I include -o example/simple -std=c++11 -Wall -Wextra
	g++ example/argument_def_test.cpp -I include -o example/argument_def_test -std=c++11 -Wall -Wextra

clean:
	rm -rf example/argument_def_test example/simple include/macro-argparse-plain.hh include/macro-argparse-jquery.hh
