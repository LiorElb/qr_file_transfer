import base64
import os
import sys
import time
from typing import IO

import cv2
import numpy

from utils import generate_qr_image


class Receiver:
    """
    A class that encapsulates all the methods needed in order to capture the QR codes from the camera input
    and write the file
    """
    qr_decoder: cv2.QRCodeDetector
    video_capture: cv2.VideoCapture

    # Takes the QR decoder and the VC stream
    def __init__(self, qr_detector: cv2.QRCodeDetector, video_capture: cv2.VideoCapture):
        self.qr_decoder = qr_detector
        self.video_capture = video_capture

        cv2.namedWindow('ACK')  # Open a window in which the ACK QRs will show

    # This is the "main" function of the class
    def read_transmission(self):
        filename = self._read_filename()
        with open(filename, 'ab+') as f:
            self._read_qr_contents_to_file(f)

    # Detect and decode the qrcode
    def _detect_qr_and_decode(self, frame: numpy.ndarray):
        data, _, _ = self.qr_decoder.detectAndDecode(frame)

        if len(data) == 0:  # This means no QR was spotted
            return None, None

        index = int(data[:1])
        content = data[1:]

        if data[1:] == '!':  # If we encountered the end of transmission QR
            self._show_ack(index)
            time.sleep(10)
            sys.exit(0)

        return index, base64.b64decode(content)

    @staticmethod
    def _show_ack(index: int):
        img = generate_qr_image(str(index).encode())
        cv2.imshow(f'ACK', img)

    def _read_filename(self):
        original_filename = self._read_filename_qr()

        # This part just makes sure we are writing to a new file,
        # if the file exists we add a number to it at the end until we have a new filename
        j = 1
        filename = original_filename
        while os.path.exists(filename):
            filename = f'{original_filename} ({j})'
            j += 1
        return filename

    # This method captures picture from the camera until we find the first QR with the filename
    def _read_filename_qr(self):
        frame = self._read_next_frame()
        while True:
            index, filename = self._detect_qr_and_decode(frame)
            if filename is not None:
                break
            frame = self._read_next_frame()
        return filename.decode()

    def _read_next_frame(self):
        _, frame = self.video_capture.read()
        if frame is None:
            raise IOError("Unable to get input from camera (was camera was shut off during transmission?)")
        return frame

    def _read_qr_contents_to_file(self, f: IO):
        expected_index = 1  # First qr we get should be indexed 1
        frame = self._read_next_frame()
        while True:
            self._before_read_actions(frame)
            index, data = self._detect_qr_and_decode(frame)
            if data is not None:
                # Handle received data
                if index == expected_index:
                    f.write(data)

                    # When we get the data we wanted, we now expect the next index.
                    expected_index = (expected_index + 1) % 10
                self._show_ack(index)  # Regardless, we show ACK for the current received packet

            # Get the next frame
            frame = self._read_next_frame()

            # This code waits until the frame arrives
            if cv2.waitKey(1) & 0xFF == ord('+'):
                break

    def _before_read_actions(self, frame):
        pass  # the main receiver doesn't do anything before reading the next QR

    def __del__(self):
        cv2.destroyAllWindows()


class DebugReceiver(Receiver):
    """
    Just like the normal Receiver, but shows the video stream from the camera on the screen
    """
    def __init__(self, qr_detector: cv2.QRCodeDetector, video_capture: cv2.VideoCapture):
        super().__init__(qr_detector, video_capture)
        cv2.namedWindow("preview")  # Video stream from camera

    def _before_read_actions(self, frame):
        cv2.imshow("preview", frame)  # Debug receiver shows the image he sees on the preview screen


# 0 means First camera or webcam
# if this doesn't capture from the camera you are want to - increment this number.
CAMERA_DEVICE_NUM = 0


def main():
    r = DebugReceiver(qr_detector=cv2.QRCodeDetector(),
                      video_capture=cv2.VideoCapture(CAMERA_DEVICE_NUM))

    r.read_transmission()


if __name__ == '__main__':
    main()
