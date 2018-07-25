import cv2
import numpy as np

MAX_FEATURES = 500
GOOD_MATCH_PERCENT = 0.15
RATIO_TEST = .85
def alignImages(im2Gray, im1):
 
  # Convert images to grayscale
  im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
  #im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
   
  # Detect ORB features and compute descriptors.
  sift = cv2.xfeatures2d.SIFT_create()
  keypoints1, descriptors1 = sift.detectAndCompute(im1Gray, None)
  keypoints2, descriptors2 = sift.detectAndCompute(im2Gray, None)
  
  # Match features.
  matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
  matches = matcher.match(descriptors1, descriptors2, None)
   
  # Sort matches by score
  matches.sort(key=lambda x: x.distance, reverse=False)

  #  # Apply ratio test
  #numGoodMatches = []
  #for match in enumerate(matches):
  #    if m.distance < 0.75*n.distance:
  #        numGoodMatches.append([m])

  # Remove not so good matches
  numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
  matches = matches[:numGoodMatches]
 
  # Draw top matches
  imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
  cv2.imwrite("matches.jpg", imMatches)
   
  # Extract location of good matches
  points1 = np.zeros((len(matches), 2), dtype=np.float32)
  points2 = np.zeros((len(matches), 2), dtype=np.float32)
 
  for i, match in enumerate(matches):
    points1[i, :] = keypoints1[match.queryIdx].pt
    points2[i, :] = keypoints2[match.trainIdx].pt
   
  # Find homography
  h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
 
  # Use homography
  height, width, channels = im2.shape
  im1Reg = cv2.warpPerspective(im1, h, (width, height))
   
  return im1Reg, h

# Read the images to be aligned

im1_16bit =  cv2.imread("../../data/image_registration_sandbox/CHESS_FL1_C_160407_234502.428_THERM-16BIT.PNG", cv2.IMREAD_ANYDEPTH)
im2 =  cv2.imread("../../data/image_registration_sandbox/CHESS_FL1_C_160407_234502.428_COLOR-8-BIT.JPG")

im1 = np.floor((im1_16bit - np.min(im1_16bit))/(np.max(im1_16bit) - np.min(im1_16bit))*256)
im1 = im1.astype(np.uint8)

#cv2.imshow('im1', im1)
#cv2.imshow('im2', im2)
#cv2.waitKey(0);                                          

im2_aligned, h = alignImages(im1, im2)

#cv2.imwrite('"../../data/image_registration_sandbox/CHESS_FL1_C_160407_234502.428_COLOR-8-BIT_aligned.JPG')

# Show final results
cv2.imshow("Image 1", im1)
cv2.imshow("Image 2", im2)
cv2.imshow("Aligned Image 2", im2_aligned)
cv2.waitKey(0)