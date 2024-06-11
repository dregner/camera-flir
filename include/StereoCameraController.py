import os
import time

import PySpin
import cv2
import pynput


class StereoCameraController:
    def __init__(self, left_serial, right_serial):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        if self.cam_list.GetSize() < 2:
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            raise Exception("At least two cameras are required for stereo vision.")
        for cam in self.cam_list:
            cam.Init()
            if cam.DeviceSerialNumber.ToString() == str(left_serial):
                self.left_cam = cam
            elif cam.DeviceSerialNumber.ToString() == str(right_serial):
                self.right_cam = cam
            else:
                cam.DeInit()

    def set_exposure_time(self, exposure_time):
        for cam in [self.left_cam, self.right_cam]:
            exposure_auto = cam.ExposureAuto.GetAccessMode()
            if exposure_auto == PySpin.RW:
                cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            cam.ExposureTime.SetValue(exposure_time)

    def set_exposure_mode(self, mode):
        for cam in [self.left_cam, self.right_cam]:
            exposure_auto = cam.ExposureAuto.GetAccessMode()
            if exposure_auto == PySpin.RW:
                cam.ExposureAuto.SetValue(mode)

    def set_gain(self, gain):
        for cam in [self.left_cam, self.right_cam]:
            gain_auto = cam.GainAuto.GetAccessMode()
            if gain_auto == PySpin.RW:
                cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            cam.Gain.SetValue(gain)

    def set_image_format(self, pixel_format):
        for cam in [self.left_cam, self.right_cam]:
            if cam.PixelFormat.GetAccessMode() == PySpin.RW:
                cam.PixelFormat.SetValue(pixel_format)

    def set_binning(self, horizontal_binning, vertical_binning):
        for cam in [self.left_cam, self.right_cam]:
            if cam.BinningHorizontal.GetAccessMode() == PySpin.RW:
                cam.BinningHorizontal.SetValue(horizontal_binning)
            if cam.BinningVertical.GetAccessMode() == PySpin.RW:
                cam.BinningVertical.SetValue(vertical_binning)
    def get_serial_numbers(self):
        return self.left_cam.DeviceSerialNumber.ToString(), self.right_cam.DeviceSerialNumber.ToString()

    def get_model(self):
        return self.left_cam.DeviceModelName.ToString(), self.right_cam.DeviceModelName.ToString()

    def get_width_size(self):
        return self.left_cam.Width.GetValue(), self.right_cam.Width.GetValue()

    def get_height_size(self):
        return self.left_cam.Height.GetValue(), self.right_cam.Height.GetValue()

    def get_available_pixel_formats(self, cam):
        pixel_formats = []
        try:
            node_pixel_format = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('PixelFormat'))
            if PySpin.IsAvailable(node_pixel_format) and PySpin.IsReadable(node_pixel_format):
                entries = node_pixel_format.GetEntries()
                for entry in entries:
                    entry = PySpin.CEnumEntryPtr(entry)  # Cast to CEnumEntryPtr
                    if PySpin.IsAvailable(entry) and PySpin.IsReadable(entry):
                        pixel_format = entry.GetSymbolic()
                        pixel_formats.append(pixel_format)
        except PySpin.SpinnakerException as ex:
            print(f"Error: {ex}")
        return pixel_formats

    def start_acquisition(self):
        self.left_cam.BeginAcquisition()
        self.right_cam.BeginAcquisition()

    def stop_acquisition(self):
        self.left_cam.EndAcquisition()
        self.right_cam.EndAcquisition()

    def capture_images(self):
        left_image_result = self.left_cam.GetNextImage()
        right_image_result = self.right_cam.GetNextImage()
        if left_image_result.IsIncomplete() or right_image_result.IsIncomplete():
            raise Exception("Image capture incomplete.")

            # Convert images to BGR8 format
        left_image = left_image_result.GetNDArray()
        right_image = right_image_result.GetNDArray()
        left_image_result.Release()
        right_image_result.Release()
        return left_image, right_image

    def save_images(self, path, counter, img_format='.png'):
        left_image, right_image = self.capture_images()
        try:
            cv2.imwrite(os.path.join(os.path.join(path,'left'), 'L'+str(counter).rjust(3, '0')+img_format), left_image)
            cv2.imwrite(os.path.join(os.path.join(path,'right'), 'R'+str(counter).rjust(3, '0')+img_format), right_image)
            print('Image {} captured successfully.'.format(counter))
        except PySpin.SpinnakerException as ex:
            print(f"Error: {ex}")


    def cleanup(self):
        self.left_cam.DeInit()
        self.right_cam.DeInit()
        self.cam_list.Clear()
        self.system.ReleaseInstance()


