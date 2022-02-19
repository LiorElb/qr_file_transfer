import cv2

from src.receiver import Receiver


def test_receiver():
    mock_video_capture = cv2.VideoCapture("artifacts/test_img01.jpeg")

    r = Receiver(qr_detector=cv2.QRCodeDetector(), video_capture=mock_video_capture)

    filename = r.get_filename()
    with open(filename, 'ab+') as f:
        r.read_qr_contents_to_file(f)
