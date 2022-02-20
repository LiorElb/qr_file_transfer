import filecmp
import os
import contextlib
from unittest.mock import patch

import cv2
import pytest

from src.receiver import Receiver


@pytest.fixture()
def no_sleep():
    """
    We make time.sleep() do nothing because receiver pauses before existing
    """
    with patch('time.sleep'):
        yield


@pytest.fixture()
def remove_files_before(request):
    with contextlib.suppress(FileNotFoundError):
        for file in request.param:
            os.remove(file)


@pytest.fixture()
def remove_files_after(request):
    yield
    with contextlib.suppress(FileNotFoundError):
        for file in request.param:
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


@pytest.mark.parametrize("remove_files_before", [["test_file.txt"]], indirect=True)
@pytest.mark.parametrize("remove_files_after", [["test_file.txt"]], indirect=True)
@pytest.mark.parametrize("receiver_with_mocked_video", ["artifacts/test_file/test_img_%02d.jpg"], indirect=True)
def test_receiver(receiver_with_mocked_video: Receiver, no_sleep, remove_files_before, remove_files_after):
    with pytest.raises(SystemExit) as ex:
        receiver_with_mocked_video.read_transmission()

    assert ex.value.code == 0  # Assert receiver existed with status code 0

    assert os.path.exists("test_file.txt")
    assert os.path.getsize('test_file.txt') != 0
    assert filecmp.cmp("artifacts/test_file/test_file.txt", "test_file.txt")


@pytest.mark.parametrize("remove_files_before", [["test_file.txt", "test_file.txt (1)", "test_file.txt (2)"]],
                         indirect=True)
@pytest.mark.parametrize("remove_files_after", [["test_file.txt", "test_file.txt (1)", "test_file.txt (2)"]],
                         indirect=True)
@pytest.mark.parametrize("receiver_with_mocked_video", ["artifacts/test_file/test_img_%02d.jpg"], indirect=True)
def test_receiver_file_naming(receiver_with_mocked_video: Receiver, no_sleep, remove_files_before, remove_files_after):
    open('test_file.txt', 'w').close()  # create an empty files with that name
    open('test_file.txt (1)', 'w').close()

    with pytest.raises(SystemExit) as ex:
        receiver_with_mocked_video.read_transmission()

    assert ex.value.code == 0  # Assert receiver existed with status code 0

    assert os.path.exists('test_file.txt')
    assert os.path.exists('test_file.txt (1)')

    assert os.path.getsize('test_file.txt') == 0
    assert os.path.getsize('test_file.txt (1)') == 0

    assert os.path.exists('test_file.txt (2)')
    assert os.path.getsize('test_file.txt (2)') != 0
    assert filecmp.cmp("artifacts/test_file/test_file.txt", "test_file.txt (2)")
