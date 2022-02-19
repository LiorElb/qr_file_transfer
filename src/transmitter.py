import base64
import sys
from pathlib import Path

import cv2

from src.utils import generate_qr_image

vc = cv2.VideoCapture(0)  # A video capturing object, which reads from computer's camera
cv2.namedWindow("Transceiver", cv2.WINDOW_FULLSCREEN)  # A windows for the QR code to be displayed on


# This is the "main" function
def transmit(file_path: Path):
    # First we transmit the file chunk by chunk
    for i, img in qr_chunks_generator(file_path):
        cv2.imshow("Transceiver", img)
        while True:
            # waitKey is required or cv.imshow wont work.
            # if the '+' key is pressed, next QR will show (for debugging purposes)
            if cv2.waitKey(1) & 0xFF == ord('+'):
                break
            # If our message was ACKed, we can move on to the next one
            if is_ack(i):
                break

    # Cleanup steps
    cv2.destroyAllWindows()


# This generator gives out all the QRs we need to transmit in order to transfer the file
def qr_chunks_generator(file_path: Path):
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


# This function reads from the camera stream and checks if it sees a QR that signals ACK for {index}
def is_ack(index):
    _, frame = vc.read()
    qr_decoder = cv2.QRCodeDetector()
    data, bbox, rectified_image = qr_decoder.detectAndDecode(frame)
    if len(data) != 0:
        if int(data) == index:
            return True
    return False


if __name__ == '__main__':
    file_to_transmit = Path(sys.argv[1])
    file_to_transmit = file_to_transmit.resolve(strict=True)  # Checks that it exists, and gives the absolute path
    transmit(file_to_transmit)
