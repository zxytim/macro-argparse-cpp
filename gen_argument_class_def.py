#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $File: gen_argument_class_def.py
# $Date: Mon Sep 08 19:46:51 2014 +0800
# $Author: Xinyu Zhou <zxytim[at]gmail[dot]com>

from itertools import permutations
import argparse


def gen_recursive(name, param_names, k=63, base=None, base_code=None):
    if base is None:
        base = len(param_names)
    param_str = ", ".join(param_names)

    ret = ''
    defaults = dict(name=name, param_str=param_str, base=base)
    for i in range(k, 0, -1):
        ret += r'''
            #define {name}_{n}({param_str}, ...) \
                {name}_{base}({param_str}); \
                {name}_{next_n}(__VA_ARGS__);
        '''.format(
                n=base + i * base,
                next_n=base + (i - 1) * base,
                **defaults)

    if base_code is not None:
        ret += r'''
            #define {name}_{base}({param_str}, ...) \
                {base_code}
        '''.format(base_code=base_code, **defaults)

    ret += r'''
        #define {name}(...) FORWARD_SUFFIX_BY_NUM_ARGS({name}_, __VA_ARGS__)
    '''.format(name=name)

    return ret


def enumerate_str_combination(lst):
    for i in xrange(1, 2**len(lst)):
        s = [lst[j] for j in xrange(len(lst)) if ((i >> j) & 1) == 1]
        for j in permutations(s):
            yield ''.join(j)


def gen_opt_parse_code():
    SPECIFIERS = 'SLWH'

    def gen_param_str(comb):
        param_dict = dict(
            S='SHORT', L='LONG', W='SWITCH_TO_VAL', H='HELP')
        return ', '.join(param_dict[c] for c in comb if c in param_dict)

    def gen_condition(comb):
        cond_dict=dict(
            S='argv[cur] == std::string(#SHORT)',
            L='argv[cur] == std::string(#LONG)')
        conds = [val for key, val in cond_dict.iteritems() if key in comb]
        if len(conds) == 0:
            raise RuntimeError('skip opt with no S and L')
        return ' || '.join(conds)

    def gen_opts(comb):
        opt_str_dict = dict(
            S='#SHORT',
            L='#LONG')
        opts = [val for key, val in opt_str_dict.iteritems() if key in comb]
        return opts

    def gen_opt_str(comb):
        return r'''\
            std::string ___opt_str = {opt_str}; \
        '''.format(opt_str='", " '.join(gen_opts(comb)))


    def gen_parse_code(comb):
        if 'W' in comb:
            code = r'''\
                ___var = typecvt<std::remove_reference<decltype(___var)>::type>(SWITCH_TO_VAL); \
                cur ++; \
                arg_status[___name] = OptionInfo::OPT_PRESENT; \
            '''
        else:  # assign value to ___var
            code = r'''\
                if (cur + 1 < argc) { \
                    ___var = typecvt<std::remove_reference<decltype(___var)>::type>(argv[cur + 1]); \
                    cur += 2; \
                    arg_status[___name] = OptionInfo::OPT_PRESENT; \
                } else { \
                    throw std::runtime_error( \
                        "additional argument needed for option `" + \
                        ___opt_str + "'"); \
                }\
            '''


        option_info_params = [
            ' ___type', '___name', '", "'.join(gen_opts(comb)),
            '___presence', '___default_val', '"{}"'.format(comb)]
        if 'H' in comb:
            option_info_params.append('HELP')

        return r'''\
            ___m_opt_info[___name] = OptionInfo({option_info_params}); \
            if (!hit && ({cond})) {{ \
                {opt_str}; \
                {code}; \
                hit = true; \
            }} \
        '''.format(
                cond=gen_condition(comb),
                opt_str=gen_opt_str(comb),
                option_info_params=', '.join(option_info_params),
                code=code)


    ret = ''
    for comb in enumerate_str_combination(SPECIFIERS):
        try:
            ret += r'''
                #define OPT_{comb}({param_str}) \
                    {parse_code}
            '''.format(
                    comb=comb,
                    param_str=gen_param_str(comb),
                    parse_code=gen_parse_code(comb))
        except RuntimeError as e:
            pass

    return ret


# gen_help_priner {{{
def gen_help_priner():
    return r'''
    class HelpPriner {
	protected:
		size_t const line_width_max = 80;

		std::vector<std::string> split_opt(std::string const &opts) {
			auto pos = opts.find(',');
			if (pos == std::string::npos)
                                return {__STRMANIP::trim_copy(opts)};
                        return {__STRMANIP::trim_copy(opts.substr(0, pos)),
                            __STRMANIP::trim_copy(opts.substr(pos + 1))};
		}

		std::string gen_opt_usage(const OptionInfo &info) {
			std::string ret;

			auto optstrs = split_opt(info.opts);
			std::sort(optstrs.begin(), optstrs.end(), [](std::string const &a, std::string const &b){
					return a.length() < b.length();
					});

			auto optstr = optstrs[0];
			ret = optstr + info.get_hint();

			if (info.presence == OPTIONAL)
				ret = "[" + ret + "]";
			return ret;
		}

		std::string gen_help_opt(const OptionInfo &info) {
			std::string ret;
			auto optstr = info.opts;
			ret = optstr + info.get_hint();
			return ret;
		}

		std::string gen_usage(std::string const &prog_name, const std::vector<OptionInfo> &infos) {
			size_t const usage_content_width_min = 50;

			std::vector<std::string> opt_usage;
			for (auto &info: infos)
				opt_usage.emplace_back(gen_opt_usage(info));


			std::string cur_line = "Usage: " + prog_name+ " ";
			std::string ret;

			size_t indent = cur_line.length();
			if (indent + usage_content_width_min > line_width_max) {
				indent = std::string("Usage: ").length();
				ret = cur_line + "\n";
				cur_line = std::string(indent, ' ');
			}

			for (size_t cur = 0; cur < opt_usage.size(); ) {
				bool has_content = false;
				while (cur < opt_usage.size()) {
					auto &cur_opt = opt_usage[cur];
					size_t margin_left = 1;
					if (!has_content) {
						margin_left = 0;
					}
					if (cur_line.length() + margin_left + cur_opt.length() < line_width_max) {
						cur_line += std::string(margin_left, ' ') + cur_opt;
						has_content = true;
						cur ++;
					} else break;
				}
				if (!has_content)
					cur_line += opt_usage[cur ++];
				ret += cur_line + "\n";
				cur_line = std::string(indent, ' ');
			}
			ret.pop_back();

			return ret;
		}

		static bool char_in_string(int ch, const std::string &str) {
			for (size_t i = 0; i < str.length(); i ++)
				if (ch == str[i])
					return true;
			return false;
		}

		std::vector<std::string> strsplit(const std::string &str, const std::string &sep = "") {

			std::vector<std::string> ret;

			auto is_sep = [&](int c) -> bool {
				if (sep.length())
					return char_in_string(c, sep);
				return isblank(c);
			};

			for (size_t i = 0; i < str.length(); ) {
				size_t j = i + 1;
				while (j < str.length() && !is_sep(str[j]))
					j ++;
				ret.emplace_back(str.substr(i, j - i));
				i = j + 1;
			}

			return ret;
		}

		std::vector<std::string> format_help_message(
				const std::string &help,
				size_t first_line_width,
				size_t line_width_max) {

			auto words = strsplit(help);
			size_t cur_line_width = first_line_width;
			std::string cur_line;
			std::vector<std::string> ret;
			for (auto &w: words) {
				for (; ;) {
					std::string next = (cur_line.length() == 0 ? "" : " ") + w;
					if (cur_line_width > cur_line.size() + next.length()) {
						cur_line += next;
						break;
					} else {
						ret.emplace_back(cur_line);
						cur_line_width = line_width_max;
						cur_line = "";
					}
				}
			}
			if (cur_line.length())
				ret.emplace_back(cur_line);
			if (ret.size() == 0)
				return {""};
			return ret;
		}


		std::string gen_option_help(const std::vector<OptionInfo> &infos) {
			int const help_message_width_max = 60,
				help_message_width_min = 30;
			std::string ret;

			assert(line_width_max > help_message_width_max);
			size_t help_message_indent = line_width_max - help_message_width_max;

			for (auto &info: infos) {
				std::string cur_line = "  " + gen_help_opt(info);
				if (cur_line.length() + 1 < help_message_indent)
					cur_line += std::string(help_message_indent - 1 - cur_line.size(), ' ');
				cur_line += " ";
				int remain = (int)line_width_max - (int)cur_line.length();

				assert(remain <= help_message_width_max);
				std::vector<std::string> help_message;
				if (remain > help_message_width_min)
					help_message = format_help_message(
							info.help,
							remain,
							help_message_width_max);
				else help_message = format_help_message(
						info.help,
						help_message_width_max,
						help_message_width_max);
				ret += cur_line + help_message[0] + "\n";
				for (size_t j = 1; j < help_message.size(); j ++)
					ret += std::string(help_message_indent, ' ') + help_message[j] + "\n";
			}
			return ret;
		}

	public:
		void print_help(std::ostream &&os, std::string const &prog_name, std::vector<OptionInfo> infos) {

			std::sort(infos.begin(), infos.end(),
					[](const OptionInfo &a, const OptionInfo &b){
					return a.presence > b.presence;
					});

			os << gen_usage(prog_name, infos) << std::endl;
			os << "Options: " << std::endl;
			os << gen_option_help(infos) << std::endl;
		}
		void print_help(std::ostream &os, std::string const &prog_name,
				const std::vector<OptionInfo> &infos) {
			print_help(std::move(os), prog_name, infos);
		}
        };
    '''
# }}}


def gen_option_info_class():
    return r'''
        struct OptionInfo { \
            enum { \
                OPT_ABSENT = 0, \
                OPT_PRESENT = 1 \
            }; \
            \
            OptionInfo() {} \
            OptionInfo( \
                std::string const &type, \
                std::string const &name, \
                std::string const &opts,  \
                int presence, \
                std::string const &default_val, \
                std::string const &specifier, \
                std::string const &help = "" \
            ): type(type), name(name), opts(opts), \
                presence(presence), \
                default_val(default_val), specifier(specifier), \
                help(help) \
            {} \
            bool is_switch() const { \
                return specifier.find('W') != std::string::npos; \
            }; \
            std::string get_hint() const { \
                if (is_switch()) \
                    return ""; \
                return " " + get_type_hint() + ":" + get_name_hint(); \
            } \
            std::string get_type_hint() const { \
                std::string ret = type; \
                if (type == "std::string") \
                    ret = "string"; \
                return to_upper(ret); \
            } \
            std::string get_name_hint() const { \
                return to_upper(name); \
            } \
            static std::string to_upper(std::string const& s) { \
                std::string ret; \
                for (size_t i = 0; i < s.length(); i ++) \
                    ret += (char)std::toupper(s[i]); \
                return ret; \
            } \
            static std::vector<std::string> split_opt(std::string const &opts) { \
                auto pos = opts.find(','); \
                if (pos == std::string::npos) \
                        return {__STRMANIP::trim_copy(opts)}; \
                return {__STRMANIP::trim_copy(opts.substr(0, pos)),  \
                    __STRMANIP::trim_copy(opts.substr(pos + 1))}; \
            } \
            std::vector<std::string> get_options() const { \
                auto p = split_opt(opts); \
                std::sort(p.begin(), p.end(), \
                    [](const std::string &a, const std::string &b){ \
                        return a.length() < b.length(); \
                    }); \
                return p;
            }; \
            std::string type, name, opts; \
            int presence; \
            std::string default_val, specifier, help; \
        };
    '''


def gen_strmanip_class():
    return r'''
    class __STRMANIP {
        public:
            inline static std::string trim_right_copy( \
              const std::string& s, \
              const std::string& delimiters = " \f\n\r\t\v" ) \
            { \
                auto pos = s.find_last_not_of( delimiters ); \
                if (pos == std::string::npos) \
                    return s; \
                return s.substr( 0, pos + 1 ); \
            } \
            \
            inline static std::string trim_left_copy( \
              const std::string& s, \
              const std::string& delimiters = " \f\n\r\t\v" ) \
            { \
                auto pos = s.find_first_not_of( delimiters ); \
                if (pos == std::string::npos) \
                    return s;  \
                return s.substr(pos); \
            } \
            \
            inline static std::string trim_copy( \
              const std::string& s, \
              const std::string& delimiters = " \f\n\r\t\v" ) \
            { \
              return trim_left_copy( trim_right_copy( s, delimiters ), delimiters ); \
            } \
    };
    '''


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--style', default='jquery',
        choices=['jquery', 'plain'],
        help='style for accessing values. jquery or plain')
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    params = 'type name default_val presence opt_parse_code'.split()

    print r'''
    #pragma once
    #include "typecvt.hh"
    #include "macro_traits.hh"

    #include <map>
    #include <cctype>
    #include <vector>
    #include <string>
    #include <cassert>
    #include <fstream>
    #include <sstream>
    #include <iostream>
    #include <algorithm>
    #include <stdexcept>
    #include <type_traits>

    '''

    if args.style == 'jquery':
        value_def_code = r'''\
                protected: \
                    type m_##name = typecvt<type>(default_val); \
                public: \
                    inline const type &name() const { \
                            return m_##name; \
                    } \
                    template <typename value_t> \
                    inline auto name(const value_t &v) -> decltype(*this) { \
                            m_##name = typecvt<type>(v); \
                            return *this; \
                    }
        '''
        value_getter = 'name()'
        value_setter = 'm_##name'
        print r'''#define DEF_POSITIONAL_ARGS \
                protected: \
                    std::vector<std::string> m_positional_args; \
                public: \
                    inline std::vector<std::string> &positional_args() { \
                        return m_positional_args; \
                    } \
                    inline const std::vector<std::string> &positional_args() const { \
                        return m_positional_args; \
                    } \
        '''
        print '#define POSITIONAL_ARGS positional_args()'
    else:
        value_def_code = r'''\
                public: \
                    type name = typecvt<type>(default_val); \
        '''
        value_getter = 'name'
        value_setter = 'name'
        print r'''#define DEF_POSITIONAL_ARGS \
                public: \
                    std::vector<std::string> positional_args; \
        '''
        print '#define POSITIONAL_ARGS positional_args'

    print gen_recursive(
        'DEF_ARGUMENT', params,
        base_code=value_def_code)


    print gen_recursive(
        'DEF_ARGUMENT_PARSER', params,
        base_code=r'''\
                {{ \
                    auto &___var = {}; \
                    std::string ___type = #type; \
                    std::string ___name = #name; \
                    std::string ___default_val = #default_val; \
                    int ___presence = presence; \
                    opt_parse_code; \
                }}
        '''.format(value_setter))

    print gen_recursive(
        'DEF_ARGUMENT_CHECK', params,
        base_code=r'''\
            switch (presence) { \
                case OPTIONAL: \
                    break; \
                case REQUIRED: \
                    if (arg_status[#name] != OptionInfo::OPT_PRESENT) { \
                        auto options = ___m_opt_info[#name].get_options(); \
                        throw std::runtime_error( \
                            "`" + options.back() + \
                            "' required but not specified."); \
                    } \
                    break; \
                default: \
                    throw std::runtime_error( \
                        ("unrecognized presence value for argument `" \
                        #name \
                        "': ") + \
                        std::to_string(presence)); \
            }
        ''')

    print gen_recursive(
        'DEF_ARGUMENT_DUMP', params,
        base_code=r'''\
            os << #name << " = " << {} << std::endl; \
        '''.format(value_getter))

    print gen_recursive(
        'DEF_ARGUMENT_SETTER', params,
        base_code=r'''\
            if (key == #name) \
                {} = typecvt<type>(val); \
        '''.format(value_setter))

    print r'''
        #define OPTIONAL 0
        #define REQUIRED 1
    '''

    print gen_opt_parse_code()

    print gen_strmanip_class()
    print gen_option_info_class()
    print gen_help_priner()


    print r'''
        #define DEF_ARGUMENT_CLASS(Name, ...) \
            class Name { \
                public: \
                    Name() { ___populate_option_info(); } \
                    Name(int argc, char *argv[]) { parse_args(argc, argv); } \
                    DEF_ARGUMENT(__VA_ARGS__); \
                public: \
                    template <typename value_type> \
                    auto set(const std::string &key, const value_type &val) \
                        -> decltype(*this) { \
                        DEF_ARGUMENT_SETTER(__VA_ARGS__); \
                        return *this; \
                    } \
                    bool parse_args(int argc, char *argv[]) { \
                        int cur = 1; \
                        std::map<std::string, int> arg_status; \
                        while (cur < argc) { \
                            bool hit = false; \
                            do { \
                                DEF_ARGUMENT_PARSER(__VA_ARGS__); \
                            } while (0); \
                            if (!hit) { \
                                POSITIONAL_ARGS.emplace_back(argv[cur]); \
                                cur ++; \
                            } \
                        } \
                        try { \
                            DEF_ARGUMENT_CHECK(__VA_ARGS__); \
                        } catch (std::runtime_error e) { \
                            std::cerr << "Error: " << e.what() << std::endl; \
                            print_help(std::cout, argv[0]); \
                            return false; \
                        } \
                        return true; \
                    } \
                    \
                    inline auto dump(std::ostream &&os) const -> decltype(*this) { \
                        DEF_ARGUMENT_DUMP(__VA_ARGS__); \
                        for (auto &p: POSITIONAL_ARGS) \
                            os << "positional_args" << " = " << p << std::endl; \
                        return *this; \
                    } \
                    inline auto dump(std::ostream &os) const -> decltype(*this) { \
                        return dump(std::move(os)); \
                    } \
                    inline auto dump(const std::string &path) const -> decltype(*this) { \
                        return dump(std::ofstream(path)); \
                    } \
                    \
                    inline static auto load(std::istream &&is) -> Name { \
                        auto ret = Name(); \
                        std::string line; \
                        int lineno = 0; \
                        while (std::getline(is, line)) { \
                            lineno ++; \
                            auto pos = line.find('='); \
                            if (pos == std::string::npos) { \
                                std::cerr << "Error reading line " << lineno << " while loading " #Name << std::endl; \
                                continue; \
                            } \
                            std::string name, val; \
                            if (pos > 0) \
                                name = line.substr(0, pos); \
                            val = line.substr(pos + 1); \
                            name = __STRMANIP::trim_copy(name); \
                            val = __STRMANIP::trim_copy(val); \
                            if (name == "positional_args") \
                                ret.POSITIONAL_ARGS.emplace_back(val); \
                            else ret.set(name, val); \
                        } \
                        ret.___populate_option_info(); \
                        return ret; \
                    } \
                    inline static auto load(std::istream &is) -> Name { \
                        return load(std::move(is)); \
                    } \
                    inline static auto load(const std::string &path) -> Name { \
                        return load(std::ifstream(path)); \
                    } \
                    \
                    inline auto print_help(std::ostream &&os, std::string const &prog_name) const -> decltype(*this) { \
                        HelpPriner().print_help(os, prog_name, get_option_info()); \
                        return *this; \
                    } \
                    inline auto print_help(std::ostream &os, std::string const &prog_name) const -> decltype(*this) { \
                        return print_help(std::move(os), prog_name); \
                    } \
                    inline std::vector<OptionInfo> get_option_info() const { \
                        std::vector<OptionInfo> ret; \
                        for (auto &p: ___m_opt_info) \
                            ret.emplace_back(p.second); \
                        return ret; \
                    } \
                    DEF_POSITIONAL_ARGS \
                protected: \
                    std::map<std::string, OptionInfo> ___m_opt_info; \
                    void ___populate_option_info() { \
                        int argc = 1; \
                        std::vector<std::string> argv = {"__dummy"}; \
                        int cur = 0; \
                        std::map<std::string, int> arg_status; \
                        bool hit = false; \
                        do { \
                            DEF_ARGUMENT_PARSER(__VA_ARGS__); \
                        } while (0); \
                    } \
            };

    '''

if __name__ == '__main__':
    main()

# vim: foldmethod=marker foldmarker=f{{{,f}}}

