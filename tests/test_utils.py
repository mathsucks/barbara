from unittest import mock

import pytest

from barbara import utils


@mock.patch('barbara.utils.os')
@mock.patch('barbara.utils.click')
def test_confirm_target_provided_confirmed(patched_click, patched_os):
    """Should match confirmation of provided target file when file exists"""
    patched_os.path.exists.return_value = True
    patched_click.prompt.return_value = True

    assert utils.confirm_target_file('provided.env')
    patched_os.path.exists.assert_called_once_with('provided.env')


@mock.patch('barbara.utils.os')
@mock.patch('barbara.utils.click')
def test_confirm_target_provided_rejected(patched_click, patched_os):
    """Should match rejection of provided target file when file exists"""
    patched_os.path.exists.return_value = True
    patched_click.prompt.return_value = False

    assert not utils.confirm_target_file('provided.env')
    patched_os.path.exists.assert_called_once_with('provided.env')


@mock.patch('barbara.utils.find_dotenv')
@mock.patch('barbara.utils.os')
@mock.patch('barbara.utils.click')
def test_confirm_target_discovered_confirmed(patched_click, patched_os, patched_find):
    """Should match confirmation of discovered target file when file exists"""
    patched_find.return_value = 'discovered.env'
    patched_os.path.exists.return_value = True
    patched_click.prompt.return_value = True

    assert utils.confirm_target_file()
    patched_os.path.exists.assert_called_once_with(patched_find.return_value)


@mock.patch('barbara.utils.find_dotenv')
@mock.patch('barbara.utils.os')
@mock.patch('barbara.utils.click')
def test_confirm_target_default_create_confirmed(patched_click, patched_os, patched_find):
    """Should match confirmation of creation of default target file"""
    patched_find.return_value = False
    patched_os.path.exists.return_value = False
    patched_click.confirm.return_value = True

    assert utils.confirm_target_file()

    patched_os.path.exists.assert_called_once_with(utils.DEFAULT_ENV_FILENAME)
    patched_click.open_file.assert_called_once_with(utils.DEFAULT_ENV_FILENAME, 'w')


@mock.patch('barbara.utils.find_dotenv')
@mock.patch('barbara.utils.os')
@mock.patch('barbara.utils.click')
def test_confirm_target_default_create_rejected(patched_click, patched_os, patched_find):
    """Should match rejection of creating default target file"""
    patched_find.return_value = False
    patched_os.path.exists.return_value = False
    patched_click.confirm.return_value = False

    with pytest.raises(SystemExit, message=1):
        assert utils.confirm_target_file()

    patched_os.path.exists.assert_called_once_with(utils.DEFAULT_ENV_FILENAME)
    patched_click.open_file.assert_not_called()
