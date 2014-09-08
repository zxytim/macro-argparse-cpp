/*
 * $File: numcvt.hh
 * $Date: Mon Sep 08 17:18:51 2014 +0800
 * $Author: Xinyu Zhou <zxytim[at]gmail[dot]com>
 */

#pragma once

#include <string>


template<class T>
inline T intcvt(int val) {
	return T(val);
}

template<>
inline std::string intcvt<std::string>(int val) {
	return std::to_string(val);
}

template<class T>
inline T floatcvt(float val) {
	return T(val);
}

template<>
inline std::string floatcvt<std::string>(float val) {
	return std::to_string(val);
}

template<class T>
inline T doublecvt(double val) {
	return T(val);
}

template<>
inline std::string doublecvt<std::string>(double val) {
	return std::to_string(val);
}

template<class T>
inline T boolcvt(bool val) {
	return T(val);
}

template<>
inline std::string boolcvt<std::string>(bool val) {
	if (val == false)
		return "false";
	return "true";
}

/*
 * vim: syntax=cpp11.doxygen foldmethod=marker foldmarker=f{{{,f}}}
 */

