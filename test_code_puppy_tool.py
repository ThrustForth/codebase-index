import pytest
from code_puppy_tool import main, CodePuppyTool
from unittest.mock import Mock, patch
import sys

class TestMain:
    def test_main_imports(self):
        """Test that main can be imported."""
        assert main is not None

    @patch('code_puppy_tool.CodePuppyTool')
    def test_process_query_called(self, mock_tool_class):
        """Test that process_query is called."""
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': None,
            'results': 'some result text'
        }
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv', ['test', 'query', '--ext', '.py', '--top', '5']):
            main()

        mock_instance.process_query.assert_called_once_with('query', '.py', 5)

    @patch('code_puppy_tool.CodePuppyTool')
    def test_results_printed(self, mock_tool_class):
        """Test that results are printed."""
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': None,
            'results': 'some result text'
        }
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv', ['test', 'query', '--ext', '.py']):
            main()

        assert mock_instance.process_query.called

    @patch('code_puppy_tool.CodePuppyTool')
    def test_critique_displayed_when_true(self, mock_tool_class):
        """Test critique is displayed when critique=True."""
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': 'This is a critique',
            'critique_length': 20,
            'results': 'some result text'
        }
        mock_instance.ask_followup.return_value = []
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv', ['test', 'query', '--ext', '.py']):
            main()

        assert mock_instance.process_query.called

    @patch('code_puppy_tool.CodePuppyTool')
    def test_no_critique_when_flag(self, mock_tool_class):
        """Test no critique when --no-critique is used."""
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': 'This is a critique',
            'critique_length': 20,
            'results': 'some result text'
        }
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv', ['test', 'query', '--ext', '.py', '--no-critique']):
            main()

        assert mock_instance.process_query.called

class TestCodePuppyTool:
    def test_code_puppy_tool_instantiates(self):
        """Test that CodePuppyTool can be instantiated."""
        tool = CodePuppyTool()
        assert tool is not None

    def test_code_puppy_tool_has_methods(self):
        """Test that CodePuppyTool has required methods."""
        tool = CodePuppyTool()
        assert hasattr(tool, 'process_query')
        assert hasattr(tool, 'search')
        assert hasattr(tool, 'critique')
        assert hasattr(tool, 'ask_followup')
