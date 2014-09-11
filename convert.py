#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""convert benchmark log for gnuplot

USAGE ::= convert <tool> <filename> [<tool> <filename> ...]
TOOL  ::= ypsilon | gosh | guile
"""
from __future__ import print_function, unicode_literals

__author__  = "letoh"
__version__ = "0.1"

import re
from collections import OrderedDict as od


_pat_suite = re.compile(r'^;;\s*(\w+)$')
_pat_case  = re.compile(r'^;;?\s*([\w]+)\s+[^\s]+')
_pat_sep   = re.compile(r'^;;?\s*-+')

def __parse_log(ins, pat_time):
    result = od()
    suite = None
    while True:
        try:
            line = ins.next()
            m = _pat_suite.match(line)
            if m:
                suite = m.groups()[0]
                result[suite] = {}
                #print('suite:', suite)
                continue
            m = _pat_case.match(line)
            if m:
                case = m.groups()[0]
                #print('case:', case, end='\t')
                while True:
                    line = ins.next()
                    m = _pat_sep.match(line)
                    if m: break
                    m = pat_time.match(line)
                    if m:
                        result[suite][case] = float(m.groups()[0])
                        #print('time:', m.groups()[0])
                        break
        except StopIteration:
            break
    return result


def parse(logs):
    gosh    = lambda ins: __parse_log(ins, re.compile(r'^;\s+real\s+([\d\.]+)'))
    guile   = lambda ins: __parse_log(ins, re.compile(r'^\s*([\d\.]+)'))
    ypsilon = lambda ins: __parse_log(ins, re.compile(r'^;;\s+([\d\.]+)\s+real'))

    bench = od()
    for tool, fname in logs:
        try:
            with open(fname, 'r') as ins:
                tool_result = eval(tool)(ins)
                #pprint(tool_result)
                bench[tool] = tool_result
        except IOError as e:
            print(e)
        except NameError as e:
            print(e)
    return bench


def main(argv, stdout):
    bench = parse(zip(*[iter(argv[1:])]*2))

    tools  = bench.keys()

    def _time(suite, case, fout=stdout):
        print(case, ' '.join(map(str, [bench[tool][suite][case] for tool in tools])), file=fout)

    def _ratio(suite, case, fout=stdout):
        d = [bench[tool][suite][case] for tool in tools]
        m = min(d)
        d2 = map(lambda x: m / x, d)
        print(case, ' '.join(map(str, d2)), file=fout)

    def show_data(fmt, fout=stdout):
        print('tools', ' '.join(tools), file=fout)
        for suite in bench[tools[0]].keys():
            #print("#", suite, file=fout)
            cases  = bench[tools[0]][suite].keys()
            for case in cases:
                fmt(suite, case, fout)
        return

    with open('bench-ratio.dat', 'w') as out:
        show_data(_ratio, out)
    with open('bench-time.dat', 'w') as out:
        show_data(_time, out)


if __name__ == '__main__':
    from sys import argv, stdout
    main(argv, stdout)
