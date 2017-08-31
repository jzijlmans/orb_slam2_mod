#http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
import numpy as np
import cv2
import glob
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('imagefolder')
parser.add_argument('outputfolder')
parser.add_argument('blocksize', help='blocksize of checkerboard blocks in mm',type=float)
parser.add_argument('-o','--outputfiles', dest='outputfiles',choices=['orbslam2','lsdslam','both'])
parser.add_argument('-b','--blockswidth', dest='blockswidth',type=int, default=8,help='amount of blocks on the checkerboard in one direction (default is 8)')
parser.add_argument('-c','--blocksheight', dest='blocksheight', type=int, default=6, help='amount of blocks on the checkerboard in the other direction (default is 6)')
parser.add_argument('-f','--fps',dest='fps', type=int, default=30, help='The fps nessesary for the creating the calibfiles (default=30)')
parser.add_argument('-w','--imagewidth', dest='imagewidth', type = int, default=640, help='The width of the images for creating the calibfiles (default = 640)')
parser.add_argument('-e','--imageheight', dest='imageheight', type = int, default=480, help='The height of the images for creating the calibfiles (default = 480)')
args = parser.parse_args()
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

print "preparing opject points"
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((args.blocksheight*args.blockswidth,3), np.float32)
objp[:,:2] = np.mgrid[0:args.blockswidth,0:args.blocksheight].T.reshape(-1,2)
objp = objp * args.blocksize #resize to m

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

print "retrieving images"
imgnames = args.imagefolder + '/*.jpg'
images = glob.glob(imgnames)

if len(images)<1:
    imgnames = args.imagefolder + '/*.png'
    print "no .jpg found trying: " + imgnames
    images = glob.glob(imgnames)
    if len(images)<1:
        sys.exit

print str(len(images))+" images retrieved as: "+ imgnames

# Create a Window
cv2.startWindowThread()
cv2.namedWindow('img',cv2.WINDOW_NORMAL)
cv2.resizeWindow('img', 800, 600)
i = 0
for fname in images:
    i += 1
    print "starting processing image nummer: "+ str(i)
    #read image and convert to grayscale image
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (args.blockswidth,args.blocksheight),None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        print"Corners are found"
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (args.blockswidth,args.blocksheight), corners2,ret)
        cv2.imshow('img',img)
        cv2.waitKey(500)
    else:
        cv2.imshow('img',img)
        cv2.waitKey(500)
        print "no corners are found"

print "done processing the images"
cv2.destroyAllWindows()
print "starting calibrations"
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print "finished calibrations"
print "The camera matrix in px is: "
print mtx
print "The disortion coefficients are: "
print dist

if args.outputfiles == 'orbslam2' or args.outputfiles == 'both':
    orbfilename = args.outputfolder + '/orb_slam2calib.yaml'
    orbfile = open(orbfilename,'w')
    orbfile.write('%YAML:1.0\n')
    orbfile.write('Camera.fx: ' + str(mtx.item(0)) + '\n')
    orbfile.write('Camera.fy: ' + str(mtx.item(4)) + '\n')
    orbfile.write('Camera.cx: ' + str(mtx.item(2)) + '\n')
    orbfile.write('Camera.cy: ' + str(mtx.item(5)) + '\n')
    orbfile.write('Camera.k1: ' + str(dist.item(0)) + '\n')
    orbfile.write('Camera.k2: ' + str(dist.item(1)) + '\n')
    orbfile.write('Camera.p1: ' + str(dist.item(2)) + '\n')
    orbfile.write('Camera.p2: ' + str(dist.item(3)) + '\n')
    orbfile.write('Camera.k3: ' + str(dist.item(4)) + '\n')
    orbfile.write('Camera.fps: ' + str(args.fps) +'\n')
    orbfile.write('Camera.RGB: 1 \nORBextractor.nFeatures: 1000 \nORBextractor.scaleFactor: 1.2\nORBextractor.nLevels: 8\nORBextractor.iniThFAST: 20 \nORBextractor.minThFAST: 7 \nViewer.KeyFrameSize: 0.05 \nViewer.KeyFrameLineWidth: 1 \nViewer.GraphLineWidth: 0.9 \nViewer.PointSize:2 \nViewer.CameraSize: 0.08 \nViewer.CameraLineWidth: 3 \nViewer.ViewpointX: 0 \nViewer.ViewpointY: -0.7 \nViewer.ViewpointZ: -1.8 \nViewer.ViewpointF: 500')
    print "orb_slam2 calibration file saved"
if args.outputfiles == 'lsdslam' or args.outputfiles =='both':
    lsdfilename = args.outputfolder + '/lsd_slamcalib.txt'
    lsdfile = open(lsdfilename,'w')
    lsdfile.write(str(mtx.item(0)) + " " + str(mtx.item(4)) + " " + str(mtx.item(2)) + " " + str(mtx.item(5)) + " ")
    lsdfile.write(str(dist.item(0)) + " " +str(dist.item(1)) + " " + str(dist.item(2)) + " " + str(dist.item(3)) + " " + str(dist.item(4)) + " ")
    lsdfile.write("\n" + str(args.imagewidth) + " " + str(args.imageheight) + "\ncrop\n640 480")
    print "lsd_slam calibration file saved"
