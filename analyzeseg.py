import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--instats', default='stats.json', help='input file for statistics')
parser.add_argument('--meta', default='meta.csv', help='annotation file in CSV format')
parser.add_argument('--metakey', default='Elevation', help='key name used for x axis')
parser.add_argument('--metapattern', default='(\d+)', help='pattern used to parse metakey field')
parser.add_argument('--statskey', default='median-v', help='key name used for y axis')
parser.add_argument('--nodisplay', action='store_true')
args = parser.parse_args()

import re
# reading CSV annotation file
import csv
examples_list = []
with open(args.meta, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',',quotechar='"')
    for row in reader:
        examples_list.append(row)

print "Number of examples: {}".format(len(examples_list))

import json
with open(args.instats, 'r') as jsonfile:
    stats = json.load(jsonfile)

examples = {}
for e in examples_list:
    if not 'ID' in e:
        continue
    eid = int(e['ID'])
    examples[eid] = e 


x = []
y = []
for imgfn in stats['stats']:
    m = re.search('(\d+)-?[ab]?\....$', imgfn)
    if not m:
        continue
    eid = int(m.groups(1)[0])
    if not eid in examples:
        continue
    if not args.metakey in examples[eid]:
        continue
    m = re.search(args.metapattern, examples[eid][args.metakey])
    if not m:
        continue
    metavalue = float(m.groups(1)[0])
    statsvalue = float(stats['stats'][imgfn][args.statskey])

    print eid, metavalue, statsvalue
    x.append(metavalue)
    y.append(statsvalue)


if not args.nodisplay:
    import matplotlib.pylab as plt
    plt.figure()

    xq = [ round((v-1000)/500.0) for v in x ]
    d = {}
    for index,vq in enumerate(xq):
        if not vq in d:
            d[vq] = []
        d[vq].append(y[index])
    print d.keys()
    plt.boxplot(d)
    plt.xticks(range(1,6), ['750-1250m', '1250-1750m', '1750-2250m', '2250-2750m', '2750-3250m'])


    plt.scatter(x, y)
    plt.xlabel(args.metakey)
    #plt.ylabel(args.statskey)
    plt.ylabel('median intensity (from darker to brighter)')
    plt.title('elevation vs. visual intensity of the butterfly')
    plt.show()
