import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('images', nargs='+')
parser.add_argument('--alpha', type=float, help="adjustment parameter for the threshold", default=1.0)
parser.add_argument('--method', choices=['otsu','gmm'], default='otsu')
parser.add_argument('--border', type=int, default=0.1)
parser.add_argument('--nodisplay', action='store_true')
parser.add_argument('--outstats', default='stats.json', help='output file for statistics')
args = parser.parse_args()

from segtools import seg_butterfly
import numpy as np
from scipy.misc import imread

if not args.nodisplay:
    import matplotlib.pyplot as plt


import json
from os.path import basename

allstats = {}

np.random.seed(1)
for index,imgfn in enumerate(args.images):
    image = imread(imgfn)
    print "{}/{} {}: {}".format( index+1, len(args.images), imgfn, image.shape )
    stats, contour, binaryimage = seg_butterfly(image, method=args.method, alpha=args.alpha, gmmborder=args.border)

    if not args.nodisplay:
        fig, ax = plt.subplots(2)

    print "Statistics in segmented region: {}".format( json.dumps(stats, indent=2) )
    allstats[basename(imgfn)] = stats

    with open(args.outstats, 'w') as f:
        json.dump({'stats': allstats, 'args': vars(args)},f,indent=2)

    if not args.nodisplay:
        ax[0].imshow(image, interpolation='nearest')
        ax[0].plot(contour[:, 1], contour[:, 0], linewidth=2)
        ax[0].axis('image')
        ax[0].set_xticks([])
        ax[0].set_yticks([])

        ax[1].imshow(binaryimage)

        plt.show()
