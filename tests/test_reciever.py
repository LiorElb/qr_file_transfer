import filecmp
import os
from unittest.mock import patch

import cv2
import pytest

from src.receiver import Receiver


@pytest.fixture()
def test_setup(request):
    filename = request.param
    if os.path.exists(filename):
        os.remove(filename)
    with patch('time.sleep'):  # Make time.sleep do nothing
        yield
    if os.path.exists(filename):
        os.remove(filename)


@pytest.mark.parametrize("test_setup", ["test_file.txt"], indirect=True)
def test_receiver(test_setup):
    mock_video_capture = cv2.VideoCapture("artifacts/test_file/test_img_%02d.jpg")
    r = Receiver(qr_detector=cv2.QRCodeDetector(), video_capture=mock_video_capture)

    filename = r.get_filename()
    with open(filename, 'ab+') as f:
        with pytest.raises(SystemExit) as ex:
            r.read_qr_contents_to_file(f)

    assert ex.value.code == 0  # Assert receiver existed with status code 0
    assert os.path.exists("test_file.txt")
    assert os.path.isfile("test_file.txt")
    assert filecmp.cmp("artifacts/test_file/test_file.txt", "test_file.txt")
