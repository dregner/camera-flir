import PySpin
import cv2


class CameraController:
    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.cam = None
        if self.cam_list.GetSize() == 0:
            self.cam_list.Clear()
            self.system.ReleaseInstance()
            raise Exception("No cameras detected.")
        self.cam = self.cam_list[0]
        self.cam.Init()

    def set_exposure_time(self, exposure_time):
        if self.cam is not None:
            exposure_auto = self.cam.ExposureAuto.GetAccessMode()
            if exposure_auto == PySpin.RW:
                self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            self.cam.ExposureTime.SetValue(exposure_time)

    def set_frame_rate(self, frame_rate):
            # Ensure frame rate is in manual mode
            if self.cam.AcquisitionFrameRateEnable.GetAccessMode() == PySpin.RW:
                self.cam.AcquisitionFrameRateEnable.SetValue(True)
            # Set the frame rate
            if self.cam.AcquisitionFrameRate.GetAccessMode() == PySpin.RW:
                self.cam.AcquisitionFrameRate.SetValue(frame_rate)

    def set_exposure_mode(self, mode):
        if self.cam is not None:
            exposure_auto = self.cam.ExposureAuto.GetAccessMode()
            if exposure_auto == PySpin.RW:
                self.cam.ExposureAuto.SetValue(mode)

    def set_gain(self, gain):
        if self.cam is not None:
            gain_auto = self.cam.GainAuto.GetAccessMode()
            if gain_auto == PySpin.RW:
                self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            self.cam.Gain.SetValue(gain)

    def set_image_format(self, pixel_format):
        if self.cam is not None:
            if self.cam.PixelFormat.GetAccessMode() == PySpin.RW:
                self.cam.PixelFormat.SetValue(pixel_format)

    def get_serial_number(self):
        if self.cam is not None:
            return self.cam.DeviceSerialNumber.ToString()

    def get_model(self):
        return self.cam.DeviceModelName.ToString()

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
        self.cam.BeginAcquisition()

    def stop_acquisition(self):
        self.cam.EndAcquisition()

    def capture_images(self):
        image_result = self.cam.GetNextImage()
        try:
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
            image = image_result
            image_result.Release()
            return image.GetNDArray()
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return None

    def cleanup(self):
        if self.cam is not None:
            self.cam.DeInit()
        self.cam_list.Clear()
        self.system.ReleaseInstance()
