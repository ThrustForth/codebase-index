#!/usr/bin/env python3

"""
Untested Code Finder

Identifies code with insufficient test coverage using multiple detection methods.
"""

from typing import List, Dict, Optional, Any
import json
import re
import os
from pathlib import Path


class CodeCoverageError(Exception):
    """Base exception for coverage-related errors."""
    pass


class UntestedCodeFinder:
    """
    Find code without sufficient test coverage.

    Args:
        source_dir: Directory containing source code
        test_dir: Optional directory containing tests
        coverage_report: Optional path to JSON coverage report
    """
    
    def __init__(self, source_dir: str, test_dir: Optional[str] = None, coverage_report: Optional[Path] = None):
        """
        Initialize with source directory, optional test directory, and optional coverage data
        """
        self.source_dir = Path(source_dir).resolve()
        self.test_dir = Path(test_dir).resolve() if test_dir else None
        self.coverage_report = coverage_report

    def find_untested_code(self) -> Dict[str, Any]:
        """
        Return dictionary containing untested code locations
        
        Returns:
            {
                "untested_files": List[str],
                "untested_functions": List[Dict[str, str]],  # [{"file": ","function": ""}]
                "method": str  # "heuristic" or "coverage_data"
            }"
        """
        results = {
            "untested_files": [],
            "untested_functions": [],
            "method": "heuristic"
        }
        
        if self.coverage_report and self.coverage_report.exists():
            try:
                coverage_data = self._parse_coverage_report(self.coverage_report)
                results = self._analyze_coverage_data(coverage_data)
                results["method"] = "coverage_data"
            except Exception as e:
                raise CodeCoverageError(f"Failed to analyze coverage report: {e}")
        else:
            results = self._analyze_heuristic(source_dir=self.source_dir, test_dir=self.test_dir)
        
        return results
    
    def _parse_coverage_report(self, report_path: Path) -> Dict[str, Any]: # type: ignore
        """
        Parse pytest coverage JSON report
        """
        with open(report_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise CodeCoverageError(f"Invalid coverage JSON: {e}")
    
    def _analyze_coverage_data(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze coverage data to find uncovered functions
        """
        results = {
            "untested_files": [],
            "untested_functions": []
        }
        
        if "results" in coverage_data:
            for result in coverage_data["results"]:
                coverage_pct = result.get("coverage", {}).get("percent", 0)
                if coverage_pct < 100:  # Consider partial coverage insufficient
                    file_path = result.get("filename", "unknown")
                    function_name = result.get("name", "unknown")
                    if file_path and function_name:
                        results["untested_functions"].append({
                            "file": file_path,
                            "function": function_name
                        })
        
        return results
    
    def _analyze_heuristic(self, source_dir: Path, test_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Heuristic analysis for missing test files
        """
        results = {
            "untested_files": [],
            "untested_functions": []
        }
        
        if test_dir and not test_dir.exists():
            raise CodeCoverageError(f"Test directory not found: {test_dir}")
        
        source_files = list(source_dir.rglob("*"))
        for file in source_files:
            if file.suffix.lower() == ".py" and not file.name.startswith("__"):  # Skip dunder files
                test_file = self._find_corresponding_test(file, test_dir)
                if not test_file:
                    results["untested_files"].append(str(file))
        
        return results
    
    def _find_corresponding_test(self, source_file: Path, test_dir: Path) -> Optional[Path]:
        """
        Find matching test file for a source file
        """
        base_name = os.path.splitext(source_file.name)[0]
        test_patterns = [
            f"test_{base_name}.py",
            f"{base_name}_test.py",
            f"test_{os.path.splitext(base_name)[0]}.py"
        ]
        for pattern in test_patterns:
            test_path = test_dir / pattern
            if test_path.exists() and test_path.is_file():
                return test_path
        return None


def main() -> None:
    import argparse, sys
    parser = argparse.ArgumentParser(description="Find untested code in a project")
    parser.add_argument("--source", required=True, help="Source directory containing code")
    parser.add_argument("--test_dir", help="Optional directory containing tests")
    parser.add_argument("--coverage_report", help="Path to JSON coverage report")
    args = parser.parse_args()
    
    finder = UntestedCodeFinder(args.source, Path(args.coverage_report) if args.coverage_report else None)
    try:
        results = finder.find_untested_code()
        print(json.dumps(results, indent=2))
    except CodeCoverageError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()