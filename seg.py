import argparse

parser = argparse.ArgumentParser()
parser.add_argument('images', nargs='+')
parser.add_argument('--alpha', type=float, help="adjustment parameter for the threshold", default=1.0)
parser.add_argument('--method', choices=['otsu','gmm'], default='otsu')
parser.add_argument('--border', type=int, default=0.1)
parser.add_argument('--nodisplay', action='store_true')
parser.add_argument('--outstats', default='stats.json', help='output file for statistics')
args = parser.parse_args()

import numpy as np

if not args.nodisplay:
    import matplotlib.pyplot as plt

from scipy.misc import imread
from skimage import data
from skimage.filter import threshold_otsu
from skimage.segmentation import clear_border, quickshift
from skimage.morphology import label, closing, square
from skimage.measure import regionprops, find_contours
from skimage.color import rgb2hsv

from sklearn.mixture import GMM
import json

allstats = {}

np.random.seed(1)
for index,imgfn in enumerate(args.images):
    image = imread(imgfn)
    print "{}/{} {}: {}".format( index+1, len(args.images), imgfn, image.shape )
    image_hsv = rgb2hsv(image)
    saturation = image_hsv[:,:,1]

    if not args.nodisplay:
        fig, ax = plt.subplots(3)

    if args.method=="otsu":
        t = args.alpha * threshold_otsu(saturation)
        print "Threshold: {}".format(t)

        contours = find_contours(saturation, t)
        binaryimage = saturation>t

        if not args.nodisplay:
            ax[0].matshow(saturation)
    else:
        g = GMM(3)
        bx = int(args.border*image.shape[1])-1
        by = int(args.border*image.shape[0])-1
        X = np.concatenate ( [ np.reshape( image_hsv[:, :bx, :], [-1,3]),
            np.reshape( image_hsv[:, -bx:, :], [-1,3]),
            np.reshape( image_hsv[:by, :, :], [-1,3]),
            np.reshape( image_hsv[-by:, :, :], [-1,3]) ] )
        print "GMM learning ..."
        g.fit(X)
        print g.means_
        print g.covars_
        Xt = np.array(np.reshape(image_hsv, [-1,3]), dtype=float)
        s = np.reshape(g.score(Xt), image_hsv.shape[:2])
        t = args.alpha * threshold_otsu(s)
        print "Threshold: {}".format(t)
        contours = find_contours(s, t)
        binaryimage = s>t

        if not args.nodisplay:
            ax[0].matshow(s)

    stats = {}

    v = image_hsv[ binaryimage, 2 ]

    stats['median-v'] = np.median(v)
    stats['mean-v'] = np.mean(v)
    stats['stddev-v'] = np.std(v)
    stats['absolute-size'] = len(v)
    stats['relative-size'] = len(v) / float( image_hsv.shape[0] * image_hsv.shape[1] )

    maxc = 0
    for n, contour in enumerate(contours):
        if len(contours[n])>len(contours[maxc]):
            maxc = n

    stats['contour-length'] = len(contours[maxc])

    print "Statistics in segmented region: {}".format( json.dumps(stats, indent=2) )
    allstats[imgfn] = stats

    with open(args.outstats, 'w') as f:
        json.dump({'stats': allstats, 'args': vars(args)},f,indent=2)

    if not args.nodisplay:
        ax[1].imshow(image, interpolation='nearest')
        ax[1].plot(contours[maxc][:, 1], contours[maxc][:, 0], linewidth=2)
        ax[1].axis('image')
        ax[1].set_xticks([])
        ax[1].set_yticks([])

        ax[2].imshow(binaryimage)

        plt.show()
