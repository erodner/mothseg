import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--alpha', type=float, help="adjustment parameter for the threshold", default=1.0)
parser.add_argument('--imagelist', help="list with all image filenames", required=True)
parser.add_argument('--repl', help="replace string for the source filename", required=True)
parser.add_argument('--search', help="search string for the source filename", required=True)
parser.add_argument('--method', choices=['otsu','gmm'], default='otsu')
parser.add_argument('--border', type=int, default=0.1)
parser.add_argument('--disableotsu', action='store_true', default=False)


args = parser.parse_args()

from scipy.misc import imread, imsave
from segtools import seg_butterfly

def readlist(listfn):
    """ read a simple text file into an array """
    with open(listfn, 'r') as textf:
        return textf.read().splitlines()

import os.path
import os
import numpy as np
import matplotlib.pylab as plt

imagelist = readlist(args.imagelist)
for imagefn in imagelist:
    dstfn = imagefn.replace( args.search, args.repl )
    print "{} -> {}".format(imagefn, dstfn)
    image = imread(imagefn)
    stats, contour, binaryimage = seg_butterfly(image, alpha=args.alpha, method=args.method, gmmborder=args.border, use_otsu=not args.disableotsu)
    print image.shape
    print binaryimage.shape
    image[np.logical_not(binaryimage),:] = 128

    try:
        os.mkdir(os.path.dirname(dstfn))
    except:
        pass

    plt.figure()
    plt.imshow(binaryimage)
    plt.show()
    #imsave(dstfn, image)

