#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import subprocess

from datetime import datetime, timedelta, date
from collections import defaultdict
import math

try:
    import ConfigParser
except:
    import configparser

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import shutil
import json, yaml

import pytz
import parsedatetime
# http://stackoverflow.com/questions/13218506/how-to-get-system-timezone-setting-and-pass-it-to-pytz-timezone
from tzlocal import get_localzone # $ pip install tzlocal
local_tz = get_localzone()

from duration import (
    to_iso8601,
    to_seconds,
    to_timedelta,
    to_tuple,
)
from coloring import TimColorer

# use_color = True

class JsonStore(object):
    """handles time log in json form"""

    def __init__(self):
        application_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.cfg_fname = os.path.abspath(os.path.join(application_path, '.tim.ini'))
        self.cfg = configparser.SafeConfigParser()

        self.cfg.add_section('tim')
        self.cfg.set('tim', 'folder', os.path.abspath(application_path))
        self.cfg.set('tim', 'editor', "vim")
        self.cfg.read(self.cfg_fname)  #no error if not found
        self.filename = os.path.abspath(os.path.join(self.cfg.get('tim','folder'), 'tim-sheet.json'))
        print("#self.filename: %s" % (self.filename))

    def load(self):
        """read from file"""
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                data = json.load(f)
        else:
            data = { 
                'work': [], 
                'interrupt_stack': [], 
                'estimate': {}, 
                'config': {
                    'autostart': False
                }
            }

        return data

    def dump(self, data):
        """write data to file"""
        with open(self.filename, 'w') as f:
            json.dump(data, f, separators=(',', ': '), indent=2)

class Tim(object):
    def __init__(self):
        self.tclr = TimColorer(use_color=True)
        self.date_format = '%Y-%m-%dT%H:%M:%SZ'
        self.store = JsonStore()
    
    

    def switch(self, name, time):
        self.end(time)
        self.begin(name, time)

    def begin(self, name, time):
        data = self.store.load()
        work = data['work']

        if work and 'end' not in work[-1]:
            print('You are already working on ' + self.tclr.yellow(work[-1]['name']) +
                    '. Stop it or use a different sheet.', file=sys.stderr)
            raise RuntimeError('You are already working on ' + work[-1]['name'] + '. Stop it or use a different sheet.')

        entry = {
            'name': name,
            'start': time,
        }

        work.append(entry)
        self.store.dump(data)

        print('Start working on ' + self.tclr.green(name) + ' at ' + time + '.')


    def printtime(self, time):
        print("You entered '" + time + "' as a test")


    def end(self, time, back_from_interrupt=True):
        if(not self.ensure_working()):
            return

        data = self.store.load()

        current = data['work'][-1]
        current['end'] = time

        start_time = self.parse_isotime(current['start'])
        # print(type(start_time), type(time))
        diff = self.timegap(start_time, self.parse_isotime(time))
        print('You stopped working on ' + self.tclr.red(current['name']) + ' at ' + time + ' (total: ' + self.tclr.bold(diff) + ').')
        self.store.dump(data)

    def set_estimate(self, name, time):
        data = self.store.load()

        data['estimate'][name] = time

        print('Set estimate ' + self.tclr.green(name) + ' to ' + time)
        self.store.dump(data)
    
    def get_estimate(self, name):
        data = self.store.load()

        return data['estimate'][name] if data['estimate'][name] else ""

    def set_config_autostart(self, value):
        data = self.store.load()

        data['config']['autostart'] = value

        self.store.dump(data)
    
    def get_config_autostart(self):
        data = self.store.load()

        return data['config']['autostart']

    def current_work(self):
        if (not self.is_working()):
            return ""
        # except SystemExit(1):
        #     return

        data = self.store.load()
        current = data['work'][-1]

        #start_time = self.parse_isotime(current['start'])
        #diff = self.timegap(start_time, datetime.utcnow())

        return current['name']

    def current_work_start_time(self):
        if (not self.is_working()):
            return None
        # except SystemExit(1):
        #     return

        data = self.store.load()
        current = data['work'][-1]

        return self.parse_isotime(current['start'])

    def get_status(self):
        if (not self.is_working()):
            return "", None
        # except SystemExit(1):
        #     return

        data = self.store.load()
        current = data['work'][-1]

        start_time = self.parse_isotime(current['start'])
        diff = self.timegap(start_time, datetime.utcnow())

        return current['name'], diff

    def diff(self, name):
        data = self.store.load()
        works_by_name = list(filter(lambda d: d['name'] == name, data['work']))

        if len(works_by_name) > 0:
            current = works_by_name[-1]

            start_time = self.parse_isotime(current['start'])
            end_time = self.parse_isotime(current['end']) if 'end' in current else datetime.utcnow()
            diff = end_time - start_time

            return diff

        return timedelta()

    def total_time(self, name):
        data = self.store.load()
        works_by_name = filter(lambda d: d['name'] == name, data['work'])

        total_seconds = 0
        for work in works_by_name:
            if work['start']:
                start_time = self.parse_isotime(work['start'])
                end_time = self.parse_isotime(work['end']) if 'end' in work else datetime.utcnow()
                diff = end_time - start_time

                total_seconds = total_seconds + diff.seconds

        delta = timedelta(seconds=total_seconds)
        return delta
    
    def total_time_str(self, name):
        data = self.store.load()
        works_by_name = filter(lambda d: d['name'] == name, data['work'])

        total_seconds = 0
        for work in works_by_name:
            if work['start']:
                start_time = self.parse_isotime(work['start'])
                end_time = self.parse_isotime(work['end']) if 'end' in work else datetime.utcnow()
                diff = end_time - start_time

                total_seconds = total_seconds + diff.seconds

        delta = timedelta(seconds=total_seconds)
        mins = math.floor(total_seconds / 60)
        hours = math.floor(mins/60)
        rem_mins = mins - hours * 60

        if mins == 0:
            return 'under 1 minute'
        elif mins < 59:
            return self.strfdelta(delta, "{minutes} minutes")
        elif mins < 1439:
            return self.strfdelta(delta, "{hours} hours and {minutes} minutes")
        else:
            return self.strfdelta(delta, " {hours} ({days} days)")

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)



    def status(self):
        name, diff = self.get_status()
        if not name:
            return ""

        print('You have been working on {0} for {1}.'
                .format(self.tclr.green(name), diff))

        return name, diff


    def hledger(self, param):
        # print("hledger param", param)
        data = self.store.load()
        work = data['work']

        # hlfname = os.path.expanduser('~/.tim.hledger')
        hlfname = os.path.join( self.store.cfg.get('tim', 'folder'), 'tim.timeclock')
        hlfile = open(hlfname, 'w')

        for item in work:
            if 'end' in item:
                str_on = "i %s %s" % (self.parse_isotime(item['start']), item['name'])
                str_off = "o %s" % (self.parse_isotime(item['end']))
                # print(str_on + "\n" + str_off)

                hlfile.write(str_on + "\n")
                hlfile.write(str_off + "\n")
                #  hlfile.write("\n")

        hlfile.close()

        cmd_list = ['hledger'] + ['-f'] + [hlfname] + param
        print("tim executes: " + " ".join(cmd_list))
        subprocess.call(cmd_list) 


    def ini(self):
        with open(self.store.cfg_fname, 'w') as configfile:
            self.store.cfg.write(configfile)

        print("#this is the ini file for tim - a tiny time keeping tool with hledger in the back")
        print("#I suggest you call tim ini > %s to start using this optional config file"
                %(os.path.abspath(self.store.cfg_fname)))


    def version(self):
        print("tim version " + __version__)
        return __version__


    #def edit(self):
    #    editor_cfg = self.store.cfg.get('tim', 'editor')
    #    print(editor_cfg)
    #    if 'EDITOR' in os.environ:
    #        cmd = os.getenv('EDITOR')
    #    if editor_cfg is not "":
    #        cmd = editor_cfg
    #    else:
    #        print("Please set the 'EDITOR' environment variable or adjust editor= in ini file", file=sys.stderr)
    #        return
    #
    #    bakname = os.path.abspath(store.filename + '.bak-' + date.today().strftime("%Y%m%d"))
    #    shutil.copy(store.filename, bakname)
    #    print("Created backup of main sheet at " + bakname + ".")
    #    print("You must delete those manually! Now begin editing!")
    #    subprocess.check_call(cmd + ' ' + store.filename, shell=True)
    

    def last_work(self):
        data = self.store.load()
        work_data = data.get('work') 
        is_working = work_data and 'end' not in data['work'][-1]
        if is_working:
            return ''

        # print(has_data)
        if work_data:
            last = work_data[-1]
            return last['name']

        return ''


    def is_working(self):
        data = self.store.load()
        work_data = data.get('work') 
        is_working = work_data and 'end' not in data['work'][-1]
        if is_working:
            return True

        return False

    def ensure_working(self):
        data = self.store.load()
        work_data = data.get('work') 
        is_working = work_data and 'end' not in data['work'][-1]
        if is_working:
            return True

        # print(has_data)
        if work_data:
            last = work_data[-1]
            print("For all I know, you last worked on {} from {} to {}".format(
                    self.tclr.blue(last['name']), self.tclr.green(last['start']), self.tclr.red(last['end'])),
                    file=sys.stderr)
            # print(data['work'][-1])
        else:
            print("For all I know, you " + self.tclr.bold("never") + " worked on anything."
                " I don't know what to do.", file=sys.stderr)

        print('See `ti -h` to know how to start working.', file=sys.stderr)
        return False


    def to_datetime(self, timestr):
        #Z denotes zulu for UTC (https://tools.ietf.org/html/rfc3339#section-2)
        # dt = parse_engtime(timestr).isoformat() + "Z" 
        dt = self.parse_engtime(timestr).strftime(self.date_format)
        return dt


    def parse_engtime(self, timestr):
    #http://stackoverflow.com/questions/4615250/python-convert-relative-date-string-to-absolute-date-stamp
        cal = parsedatetime.Calendar()
        if timestr is None or timestr is "":\
            timestr = 'now'

        #example from here: https://github.com/bear/parsedatetime/pull/60
        ret = cal.parseDT(timestr, tzinfo=local_tz)[0]
        ret_utc = ret.astimezone(pytz.utc)
        # ret = cal.parseDT(timestr, sourceTime=datetime.utcnow())[0]
        return ret_utc
        

    def parse_isotime(self, isotime):
        return datetime.strptime(isotime, self.date_format)


    def timegap(self, start_time, end_time):
        diff = end_time - start_time

        mins = math.floor(diff.seconds / 60)
        hours = math.floor(mins/60)
        rem_mins = mins - hours * 60

        if mins == 0:
            return 'under 1 minute'
        elif mins < 59:
            return '%d minutes' % (mins)
        elif mins < 1439:
            return '%d hours and %d minutes' % (hours, rem_mins)
        else:
            return "more than a day (%d hours)" % (hours)
   

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


def console_main():
    fn, args = parse_args()
    fn(**args)
