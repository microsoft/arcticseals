import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import numpy as np

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15
RATIO_TEST = .85
MATCH_HEIGHT = 512
MIN_MATCHES = 4
MIN_INLIERS = 4

def computeTransform(imgRef, img, warp_mode = cv2.MOTION_HOMOGRAPHY, matchLowRes=True):
 
    # Convert images to grayscale    
    if (len(img.shape) == 3 and img.shape[2] == 3):
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        imgGray = img
 
    if (len(imgRef.shape) == 3 and imgRef.shape[2] == 3): 
        imgRefGray = cv2.cvtColor(imgRef, cv2.COLOR_BGR2GRAY)
    else:
        imgRefGray = imgRef

    # resize if requested
    if (matchLowRes):
        aspect = imgRefGray.shape[1]/imgRefGray.shape[0]
        imgRefGray = cv2.resize(imgRefGray, (int(MATCH_HEIGHT*aspect), MATCH_HEIGHT))
    
    # Detect SIFT features and compute descriptors.
    sift = cv2.xfeatures2d.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(imgGray, None)
    keypoints2, descriptors2 = sift.detectAndCompute(imgRefGray, None)

    if (len(keypoints1) == 0):
        print("not enough keypoints")
        return False, np.identity(3)

    if (len(keypoints2) == 0):
        print("not enough keypoints")
        return False, np.identity(3)

    # scale feature points back to original size
    if (matchLowRes):
        scale = imgRef.shape[0]/imgRefGray.shape[0]
        for i in range(0, len(keypoints2)):
            keypoints2[i].pt = (keypoints2[i].pt[0]*scale, keypoints2[i].pt[1]*scale)
            
    # Pick good features
    if (RATIO_TEST < 1):
        # ratio test
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
   
        # Apply ratio test
        goodMatches = []
        for m, n in matches:
            if m.distance < RATIO_TEST*n.distance:
                goodMatches.append(m)

        matches = goodMatches
    else:
        # top percentage matches
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = matcher.match(descriptors1, descriptors2)
   
        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]
   
    print("%d matches" % len(matches))

    if (len(matches) < MIN_MATCHES):
        print("not enough matches")
        return False, np.identity(3)

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)
 
    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
 
    print("%d inliers" % sum(mask))

    if (sum(mask) < MIN_INLIERS):
        print("not enough inliers")
        return False, np.identity(3)

    # if non homography requested, compute from inliers
    if warp_mode != cv2.MOTION_HOMOGRAPHY:
        points1Inliers = []
        points2Inliers = []

        for i in range(0, len(mask)):
            if (int(mask[i]) == 1):
                points1Inliers.append(points1[i,:])
                points2Inliers.append(points2[i,:])
             
        a = cv2.estimateRigidTransform(np.asarray(points1Inliers), np.asarray(points2Inliers), (warp_mode == cv2.MOTION_AFFINE))
        h = np.identity(3)

        # turn in 3x3 transform
        h[0,:] = a[0,:]
        h[1,:] = a[1,:]

    return True, h

# projective transform of a point
def warpPoint(pt, h):
    pt = [pt[0], pt[1], 1]
    ptT = np.dot(h,pt)
    ptT = [ptT[0]/ptT[2], ptT[1]/ptT[2]]
    return ptT

# read and normlize IR image
def imreadIR(fileIR, percent=0.01):
    img =  cv2.imread(fileIR, cv2.IMREAD_ANYDEPTH)

    if (not img is None):
        imgNorm = np.floor((img - np.percentile(img, percent))/(np.percentile(img, 100-percent) - np.percentile(img, percent))*256)

    return imgNorm.astype(np.uint8), img

def registerThermalAndColorImages(file, fileOut, folder, displayResults=False):
    
    hotspots = []

    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # header row
        headers = next(reader, None)

        for row in reader:
            hotspots.append(row)

    for i in range(0, len(hotspots)):

        hotspot = hotspots[i]

        fileIR = folder + hotspot[2]
        fileRGB = folder + hotspot[4]
        x = float(hotspot[5])
        y = float(hotspot[6])

        print('%d:\t%s\n\t%s' %(i, fileIR, fileRGB))

        thumb = [-1, -1, -1, -1]

        # Read the images to be aligned
        img, img16bit = imreadIR(fileIR)

        if (img is None):
            print('\nnot found\n')
            hotspots[i][7:11] = thumb
            continue

        imgRef =  cv2.imread(fileRGB)

        if (imgRef is None):
            print('\nnot found\n')
            hotspots[i][7:11] = thumb
            continue

        # omcpute transform
        ret, transform = computeTransform(imgRef, img)
    
        if (ret):
            pt = [x, y]
            ptWarped = np.round(warpPoint(pt, transform))

            thumb = [int(ptWarped[0]-256), int(ptWarped[1]-256), int(ptWarped[0]+256), int(ptWarped[1]+256)]

            if (displayResults):
                # warp IR image
                imgWarped = cv2.warpPerspective(img, transform, (imgRef.shape[1], imgRef.shape[0]))
                #img16bitWarped = cv2.warpPerspective(img16bit, transform, (imgRef.shape[1], imgRef.shape[0]))

                # display everything
                plt.figure()
                plt.subplot(2, 2, 1)
                plt.imshow(img, cmap='gray')
                plt.plot(pt[0],pt[1],color='red', marker='o')
                plt.title("Orig IR")

                plt.subplot(2, 2, 2)
                plt.imshow(imgWarped, cmap='gray')
                plt.plot(ptWarped[0],ptWarped[1],color='red', marker='o')
                plt.title("Aligned IR")

                plt.subplot(2, 2, 3)
                plt.imshow(cv2.cvtColor(imgRef, cv2.COLOR_BGR2RGB))
                plt.plot(ptWarped[0],ptWarped[1],color='red', marker='o')
                plt.title("Orig RGB")

                plt.subplot(2, 2, 4)  
                thumb = imgRef[thumb[1]:thumb[3], thumb[0]:thumb[2],:]
                plt.imshow(cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB))
                plt.title("Thumb RGB")

                plt.show()
        else:

            if (displayResults):
                plt.figure()
                plt.subplot(1, 2, 1)
                plt.imshow(img, cmap='gray')
                plt.title("Orig IR")

                plt.subplot(1, 2, 2)
                plt.imshow(cv2.cvtColor(imgRef, cv2.COLOR_BGR2RGB))
                plt.title("Orig RGB")

                plt.show()

            print('alignment failed!')

        hotspots[i][7:11] = thumb

    with open(fileOut, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow(headers)
        for i in range(0, len(hotspots)): 
            
            writer.writerow(hotspots[i])
