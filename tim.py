#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess

from timmu.tim.timscript import Tim


def helpful_exit(msg=__doc__):
    print(msg, file=sys.stderr)
    raise SystemExit

def parse_args(argv=sys.argv):
    global use_color
    tim = Tim()

    #argv = [arg.decode('utf-8') for arg in argv]

    if '--no-color' in argv:
        use_color = False
        argv.remove('--no-color')

    # prog = argv[0]
    if len(argv) == 1:
        helpful_exit('You must specify a command.')

    head = argv[1]
    tail = argv[2:]
      
    if head in ['-h', '--help', 'h', 'help']:
        helpful_exit()

    #elif head in ['e', 'edit']:
    #    fn = tim.edit
    #    args = {}

    elif head in ['bg', 'begin','o', 'on']:
        if not tail:
            helpful_exit('Need the name of whatever you are working on.')

        fn = tim.begin
        args = {
            'name': tail[0],
            'time': tim.to_datetime(' '.join(tail[1:])),
        }

    elif head in ['sw', 'switch']:
        if not tail:
            helpful_exit('I need the name of whatever you are working on.')

        fn = tim.switch
        args = {
            'name': tail[0],
            'time': tim.to_datetime(' '.join(tail[1:])),
        }

    elif head in ['f', 'fin', 'end', 'nd']:
        fn = tim.end
        args = {'time': tim.to_datetime(' '.join(tail))}

    elif head in ['st', 'status']:
        fn = tim.status
        args = {}

    #elif head in ['l', 'log']:
    #    fn = tim.log
    #    args = {'period': tail[0] if tail else None}

    elif head in ['hl', 'hledger']:
        fn = tim.hledger
        args = {'param': tail}

    elif head in ['hl1']:
        fn = tim.hledger
        args = {'param': ['balance', '--daily','--begin', 'today'] + tail}
    
    elif head in ['hl2']:
        fn = tim.hledger
        args = {'param': ['balance', '--daily','--begin', 'this week'] + tail}

    elif head in ['hl3']:
        fn = tim.hledger
        args = {'param': ['balance', '--weekly','--begin', 'this month'] + tail}

    elif head in ['hl4']:
        fn = tim.hledger
        args = {'param': ['balance', '--monthly','--begin', 'this year'] + tail}

    elif head in ['ini']:
        fn = tim.ini
        args = {}

    elif head in ['--version', '-v']:
        fn = tim.version
        args = {}

    elif head in ['pt', 'printtime']:
        fn = tim.printtime
        args = {'time': tim.to_datetime(' '.join(tail))}
    else:
        helpful_exit("I don't understand command '" + head + "'")

    return fn, args


def main():
    fn, args = parse_args()
    fn(**args)

if __name__ == '__main__':
    main()