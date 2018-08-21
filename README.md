# Segmentation of moth and butterfly images

This repository collects a few tools to segment and analyze moth images
with canonical poses. With standard and very simple segmentation
techniques, we are able to perform a large-scale quantification of a
huge dataset estimating sizes and color information. Furthermore, we can
process images with a small calibration pattern to allow for estimating absolute
measures.

Author: _Erik Rodner_ (Computer Vision Group, Friedrich Schiller
University of Jena)

## What you need to use this software

1. Python 2.7
2. numpy, scipy
3. matplotlib/pylab for visualization
4. skimage for image processing
5. Other common python packages, such as json etc.
6. Linux or MacOS; the program should also run on Windows with minor
   modifications

## Segmentation and quantification

The main tool for segmentation is ``seg.py``. If you have everything
installed and want to run a first test, simply call the program as
follows from your command line:
```bash
python seg.py test.jpg
```
which should output the following on the terminal
```
1/1 test.jpg: (1024, 683)
Threshold: 0.201171875
Calibration length bounds: 11.0 <= d <= 25.8
Statistics in segmented region: {
  "stddev-saturation": 0.12536324390038833, 
  "height-calibrated": 38.492167681756925, 
  "calibration-length": 12.5, 
  "c-xmin": 79.718389423076928, 
  "seg-absolute-size": 175535, 
  "seg-relative-size": 0.2509822817532943, 
  "c-length": 7839, 
  "mean-intensity": 0.30125312140978533, 
  "median-intensity": 0.25882352941176473, 
  "stddev-intensity": 0.16121264171588823, 
  "c-xmax": 944.6045903344849, 
  "mean-saturation": 0.3842628444646306, 
  "c-ymin": 94.471512957317074, 
  "median-saturation": 0.36170212765957449, 
  "c-area": 199125.72196888566, 
  "c-area-calibrated": 1274.4046206008682, 
  "c-ymax": 575.62360897927863, 
  "width-calibrated": 69.190896072912636
}
```
and in addition show the following on the screen:
![alt text](https://github.com/erodner/mothseg/blob/master/doc/screenshot.png "Screenshot of a demo result")

You can specify multiple images on the command line if you want to perform processing for the entire dataset.
In this case, I recommend to use:
```
python seg.py --displaymode pdf --outstats results.json test1.jpg test2.jpg ...
```
to write out the results as text to ``results.json`` (in JSON format) and as images to several pdf files.
Furthermore, the segmentation can be controlled with some parameters for adjusting it to your images, please see ``python seg.py -h`` for details.

With the second Version all .jpeg files in the working-direction getting grapped and processed.
```bash
python seg2.py
```


## Alternative calibration pattern

As a calibration pattern, we can also assume a simple black bar (showing 1cm) on the bottom right corner as follows:
```
python seg.py --calibration_pattern black_bar --calibration_pos bottom_right --calibration_relative_width 0.4 --calibration_relative_height 0.05 test2.jpg 
```

The result should be:
![alt text](https://github.com/erodner/mothseg/blob/master/doc/screenshot2.png "Screenshot of a demo result with a black bar calibration pattern")


## Attributes calculated

The following attributes are calculated for each moth. If the scale was not detected or the result of the scale was not in the specified bounds, 
all attributes marked with ```-calibrated``` are not calculated. 

* ```calibration-length```: pixels/mm (derived from the mm-scale in the image)
* ```seg-absolute-size```: area in pixel of the moth derived from the binary segmentation
* ```seg-relative-size```: relative area spanned by the moth derived from the binary segmentation
* ```mean-hue```: mean of the moth hue (H channel of the HSV colour space, derived from binary segmentation)
* ```median-hue```: median of the moth hue (H channel of the HSV colour space, derived from the binary segmentation)
* ```stddev-hue```: standard deviation of the moth hue (H channel of the HSV colour space, derived from the binary segmentation)
* ```mean-intensity```: mean of the moth intensity (V channel of the HSV colour space, derived from binary segmentation)
* ```median-intensity```: median of the moth intensity (V channel of the HSV colour space, derived from the binary segmentation)
* ```stddev-intensity```: standard deviation of the moth intensity (V channel of the HSV colour space, derived from the binary segmentation)
* ```mean-saturation```: mean of the saturation of the segmented moth (segmentation based on binary segmentation)
* ```median-saturation```: median of the saturation of the segmented moth (segmentation based on binary segmentation)
* ```stddev-saturation```: standard deviation of the saturation of the segmented moth (segmentation based on binary segmentation) 
* ```c-length```: length of the moth contour in pixel
* ```c-xmin```: x-coordinate (in pixel) of the left-most pixel of the contour
* ```c-xmax```: x-coordinate (in pixel) of the right-most pixel of the contour
* ```c-ymin```: y-coordinate (in pixel) of the top-most pixel of the contour
* ```c-ymax```: y-coordinate (in pixel) of the bottom-most pixel of the contour
* ```c-area```: area in pixel of the moth derived from the contour
* ```c-area-calibrated```: area in mm (estimated from the scale in the image) of the moth derived from the contour
* ```height-calibrated```: height of the moth in mm (calibrated using the mm-scale in the image)
* ```width-calibrated```: width of the moth in mm (calibrated using the mm-scale in the image)

## Further notes

1. The calibration can fail for which in this case the respective variables ``c-area-calibrated``, ``height-calibrated``, and ``width-calibrated`` are
not available in the results.
2. The segmentation and calibration pattern detection is simple and might need some additional thoughts for more difficult datasets.
3. If the segmentation fails, try to adjust the alpha parameter by ``--alpha 0.8`` or something similar. Good luck :)

## Disclaimer

This work has been created as part of a cooperation project at the University of Jena and a later update in 2017. The images have been provided by Gunnar Brehm.
