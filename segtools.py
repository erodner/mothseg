""" Simple algorithms for segmenting butterflies """
import numpy as np
from skimage.filters import threshold_otsu
from skimage.measure import find_contours
from skimage.color import rgb2hsv

mixture_disabled = True
try:
    from sklearn.mixture import GMM
except ImportError:
    mixture_disabled = False

def seg_butterfly(image, method = "otsu", alpha = 1.0, gmmborder = 0.1):
    """ segment a given image and return statistics of the largest object """
    image_hsv = rgb2hsv(image)
    saturation = image_hsv[:, :, 1]

    if method == "otsu":
        t = alpha * threshold_otsu(saturation)
        print "Threshold: {}".format(t)

        contours = find_contours(saturation, t)
        binaryimage = saturation>t

    elif not mixture_disabled:
        g = GMM(3)
        bx = int(gmmborder*image.shape[1])-1
        by = int(gmmborder*image.shape[0])-1
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

    # compute bounding box
    stats['xmin'] = np.amin( contours[maxc][:,1] )
    stats['xmax'] = np.amax( contours[maxc][:,1] )
    stats['ymin'] = np.amin( contours[maxc][:,0] )
    stats['ymax'] = np.amax( contours[maxc][:,0] )

    return stats, contours[maxc], binaryimage
