from collections import OrderedDict
from unittest import mock

import pytest

from barbara import utils
from barbara.variables import EnvVariable
from barbara.variables import EnvVariableTemplate


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


@mock.patch('barbara.utils.click')
def test_prompt_user_for_value(patched_click):
    """Should request user response for key, and suggest default if provided"""
    patched_click.prompt.return_value = 'user-response'
    result = utils.prompt_user_for_value(EnvVariable('test-key', 'test-default'))
    assert result == 'user-response'
    patched_click.prompt.assert_called_once_with('test-key', default='test-default', type=str)


@mock.patch('barbara.utils.click')
def test_prompt_user_for_value_with_subvariables(patched_click):
    """Should request user response for each found variable and replace in template"""
    patched_click.prompt.side_effect = ['b', 'd']

    result = utils.prompt_user_for_value(EnvVariableTemplate('test-key',
                                                             template='{a}{c}',
                                                             subvariables=[EnvVariable('a', 'b'),
                                                                           EnvVariable('c', 'd')]))
    assert result == 'bd'


@mock.patch('barbara.utils.prompt_user_for_value', return_value='new-value')
def test_merge_with_prompts_matching_with_skip(patched_get):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = OrderedDict(**{'A': 'existing-value-a', 'B': 'existing-value-b'})
    template = OrderedDict(**{'B': 'template-value-b', 'A': 'template-value-a'})
    merged = utils.merge_with_prompts(existing, template, skip_existing=True)
    patched_get.assert_not_called()
    assert merged['A'] == 'existing-value-a'
    assert merged['B'] == 'existing-value-b'


@mock.patch('barbara.utils.prompt_user_for_value', side_effect=['new-value-a', 'new-value-b'])
def test_merge_with_prompts_matching_without_skip(patched_get):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = OrderedDict(**{'A': 'existing-value-a', 'B': 'existing-value-b'})
    template = OrderedDict(**{'B': 'template-value-b', 'A': 'template-value-a'})
    merged = utils.merge_with_prompts(existing, template, skip_existing=False)
    assert merged['A'] == 'new-value-a'
    assert merged['B'] == 'new-value-b'
