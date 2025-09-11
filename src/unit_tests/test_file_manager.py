import os
import json
import pytest
from unittest.mock import patch
from ..utils.file_manager import FilesMngr


@pytest.fixture
def file_manager():
    return FilesMngr()


# ---------------------------
# Tests for is_pass_exist
# ---------------------------
class TestIsPassExist:
    def test_existing_path(self, file_manager, tmp_path):
        """
        Should pass when the file exists
        """
        path = tmp_path / "file.txt"
        path.write_text("content")
        assert file_manager.is_pass_exist(str(path)) is None

    def test_invalid_path(self, file_manager):
        """
        Should raise ValueError when the path does not exist
        """
        path = "/non/existent/path"
        with pytest.raises(ValueError, match="does not exist"):
            file_manager.is_pass_exist(path)


# ---------------------------
# Tests for isTestingFile
# ---------------------------
class TestIsTestingFile:
    def test_correct_extension(self, file_manager, tmp_path):
        """
        Test that isTestingFile returns True for a valid file with the correct extension.
        """
        test_file = tmp_path / "test.py"
        test_file.touch()
        assert file_manager.isTestingFile(str(test_file), "py") is True

    def test_incorrect_extension(self, file_manager, tmp_path):
        """
        Test that isTestingFile raises ValueError for a file with an incorrect extension.
        """
        test_file = tmp_path / "test.txt"
        test_file.touch()
        with pytest.raises(ValueError, match="is not a .py file"):
            file_manager.isTestingFile(str(test_file), "py")

    def test_path_is_directory(self, file_manager, tmp_path):
        """
        Should raise ValueError when the path is a directory instead of a file
        """
        with pytest.raises(ValueError, match="is not a .py file"):
            file_manager.isTestingFile(str(tmp_path), "py")


# ---------------------------
# Tests for compare
# ---------------------------
class TestCompare:
    def test_identical_files(self, file_manager, tmp_path):
        """
        Test that compare returns no differences for identical files.
        Identical files should return an empty diff
        """
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same\ncontent\n")
        f2.write_text("same\ncontent\n")
        assert file_manager.compare(str(f1), str(f2)) == []

    def test_different_files(self, file_manager, tmp_path):
        """
        Test that compare returns differences for files with different content.
        Different files should show differences in diff output
        """
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("line1\n")
        f2.write_text("line2\n")
        diff = file_manager.compare(str(f1), str(f2))
        assert any("line1" in d or "line2" in d for d in diff)


class TestCompareEdgeCases:
    def test_empty_files(self, file_manager, tmp_path):
        """
        Test that compare returns no differences for empty files.
        Empty files should return an empty diff"""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("")
        f2.write_text("")
        assert file_manager.compare(str(f1), str(f2)) == []

    def test_one_file_missing(self, file_manager, tmp_path):
        """
        Test that compare raises FileNotFoundError if one file is missing.
        If one file is missing, it should raise an error
        """
        f1 = tmp_path / "exists.txt"
        f1.write_text("content")
        f2 = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError):
            file_manager.compare(str(f1), str(f2))


# ---------------------------
# Tests for compareAplanByPathes
# ---------------------------
class TestCompareAplanByPathes:
    def test_identical_files(self, file_manager, tmp_path, caplog):
        """
        Test that compareAplanByPathes returns no differences for identical files.
        Identical files should not log differences
        """
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "test.act").write_text("same\n")
        (dir2 / "test.act").write_text("same\n")

        result = file_manager.compareAplanByPathes(str(dir1), str(dir2), [".act"])
        assert result is False
        assert "are the same" in caplog.text

    def test_different_files(self, file_manager, tmp_path, caplog):
        """
        Test that compareAplanByPathes logs differences for files with different content.
        Different files in directories should return True (differences found)
        """
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "test.act").write_text("aaa\n")
        (dir2 / "test.act").write_text("bbb\n")

        result = file_manager.compareAplanByPathes(str(dir1), str(dir2), [".act"])
        assert result is True
        assert "differences" in caplog.text


# ---------------------------
# Tests for remove_directory
# ---------------------------
class TestRemoveDirectory:
    def test_existing_directory(self, file_manager, tmp_path, caplog):
        """
        Test that remove_directory removes an existing directory.
        Directory should be deleted if it exists
        """
        dir1 = tmp_path / "dir_to_remove"
        dir1.mkdir()
        file_manager.remove_directory(str(dir1))
        assert not dir1.exists()
        assert "has been removed" in caplog.text

    def test_missing_directory(self, file_manager, tmp_path, caplog):
        """
        Test that remove_directory does nothing for a non-existing directory.
        If the directory does not exist, it should log a warning
        """
        dir1 = tmp_path / "non_existing"
        file_manager.remove_directory(str(dir1))
        assert "does not exist" in caplog.text

    def test_path_is_file(self, file_manager, tmp_path, caplog):
        """
        Test that remove_directory raises an error if the path is a file.
        If the path is a file, it should log a warning and not delete anything
        """
        f = tmp_path / "not_a_dir.txt"
        f.write_text("content")
        file_manager.remove_directory(str(f))
        assert "does not exist" in caplog.text


# ---------------------------
# Tests for load_examples_from_json
# ---------------------------
class TestLoadExamplesFromJson:
    def test_valid_json(self, file_manager, tmp_path):
        """
        Test that load_examples_from_json loads a valid JSON file.
        Should return a list of dictionaries from a valid JSON file
        """
        data = [{"a": "1"}, {"b": "2"}]
        f = tmp_path / "examples.json"
        f.write_text(json.dumps(data))
        result = file_manager.load_examples_from_json(str(f))
        assert result == data

    def test_file_not_found(self, file_manager, tmp_path, caplog):
        """
        Test that load_examples_from_json returns an empty list for a non-existing file.
        If the file does not exist, it should log a warning and return an empty list"""
        f = tmp_path / "missing.json"
        result = file_manager.load_examples_from_json(str(f))
        assert result == []
        assert "not found" in caplog.text

    def test_invalid_type(self, file_manager, tmp_path):
        """
        Test that load_examples_from_json raises TypeError for invalid JSON format.
        If the JSON file does not contain a list, it should raise a TypeError
        """
        f = tmp_path / "invalid.json"
        f.write_text(json.dumps({"not": "a list"}))
        with pytest.raises(TypeError):
            file_manager.load_examples_from_json(str(f))

    def test_invalid_json_format(self, file_manager, tmp_path):
        """
        Test that load_examples_from_json raises JSONDecodeError for invalid JSON.
        If the JSON file is not valid, it should raise a JSONDecodeError
        """
        f = tmp_path / "broken.json"
        f.write_text("{not valid json")
        with pytest.raises(json.JSONDecodeError):
            file_manager.load_examples_from_json(str(f))

    def test_empty_json_list(self, file_manager, tmp_path):
        """
        Test that load_examples_from_json returns an empty list for an empty JSON array.
        If the JSON file is an empty list, it should return an empty list
        """
        f = tmp_path / "empty.json"
        f.write_text("[]")
        result = file_manager.load_examples_from_json(str(f))
        assert result == []

    def test_json_list_not_dicts(self, file_manager, tmp_path):
        """
        Test that load_examples_from_json accepts a list of non-dict items.
        If the JSON file contains a list of non-dict items, it should still return them
        """
        f = tmp_path / "not_dicts.json"
        f.write_text(json.dumps(["a", "b", "c"]))
        result = file_manager.load_examples_from_json(str(f))
        assert result == [
            "a",
            "b",
            "c",
        ]  # should pass, since only type(list) is checked


# ---------------------------
# Tests for replace_filename
# ---------------------------
class TestReplaceFilename:
    def test_basic_replacement(self, file_manager):
        """
        Test that replace_filename correctly replaces the filename in a path.
        Should return a new path with the updated filename
        """
        path = "/tmp/somefile.txt"
        new = file_manager.replace_filename(path, "new.txt")
        assert new == "/tmp/new.txt"

    def test_custom_path(self, file_manager):
        """
        Test that replace_filename works with a custom path and new filename.
        Should return a new path with the updated filename
        """
        path = "/path/to/old_file.txt"
        new_filename = "new_file.md"
        expected = "/path/to/new_file.md"
        assert file_manager.replace_filename(path, new_filename) == expected

    def test_no_directory_component(self, file_manager):
        """
        Test that replace_filename works when the path has no directory component.
        Should return the new filename directly
        """
        path = "file.txt"
        new = file_manager.replace_filename(path, "new.txt")
        assert new == "new.txt"
