from include.StereoCameraController import StereoCameraController
import cv2
import numpy as np
import PySpin
import time
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stereo camera controller')
    parser.add_argument('--save_images', metavar='S', help='Save images', type=bool, default=False)
    args = parser.parse_args()

    if args.save_images:
        path_to_image = '/home/daniel/Pictures/calib_sm2_binning'
        os.makedirs(path_to_image, exist_ok=True)
        os.makedirs(path_to_image + '/left', exist_ok=True)
        os.makedirs(path_to_image + '/right', exist_ok=True)

    # stereo_ctrl = StereoCameraController(left_serial=16378749, right_serial=16378734) # fringe projection
    # stereo_ctrl = StereoCameraController(left_SN=16378753, right_SN=16378754) # stereo passive
    stereo_ctrl = StereoCameraController(left_SN=14376429, right_SN=14376435, gige=True)  # stereo ethernet

    try:
        # Set camera parameters
        stereo_ctrl.set_exposure_time(16660.0)  # (us) Para n ter interf. rede elétrica (60 Hz). (1/60s = 0,016 Hz)
        stereo_ctrl.set_exposure_mode(PySpin.ExposureAuto_Off)  # Set exposure mode to manual
        stereo_ctrl.set_gain(1)  # Set gain (dB)
        stereo_ctrl.set_image_format(PySpin.PixelFormat_Mono8)  # Set image format to Mono8
        stereo_ctrl.set_binning(1, 1)
        # Get and print available pixel formats for left and right cameras
        left_pixel_formats = stereo_ctrl.get_available_pixel_formats(stereo_ctrl.left_cam)
        right_pixel_formats = stereo_ctrl.get_available_pixel_formats(stereo_ctrl.right_cam)
        print(f"Left Camera Available Pixel Formats: {left_pixel_formats}")
        print(f"Right Camera Available Pixel Formats: {right_pixel_formats}")
        # Get and print the serial numbers
        left_serial, right_serial = stereo_ctrl.get_serial_numbers()
        left_model, right_model = stereo_ctrl.get_model()
        print(f"Left Camera:   {left_model, left_serial}")
        print(f"Right Camera: {right_model, right_serial}")

        # Start acquisition
        stereo_ctrl.start_acquisition()
        start_time = time.time()
        frames = 0
        fps = 0
        k = 0
        count = 0
        # Capture synchronized images
        while k != 27:
            k = cv2.waitKey(10)
            left_image, right_image = stereo_ctrl.capture_images()
            if args.save_images and k == 32:
                stereo_ctrl.save_images(path=path_to_image, counter=count, img_format='.png')
                count += 1

            img_concatenate = np.concatenate((left_image, right_image), axis=1)
            cv2.namedWindow('Stereo', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Stereo', int(img_concatenate.shape[1] / 2), int(img_concatenate.shape[0] / 2))
            cv2.imshow('Stereo', img_concatenate)
            # cv2.imshow('left', left_image)
            # cv2.imshow('right', right_image)
            frames += 1
            if (time.time() - start_time) > 1:
                fps = round(frames / (time.time() - start_time), 1)
                frames = 0
                start_time = time.time()
            # print(fps)
        # Process images as needed...

    finally:
        print("Camera closed")
        # Stop acquisition and cleanup resources
        stereo_ctrl.stop_acquisition()
        stereo_ctrl.cleanup()
