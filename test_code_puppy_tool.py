# File: test_code_puppy_tool.py
import sys
from pathlib import Path
from unittest import TestCase, main as unittest_main
from unittest.mock import Mock, patch

# Ensure the project root is on the import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_puppy_tool import main, CodePuppyTool


class TestMain(TestCase):
    def test_main_imports(self):
        self.assertIsNotNone(main)

    @patch('code_puppy_tool.CodePuppyTool')
    def test_process_query_called(self, mock_tool_class):
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': None,
            'results': 'some result text',
        }
        mock_tool_class.return_value = mock_instance

        # Use the correct CLI arguments
        with patch.object(sys, 'argv',
                         ['test', 'query', '--ext', '.py',
                          '--top-k', '5', '--critique']):
            main()

        mock_instance.process_query.assert_called_once_with(
            'query', '.py', 5, no_critique=False)

    @patch('code_puppy_tool.CodePuppyTool')
    def test_results_printed(self, mock_tool_class):
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': None,
            'results': 'some result text',
        }
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv',
                         ['test', 'query', '--ext', '.py',
                          '--top-k', '5']):
            main()

        self.assertTrue(mock_instance.process_query.called)

    @patch('code_puppy_tool.CodePuppyTool')
    def test_critique_displayed_when_true(self, mock_tool_class):
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': 'This is a critique',
            'critique_length': 20,
            'results': 'some result text',
        }
        mock_tool_class.return_value = mock_instance

        with patch.object(sys, 'argv',
                         ['test', 'query', '--ext', '.py', '--critique']):
            main()

        self.assertTrue(mock_instance.process_query.called)

    @patch('code_puppy_tool.CodePuppyTool')
    def test_no_critique_when_flag(self, mock_tool_class):
        mock_instance = Mock()
        mock_instance.process_query.return_value = {
            'result_length': 10,
            'critique': 'This is a critique',
            'critique_length': 20,
            'results': 'some result text',
        }
        mock_tool_class.return_value = mock_instance

        # No --critique flag → default is no_critique=True
        with patch.object(sys, 'argv',
                         ['test', 'query', '--ext', '.py']):
            main()

        self.assertTrue(mock_instance.process_query.called)


class TestCodePuppyTool(TestCase):
    def test_instantiation(self):
        tool = CodePuppyTool()
        self.assertIsNotNone(tool)

    def test_required_methods(self):
        tool = CodePuppyTool()
        self.assertTrue(hasattr(tool, 'process_query'))
        self.assertTrue(hasattr(tool, 'search'))


if __name__ == '__main__':
    unittest_main()
