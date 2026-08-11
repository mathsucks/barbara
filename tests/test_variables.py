import subprocess
from unittest import mock

import pytest

from barbara.variables import GitCommitVariable


@pytest.fixture(name="patched_subprocess_output")
def patch_subprocess_output():
    with mock.patch("barbara.variables.subprocess.check_output") as patched_subprocess_output:
        yield patched_subprocess_output


class TestGitCommitVariable:
    def test_generate(self, patched_subprocess_output):
        """Should truncate the commit hash to the requested length."""
        patched_subprocess_output.return_value = "1234567890abcdef"
        assert GitCommitVariable("COMMIT", 7).generate() == "1234567"

    def test_generate_outside_repository(self, patched_subprocess_output):
        """Should fall back to UNKNOWN when the working directory is not a repository."""
        patched_subprocess_output.side_effect = subprocess.CalledProcessError(128, "git")
        assert GitCommitVariable("COMMIT", 7).generate() == "UNKNOWN"

    def test_generate_without_git_installed(self, patched_subprocess_output):
        """Should fall back to UNKNOWN when the git binary is unavailable."""
        patched_subprocess_output.side_effect = FileNotFoundError(2, "No such file or directory: 'git'")
        assert GitCommitVariable("COMMIT", 7).generate() == "UNKNOWN"
