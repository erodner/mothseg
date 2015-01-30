import argparse
import sys
import os
import csv
from glob import glob
import re
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--meta', help='CSV file with annotations')
parser.add_argument('--src', help='Directory with images', default='./')
parser.add_argument('--mode', choices=['copy', 'link', 'show'], default='show')
parser.add_argument('--dst', help='destination directory', default='classes/')
parser.add_argument('--prefix', help='File pattern', default='Ec-Geo-')

args = parser.parse_args()


examples = []
with open(args.meta, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',',quotechar='"')
    for row in reader:
        examples.append(row)

print "Number of examples: {}".format(len(examples))

reexprs = ['\....$', '-a\....$', 'a\....$']

for e in examples:
    if not 'ID' in e:
        continue

    if not 'Art-Nr' in e:
        continue

    eid = e['ID']
    try:
        classid = int(e['Art-Nr'])
    except ValueError, KeyError:
        logging.warn('Unknown category for {}'.format(eid))
        classid = 0


    globmask = args.src + args.prefix + eid + '*'
    results = sorted(glob(globmask))

    matchingfn = None
    matchingfnbase = None
    for reexpr in reexprs:
        for r in results:
            m = re.search(args.prefix + '(' + eid + reexpr + ')', r)
            if m:
                matchingfn = r
                matchingfnbase = m.groups(1)[0]
                break

        if not matchingfn is None:
            break

    if not matchingfn is None:
        dstdir = '%s/%08d' % (args.dst, int(classid))
        dstfile = '%s/%s' % (dstdir, matchingfnbase)

        if args.mode=='show':
            print matchingfn, classid, dstfile
        elif args.mode=='copy':
            pass
        elif args.mode=='link':
            try:
                os.mkdir(dstdir)
            except:
                pass

            try:
                os.symlink(matchingfn, dstfile)
            except:
                pass


    else:
        logging.warn('Image missing for {}'.format(eid))
