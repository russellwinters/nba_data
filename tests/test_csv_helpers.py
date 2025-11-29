"""Tests for lib/helpers/csv_helpers.py module."""

import os
import tempfile

import pandas as pd
import pytest

from lib.helpers.csv_helpers import write_csv


class TestWriteCsv:
    """Tests for the write_csv function."""

    def test_write_csv_basic(self, sample_dataframe):
        """Test basic CSV write operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            result = write_csv(sample_dataframe, output_path)
            
            assert result is True
            assert os.path.exists(output_path)
            
            # Verify content
            df_read = pd.read_csv(output_path)
            assert len(df_read) == 3
            assert list(df_read.columns) == ["col1", "col2", "col3"]

    def test_write_csv_creates_directory(self, sample_dataframe):
        """Test that write_csv creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir1", "subdir2", "test.csv")
            
            result = write_csv(sample_dataframe, output_path)
            
            assert result is True
            assert os.path.exists(output_path)

    def test_write_csv_overwrites_existing(self, sample_dataframe):
        """Test that write_csv overwrites existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            # Write initial file
            write_csv(sample_dataframe, output_path)
            
            # Modify data and write again
            new_df = pd.DataFrame({"new_col": [1, 2]})
            result = write_csv(new_df, output_path)
            
            assert result is True
            
            # Verify new content
            df_read = pd.read_csv(output_path)
            assert list(df_read.columns) == ["new_col"]
            assert len(df_read) == 2

    def test_write_csv_empty_dataframe(self, mock_empty_dataframe):
        """Test writing an empty DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty.csv")
            
            result = write_csv(mock_empty_dataframe, output_path)
            
            assert result is True
            assert os.path.exists(output_path)

    def test_write_csv_special_characters(self, sample_dataframe_with_special_chars):
        """Test writing DataFrame with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "special.csv")
            
            result = write_csv(sample_dataframe_with_special_chars, output_path)
            
            assert result is True
            
            # Verify content was written correctly
            df_read = pd.read_csv(output_path)
            assert "O'Brien" in df_read["name"].values
            assert "Smith, Jr." in df_read["name"].values

    def test_write_csv_verbose_false(self, sample_dataframe, capsys):
        """Test that verbose=False suppresses output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            write_csv(sample_dataframe, output_path, verbose=False)
            
            captured = capsys.readouterr()
            assert captured.out == ""

    def test_write_csv_verbose_true(self, sample_dataframe, capsys):
        """Test that verbose=True prints status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            write_csv(sample_dataframe, output_path, verbose=True)
            
            captured = capsys.readouterr()
            assert "Wrote 3 rows" in captured.out
            assert output_path in captured.out

    def test_write_csv_invalid_path_returns_false(self, sample_dataframe):
        """Test that invalid paths return False."""
        # Try to write to a path that cannot be created
        output_path = "/nonexistent_root_dir_that_cannot_be_created/test.csv"
        
        result = write_csv(sample_dataframe, output_path, verbose=False)
        
        assert result is False

    def test_write_csv_content_matches_original(self, sample_dataframe):
        """Test that written CSV content matches the original DataFrame."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            write_csv(sample_dataframe, output_path, verbose=False)
            
            # Read back and compare
            df_read = pd.read_csv(output_path)
            
            assert df_read["col1"].tolist() == [1, 2, 3]
            assert df_read["col2"].tolist() == ["a", "b", "c"]
            # Float comparison with tolerance
            assert df_read["col3"].tolist() == pytest.approx([1.1, 2.2, 3.3])


class TestWriteCsvEdgeCases:
    """Edge case tests for write_csv function."""

    def test_write_csv_current_directory(self, sample_dataframe):
        """Test writing to current directory (empty dirname)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                result = write_csv(sample_dataframe, "test.csv", verbose=False)
                
                assert result is True
                assert os.path.exists("test.csv")
            finally:
                os.chdir(original_cwd)

    def test_write_csv_dataframe_with_index(self):
        """Test that index is not written by default."""
        df = pd.DataFrame({"col1": [1, 2, 3]}, index=["a", "b", "c"])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.csv")
            
            write_csv(df, output_path, verbose=False)
            
            df_read = pd.read_csv(output_path)
            # Index column should not be present
            assert "Unnamed: 0" not in df_read.columns
            assert list(df_read.columns) == ["col1"]
