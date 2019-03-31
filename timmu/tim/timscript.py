#from __future__ import print_function
#from __future__ import unicode_literals

import sys
import os
import subprocess

from datetime import datetime, timedelta, date, timezone
from dateutil import parser
from dateutil.relativedelta import relativedelta
import math

import configparser
from io import StringIO

import shutil
import json


#from duration import (
#    to_iso8601,
#    to_seconds,
#    to_timedelta,
#    to_tuple,
#)
from .coloring import TimColorer

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
        self.date_format_hledger = '%Y/%m-/%d %H:%M:%S'
        self.store = JsonStore()

        self.data = self.store.load()
        if not 'config' in self.data:
            self.data['config'] = {}
        if not 'work' in self.data:
            self.data['work'] = []

        self.data_map = self.gen_map(self.data)
    
    

    def switch(self, name, time):
        self.end(time)
        self.begin(name, time)

    def begin(self, name, time):
        self.data = self.store.load()
        work = self.data['work']

        if work and 'end' not in work[-1]:
            print('You are already working on ' + self.tclr.yellow(work[-1]['name']) +
                    '. Stop it or use a different sheet.', file=sys.stderr)
            raise RuntimeError('You are already working on ' + work[-1]['name'] + '. Stop it or use a different sheet.')

        entry = {
            'name': name,
            'start': time,
        }

        work.append(entry)
        self.store.dump(self.data)

        print('Start working on ' + self.tclr.green(name) + ' at ' + time + '.')


    def printtime(self, time):
        print("You entered '" + time + "' as a test")


    def end(self, time, back_from_interrupt=True):
        if(not self.ensure_working()):
            return

        self.data = self.store.load()

        current = self.data['work'][-1]
        current['end'] = time

        start_time = self.parse_isotime(current['start'])
        # print(type(start_time), type(time))
        diff = self.timegap(start_time, self.parse_isotime(time))
        print('You stopped working on ' + self.tclr.red(current['name']) + ' at ' + time + ' (total: ' + self.tclr.bold(diff) + ').')

        self.store.dump(self.data)

        self.hledger_save(self.data)
        self.data_map = self.gen_map(self.data)
        print(json.dumps(self.data_map, indent=4, sort_keys=True, default=str))

    def set_estimate(self, name, time):
        self.data = self.store.load()

        if not self.data['estimate']:
            self.data['estimate'] = {}

        self.data['estimate'][name] = time

        print('Set estimate ' + self.tclr.green(name) + ' to ' + time)
        self.store.dump(self.data)
    
    def get_estimate(self, name):
        #self.data = self.store.load()

        return self.data['estimate'] if 'estimate' in self.data and name in self.data['estimate'] else ""

    def set_config_autostart(self, value):
        self.data = self.store.load()

        self.data['config']['autostart'] = value

        self.store.dump(data)
    
    def get_config_autostart(self):
        #data = self.store.load()

        return self.data['config']['autostart'] if 'config' in self.data and 'autostart' in self.data['config'] else False

    def current_work(self):
        if (not self.is_working()):
            return ""
        # except SystemExit(1):
        #     return

        #data = self.store.load()
        current = self.data['work'][-1]

        #start_time = self.parse_isotime(current['start'])
        #diff = self.timegap(start_time, datetime.now(timezone.utc))

        return current['name']

    def current_work_start_time(self):
        if (not self.is_working()):
            return None
        # except SystemExit(1):
        #     return

        #data = self.store.load()
        current = self.data['work'][-1]

        return self.parse_isotime(current['start'])

    def get_status(self):
        if (not self.is_working()):
            return "", None
        # except SystemExit(1):
        #     return

        #data = self.store.load()
        current = self.data['work'][-1]

        start_time = self.parse_isotime(current['start'])
        diff = self.timegap(start_time, datetime.now(timezone.utc))

        return current['name'], diff

    def diff(self, name):
        #data = self.store.load()
        works_by_name = list(filter(lambda d: d['name'] == name, self.data['work']))

        if len(works_by_name) > 0:
            current = works_by_name[-1]

            start_time = self.parse_isotime(current['start'])
            end_time = self.parse_isotime(current['end']) if 'end' in current else datetime.now(timezone.utc)
            diff = end_time - start_time

            return diff

        return timedelta()

    def total_time(self, name):
        #data = self.store.load()
        works_by_name = filter(lambda d: d['name'] == name, self.data['work'])

        total_seconds = 0
        for work in works_by_name:
            if work['start']:
                start_time = self.parse_isotime(work['start'])
                end_time = self.parse_isotime(work['end']) if 'end' in work else datetime.now(timezone.utc)
                diff = end_time - start_time

                total_seconds = total_seconds + diff.seconds

        delta = timedelta(seconds=total_seconds)
        return delta
    
    def total_time_str(self, name):
        #data = self.store.load()
        works_by_name = filter(lambda d: d['name'] == name, self.data['work'])

        total_seconds = 0
        for work in works_by_name:
            if 'start' in  work and work['start']:
                start_time = self.parse_isotime(work['start'])
                end_time = self.parse_isotime(work['end']) if 'end' in work else datetime.now(timezone.utc)
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
            return '{:02}:{:02} ({} days)'.format(int(hours), int(mins), delta.days)

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


    def hledger_save(self, data):
        work = data['work']

        # hlfname = os.path.expanduser('~/.tim.hledger')
        hlfname = os.path.join( self.store.cfg.get('tim', 'folder'), 'tim.timeclock')
        hlfile = open(hlfname, 'w')

        for item in work:
            if 'end' in item:
                str_on = "i %s %s" % (self.parse_isotime_str_hledger(item['start']), item['name'])
                str_off = "o %s" % (self.parse_isotime_str_hledger(item['end']))
                # print(str_on + "\n" + str_off)

                hlfile.write(str_on + "\n")
                hlfile.write(str_off + "\n")
                #  hlfile.write("\n")

        hlfile.close()

        return hlfname

    def hledger(self, param):
        # print("hledger param", param)
        data = self.store.load()
        hlfname = self.hledger_save(data)

        cmd_list = ['hledger', '-f', hlfname].extend(param.split(' '))
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
        #data = self.store.load()
        work_data = self.data.get('work')
        is_working = work_data and not 'end' in work_data[-1]
        if is_working:
            return ''

        # print(has_data)
        if work_data:
            last = work_data[-1]
            return last['name']

        return ''


    def is_working(self):
        #data = self.store.load()
        work_data = self.data.get('work')
        is_working = work_data and not 'end' in work_data[-1]
        if is_working:
            return True

        return False

    def ensure_working(self):
        #data = self.store.load()
        work_data = self.data.get('work') 
        is_working = work_data and not 'end' in work_data[-1]
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
        dt = self.parse_engtime(timestr).isoformat()
        return dt


    def parse_engtime(self, timestr):
        if timestr is None or timestr is "":
            return datetime.now(timezone.utc)

        try:
            LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
            tzinfos={ "tzname": LOCAL_TIMEZONE }
            dt = parser.parse(timestr, tzinfos=tzinfos)

            dt = dt.astimezone(timezone.utc)

            return dt
        except ValueError:
            timestr = self.get_past_date(timestr)
            dt = parser.parse(timestr)

            return dt

        return datetime.now(timezone.utc)
        
    def get_past_date(self, str_days_ago):
        # https://stackoverflow.com/questions/12566152/python-x-days-ago-to-datetime
        now = datetime.now(timezone.utc)

        splitted = str_days_ago.split()
        if len(splitted) == 1 and splitted[0].lower() == 'today':
            return str(now.isoformat())
        elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
            date = now - relativedelta(days=1)
            return str(date.isoformat())
        elif len(splitted) == 3 and splitted[2].lower() in ['ago']:
            if splitted[1].lower() in ['second', 'seconds', 'sec', 's']:
                date = now - relativedelta(seconds=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['minute', 'minutes', 'min', 'm']:
                date = now - relativedelta(minutes=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
                date = now - relativedelta(hours=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['day', 'days', 'd']:
                date = now - relativedelta(days=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
                date = now - relativedelta(weeks=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
                date = now - relativedelta(months=int(splitted[0]))
                return str(date.isoformat())
            elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
                date = now - relativedelta(years=int(splitted[0]))
                return str(date.isoformat())
        
        return str(now.isoformat())

    def parse_isotime(self, isotime):
        LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
        tzinfos={ "tzname": LOCAL_TIMEZONE }
        dt = parser.parse(isotime, tzinfos=tzinfos)

        dt = dt.astimezone(timezone.utc)
        return dt

    def parse_isotime_str(self, isotime):
        return self.parse_isotime(isotime).strftime(self.date_format)

    def parse_isotime_str_hledger(self, isotime):
        return self.parse_isotime(isotime).strftime(self.date_format_hledger)

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
   
    def gen_map(self, data):
        works = data['work']

        ret = {}

        total_seconds = 0
        for work in works:
            if work['start']:
                name = work['name']

                start_time = self.parse_isotime(work['start'])
                end_time = self.parse_isotime(work['end']) if 'end' in work else datetime.now(timezone.utc)
                diff = end_time - start_time

                total_seconds = total_seconds + diff.seconds

                delta = timedelta(seconds=total_seconds)
                mins = math.floor(total_seconds / 60)
                hours = math.floor(mins/60)
                rem_mins = mins - hours * 60

                if mins == 0:
                    dura_str = 'under 1 minute'
                elif mins < 59:
                    dura_str = self.strfdelta(delta, "{minutes} minutes")
                elif mins < 1439:
                    dura_str = self.strfdelta(delta, "{hours} hours and {minutes} minutes")
                else:
                    dura_str = self.strfdelta(delta, " {hours} ({days} days)")


                nn = ""
                for n in name.split(':'):
                    nn = nn + ":" + n if nn != "" else n

                    if nn:
                        if not nn in ret:
                            ret[nn] = {}
                            ret[nn]['work'] = []
                            ret[nn]['delta'] = timedelta(0)
                            ret[nn]['total_seconds'] = 0
                            ret[nn]['name'] = nn

                        entry = { 
                            'start': start_time,
                            'end': end_time,
                            'diff': diff, 
                            'dura_str': dura_str 
                        }    
                        
                        ret[nn]['work'].append(entry)
                        ret[nn]['delta'] = ret[nn]['delta'] + delta
                        ret[nn]['name'] = nn
                        ret[nn]['total_seconds'] = ret[nn]['total_seconds'] + total_seconds

        return ret