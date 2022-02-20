import filecmp
import os
import pytest

from receiver import Receiver


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
