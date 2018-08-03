from image_registration import *

def main():
  
    fileIR = "../../../data/image_registration_sandbox/CHESS_FL1_C_160407_234502.428_THERM-16BIT.PNG"
    fileRGB = "../../../data/image_registration_sandbox/___CHESS_FL1_C_160407_234502.428_COLOR-8-BIT.JPG"
    fileAligned = "../../../data/image_registration_sandbox/CHESS_FL1_C_160407_234502.428_THERM-16BIT_aligned.JPG"
    fileRGBAAligned = "../../../data/image_registration_sandbox/___CHESS_FL1_C_160407_234502.428_COLOR-8-BIT_rgba_aligned.png"

    # Read the images to be aligned
    img = imreadIR(fileIR)
    imgRef =  cv2.imread(fileRGB)

    # omcpute transform
    ret, transform = computeTransform(imgRef, img)

    if (not ret):
        print("failed!!!")
        return

    # warp IR image
    imgWarped = cv2.warpPerspective(img, transform, (imgRef.shape[1], imgRef.shape[0]))

    # sample hotspot
    pt = [520, 288]

    # warp hotspot
    ptWarped = warpPoint(pt, transform)

    # write warped IR image
    cv2.imwrite(fileAligned, imgWarped)

    # must write as .png to save with alpha channel, warning this will be a big file
    b_channel, g_channel, r_channel = cv2.split(imgRef)
    imgBGRA = cv2.merge((b_channel, g_channel, r_channel, imgWarped))

    cv2.imwrite(fileRGBAAligned, imgBGRA)

    # display everything
    plt.figure()
    plt.imshow(img, cmap='gray')
    plt.plot(pt[0],pt[1],color='red', marker='o')
    plt.title("Orig IR")

    plt.figure()
    plt.imshow(imgWarped, cmap='gray')
    plt.plot(ptWarped[0],ptWarped[1],color='red', marker='o')
    plt.title("Aligned IR")

    plt.figure()
    plt.imshow(cv2.cvtColor(imgRef, cv2.COLOR_BGR2RGB))
    plt.plot(ptWarped[0],ptWarped[1],color='red', marker='o')
    plt.title("Orig RGB")

    plt.show()

if __name__ == '__main__':
    main()

