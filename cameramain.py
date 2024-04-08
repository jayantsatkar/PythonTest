'''version 1 image unwrapping and stitching with NI input 0 or single from IDS 
program is not ending and image saving in DB is pending 
22 feb DB is done but not program is not ending currenty 
'''

import sys
import time 

from datetime import datetime

try:
    from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QMainWindow, QMessageBox, QWidget, QPushButton
    from PySide6.QtGui import QImage
    from PySide6.QtCore import Qt, Slot, QTimer
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton

except ImportError:
    from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QMainWindow, QMessageBox, QWidget
    from PySide2.QtGui import QImage
    from PySide2.QtCore import Qt, Slot, QTimer

from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
from ids_peak import ids_peak_ipl_extension

from display import Display
import cv2 ## Commented by Jayant
import os
import numpy as np
import nidaqmx


VERSION = "1.2.0"
FPS_LIMIT = 50
#output_dir = r"C:\Users\TMC8\Desktop\Casting Inspection borescope sw\01 Python - video to 2D unwrapped image\tonytrail\outputdir"
output_dir = r'C:\Users\jayan\Desktop\Python\output_dir'
unwrapped_images = []
center_x = 945
center_y = 557
ring_radius = 240
thickness = 2
rect_width = int(2 * np.pi * (ring_radius + thickness))

#unwrapped_output_dir = r"C:\Users\TMC8\Desktop\Casting Inspection borescope sw\01 Python - video to 2D unwrapped image\tonytrail\unwrappingimage"
unwrapped_output_dir = r'C:\Users\jayan\Desktop\Python\unwrapped_output_dir'
os.makedirs(unwrapped_output_dir, exist_ok=True)

#DB_output_dir = r"C:\Users\TMC8\Desktop\Casting Inspection borescope sw\01 Python - video to 2D unwrapped image\tonytrail\DB"
DB_output_dir = r'C:\Users\jayan\Desktop\Python\DB_output_dir'
os.makedirs(DB_output_dir, exist_ok=True)

# Output directory for stitched image
#stitched_output_dir = r"C:\Users\TMC8\Desktop\Casting Inspection borescope sw\01 Python - video to 2D unwrapped image\tonytrail\stitchingimage"
stitched_output_dir = r'C:\Users\jayan\Desktop\Python\stitched_output_dir'
os.makedirs(stitched_output_dir, exist_ok=True)
class MainWindow(QMainWindow):
 
    def __init__(self, parent: QWidget = None):
        self.__frame_count = 0
        super().__init__(parent)
        
        self.widget = QWidget(self)
        self.__layout = QVBoxLayout()
        self.widget.setLayout(self.__layout)
        self.setCentralWidget(self.widget)

        self.__device = None
        self.__acquisition_running = False
        self.__nodemap_remote_device = None
        self.__datastream = None

        self.__display = None
        self.__acquisition_timer = QTimer()
        self.__frame_counter = 0
        self.__error_counter = 0
        self.__acquisition_running = False

        self.__label_infos = None
        self.__label_version = None
        self.__label_aboutqt = None

        '''central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        button = QPushButton("Click me ", central_widget)
        button.clicked.connect(self.button_clicked)

        layout.addWidget(button)
        self.setCentralWidget(central_widget)'''

        #self.ni_check_timer = QTimer(self)
        #self.ni_check_timer.timeout.connect(self.check_ni_lines)
        #self.ni_check_timer.start(1000)

        # initialize peak library
        ids_peak.Library.Initialize()

        if self.__open_device():
            try:
                # Create a display for the camera image
                self.__display = Display()
                self.__layout.addWidget(self.__display)
                if not self.__start_acquisition():
                    QMessageBox.critical(self, "Unable to start acquisition!", QMessageBox.Ok)
            except Exception as e:
                QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)

        else:
            self.__destroy_all()
            sys.exit(0)

        self.__create_statusbar()

        self.setMinimumSize(700, 500)
    
    def button_clicked(self):
        print("Button clicked!")
        
    def __del__(self):
        self.__destroy_all()

    def __destroy_all(self):
        # Stop acquisition
        self.__stop_acquisition()

        # Close device and peak library
        self.__close_device()
        ids_peak.Library.Close()

    def __open_device(self):
        try:
            # Create instance of the device manager
            device_manager = ids_peak.DeviceManager.Instance()

            # Update the device manager
            device_manager.Update()

            # Return if no device was found
            if device_manager.Devices().empty():
                QMessageBox.critical(self, "Error", "No device found!", QMessageBox.Ok)
                return False

            # Open the first openable device in the managers device list
            for device in device_manager.Devices():
                if device.IsOpenable():
                    self.__device = device.OpenDevice(ids_peak.DeviceAccessType_Control)
                    break

            # Return if no device could be opened
            if self.__device is None:
                QMessageBox.critical(self, "Error", "Device could not be opened!", QMessageBox.Ok)
                return False

            # Open standard data stream
            datastreams = self.__device.DataStreams()
            if datastreams.empty():
                QMessageBox.critical(self, "Error", "Device has no DataStream!", QMessageBox.Ok)
                self.__device = None
                return False

            self.__datastream = datastreams[0].OpenDataStream()

            # Get nodemap of the remote device for all accesses to the genicam nodemap tree
            self.__nodemap_remote_device = self.__device.RemoteDevice().NodeMaps()[0]

            # To prepare for untriggered continuous image acquisition, load the default user set if available and
            # wait until execution is finished
            try:
                self.__nodemap_remote_device.FindNode("UserSetSelector").SetCurrentEntry("Default")
                self.__nodemap_remote_device.FindNode("UserSetLoad").Execute()
                self.__nodemap_remote_device.FindNode("UserSetLoad").WaitUntilDone()
            except ids_peak.Exception:
                # Userset is not available
                pass

            # Get the payload size for correct buffer allocation
            payload_size = self.__nodemap_remote_device.FindNode("PayloadSize").Value()

            # Get minimum number of buffers that must be announced
            buffer_count_max = self.__datastream.NumBuffersAnnouncedMinRequired()

            # Allocate and announce image buffers and queue them
            for i in range(buffer_count_max):
                buffer = self.__datastream.AllocAndAnnounceBuffer(payload_size)
                self.__datastream.QueueBuffer(buffer)

            return True
        except ids_peak.Exception as e:
            QMessageBox.critical(self, "Exception", str(e), QMessageBox.Ok)

        return False

    def __close_device(self):
        """
        Stop acquisition if still running and close datastream and nodemap of the device
        """
        # Stop Acquisition in case it is still running
        self.__stop_acquisition()

        # If a datastream has been opened, try to revoke its image buffers
        if self.__datastream is not None:
            try:
                for buffer in self.__datastream.AnnouncedBuffers():
                    self.__datastream.RevokeBuffer(buffer)
            except Exception as e:
                QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

    def __start_acquisition(self):
        """
        Start Acquisition on camera and start the acquisition timer to receive and display images

        :return: True/False if acquisition start was successful
        """
        # Check that a device is opened and that the acquisition is NOT running. If not, return.
        if self.__device is None:
            return False
        if self.__acquisition_running is True:
            return True

        # Get the maximum framerate possible, limit it to the configured FPS_LIMIT. If the limit can't be reached, set
        # acquisition interval to the maximum possible framerate
        try:
            max_fps = self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
            target_fps = min(max_fps, FPS_LIMIT)
            self.__nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(target_fps)
        except ids_peak.Exception:
            # AcquisitionFrameRate is not available. Unable to limit fps. Print warning and continue on.
            QMessageBox.warning(self, "Warning",
                                "Unable to limit fps, since the AcquisitionFrameRate Node is"
                                " not supported by the connected camera. Program will continue without limit.")

        # Setup acquisition timer accordingly
        self.__acquisition_timer.setInterval((1 / target_fps) * 1000)
        self.__acquisition_timer.setSingleShot(False)
        self.__acquisition_timer.timeout.connect(self.on_acquisition_timer)

        try:
            # Lock critical features to prevent them from changing during acquisition
            self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(1)

            # Start acquisition on camera
            self.__datastream.StartAcquisition()
            self.__nodemap_remote_device.FindNode("AcquisitionStart").Execute()
            self.__nodemap_remote_device.FindNode("ExposureTime").SetValue(13500)
            self.__nodemap_remote_device.FindNode("Gain").SetValue(4)
            self.__nodemap_remote_device.FindNode("BalanceWhiteAuto").SetCurrentEntry("Continuous")
            self.__nodemap_remote_device.FindNode("AcquisitionStart").WaitUntilDone()
            

        except Exception as e:
            print("Exception: " + str(e))
            return False

        # Start acquisition timer
        self.__acquisition_timer.start()
        self.__acquisition_running = True

        return True

    def __stop_acquisition(self):
        """
        Stop acquisition timer and stop acquisition on camera
        :return:
        """
        # Check that a device is opened and that the acquisition is running. If not, return.
        if self.__device is None or self.__acquisition_running is False:
            return

        # Otherwise try to stop acquisition
        try:
            remote_nodemap = self.__device.RemoteDevice().NodeMaps()[0]
            remote_nodemap.FindNode("AcquisitionStop").Execute()

            # Stop and flush datastream
            self.__datastream.KillWait()
            self.__datastream.StopAcquisition(ids_peak.AcquisitionStopMode_Default)
            self.__datastream.Flush(ids_peak.DataStreamFlushMode_DiscardAll)

            self.__acquisition_running = False

            # Unlock parameters after acquisition stop
            if self.__nodemap_remote_device is not None:
                try:
                    self.__nodemap_remote_device.FindNode("TLParamsLocked").SetValue(0)
                except Exception as e:
                    QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

        except Exception as e:
            QMessageBox.information(self, "Exception", str(e), QMessageBox.Ok)

    def __create_statusbar(self):
        status_bar = QWidget(self.centralWidget())
        status_bar_layout = QHBoxLayout()
        status_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.__label_infos = QLabel(status_bar)
        self.__label_infos.setAlignment(Qt.AlignLeft)
        status_bar_layout.addWidget(self.__label_infos)
        status_bar_layout.addStretch()

        self.__label_version = QLabel(status_bar)
        self.__label_version.setText("simple_live_qtwidgets v" + VERSION)
        self.__label_version.setAlignment(Qt.AlignRight)
        status_bar_layout.addWidget(self.__label_version)

        self.__label_aboutqt = QLabel(status_bar)
        self.__label_aboutqt.setObjectName("aboutQt")
        self.__label_aboutqt.setText("<a href='#aboutQt'>About Qt</a>")
        self.__label_aboutqt.setAlignment(Qt.AlignRight)
        self.__label_aboutqt.linkActivated.connect(self.on_aboutqt_link_activated)
        status_bar_layout.addWidget(self.__label_aboutqt)
        status_bar.setLayout(status_bar_layout)

        self.__layout.addWidget(status_bar)

    def update_counters(self):
        """
        This function gets called when the frame and error counters have changed
        :return:
        """
        self.__label_infos.setText("Acquired: " + str(self.__frame_counter) + ", Errors: " + str(self.__error_counter))
    

    @Slot()
    def on_acquisition_timer(self):
        start_trigger_channel = "Dev1/port0/line0"
        stop_trigger_channel = "Dev1/port0/line1"
        cycle_count = 0
        # Function to unwrap a circular slice into a rectangular image
        def unwrap_image(image, center_x, center_y, ring_radius, thickness, rect_width):
            unwrapped_image = np.zeros((thickness, rect_width, image.shape[2]), dtype=image.dtype)
            angle_step = 0.18  # Step size for angle (in degrees)
            r_step = 1        # Step size for r

            for angle in np.arange(0, 360, angle_step):
                for r in np.arange(0, thickness, r_step):
                    src_x = int(center_x + (ring_radius + r) * np.cos(np.radians(angle)))
                    src_y = int(center_y + (ring_radius + r) * np.sin(np.radians(angle)))

                    dst_x = int((angle / 360) * rect_width)
                    dst_y = int(r / r_step)

                    if 0 <= dst_y < thickness and 0 <= dst_x < rect_width:
                        unwrapped_image[dst_y, dst_x, :] = image[src_y, src_x, :]
            return unwrapped_image
        
        def stitch_images_vertically(images):
            #common_width = 640 
            #common_height = 480
            #resized_images = [cv2.resize(img, (common_width, common_height)) for img in images]
            return np.vstack(images)
        
        try:
            # Check if start trigger signal is received
            with nidaqmx.Task() as start_trigger_task:
                start_trigger_task.di_channels.add_di_chan(start_trigger_channel)
                #stop_trigger_task.di_channels.add_di_chan(stop_trigger_channel)
                # Get buffer from device's datastream
                buffer = self.__datastream.WaitForFinishedBuffer(5000)

                # Create IDS peak IPL image for debayering and convert it to RGBa8 format
                ipl_image = ids_peak_ipl_extension.BufferToImage(buffer)
                converted_ipl_image = ipl_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGRa8)
                

                # Queue buffer so that it can be used again
                self.__datastream.QueueBuffer(buffer)

                # Get raw image data from converted image and construct a QImage from it
                image_np_array = converted_ipl_image.get_numpy_1D()
                image = QImage(image_np_array,
                            converted_ipl_image.Width(), converted_ipl_image.Height(),
                            QImage.Format_RGB32)

                # Make an extra copy of the QImage to make sure that memory is copied and can't get overwritten later on
                image_cpy = image.copy()

                # Convert QImage to numpy array
                image_np_array = np.frombuffer(image_cpy.bits(), dtype=np.uint8).reshape(image_cpy.height(), image_cpy.width(), 4)

                # Make an extra copy of the numpy array to ensure memory is copied
                image_np_copy = image_np_array.copy()
                while start_trigger_task.read():

                    output_path = os.path.join(output_dir, f'frame_{self.__frame_count:04d}.jpg')
                    cv2.imwrite(output_path, image_np_copy)

                    unwrapped_image = unwrap_image(image_np_copy, center_x, center_y, ring_radius, thickness, rect_width)
                    unwrapped_images.append(unwrapped_image)

                # Display the unwrapped image in real-time
                    cv2.imshow('Unwrapped Image', unwrapped_image)
                    unwrapoutfile = f'unwrapped_photo_{self.__frame_count:04d}.jpg'
                    unwrapped_path = os.path.join(unwrapped_output_dir,unwrapoutfile)
                    cv2.imwrite(unwrapped_path,unwrapped_image)

                    self.__frame_count += 1
                    # Emit signal that the image is ready to be displayed
                    self.__display.on_image_received(image_cpy)
                    self.__display.update()

                    # Increase frame counter
                    self.__frame_counter += 1
                    break 
                
                
                    #cv2.imshow('result',stitched_result) 
                


        except ids_peak.Exception as e:
            self.__error_counter += 1
            print("Exception: " + str(e))

        

        with  nidaqmx.Task() as stop_trigger_task:
            stop_trigger_task._di_channels.add_di_chan(stop_trigger_channel)
            def delete_files_in_folder(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            while stop_trigger_task.read():
                all_files = os.listdir(unwrapped_output_dir)
                image_files = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

                image_paths = [os.path.join(unwrapped_output_dir, img_file) for img_file in image_files]

                unwimage = [cv2.imread(path) for path in image_paths]
            
                if len(unwimage) > 0:
                    stitched_result = stitch_images_vertically(unwimage)
                    im=stitched_result
                    stitched_output_filename = f'stitched_frame_{cycle_count}.jpg'
                    stitched_output_path = os.path.join(stitched_output_dir, stitched_output_filename)
                    cv2.imwrite(stitched_output_path, stitched_result)
                    cycle_count += 1
                else:
                    print("there are No image available")


                cv2.imshow('Stitched Result', stitched_result)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                db_image_filename = f'image_{timestamp}.jpg'
                db_image_path = os.path.join(DB_output_dir, db_image_filename)
                cv2.imwrite(db_image_path, im)
                delete_files_in_folder(unwrapped_output_dir)
                delete_files_in_folder(stitched_output_dir)
                print("the image is delete ")
                print(f'Image saved to database directory as {db_image_filename}')
                
                
                
                
                
                

    # Update counters
        self.update_counters()
        
        


    @Slot(str)
    def on_aboutqt_link_activated(self, link):
        if link == "#aboutQt":
            QMessageBox.aboutQt(self, "Bosch ")