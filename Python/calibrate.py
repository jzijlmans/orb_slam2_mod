#http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
import numpy as np
import cv2
import glob
import sys

blocksize = 27.4 #mm
pxmm = 1.12*0.001#px size in mm
if len(sys.argv) == 2: #if the user has provided enough arguments
    #extract the arguments
    imagefolder = sys.argv[1]
else:
    print "Please use as following: claibrate.py imagefolder [lsd_cal_output_folder/name]"
    sys.exit
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

print "preparing opject points"
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*8,3), np.float32)
objp[:,:2] = np.mgrid[0:8,0:6].T.reshape(-1,2)
objp = objp * blocksize #resize to m

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

print "retrieving images"
imgnames = imagefolder + '/*.jpg'
images = glob.glob(imgnames)
print str(len(images))+" images retrieved as: "+ imgnames

if len(images)<1:
    print "There are no images in this directory:" + imgnames
    sys.exit

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
    ret, corners = cv2.findChessboardCorners(gray, (8,6),None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        print"Corners are found"
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (8,6), corners2,ret)
        cv2.imshow('img',img)
        cv2.waitKey(500)

print "done processing the images"
cv2.destroyAllWindows()
print "starting calibrations"
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print "finished calibrations"
print "The camera matrix in px is: "
print mtx
# print "The camera matrix in mm is: "
# mtxmm = mtx * pxmm
# print mtxmm
print "The disortion coefficients are: "
print dist
# print "The rotation vector is: "
# print rvecs
# print "The translation vector is: "
# print tvecs
