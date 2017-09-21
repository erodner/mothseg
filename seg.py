import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('images', nargs='+', help='input images')
parser.add_argument('--alpha', type=float, help="adjustment parameter for the automatic global threshold", default=1.0)
parser.add_argument('--method', choices=['otsu','gmm'], help='segmentation method (global otsu threshold or GMM estimation)', default='otsu')
parser.add_argument('--border', type=int, default=0.1, help='relative border definition (used by GMM)')
parser.add_argument('--displaymode', choices=['disabled', 'pdf', 'png', 'screen'], help='whether to show the segmentation result (screen), to write it to a file (pdf, png), or to skip it (disabled)',
    default='screen')
parser.add_argument('--nocalibration', action='store_true', help='disable calibration')
parser.add_argument('--outstats', default='stats.json', help='output file for statistics')
parser.add_argument('--calibration_pattern', default='checkerboard', help='which calibration pattern should be assumed (checkerboard or black_bar)',
        choices=["checkerboard", "black_bar"])
parser.add_argument('--calibration_pos', default='bottom_left', help='where is the calibration pattern located (bottom_left, bottom_right, top_left, top_right)',
        choices=["bottom_left", "bottom_right", "top_left", "top_right"])
parser.add_argument("--calibration_relative_height", type=float, default=0.3)
parser.add_argument("--calibration_relative_width", type=float, default=0.1)

args = parser.parse_args()

from segtools import *
import numpy as np
from scipy.misc import imread

if args.displaymode!='disabled':
    import matplotlib.pyplot as plt


import json
from os.path import basename, splitext

allstats = {}

np.random.seed(1)
for index,imgfn in enumerate(args.images):
    image = imread(imgfn)
    print "{}/{} {}: {}".format( index+1, len(args.images), imgfn, (image.shape[1], image.shape[0]) )
    stats, contour, binaryimage = seg_butterfly(image, method=args.method, alpha=args.alpha, gmmborder=args.border)

    if not args.nocalibration:
        cal_length = estimate_calibration_length(image, calibration_pattern=args.calibration_pattern, 
                crop_x=args.calibration_relative_width, crop_y=args.calibration_relative_height, pos=args.calibration_pos)
        if cal_length>0:
            stats['c-area-calibrated'] = stats['c-area']/cal_length**2
            stats['width-calibrated'] = (stats['c-xmax']-stats['c-xmin'])/cal_length
            stats['height-calibrated'] = (stats['c-ymax']-stats['c-ymin'])/cal_length
            stats['calibration-length'] = cal_length

    print "Statistics in segmented region: {}".format( json.dumps(stats, indent=2) )
    imgfn_base = basename(imgfn)
    allstats[imgfn_base] = stats

    with open(args.outstats, 'w') as f:
        json.dump({'stats': allstats, 'args': vars(args)},f,indent=2)

    if args.displaymode!='disabled':
        plt.figure()
        plt.subplot(1,2,1)
        plt.imshow(image, interpolation='nearest')
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)
        rx = [ stats['c-xmin'], stats['c-xmax'], stats['c-xmax'], stats['c-xmin'], stats['c-xmin'] ]
        ry = [ stats['c-ymin'], stats['c-ymin'], stats['c-ymax'], stats['c-ymax'], stats['c-ymin'] ]
        plt.plot(rx, ry, 'm--', linewidth=0.5)

        plt.gca().arrow( stats['c-xmin'], stats['c-ymax'], stats['c-xmax']-stats['c-xmin'], 0, length_includes_head=True, width=3 )
        plt.gca().arrow( stats['c-xmax'], stats['c-ymax'], -stats['c-xmax']+stats['c-xmin'], 0, length_includes_head=True, width=3 )

        if not 'calibration-length' in stats:
            lengthx = '{:.0f} pixels'.format(stats['c-xmax']-stats['c-xmin'])
        else:
            lengthx = '{:.2f} mm'.format(stats['width-calibrated'])

        plt.text( 0.5 * (stats['c-xmax'] + stats['c-xmin']), stats['c-ymax'] + 20, 
                  lengthx, 
                  horizontalalignment='center', verticalalignment='top', fontsize=18)
        plt.axis('image')
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.title('Segmented outline and box')

        plt.subplot(1,2,2)
        plt.imshow(binaryimage)
        plt.title('Binary segmentation of the image')
        
        if args.displaymode=='screen':
            plt.show()
        else:
            imgfn_base_without_ext, ext = splitext(imgfn_base)
            outfn = imgfn_base_without_ext + '.' + args.displaymode
            print ("Writing figure to {}".format(outfn))
            plt.savefig(outfn)
