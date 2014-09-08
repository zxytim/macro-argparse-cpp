/*
 * $File: strcvt.hh
 * $Date: Mon Sep 08 03:15:14 2014 +0800
 * $Author: Xinyu Zhou <zxytim[at]gmail[dot]com>
 */

#pragma once

#include <string>
#include <cstdlib>


template<class T>
inline T strcvt(const std::string &val) {
	return T(val);
}

template<>
inline bool strcvt<bool>(const std::string &val) {
	if (val == "0" || val == "false")
		return false;
	return true;
}

#define DEF_STR2NUM_TEMPLATE(type, cvt) \
	template<> \
	inline type strcvt<type>(const std::string &val) { \
		if (val == "false") \
			return 0; \
		else if (val == "true") \
			return 1; \
		return cvt(val.c_str()); \
	} \


DEF_STR2NUM_TEMPLATE(int, atoi);
DEF_STR2NUM_TEMPLATE(float, atof);
DEF_STR2NUM_TEMPLATE(double, atof);

/*
 * vim: syntax=cpp11.doxygen foldmethod=marker foldmarker=f{{{,f}}}
 */

