import os
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import pickle
import time

def square_crop(image, x_pos, y_pos, size=35):
    """Returns a square crop of size centered on (x_pos, y_pos)
    Inputs:
        image: np.ndarray, image data in an array
        x_pos: int, x-coordinate of the hotspot
        y_pos: int, y-coordinate of the hotspot
        size: int, side length for the returned crop
    Outputs:
        cropped_image: np.ndarray, cropped image data of size (size x size)
    """
    size = (np.floor(size/2) * 2 + 1).astype(np.int) #Forces size to be odd
    offset = ((size - 1) / 2).astype(np.int)

    x_low = x_pos - offset
    x_high = x_pos + offset + 1

    y_low = y_pos - offset
    y_high = y_pos + offset + 1

    if x_low < 0:
        x_high = x_high - x_low
        x_low = 0
    
    if x_high > image.shape[1]:
        x_low = x_low - (x_high - image.shape[1])
        x_high = image.shape[1]

    if y_low < 0:
        y_high = y_high - y_low
        y_low = 0

    if y_high > image.shape[0]:
        y_low = y_low - (y_high - image.shape[0])
        y_high = image.shape[0]

    cropped_image = image[y_low:y_high, x_low:x_high]

    return cropped_image

# Main Program
data_file = '../arcticseals/data/train.csv'
data_directory = './ArcticSealsData01_Thermal_N'

df = pd.read_csv(data_file)

print(df.columns)
print(len(df))

thumb_size = 35
if os.path.isfile('train_data.p'):
    data = pickle.load(open('train_data.p','rb'))
else:
    data = np.zeros((len(df), thumb_size**2))

    for ix in range(len(df)):
        try:
            file_name = os.path.join(data_directory,df['filt_thermal16'][ix])
            file_name = file_name.replace('16BIT','8BIT-N')

            image = np.array(Image.open(file_name))
            cropped = square_crop(image, df['x_pos'][ix], df['y_pos'][ix])
            data[ix,:] = cropped.flatten()
        except FileNotFoundError:
            print('Could not find: {}'.format(file_name))
    
    pickle.dump(data, open('train_data.p', 'wb'))

y_index, y_catagories = df['hotspot_type'].factorize()


from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

n_estimators_rfc = 20
n_components_pca = 25

rfc = RandomForestClassifier()
pca = PCA()

pca_rfc = Pipeline([('pca', pca), ('rfc', rfc)])
pca_rfc.set_params(pca__n_components=n_components_pca, rfc__n_estimators=n_estimators_rfc)
pca_rfc.fit(data, y_index)

param_grid = [{'pca__n_components': [10, 15, 20, 25, 50, 100],
                'rfc__n_estimators': [10, 15, 20, 25, 50, 100]}]

#param_grid = [{'pca__n_components': [5, 10, 15],
#                'rfc__n_estimators': [5, 10]}]

clf = GridSearchCV(pca_rfc, param_grid, scoring="accuracy", cv=5)
clf.fit(data, y_index)
params = clf.cv_results_
results = params['mean_test_score']
max_index = np.argmax(results)
print(params['params'][max_index])

save_file = 'pca_rfc_model_{}.p'.format(time.strftime('%Y%m%d_%H%M%S'))
pickle.dump(clf, open(save_file, 'wb'))

print('Wrote classifier to: {}'.format(save_file))


'''
pca.fit(data)
data_pca = pca.transform(data)
# Plots the eigen seals
explained_variance = pca.explained_variance_ratio_
eigen_seals = pca.components_.reshape((n_components_pca, thumb_size, thumb_size))
for ix in range(eigen_seals.shape[0]):
    plt.imshow(eigen_seals[ix,:,:])
    plt.colorbar()
    plt.title('Eigen Seal: {}, Explained Variance: {}'.format(ix, explained_variance[ix]))
    plt.show(block=True)
'''

'''
from sklearn.metrics import confusion_matrix
# Confusion Matrix on self
y_predict = clf.predict(data)
cm = confusion_matrix(y_predict, y_index)

print('Confusion Matrix:')
print(cm)
'''