from barbara import readers


class TestEnvReader:
    reader = readers.EnvReader

    def assert_env_value(self, env, key, value):
        assert env[key] == value

    def test_read_single_line(self, tmpdir):
        """Should contain key name in result"""
        p = tmpdir.join(".env")
        p.write("key=value")

        r = self.reader(p)
        values = r.read()
        assert "key" in values

    def test_read_multi_line(self, tmpdir):
        """Should ignore whitespace and contain both key names in the result"""
        p = tmpdir.join(".env")
        p.write(
            """
        key=value
        derp=pants
        """
        )

        r = self.reader(p)
        values = r.read()
        assert "key" in values
        assert "derp" in values

    def test_read_single_line_with_comment(self, tmpdir):
        """Should not trip up on comments in file contents"""
        p = tmpdir.join(".env")
        p.write(
            """
        # Comment line
        withcomment=hasvalue
        """
        )

        r = self.reader(p)
        env = r.read()
        assert "withcomment" in env
        self.assert_env_value(env, "withcomment", "hasvalue")

    def test_read_multi_line_with_comment(self, tmpdir):
        """Should not clobber with commented values"""
        p = tmpdir.join(".env")
        p.write(
            """
        # Comment line
        withcomment=hasvalue
        # withcomment=ignoreme
        """
        )

        r = self.reader(p)
        env = r.read()
        assert "withcomment" in env
        self.assert_env_value(env, "withcomment", "hasvalue")


class TestYAMLConfigReader:
    def test_read_single_line(self, tmpdir):
        """Should contain key name in result"""
        p = tmpdir.join("env-template.yml")
        p.write(
            """
        schema-version: 2
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development
        """
        )

        r = readers.YAMLTemplateReader(p)
        template = r.read()
        assert "ENVIRONMENT_NAME" in template["environment"]

    def test_read_multi_line(self, tmpdir):
        """Should ignore whitespace and contain both key names in the result"""
        p = tmpdir.join("env-template.yml")
        p.write(
            """
        schema-version: 2.0
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development
          DATABASE_URL: sqlite:///simple.db
        """
        )

        r = readers.YAMLTemplateReader(p)
        template = r.read()
        assert "ENVIRONMENT_NAME" in template["environment"]
        assert "DATABASE_URL" in template["environment"]

    def test_read_single_line_with_comment(self, tmpdir):
        """Should not trip up on comments in file contents"""
        p = tmpdir.join("env-template.yml")
        p.write(
            """
        schema-version: 2.0
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development  # this is not part of the value
        """
        )

        r = readers.YAMLTemplateReader(p)
        template = r.read()
        assert "ENVIRONMENT_NAME" in template["environment"]
        assert template["environment"]["ENVIRONMENT_NAME"].preset == "development"

    def test_read_multi_line_with_comment(self, tmpdir):
        """Should not clobber with commented values"""
        p = tmpdir.join("env-template.yml")
        p.write(
            """
        schema-version: 2.0
        environment:
          ENVIRONMENT_NAME: development
          # ENVIRONMENT_NAME: not-development
        """
        )

        r = readers.YAMLTemplateReader(p)
        template = r.read()["environment"]
        assert "ENVIRONMENT_NAME" in template
        assert template["ENVIRONMENT_NAME"].preset == "development"
