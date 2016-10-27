""" Simple algorithms for segmenting butterflies """
import numpy as np
from skimage.filters import threshold_otsu
from skimage.measure import find_contours
from skimage.color import rgb2hsv

mixture_disabled = False
try:
    from sklearn.mixture import GMM
except ImportError:
    mixture_disabled = True

# Use Green's theorem to compute the area
# enclosed by the given contour.
def contour_area(vs):
    a = 0
    x0,y0 = vs[0]
    for [x1,y1] in vs[1:]:
        dx = x1-x0
        dy = y1-y0
        a += 0.5*(y0*dx - x0*dy)
        x0 = x1
        y0 = y1
    return a

def seg_butterfly(image, method = "otsu", alpha = 1.0, gmmborder = 0.1, use_otsu = True):
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
        if use_otsu:
            t = alpha * threshold_otsu(s)
        else:
            t = alpha

        print "Threshold: {}".format(t)
        contours = find_contours(s, t)
        binaryimage = s>t
    else:
        raise Exception("Method not supported!")

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

    stats['c-length'] = len(contours[maxc])
    stats['c-area'] = contour_area(contours[maxc])

    # compute bounding box
    stats['c-xmin'] = np.amin( contours[maxc][:,1] )
    stats['c-xmax'] = np.amax( contours[maxc][:,1] )
    stats['c-ymin'] = np.amin( contours[maxc][:,0] )
    stats['c-ymax'] = np.amax( contours[maxc][:,0] )

    return stats, contours[maxc], binaryimage
