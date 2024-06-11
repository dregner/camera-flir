from include.CameraController import CameraController
import PySpin
import cv2
import numpy as np
import time
import os
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Camera Control')
    parser.add_argument('--save_images', metavar='S', help='Save images', type=bool, default=False)
    args = parser.parse_args()
    cam_ctrl = CameraController()
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1600, 1200)
    test_name = 'bfs-12_f6'
    if args.save_images:
        path_to_image = '/home/daniel/Pictures/{}'.format(test_name)
        os.makedirs(path_to_image, exist_ok=True)
    try:
        # Set camera parametersh
        cam_ctrl.set_exposure_time(16660.0)  # Set exposure time to 10000 microseconds
        cam_ctrl.set_exposure_mode(PySpin.ExposureAuto_Continuous)  # Set exposure mode to auto continuous
        cam_ctrl.set_gain(1.0)  # Set gain to 5 dB
        cam_ctrl.set_image_format(PySpin.PixelFormat_Mono8)  # Set image format to Mono8
        pixel_formats = cam_ctrl.get_available_pixel_formats(cam_ctrl.cam)
        cam_ctrl.set_frame_rate(10)
        print(f" Camera Available Pixel Formats: {pixel_formats}")
        print("Seria: {}".format(cam_ctrl.get_model()))
        # Get and print the serial number
        serial_number = cam_ctrl.get_serial_number()
        print(f"Camera Serial Number: {serial_number}")

        # Start acquisition
        cam_ctrl.start_acquisition()
        start_time = time.time()
        frames = 0
        fps = 0
        k = 0
        count = 0

        # Capture synchronized images
        while k != 27:
            k = cv2.waitKey(1)
            image = cam_ctrl.capture_images()

            if args.save_images and k == 32:
                cam_ctrl.save_images(path=path_to_image, counter=count, img_format='.png')
                count += 1

            cv2.imshow('image', image)
            frames += 1
            if (time.time() - start_time) > 1:
                fps = round(frames / (time.time() - start_time), 1)
                print(f"FPS: {fps}")
                frames = 0
                start_time = time.time()

        # Process images as needed...
    finally:
        # Cleanup resources
        cam_ctrl.stop_acquisition()
        cam_ctrl.cleanup()
