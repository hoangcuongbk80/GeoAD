import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import shutil

objects = {'Object1':1, 'Object2':2, 'Object3':3, 'Object4':4, 'Object5':5, 'Object6':6,
            'Object7':7, 'Object8':8, 'Object9': 9, 'Object10':10}

data_dir = '/blender-scripts/data'
start_scene = 0
end_scene = 1

for s in range(start_scene, end_scene):
    scene_dir = os.path.join(data_dir, str(s))
    anomaly_dir = os.path.join(scene_dir, 'anomaly')
    if os.path.isdir(anomaly_dir):
        shutil.rmtree(anomaly_dir)
    os.mkdir(anomaly_dir)

    depth_dir = os.path.join(scene_dir, 'depth')
    num_samples = len(os.listdir(depth_dir))
    for i in range(0, num_samples):
        anomaly_img = np.zeros((480, 640), dtype=np.uint8)
        for obj in objects:
            img_dir = os.path.join(scene_dir + '/mask/', obj, str(i) + '.png')
            if os.path.isfile(img_dir):  
                img = cv2.imread(img_dir, -1)
                anomaly_img = np.where(img > 100, objects[obj], anomaly_img)
        save_dir = os.path.join(anomaly_dir, str(i) + '.png')
        cv2.imwrite(save_dir, anomaly_img)
        print('saved: ', save_dir)
plt.imshow(anomaly_img, aspect='auto')
plt.show()
