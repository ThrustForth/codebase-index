#!/usr/bin/env python3
"""
Security Pattern Search Tool
Dedicated tool for finding security vulnerabilities like SQL injection, XSS, etc.
"""

import re
import json
from typing import List, Dict
from pathlib import Path
import subprocess

DB_PATH = "/home/mine/projects/codebase-index/db"

# Security patterns to detect
SECURITY_PATTERNS = {
    "sql_injection": [
        r"(execute|executemany|raw|cursor)\s*\(\s*['\"].*%s|['\"].*\+|['\"].*format|['\"].*f['\"]",
        r"\.execute\s*\(\s*f['\"].*\{",
        r"SELECT\s+.*\s+FROM\s+.*\+",
        r"INSERT\s+INTO\s+.*\+",
        r"UPDATE\s+.*\s+SET\s+.*\+",
        r"DELETE\s+FROM\s+.*\+",
    ],
    "xss": [
        r"render_template_string\s*\(\s*f['\"]",
        r"innerHTML\s*=\s*[^;]+;",
        r"document\.write\s*\(",
        r"\.html\s*\(\s*[^;]+;\s*\+\s*",
    ],
    "hardcoded_secrets": [
        r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
        r"aws_access_key|aws_secret_key",
        r"private_key\s*=\s*['\"]",
    ],
    "command_injection": [
        r"os\.system\s*\(\s*[^;]+;",
        r"subprocess\.(call|run|Popen)\s*\(\s*[^;]*\+",
        r"eval\s*\(\s*[^;]+;",
        r"exec\s*\(\s*[^;]+;",
    ],
    "insecure_random": [
        r"random\.random\s*\(",
        r"random\.randint\s*\(",
        r"random\.choice\s*\(",
    ],
    "missing_validation": [
        r"request\.(args|form|json)\s*[^;]*[^valid]",
        r"request\.data\s*[^;]*[^valid]",
    ]
}

def search_security_patterns(query: str = "", extent: int = 5) -> Dict:
    """
    Search for security vulnerability patterns in codebase.
    
    Args:
        query: Optional filter term
        extent: Number of results per category
        
    Returns:
        Dict with found patterns and risk assessment
    """
    findings = {}
    
    # Get all Python files
    project_root = Path.cwd()
    while project_root != project_root.parent and not (project_root / '.git').is_dir():
        project_root = project_root.parent
    
    # Search each pattern category
    for category, patterns in SECURITY_PATTERNS.items():
        results = []
        for pattern in patterns:
            # Use grep for pattern matching
            cmd = f"grep -rn --include='*.py' -E '{pattern}' {project_root}"
            try:
                output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if output.returncode == 0 and output.stdout.strip():
                    lines = output.stdout.strip().split('\n')[:extent]
                    results.extend(lines)
            except subprocess.TimeoutExpired:
                continue
        
        if results:
            findings[category] = {
                "matches": results,
                "risk_level": "HIGH" if category in ["sql_injection", "command_injection"] else "MEDIUM"
            }
    
    return {
        "query": query,
        "total_findings": sum(len(v["matches"]) for v in findings.values()),
        "findings": findings,
        "recommendations": _generate_recommendations(findings)
    }

def _generate_recommendations(findings: Dict) -> List[str]:
    """Generate security recommendations based on findings."""
    recommendations = []
    
    if "sql_injection" in findings:
        recommendations.append(
            "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
        )
    
    if "xss" in findings:
        recommendations.append(
            "Use auto-escaping templates and sanitize all user input before rendering"
        )
    
    if "hardcoded_secrets" in findings:
        recommendations.append(
            "Move secrets to environment variables or secret management service"
        )
    
    if "command_injection" in findings:
        recommendations.append(
            "Avoid shell commands with user input; use subprocess with shell=False and list args"
        )
    
    if "missing_validation" in findings:
        recommendations.append(
            "Implement input validation and type checking for all request parameters"
        )
    
    return recommendations

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Security Pattern Search Tool")
    parser.add_argument("--query", default="", help="Additional filter term")
    parser.add_argument("--extent", type=int, default=5, help="Results per category")
    args = parser.parse_args()
    
    results = search_security_patterns(args.query, args.extent)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()