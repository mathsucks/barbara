from unittest import mock

from barbara.writers import Writer


@mock.patch("barbara.writers.os")
@mock.patch("barbara.writers.shutil")
def test_writer_writes(patched_shutil, patched_os):
    """Should open the target file and write to it"""
    env_file = mock.MagicMock()
    Writer(env_file, {"test-key": "test-value"}).write()
    env_file.open().__enter__().write.assert_called()


@mock.patch("barbara.writers.shutil")
@mock.patch("barbara.writers.os")
def test_writer_backup(patched_os, patched_shutil):
    """Should backup and then clean up backup when writing"""
    env_file = mock.MagicMock()
    Writer(env_file, {"test-key": "test-value"}).write()
    patched_shutil.copy2.assert_called()
    patched_os.remove.assert_called()
