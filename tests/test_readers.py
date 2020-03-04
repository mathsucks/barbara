from barbara import readers
from barbara.variables import GitCommitVariable


class TestEnvReader:
    reader_class = readers.EnvReader

    def assert_env_value(self, env, key, value):
        assert env[key] == value

    def test_read_single_line(self, tmp_path):
        """Should contain key name in result"""
        path = tmp_path / ".env"
        path.write_text("key=value")

        reader = self.reader_class(path)
        values = reader.read()
        assert "key" in values

    def test_read_multi_line(self, tmp_path):
        """Should ignore whitespace and contain both key names in the result"""
        path = tmp_path / ".env"
        path.write_text(
            """
        key=value
        derp=pants
        """
        )

        reader = self.reader_class(path)
        values = reader.read()
        assert "key" in values
        assert "derp" in values

    def test_read_single_line_with_comment(self, tmp_path):
        """Should not trip up on comments in file contents"""
        path = tmp_path / ".env"
        path.write_text(
            """
        # Comment line
        withcomment=hasvalue
        """
        )

        reader = self.reader_class(path)
        env = reader.read()
        assert "withcomment" in env.keys()
        self.assert_env_value(env, "withcomment", "hasvalue")

    def test_read_multi_line_with_comment(self, tmp_path):
        """Should not clobber with commented values"""
        path = tmp_path / ".env"
        path.write_text(
            """
        # Comment line
        withcomment=hasvalue
        # withcomment=ignoreme
        """
        )

        reader = self.reader_class(path)
        env = reader.read()
        assert "withcomment" in env
        self.assert_env_value(env, "withcomment", "hasvalue")


class TestYAMLConfigReader:
    def test_read_single_line(self, tmp_path):
        """Should contain key name in result"""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development
        """
        )

        reader = readers.YAMLTemplateReader(path)
        template = reader.read()
        assert "ENVIRONMENT_NAME" in template["environment"]

    def test_read_multi_line(self, tmp_path):
        """Should ignore whitespace and contain both key names in the result"""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2.0
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development
          DATABASE_URL: sqlite:///simple.db
        """
        )

        reader = readers.YAMLTemplateReader(path)
        template = reader.read()
        assert "ENVIRONMENT_NAME" in template["environment"]
        assert "DATABASE_URL" in template["environment"]

    def test_read_single_line_with_comment(self, tmp_path):
        """Should not trip up on comments in file contents"""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2.0
        project:
          name: test

        environment:
          ENVIRONMENT_NAME: development  # this is not part of the value
        """
        )

        reader = readers.YAMLTemplateReader(path)
        template = reader.read()
        assert "ENVIRONMENT_NAME" in template["environment"]
        assert template["environment"]["ENVIRONMENT_NAME"].preset == "development"

    def test_read_multi_line_with_comment(self, tmp_path):
        """Should not clobber with commented values"""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2.0
        environment:
          ENVIRONMENT_NAME: development
          # ENVIRONMENT_NAME: not-development
        """
        )

        reader = readers.YAMLTemplateReader(path)
        template = reader.read()["environment"]
        assert "ENVIRONMENT_NAME" in template
        assert template["ENVIRONMENT_NAME"].preset == "development"

    def test_find_git_commit(self, tmp_path):
        """Should detect and use git commit hash generator instead of regular environment variable."""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2.0
        environment:
          COMMIT: "@@GIT_COMMIT:7@@"
        """
        )
        reader = readers.YAMLTemplateReader(path)
        template = reader.read()["environment"]
        assert "COMMIT" in template
        assert template["COMMIT"] == GitCommitVariable("COMMIT", "7")

    def test_find_git_commit__malformed_variable(self, tmp_path):
        """Should not detect git commit variable when malformed."""
        path = tmp_path / "env-template.yml"
        path.write_text(
            """
        schema-version: 2.0
        environment:
          COMMIT: "@@GIT_COMMIT:7"
        """
        )
        reader = readers.YAMLTemplateReader(path)
        template = reader.read()["environment"]
        assert "COMMIT" in template
        assert not isinstance(template["COMMIT"], GitCommitVariable)
