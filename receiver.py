import base64
import os
import sys
import time
from typing import IO

import cv2
import numpy

from utils import generate_qr_image

DEBUG = os.getenv("QR_RECEIVER_DEBUG", False)

if DEBUG:
    cv2.namedWindow("preview")

cv2.namedWindow('ACK')  # Window in which the ACK QRs will show
vc = cv2.VideoCapture(0)  # Video stream from camera


def detect_qr_and_decode(frame: numpy.ndarray):
    qr_decoder = cv2.QRCodeDetector()

    # Detect and decode the qrcode
    data, bbox, rectified_image = qr_decoder.detectAndDecode(frame)

    if len(data) == 0:  # This means no QR was spotted
        return None, None

    index = int(data[:1])
    content = data[1:]

    if data[1:] == '!':  # If we encountered the end of transmission QR
        show_ack(index)
        time.sleep(10)
        sys.exit(0)

    return index, base64.b64decode(content)


def show_ack(index: int):
    img = generate_qr_image(str(index).encode())
    cv2.imshow(f'ACK', img)


def _get_filename():
    original_filename = _read_filename_qr()

    # This part just makes sure we are writing to a new file,
    # if the file exists we add a number to it at the end untill we have a new filename
    j = 1
    filename = original_filename
    while os.path.exists(filename):
        filename = original_filename + f'({j})'
        j += 1
    return filename


# This method captures picture from the camera until we find the first QR with the filename
def _read_filename_qr():
    _, frame = vc.read()
    while True:
        index, filename = detect_qr_and_decode(frame)
        if filename is not None:
            break
        _, frame = vc.read()
    return filename.decode()


def read_qr_contents_to_file(f: IO):
    expected_index = 1
    _, frame = vc.read()
    while True:
        if DEBUG:
            cv2.imshow("preview", frame)
        index, data = detect_qr_and_decode(frame)
        if data is not None:
            if index == expected_index:
                f.write(data)
                expected_index = (expected_index + 1) % 10
            show_ack(index)

        _, frame = vc.read()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    filename = _get_filename()

    with open(filename, 'ab+') as f:
        read_qr_contents_to_file(f)


if __name__ == '__main__':
    main()
