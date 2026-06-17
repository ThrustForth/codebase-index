#!/usr/bin/env python3
import json, os, logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Configure debugging logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def categorize_event(task_type: str, critique: str, task_file: str) -> str:
    t = (task_type or '').lower()
    c = (critique or '').lower()
    f = (task_file or '').lower()
    if 'recent_change' in t:
        return 'recent_change'
    if 'error' in t or 'exception' in t or 'error' in f:
        return 'runtime_error'
    if 'ollama' in c or 'timeout' in c:
        return 'ollama_timeout'
    if 'monitoring' in c or 'monitoring' in t:
        return 'monitoring'
    if 'critique' in t or 'review' in t:
        return 'critique'
    return 'other'

PROJECT_PATH = Path('~/projects/codebase-index').expanduser()
CRITIQUES_DIR = PROJECT_PATH / 'critiques'
ERRORS_LOG = PROJECT_PATH / 'errors.log'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open('dashboard/index.html', 'r') as f:
                self.wfile.write(f.read().encode())
        elif self.path == '/events':
            # Initialize counters
            scanned_critique_files = 0
            parsed_events = 0
            skipped_files = 0
            error_log_lines_added = 0
            events = []

            # Scan critique files
            critique_files = list(CRITIQUES_DIR.glob('*.json'))
            scanned_critique_files = len(critique_files)
            logger.debug(f"Scanning {scanned_critique_files} critique files at {CRITIQUES_DIR}")

            for json_file in critique_files:
                try:
                    data = json.load(open(json_file))
                    parsed_events += 1
                    events.append({
                        'timestamp': data.get('timestamp') or datetime.fromtimestamp(
                            Path(data.get('task_file', '')).stat().st_mtime
                        ).isoformat(),
                        'file': data.get('task_file', ''),
                        'type': data.get('task_type', ''),
                        'category': categorize_event(data.get('task_type', ''), data.get('critique', ''), data.get('task_file', ''),),
                        'tag': categorize_event(data.get('task_type', ''), data.get('critique', ''), data.get('task_file', '')),
                        'snippet': data.get('critique', '')[:120].replace('\n', ' ') + '...',
                    })
                except Exception as e:
                    logger.debug(f"Skipped file {json_file}: {e}")
                    skipped_files += 1

            # Process error log lines
            if ERRORS_LOG.exists():
                with open(ERRORS_LOG, 'r') as f:
                    for line in f:
                        if 'Error detected:' in line:
                            ts = line.split('[')[1].split(']')[0]
                            events.append({
                                'timestamp': ts,
                                'file': 'errors.log',
                                'type': 'error',
                                'category': 'runtime_error',
                                'snippet': line.strip(),
                            })
                            error_log_lines_added += 1

            # Sort events newest first
            events.sort(key=lambda x: x['timestamp'], reverse=True)

            # Build diagnostic payload
            payload = {
                "meta": {
                    "scanned_critique_files": scanned_critique_files,
                    "parsed_events": parsed_events,
                    "skipped_files": skipped_files,
                    "error_log_lines_added": error_log_lines_added,
                    "total_events": len(events),
                },
                "events": events,
            }

            logger.debug(
                f"Payload built: meta={payload['meta']}, total_events={len(events)}"
            )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()