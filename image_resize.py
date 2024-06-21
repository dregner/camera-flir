import cv2
import numpy as np
import os

PATH = '/home/daniel/Insync/daniel.regner@labmetro.ufsc.br/Google Drive - Shared drives/VORIS  - Equipe/Sistema de Medição 2 -Stereo Passivo - ORB SLAM/Softwares/matlab'
ORIGINAL_IMG = 'calib_sm2_1'
OUTPUT_IMG = 'calib_sm2_resized_800_600'
camera = ['left', 'right']
if __name__ == '__main__':
    for side in camera:
        input_imgs = os.listdir(os.path.join(PATH, ORIGINAL_IMG, side))
        os.makedirs(os.path.join(PATH, OUTPUT_IMG, side), exist_ok=True)
        for img in input_imgs:
            image = cv2.imread(os.path.join(PATH, ORIGINAL_IMG, side, img), 0)
            resized_img = cv2.resize(image, (800, 600))
            cv2.imwrite(os.path.join(PATH, OUTPUT_IMG, side, img), resized_img)
