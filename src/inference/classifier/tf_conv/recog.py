
# coding: utf-8

# In[3]:



import logging
logging.getLogger('tensorflow').disabled = True

import sys
import os                  # dealing with directories
import imp
import cv2                 # working with, mainly resizing, images
import numpy as np         # dealing with arrays
from random import shuffle # mixing up or currently ordered data that might lead our network astray in training.

#CUR_DIR = 'D:/python/seal/cur/foo.jpg'
path = sys.argv[1]  
IMG_SIZE = 50
LR = 1e-3


MODEL_NAME = 'garage-{}-{}.model'.format(LR, '6conv-basic-video') # just so we remember which saved model


# In[4]:


testing_data = []
img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (IMG_SIZE,IMG_SIZE))
testing_data.append([np.array(img), 1])


# In[5]:


import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

convnet = input_data(shape=[None, IMG_SIZE, IMG_SIZE, 1], name='input')

convnet = conv_2d(convnet, 32, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 64, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 32, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 64, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 32, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 64, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = fully_connected(convnet, 1024, activation='relu')
convnet = dropout(convnet, 0.8)

convnet = fully_connected(convnet, 2, activation='softmax')
convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet, tensorboard_dir='log')


# In[6]:


if os.path.exists('{}.meta'.format(MODEL_NAME)):
    model.load(MODEL_NAME)
    print('model loaded!')
    print('=============')


# In[7]:


import matplotlib.pyplot as plt
def getImgData(data_array, idx):
    img = data_array[idx]
    img_data = img[0]    # picture data == array([[187, 191, 193, ..., 148, 143, 134] ...
    img_num = img[1]     # cat
    
    orig = img_data
    data = img_data.reshape(IMG_SIZE,IMG_SIZE,1)
    model_out = model.predict([data])[0]
    
    if np.argmax(model_out) == 1: str_label='Anomoly'
    else: str_label='Animal'
    return orig, str_label

img, label = getImgData(testing_data,0)

print(label)

fig=plt.figure()
y = fig.add_subplot(1,1,1)
y.imshow(img,cmap='gray')
plt.title(label)
y.axes.get_xaxis().set_visible(False)
y.axes.get_yaxis().set_visible(False)

