""" Simple algorithms for segmenting butterflies """
import numpy as np
from skimage.filters import threshold_otsu
from skimage.measure import find_contours
from skimage.color import rgb2hsv, rgb2gray
import skimage
from skimage import feature
from scipy.spatial.distance import pdist, squareform

mixture_disabled = False
try:
    from sklearn.mixture import GMM
except ImportError:
    mixture_disabled = True

grabcut_disabled = False
try:
    from cv2 import grabCut
    import cv2
except ImportError:
    grabcut_disabled = True

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
    saturation = image_hsv[ :, :, 1 ]

   
    if method == "otsu":
        t = alpha * threshold_otsu(saturation)
        print "Threshold: {}".format(t)

        contours = find_contours(saturation, t)
        binaryimage = saturation>t

    elif not mixture_disabled and method=="gmm":
        g = GMM(3)
        bx = int(gmmborder*image.shape[1])-1
        by = int(gmmborder*image.shape[0])-1
        X = np.concatenate ( [ np.reshape( image_hsv[:, :bx, :], [-1,3]),
            np.reshape( image_hsv[:, -bx:, :], [-1,3]),
            np.reshape( image_hsv[:by, :, :], [-1,3]),
            np.reshape( image_hsv[-by:, :, :], [-1,3]) ] )
        print "GMM learning ..."
        g.fit(X)
        Xt = np.array(np.reshape(image_hsv, [-1,3]), dtype=float)
        s = np.reshape(g.score(Xt), image_hsv.shape[:2])
        if use_otsu:
            t = alpha * threshold_otsu(s)
        else:
            t = alpha

        print "Threshold: {}".format(t)
        contours = find_contours(s, t)
        binaryimage = s>t
    elif not grabcut_disabled and method=="grabcut":
        grabcut_mask = np.zeros(image.shape[:2],np.uint8)
        grabcut_rect = (int(image.shape[1]*0.05), int(image.shape[0]*0.1), 
                        int(image.shape[1]*0.9), int(image.shape[0]*0.8))
        bgd_model = np.zeros((1,65),np.float64)
        fgd_model = np.zeros((1,65),np.float64)
        grabCut(image.astype(np.uint8), grabcut_mask, grabcut_rect, 
                bgd_model, fgd_model,
                10, cv2.GC_INIT_WITH_RECT )
        grabcut_mask[grabcut_mask==2] = 0
        grabcut_mask[grabcut_mask==3] = 1
        binaryimage = grabcut_mask
        contours = find_contours(binaryimage, 0.5)
    else:
        raise Exception("Method {} not supported!".format(method))
   
    # The intensity channel
    value_channel = image_hsv[ binaryimage, 2 ]
    # The saturation channel
    saturation = image_hsv[ binaryimage, 1 ]
    # The hue channel
    hue = image_hsv[ binaryimage, 0 ]


    stats = {}

    stats['median-intensity'] = np.median(value_channel)
    stats['mean-intensity'] = np.mean(value_channel)
    stats['stddev-intensity'] = np.std(value_channel)
    stats['median-saturation'] = np.median(saturation)
    stats['mean-saturation'] = np.mean(saturation)
    stats['stddev-saturation'] = np.std(saturation)
    stats['median-hue'] = np.median(hue)
    stats['mean-hue'] = np.mean(hue)
    stats['stddev-hue'] = np.std(hue)
    stats['seg-absolute-size'] = len(value_channel)
    stats['seg-relative-size'] = len(value_channel) / float( image_hsv.shape[0] * image_hsv.shape[1] )

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

# See the ipython notebook for details on the following code
def estimate_corners(imgr):
    response = feature.corner_shi_tomasi(imgr)
    corners = feature.corner_peaks(response, min_distance=5)
    return corners

def optimize_quant_error(A, verbose=False):
    smallest_quant_error = float("inf")
    max_d = np.percentile(A, 20)
    min_d = np.percentile(A, 1)
    print ("Calibration length bounds: {} <= d <= {}".format(min_d, max_d))
    for d in np.arange(min_d,max_d,0.25):
        grid = np.arange(0,np.max(A)+d,d)
        if len(grid)<=2: continue

        # compute quantization error
        bins = (grid[:-1]+grid[1:])/2.0
        prototypes = grid[1:-1]
        bin_assignment = np.digitize(A, bins) - 1
        bin_assignment[bin_assignment==-1] = 0
        bin_assignment[bin_assignment==len(prototypes)] = len(prototypes)-1
    
        # quantization error with BIC model selection
        # adhoc version
        n = len(A)
        quant_error = np.linalg.norm(A - prototypes[bin_assignment]) + len(prototypes)*np.log(n)
        # theoretically derived criterion
        #quant_error = n*np.log(2*np.pi) + np.linalg.norm(A - prototypes[bin_assignment])**2 + len(prototypes)*np.log(n)
       
        if verbose:
            print ("{}: {} {}".format(d, quant_error, unused_bins))
        if quant_error < smallest_quant_error:
            smallest_quant_error = quant_error
            best_distance = d

    return best_distance


def estimate_calibration_length(img, calibration_pattern="checkerboard", crop_x=0.1, crop_y=0.3, pos="bottom_left"):
    w = int(crop_x * img.shape[1])
    h = int(crop_y * img.shape[0])
    if pos=="bottom_left":
        img_crop = img[-h:,:w,:]
    elif pos=="bottom_right": 
        img_crop = img[-h:,-w:,:]
    elif pos=="top_left": 
        img_crop = img[:h,:w,:]
    elif pos=="top_right": 
        img_crop = img[:h,-w:,:]
    else:
        raise Exception("Unknown location type: {}".format(pos))

    imgr = skimage.color.rgb2gray(img_crop)
    
    if calibration_pattern=="checkerboard":
        corners = estimate_corners(imgr)
        if len(corners)==0:
            return -1
        A = pdist(corners, metric='cityblock')
        return optimize_quant_error(A)
    elif calibration_pattern=="black_bar":
        proj = np.sum(imgr, axis=0)
        grad_proj = proj[1:] - proj[:-1]
        calibration_length = np.abs(np.argmin(grad_proj) - np.argmax(grad_proj))
        return calibration_length/10.0
    else:
        raise Exception("Unknown calibration pattern type: {}".format(calibration_pattern))

