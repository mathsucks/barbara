from collections import OrderedDict
from unittest import mock

from barbara import Writer


@mock.patch('barbara.writer.shutil')
@mock.patch('barbara.writer.os')
@mock.patch('barbara.writer.click')
def test_writer_writes(patched_click, *args):
    """Should open the target file and write to it"""
    Writer('.env', OrderedDict(**{'test-key': 'test-value'})).write()
    patched_click.open_file.assert_called_with('.env', 'w')


@mock.patch('barbara.writer.click')
@mock.patch('barbara.writer.shutil')
@mock.patch('barbara.writer.os')
def test_writer_backup(patched_os, patched_shutil, *args):
    """Should backup and then clean up backup when writing"""
    Writer('.env', OrderedDict(**{'test-key': 'test-value'})).write()
    patched_shutil.copy.assert_called()
    patched_os.remove.assert_called()
