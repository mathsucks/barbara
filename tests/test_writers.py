from collections import OrderedDict
from unittest import mock

from barbara.writers import Writer


@mock.patch('barbara.writers.shutil')
@mock.patch('barbara.writers.os')
@mock.patch('barbara.writers.click')
def test_writer_writes(patched_click, *args):
    """Should open the target file and write to it"""
    Writer('.env', OrderedDict(**{'test-key': 'test-value'})).write()
    patched_click.open_file.assert_called_with('.env', 'w')


@mock.patch('barbara.writers.click')
@mock.patch('barbara.writers.shutil')
@mock.patch('barbara.writers.os')
def test_writer_backup(patched_os, patched_shutil, *args):
    """Should backup and then clean up backup when writing"""
    Writer('.env', OrderedDict(**{'test-key': 'test-value'})).write()
    patched_shutil.copy.assert_called()
    patched_os.remove.assert_called()
