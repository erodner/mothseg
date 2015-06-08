import argparse

parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--imagelist', default='imagelist.txt')
parser.add_argument('--labels', default='labels.txt')
parser.add_argument('--trid', default='tr_ID.txt')
parser.add_argument('--dstdir', default='reduced/')
parser.add_argument('--brehmselection', help='CSV file of Gunnar Brehm with the selection of images', default='/home/rodner/data/ecuador-butterflies/meta/Appendix-Tab3-neu.csv')

args = parser.parse_args()

import os

try:
    os.mkdir(args.dstdir)
except OSError:
    pass

import csv
import re

listed_ids = {}
with open(args.brehmselection, 'rb') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        idfield = row['Sample ID']
        # We only care about the fields with the syntax ID <number>
        # or ID <number>[a-z]
        m = re.match('ID (\d+[a-z]?)', idfield)
        if m:
            realid = m.groups(1)[0]
            if realid in listed_ids:
                raise Exception('Duplicate ID in CSV file: {}'.format(realid))

            listed_ids[realid] = row


print "Number of IDs in the selection: {}".format(len(listed_ids))

def readlist(listfn):
    """ read a simple text file into an array """
    with open(listfn, 'r') as textf:
        return textf.read().splitlines()

labels = readlist(args.labels)
imagelist = readlist(args.imagelist)

if len(imagelist) != len(labels):
    raise Exception("Length of input lists do not match")

print "Number of IDs in lists: {}".format(len(imagelist))

import os.path
classes_index = {}
for k, imagefn in enumerate(imagelist):
    m = re.search('([^\/\\\\]+)[\/\\\\]([^\/\\\\]+)\.[^\.]+$', imagefn)
    if not m:
        raise Exception('Image file {} does not match pattern for ID parsing'.format(imagefn))
    imagefn_class = m.groups(1)[0]
    imagefn_id = m.groups(1)[1]


    if imagefn_id in listed_ids:
        if not imagefn_class in classes_index:
            classes_index[imagefn_class] = set()
        classes_index[imagefn_class].add(k)


labels_filtered = []
trid_filtered = []
imagelist_filtered = []

no_selected_classes = 0
for myclass in classes_index:
    if len(classes_index[myclass]) >= 2:
        no_selected_classes += 1
        for index_in_classlist, k in enumerate(classes_index[myclass]):
            labels_filtered.append(labels[k])
            # "For the Ecuador dataset, all except of one image for each
            #  category has been used for training"
            if index_in_classlist < len(classes_index[myclass])-1:
                trid_filtered.append('1')
            else:
                trid_filtered.append('0')
            imagelist_filtered.append(imagelist[k])

print "Number of finally selected IDs: {}".format(len(imagelist_filtered))
print "Number of finally selected classes: {}".format(no_selected_classes)

def writenewlist(origfn, dstdir, thelist):
    """ write a new list to the destination directory """
    with open( os.path.join(dstdir, os.path.basename(origfn)), 'w') as textf:
        textf.write('\n'.join(thelist))

writenewlist( args.imagelist, args.dstdir, imagelist_filtered )
writenewlist( args.labels, args.dstdir, labels_filtered )
writenewlist( args.trid, args.dstdir, trid_filtered )
