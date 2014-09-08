#include "macro-argparse-jquery.hh"

#include <iostream>

DEF_ARGUMENT_CLASS(
	Argument,
	std::string,	input,		"",				REQUIRED, OPT_SLH(-i, --input, "I'm input"),
	std::string,	output,		"output.txt",	OPTIONAL, OPT_L(--output),
	int,			alpha,		"124",			OPTIONAL, OPT_SH(-a, "a brief help message"),
	bool,			beta,		false,			OPTIONAL, OPT_LW(--beta, true),
	std::string,	long_help,	"",				REQUIRED, OPT_LH(
		--long-help,
		"I have a very long help message that may break the typography I managed to keep. "
		"What will this help message look like when it's printed in the console? "
		"You can print me ugly or I'll let you feel pain in your ass!")
	);


int main(int argc, char *argv[]) {
	std::string file = "/tmp/arguments.txt";

	Argument args;
	args.print_help(std::cout, argv[0]);

	args.parse_args(argc, argv);
	std::cout << "====================" << std::endl;

	args.dump(std::cout).dump(file).load(file);
	std::cout << "====================" << std::endl;

	args.alpha(5).output(3);
	args.dump(std::cout);
	std::cout << "====================" << std::endl;

	args.alpha("12341234").alpha(123);
	args.set("alpha", "1234567");
	std::cout << args.alpha() << std::endl;
	std::cout << "====================" << std::endl;

	return 0;
}

