import argparse

parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--imagelist', default='imagelist.txt')
parser.add_argument('--dstdir', default='thumbnails/')
parser.add_argument('--labels', default=None)

args = parser.parse_args()

import os
import re


def readlist(listfn):
    """ read a simple text file into an array """
    with open(listfn, 'r') as textf:
        return textf.read().splitlines()

imagelist = readlist(args.imagelist)
if not args.labels is None:
    labels = readlist(args.labels)

import os.path
classes_index = {}
for k, imagefn in enumerate(imagelist):
    if args.labels is None:
        m = re.search('([^\/\\\\]+)[\/\\\\]([^\/\\\\]+)\.[^\.]+$', imagefn)
        if not m:
            raise Exception('Image file {} does not match pattern for ID parsing'.format(imagefn))
        imagefn_class = m.groups(1)[0]
        imagefn_id = m.groups(1)[1]
    else:
        m = re.search('([^\/\\\\]+)\.[^\.]+$', imagefn)
        if not m:
            raise Exception('Image file {} does not match pattern for ID parsing'.format(imagefn))
        imagefn_class = labels[k]
        imagefn_id = m.groups(1)[0]


    if not imagefn_class in classes_index:
        classes_index[imagefn_class] = set()
    classes_index[imagefn_class].add(imagefn)

for myclass in classes_index:
    mylist = ' '.join(classes_index[myclass])

    avgout = os.path.join(args.dstdir, myclass + '.png')
    print "convert -geometry \!100x\!62 {} -average -flatten {}".format(mylist, avgout)
