#!/usr/bin/env python

import os
import re
import argparse
import shutil

parser = argparse.ArgumentParser("tidyINRAdata")
parser.add_argument('--input', help = "Input folder", type = str)
parser.add_argument('--output', help = "Output folder", type = str)
args = parser.parse_args()


p = re.compile(r"(?P<unknowncode>\w+-\w+)_ARCH(?P<date1>\d{4}-\d{2}-\d{2})(?P<date2>\d{4}-\d{2}-\d{2})\s(?P<time>\d{2}_\d{2}_\d{2})vis_(?P<view>(sv|tv))(?P<angle>\d+)\.png")

count = {}
manylist = []
for root, dirs, files in os.walk(os.path.normpath(args.input)):
    for f in files:
        print "current filename: %s" % f
        m = p.match(f)
        if m:
            date = m.group('date2')
            time = m.group('time')
            view = m.group('view')
            angle = m.group('angle')
            print date+" "+time+" "+view+" "+angle
            if not date in count:
                count[date] = 0
            if not os.path.exists(os.path.join(args.output, date)):
                os.mkdir(os.path.join(args.output,date))
            shutil.copy(os.path.join(root,f), os.path.join(args.output,date)) 
            if view == 'sv':
                os.rename(os.path.join(args.output, date, f), os.path.join(args.output,date, "Image_C0_%03d.png"%int(angle)))
                count[date] += 1
            elif view == 'tv':
                os.rename(os.path.join(args.output, date, f), os.path.join(args.output,date, "Image_C34_%03d.png"%int(angle)))
            if count[date] > 2 and not date in manylist :
                manylist.append(date)
                
        else:
            print "No match found."

manylist = sorted(manylist)
with open(os.path.join(args.output, "report.txt"),'w') as f:
    for row in manylist:
        f.write("%s\n"%row)


