from unittest import mock

import pytest
from barbara import utils
from barbara.variables import EnvVariable, GitCommitVariable


@pytest.fixture(name="template")
def create_stub_template():
    template = {
        "A": EnvVariable("A", "existing-value-a"),
        "B": EnvVariable("B", "existing-value-b"),
        "C": EnvVariable("C", "existing-value-c"),
    }
    return template


@pytest.fixture(name="auto_var_template")
def create_stub_template_with_auto_variables():
    template = {
        "A": EnvVariable("A", "existing-value-a"),
        "B": EnvVariable("B", "existing-value-b"),
        "C": EnvVariable("C", "existing-value-c"),
        "D": GitCommitVariable("D", 7),
    }
    return template


@mock.patch("barbara.utils.click")
@mock.patch("barbara.utils.create_target_file")
def test_confirm_target_default_create_confirmed(patched_create_target, patched_click, tmp_path):
    """Should match confirmation of creation of default target file"""
    patched_click.confirm.return_value = True
    assert utils.confirm_target_file(tmp_path / "missing.env")

    patched_create_target.assert_called_once_with(tmp_path / "missing.env")


@mock.patch("barbara.utils.click")
@mock.patch("barbara.utils.create_target_file")
def test_confirm_target_default_create_rejected(patched_create_target, patched_click, tmp_path):
    """Should match rejection of creating default target file"""
    patched_click.confirm.return_value = False

    with pytest.raises(SystemExit, match=r"1"):
        assert utils.confirm_target_file(tmp_path / "missing.env")

    patched_create_target.assert_not_called()


@mock.patch("barbara.utils.click")
def test_confirm_target_provided_confirmed(patched_click, tmp_path):
    """Should match confirmation of provided target file when file exists"""
    patched_click.prompt.return_value = True

    target_file = tmp_path / "exists.env"
    assert not target_file.exists()
    assert utils.confirm_target_file(target_file)
    assert target_file.exists()


@mock.patch("barbara.utils.click")
@mock.patch("barbara.utils.create_target_file")
def test_confirm_target_provided_rejected(patched_create_target, patched_click, tmp_path):
    """Should match rejection of provided target file when file exists"""
    patched_click.confirm.return_value = False

    target_file = tmp_path / "exists.env"
    assert not target_file.exists()
    with pytest.raises(SystemExit, match=r"1"):
        utils.confirm_target_file(target_file)
    patched_create_target.assert_not_called()


def test_merge_with_presets_matching_with_skip(template):
    """Should merge two ordered dictionaries with matching keys and use existing and presets for any keys"""
    existing = {"A": "existing-value-a", "B": "existing-value-b"}
    merged = utils.merge_with_presets(existing, template, skip_existing=True)
    assert merged["A"] == "existing-value-a"
    assert merged["B"] == "existing-value-b"
    assert merged["C"] == "existing-value-c"


def test_merge_with_presets_matching_without_skip(template):
    """Should merge two ordered dictionaries with matching keys and only presets for any keys"""
    existing = {"A": "existing-value-a", "B": "existing-value-b"}
    merged = utils.merge_with_presets(existing, template, skip_existing=False)
    assert merged["A"] == "existing-value-a"
    assert merged["B"] == "existing-value-b"
    assert merged["C"] == "existing-value-c"


@mock.patch("barbara.utils.prompt_user_for_value", return_value="new-value")
def test_merge_with_prompts_matching_with_skip(patched_get, template):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = {"A": "existing-value-a", "B": "existing-value-b"}
    merged = utils.merge_with_prompts(existing, template, skip_existing=True)
    patched_get.assert_called_once_with(EnvVariable("C", "existing-value-c"))
    assert merged["A"] == "existing-value-a"
    assert merged["B"] == "existing-value-b"
    assert merged["C"] == "new-value"


@mock.patch("barbara.utils.prompt_user_for_value", side_effect=["new-value-a", "new-value-b", "new-value-c"])
def test_merge_with_prompts_matching_without_skip(patched_get, template):
    """Should merge two ordered dictionaries with matching keys and not prompt for any keys"""
    existing = {"A": "existing-value-a", "B": "existing-value-b"}
    merged = utils.merge_with_prompts(existing, template, skip_existing=False)
    assert merged["A"] == "new-value-a"
    assert merged["B"] == "new-value-b"
    assert merged["C"] == "new-value-c"


@mock.patch("barbara.utils.click")
def test_prompt_user_for_value(patched_click):
    """Should request user response for key, and suggest default if provided"""
    patched_click.prompt.return_value = "user-response"
    result = utils.prompt_user_for_value(EnvVariable("test-key", "test-default"))
    assert result == "user-response"
    patched_click.prompt.assert_called_once_with("test-key", default="test-default", type=str)
