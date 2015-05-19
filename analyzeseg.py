import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--instats', default='stats.json', help='input file for statistics')
parser.add_argument('--meta', default='meta.csv', help='annotation file in CSV format')
parser.add_argument('--metakey', default='Elevation', help='key name used for x axis')
parser.add_argument('--metapattern', default='(\d+)', help='pattern used to parse metakey field')
parser.add_argument('--metatype', choices=['float', 'categorical'], help='type of the metakey field')
parser.add_argument('--statskey', default='median-v', help='key name used for y axis')
parser.add_argument('--nodisplay', action='store_true')
parser.add_argument('--plotmode', choices=['histelevation', 'hist', 'scatter'], default='scatter', help='type of plot')
parser.add_argument('--filter', choices=['dayactive', 'none'], help='filter option', default='none')
args = parser.parse_args()

import re
# reading CSV annotation file
import csv
import scipy.stats
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
print "# ExampleID, MetaValue, StatsValue"
for imgfn in stats['stats']:
    m = re.search('(\d+)-?[ab]?\....$', imgfn)
    if not m:
        continue
    eid = int(m.groups(1)[0])
    if not eid in examples:
        continue

    if args.filter=="dayactive":
        if examples[eid]['Fang'] != 'day':
            continue

    if not args.metakey in examples[eid]:
        continue
    m = re.search(args.metapattern, examples[eid][args.metakey])
    if not m:
        continue

    if args.metatype=='float':
        metavalue = float(m.groups(1)[0])
    else:
        metavalue = m.groups(1)[0]
    statsvalue = float(stats['stats'][imgfn][args.statskey])

    print eid, metavalue, statsvalue
    x.append(metavalue)
    y.append(statsvalue)


if args.metatype=='float':
    print "Pearson correlation coefficient: ", scipy.stats.pearsonr(x,y)
    print "Spearman rank-order coefficient: ", scipy.stats.spearmanr(x,y)

if not args.nodisplay:
    import matplotlib.pylab as plt

    # histogram plot
    plt.figure()

    if args.plotmode=="histelevation":
        xq = [ round((v-1000)/500.0) for v in x ]
        d = {}
        for index,vq in enumerate(xq):
            if not vq in d:
                d[vq] = []
            d[vq].append(y[index])
        print d.keys()
        plt.boxplot(d)
        plt.xticks(range(1,6), ['750-1250m', '1250-1750m', '1750-2250m', '2250-2750m', '2750-3250m'])

        plt.title('elevation vs. visual intensity')
    elif args.plotmode=="hist":
        classes = dict(day=0, q=1, q2=1, cat=1, qual=1, nad=1, raus=1)
        xq = [ classes[v] for v in x ]
        d = {}
        for index,vq in enumerate(xq):
            if not vq in d:
                d[vq] = []
            d[vq].append(y[index])
        plt.boxplot(d)
        plt.xticks(range(1,3), ['day active', 'not day active'])

        plt.title('activity type vs. visual intensity')
    else:
        plt.scatter(x, y)


    #plt.ylabel('median intensity (from darker to brighter)')
    plt.ylabel(args.statskey)
    plt.xlabel(args.metakey)
    plt.show()

    plt.show()
