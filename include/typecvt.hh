/*
 * $File: typecvt.hh
 * $Date: Mon Sep 08 17:19:37 2014 +0800
 * $Author: Xinyu Zhou <zxytim[at]gmail[dot]com>
 */

#pragma once

#include "strcvt.hh"
#include "numcvt.hh"

template <typename to_t, typename from_t>
to_t typecvt(from_t const &val) {
	return to_t(val);
};


template <typename to_t>
to_t typecvt(std::string const &val) {
	return strcvt<to_t>(val);
}


template <typename to_t>
to_t typecvt(char *val) {
	return strcvt<to_t>(std::string(val));
}

template <typename to_t, size_t N>
to_t typecvt(char const (&val)[N]) {
	return strcvt<to_t>(std::string(val));
}

template <typename to_t>
to_t typecvt(int val) {
	return intcvt<to_t>(val);
}

template <typename to_t>
to_t typecvt(bool val) {
	return boolcvt<to_t>(val);
}

template <typename to_t>
to_t typecvt(float val) {
	return floatcvt<to_t>(val);
}

template <typename to_t>
to_t typecvt(double val) {
	return doublecvt<to_t>(val);
}

/*
 * vim: syntax=cpp11.doxygen foldmethod=marker foldmarker=f{{{,f}}}
 */

