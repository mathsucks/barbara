from unittest import mock

import pytest

from barbara import readers


def test_read_single_line(tmpdir):
    """Should contain key name in result"""
    p = tmpdir.join('.env')
    p.write('key=value')

    r = readers.EnvTemplateReader(p)
    values = r.read()
    assert 'key' in values


def test_read_multi_line(tmpdir):
    """Should ignore whitespace and contain both key names in the result"""
    p = tmpdir.join('.env')
    p.write('''
    key=value
    derp=pants
    ''')

    r = readers.EnvTemplateReader(p)
    values = r.read()
    assert 'key' in values
    assert 'derp' in values


def test_read_single_line_with_comment(tmpdir):
    """Should not trip up on comments in file contents"""
    p = tmpdir.join('.env')
    p.write("""
    # Comment line
    withcomment=hasvalue
    """)

    r = readers.EnvTemplateReader(p)
    env = r.read()
    assert 'withcomment' in env
    assert env['withcomment'].preset == 'hasvalue'


def test_read_multi_line_with_comment(tmpdir):
    """Should not clobber with commented values"""
    p = tmpdir.join('.env')
    p.write("""
    # Comment line
    withcomment=hasvalue
    # withcomment=ignoreme
    """)

    r = readers.EnvTemplateReader(p)
    env = r.read()
    assert 'withcomment' in env
    assert env['withcomment'].preset =='hasvalue'


@mock.patch('barbara.readers.boto3')
def test_read_from_ssm(patched_boto3):
    """Should retrieve deployment values from AWS SSM."""
    value_formatter = lambda value: {'Parameter': {'Value': value}}
    patched_boto3.client().get_parameter.side_effect = [
        value_formatter('value'), value_formatter('pants')
    ]

    r = readers.SSMReader('/prefix/', ['key', 'derp'])
    values = r.read()

    assert 'key' in values
    assert 'derp' in values
    assert values['key'] == 'value'
    assert values['derp'] == 'pants'


@pytest.mark.parametrize('template,sub_name,sub_default', [
    ('[test]', 'test', None),
    ('\[[test]\]', 'test', None),
    ('[test:tset]', 'test', 'tset'),
    ('[test:[tset:test]]', 'tset', 'test'),
    ('http://[username:user]:password@host.com/path', 'username', 'user'),
])
def test_subvariables(template, sub_name, sub_default):
    """Should parse subvariables within reason"""
    result = next(readers.EnvTemplateReader.find_subvariables(template))
    assert result[0] == sub_name
    assert result[1] == sub_default
