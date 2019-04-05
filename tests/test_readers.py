from unittest import mock

import pytest

import yaml
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


class TestEnvTemplateReader(TestEnvReader):
    reader = readers.EnvTemplateReader

    def assert_env_value(self, env, key, value):
        assert env[key].preset == value

    @pytest.mark.parametrize(
        "template,sub_name,sub_default",
        [
            ("[test]", "test", None),
            (r"\[[test]\]", "test", None),
            ("[test:tset]", "test", "tset"),
            ("[test:[tset:test]]", "tset", "test"),
            ("http://[username:user]:password@host.com/path", "username", "user"),
        ],
    )
    def test_subvariables(self, template, sub_name, sub_default):
        """Should parse subvariables within reason"""
        result = next(self.reader.find_subvariables(template))
        assert result[0] == sub_name
        assert result[1] == sub_default


class TestSSMReader:
    @mock.patch("barbara.readers.boto3")
    def test_read_from_ssm(self, patched_boto3):
        """Should retrieve deployment values from AWS SSM."""
        value_formatter = lambda value: {"Parameter": {"Value": value}}  # noqa
        patched_boto3.client().get_parameter.side_effect = [value_formatter("value"), value_formatter("pants")]

        r = readers.SSMReader(["/prefix/key", "/prefix/derp"])
        values = r.read()

        assert "key" in values
        assert "derp" in values
        assert values["key"] == "value"
        assert values["derp"] == "pants"


class TestYAMLConfigReader:
    def test_read_single_line(self, tmpdir):
        """Should contain key name in result"""
        p = tmpdir.join(".env.yml")
        p.write(
            """
        project: test

        environment:
          ENVIRONMENT_NAME: development
        """
        )

        r = readers.YAMLConfigReader(p)
        values = r.read()
        assert "ENVIRONMENT_NAME" in values

    def test_read_multi_line(self, tmpdir):
        """Should ignore whitespace and contain both key names in the result"""
        p = tmpdir.join(".env.yml")
        p.write(
            """
        project: test

        environment:
          ENVIRONMENT_NAME: development
          DATABASE_URL: sqlite:///simple.db
        """
        )

        r = readers.YAMLConfigReader(p)
        values = r.read()
        assert "ENVIRONMENT_NAME" in values
        assert "DATABASE_URL" in values

    def test_read_single_line_with_comment(self, tmpdir):
        """Should not trip up on comments in file contents"""
        p = tmpdir.join(".env.yml")
        p.write(
            """
        project: test

        environment:
          ENVIRONMENT_NAME: development  # this is not part of the value
        """
        )

        r = readers.YAMLConfigReader(p)
        env = r.read()
        assert "ENVIRONMENT_NAME" in env
        assert env["ENVIRONMENT_NAME"].preset == "development"

    def test_read_multi_line_with_comment(self, tmpdir):
        """Should not clobber with commented values"""
        p = tmpdir.join(".env.yml")
        p.write(
            """
        environment:
          ENVIRONMENT_NAME: development
          # ENVIRONMENT_NAME: not-development
        """
        )

        r = readers.YAMLConfigReader(p)
        env = r.read()
        assert "ENVIRONMENT_NAME" in env
        assert env["ENVIRONMENT_NAME"].preset == "development"

    def test_subvariables(self):
        """Should parse subvariables correctly"""
        p = yaml.load(
            """
        ENVIRONMENT_NAME:
          template: "{part1}-{part2}"
          subvariables:
            subvar1: subvalue1
            subvar2: subvalue2
        """,
            Loader=yaml.SafeLoader,
        )

        subvars = list(readers.YAMLConfigReader.find_subvariables(p["ENVIRONMENT_NAME"]))
        assert subvars[0].name == "subvar1"
        assert subvars[0].preset == "subvalue1"
        assert subvars[1].name == "subvar2"
        assert subvars[1].preset == "subvalue2"

    def test_key_list(self, tmpdir):
        """Should generate accurate key lists"""
        p = tmpdir.join(".env.yml")
        p.write(
            """
        project: test

        environment:
          DEBUG: 1
          ENVIRONMENT_NAME: development
          DATABASE_URL: sqlite:///simple.db
          NODE_NAME: localhost

        deployments:
          - DEBUG
          - sandbox:
            - ENVIRONMENT_NAME
            - DATABASE_URL
            - app_server:
              - NODE_NAME
            - worker:
              - NODE_NAME
              - DATABASE_URL
        """
        )
        r = readers.YAMLConfigReader(p)
        key_list = r.generate_key_list_for_resource("/test/sandbox/worker/")
        assert "/test/DEBUG" in key_list
        assert "/test/sandbox/ENVIRONMENT_NAME" in key_list
        assert "/test/sandbox/worker/NODE_NAME" in key_list
        assert "/test/sandbox/worker/DATABASE_URL" in key_list
        assert len(key_list) == 4
