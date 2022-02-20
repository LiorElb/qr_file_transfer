import base64
import sys
from pathlib import Path

import cv2

from utils import generate_qr_image


class Transmitter:
    video_capture: cv2.VideoCapture

    def __init__(self, video_capture: cv2.VideoCapture):
        self.video_capture = video_capture

        cv2.namedWindow("Transceiver", cv2.WINDOW_FULLSCREEN)  # A window for the QR code to be displayed on

    def transmit(self, file_path: Path):
        """
        This is the "main" function
        """

        # First we transmit the file chunk by chunk
        for i, img in self.qr_chunks_generator(file_path):
            cv2.imshow("Transceiver", img)
            while True:
                # waitKey is required or cv.imshow wont work.
                # if the '+' key is pressed, next QR will show (for debugging purposes)
                if cv2.waitKey(1) & 0xFF == ord('+'):
                    break
                # If our message was ACKed, we can move on to the next one
                if self.is_message_acknowledged(index=i):
                    break

        # Cleanup steps
        cv2.destroyAllWindows()

    @staticmethod
    def qr_chunks_generator(file_path: Path):
        """
        This generator gives out all the QRs we need to transmit in order to transfer the file
        """

        # Initial QR - the filename
        i = 0
        qr_data = str(i).encode() + base64.b64encode(file_path.name.encode())
        img = generate_qr_image(qr_data=qr_data)
        yield i, img
        i = (i + 1) % 10

        # All the file data QRs, in chunks
        with open(file_path, 'rb') as f:
            while data := f.read(45):
                message_index = str(i).encode()
                qr_data = message_index + base64.b64encode(data)
                img = generate_qr_image(qr_data)
                yield i, img
                i = (i + 1) % 10

        # The "End of transmission" QR code
        message_index = str(i).encode()
        qr_data = message_index + b'!'
        img = generate_qr_image(qr_data=qr_data)
        yield i, img

    def is_message_acknowledged(self, index):
        """
        This function reads from the camera stream and checks if it sees a QR that signals ACK for {index}
        """
        _, frame = self.video_capture.read()
        qr_decoder = cv2.QRCodeDetector()
        data, bbox, rectified_image = qr_decoder.detectAndDecode(frame)
        if len(data) != 0:
            if int(data) == index:
                return True
        return False


# 0 means First camera or webcam
# if this doesn't capture from the camera you are want to - increment this number.
CAMERA_DEVICE_NUM = 0


def main():
    if len(sys.argv) < 2:
        raise ValueError(f'Missing argument - file to transmit\n'
                         f'Usage: python3 {Path(sys.argv[0]).name} <path of file to transmit>')

    file_to_transmit = Path(sys.argv[1])
    file_to_transmit = file_to_transmit.resolve(strict=True)  # Gives an indicative error if file is not found

    t = Transmitter(video_capture=cv2.VideoCapture(CAMERA_DEVICE_NUM))
    t.transmit(file_to_transmit)


if __name__ == '__main__':
    main()
