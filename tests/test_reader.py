from barbara import reader


def test_read_single_line(tmpdir):
    """Should contain key name in result"""
    p = tmpdir.join('.env')
    p.write('key=value')

    r = reader.Reader(p)
    values = r.read()
    assert 'key' in values


def test_read_multi_line(tmpdir):
    """Should ignore whitespace and contain both key names in the result"""
    p = tmpdir.join('.env')
    p.write('''
    key=value
    derp=pants
    ''')

    r = reader.Reader(p)
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

    r = reader.Reader(p)
    env = r.read()
    assert 'withcomment' in env
    assert 'hasvalue' in env.values()


def test_read_multi_line_with_comment(tmpdir):
    """Should not clobber with commented values"""
    p = tmpdir.join('.env')
    p.write("""
    # Comment line
    withcomment=hasvalue
    # withcomment=ignoreme
    """)

    r = reader.Reader(p)
    env = r.read()
    assert 'withcomment' in env
    assert 'hasvalue' in env.values()
