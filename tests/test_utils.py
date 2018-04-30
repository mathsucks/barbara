from collections import OrderedDict
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


@mock.patch('barbara.utils.click')
@mock.patch('barbara.utils.VARIABLE_MATCHER')
def test_get_value_for_key(patched_matcher, patched_click):
    """Should request user response for key, and suggest default if provided"""
    patched_matcher.search.return_value = False
    patched_click.prompt.return_value = 'user-response'
    result = utils.get_value_for_key('test-key', 'test-default')
    assert result == 'user-response'
    patched_click.prompt.assert_called_once_with('test-key', default='test-default', type=str)


@mock.patch('barbara.utils.click')
@mock.patch('barbara.utils.find_subvariables')
@mock.patch('barbara.utils.VARIABLE_MATCHER')
def test_get_value_for_key_with_subvariables(patched_matcher, patched_find, patched_click):
    """Should request user response for each found variable and replace in template"""
    patched_matcher.match.return_value = True
    patched_click.prompt.side_effect = ['b', 'd']
    patched_find.side_effect = [[['[a:b]', 'a', 'b'], ['[c:d]', 'c', 'd', ]]]

    result = utils.get_value_for_key('test-key', '[a:b][c:d]')
    assert result == 'bd'



@pytest.mark.parametrize('template,subvariable,sub_name,sub_default',[
    ('[test]', '[test]', 'test', None),
    ('\[[test]\]', '[test]', 'test', None),
    ('[test:tset]', '[test:tset]', 'test', 'tset'),
    ('[test:[tset:test]]', '[tset:test]', 'tset', 'test'),
    ('http://[username:user]:password@host.com/path', '[username:user]', 'username', 'user'),
])
def test_subvariables(template, subvariable, sub_name, sub_default):
    """Should parse subvariables within reason"""
    result = next(utils.find_subvariables(template))
    assert result[0] == subvariable
    assert result[1] == sub_name
    assert result[2] == sub_default


@mock.patch('barbara.utils.get_value_for_key', return_value='new-value')
def test_merge_with_prompts_matching_with_skip(patched_get):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = OrderedDict(**{'A': 'existing-value-a', 'B': 'existing-value-b'})
    template = OrderedDict(**{'B': 'template-value-b', 'A': 'template-value-a'})
    merged = utils.merge_with_prompts(existing, template, skip_existing=True)
    patched_get.assert_not_called()
    assert merged['A'] == 'existing-value-a'
    assert merged['B'] == 'existing-value-b'


@mock.patch('barbara.utils.get_value_for_key', side_effect=['new-value-a', 'new-value-b'])
def test_merge_with_prompts_matching_without_skip(patched_get):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = OrderedDict(**{'A': 'existing-value-a', 'B': 'existing-value-b'})
    template = OrderedDict(**{'B': 'template-value-b', 'A': 'template-value-a'})
    merged = utils.merge_with_prompts(existing, template, skip_existing=False)
    assert merged['A'] == 'new-value-a'
    assert merged['B'] == 'new-value-b'
