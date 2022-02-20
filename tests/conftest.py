import contextlib
import os
from unittest.mock import patch

import cv2
import pytest

from receiver import Receiver


@pytest.fixture()
def no_sleep():
    """
    We make cv2.waitKey() do nothing in the end delay because receiver pauses before existing
    """
    waitkey = cv2.waitKey

    def new_waitKey(delay):
        if delay != 1:
            return -1
        return waitkey(delay)

    with patch('cv2.waitKey', new_waitKey):
        yield


@pytest.fixture()
def remove_files_before(request):
    for file in request.param:
        with contextlib.suppress(FileNotFoundError):
            os.remove(file)


@pytest.fixture()
def remove_files_after(request):
    yield
    for file in request.param:
        with contextlib.suppress(FileNotFoundError):
            os.remove(file)


@pytest.fixture()
def receiver_with_mocked_video(request):
    """
    request should contain the path to the series of test images to feed into the VideoCapture object
    """

    # This is a feature of cv2.VideoCapture - it mocks the input stream from a set of photos
    # Documentation - https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html
    mock_video_capture = cv2.VideoCapture(request.param)

    return Receiver(qr_detector=cv2.QRCodeDetector(), video_capture=mock_video_capture)
