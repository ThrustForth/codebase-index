import pytest
import sys
from typing import Optional, List

def run_pytest_with_coverage(test_dirs: Optional[List[str]] = None) -> int:
    """
    Runs pytest with coverage reporting.

    Args:
        test_dirs: List of test directories (default: current directory)

    Returns:
        pytest exit code (0=success, non-zero=failure)
    """
    try:
        args = ["pytest"]
        if test_dirs:
            args.extend(test_dirs)
        # Add coverage arguments if plugin installed
        if pytest.__version__ >= '7.0':
            args.extend(["--cov", "."])
        return pytest.main(args)
    except pytest.PytestUsageError as e:
        print(f"Usage error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Test execution failed: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    import sys
    dirs = sys.argv[1:] if len(sys.argv) > 1 else None
    sys.exit(run_pytest_with_coverage(dirs))