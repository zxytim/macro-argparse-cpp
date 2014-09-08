#include "macro-argparse-plain.hh"

DEF_ARGUMENT_CLASS(
	Argument,
	std::string,	name,		"zxytim",	OPTIONAL, OPT_SLH(-n, --name, "who to say"),
	std::string,	content,	"Bonjour",	OPTIONAL, OPT_SH(-c, "what to say"),
	int,			times,		1,			REQUIRED, OPT_LH(--times, "say how many times?"),
	bool,			decorate,	false,		OPTIONAL, OPT_SLWH(-d, --decorate, true, "decoreate the output")
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
