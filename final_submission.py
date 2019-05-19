import os
import cv2
import numpy as np
from model import get_model,get_model2
from skimage.measure import label
from skimage.measure import regionprops
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.morphology import closing, square
from skimage.color import label2rgb

IMG_ROWS = 128
IMG_COLS = 128
SMOOTH = 1.0
CLEAN_THRESH = 20
THRESH = 100

model = get_model(train=False)
model.load_weights("Model_Weights.hdf5")

model2 = get_model2()
model2.load_weights("WEIGHTS.hdf5")


def classify(img_path):
    img_ = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img_path)

    img = img_
    img[img <= CLEAN_THRESH] = 255
    mask_img = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

    ret, thresh_img = cv2.threshold(img, THRESH, 255, cv2.THRESH_BINARY_INV)
    img_label = label(thresh_img)

    for region in regionprops(img_label):
        minr, minc, maxr, maxc = region.bbox
        if region.area < 500:
            continue
        r, c = (minr + maxr - int(IMG_ROWS)) / 2, (minc + maxc - int(IMG_COLS)) / 2
        if r < 0:
            r = 0
        if c < 0:
            c = 0
        if r + int(IMG_ROWS) > img.shape[0]:
            r = img.shape[0] - int(IMG_ROWS)
        if c + int(IMG_COLS) > img.shape[1]:
            c = img.shape[1] - int(IMG_COLS)
        r = int(r)
        c = int(c)
        test_img = img[r:r + int(IMG_ROWS), c:c + int(IMG_COLS)]
        if test_img.shape != (int(IMG_ROWS), int(IMG_COLS)):
            continue

        test_img = np.array([[test_img]], dtype=np.float32)
        test_img /= 255.0
        test_mask_img = model.predict(test_img.transpose(0, 2, 3, 1), verbose=1)
        test_mask_img = (test_mask_img * 255.0).astype(np.uint8)
        test_mask_img = test_mask_img.transpose(0, 3, 1, 2)[0][0]
        
        mask_img[r:r + int(IMG_ROWS), c:c + int(IMG_COLS)] = test_mask_img

    thresh = threshold_otsu(mask_img)
    bw = closing(mask_img > thresh, square(3))
    cleared = clear_border(bw)
    label_image = label(cleared)

    proposals = []
    for region in regionprops(label_image):
        if region.area >= 100:
            minr, minc, maxr, maxc = region.bbox
            crop_img = img2[minr:maxr, minc:maxc]
            proposals.append(crop_img)

    i = 0
    for img_f in proposals:
        i+=1
        cv2.imwrite("img_"+ str(i) + ".jpg", img_f)
        img_file = cv2.resize(img_f, (80, 60))
        test_img = np.array([img_file], dtype=np.float32)
        test_img /= 255.0
        y_pred = model2.predict(test_img)
        Y_pred_class = np.argmax(y_pred,axis=1) 
        print(Y_pred_class)



classify("/data/home/dxtr/WBC_Segmentaion/SigTuple_data/Test_Data/5ABD740F744D.jpg")