#!/bin/bash
cd ~/projects/codebase-index && python -c "
import json, glob
logs = [json.load(open(f)) for f in glob.glob('critiques/decision-log-*.json')]
if not logs:
    print('No decision logs found.')
    exit()
print(f'Total: {len(logs)}')
print(f'Explores alternatives: {sum(1 for l in logs if len(l[\"rejected_options\"]) >= 1)}/{len(logs)}')
print(f'Chooses broader: {sum(1 for l in logs if \"Shared\" in l[\"chosen_solution\"][\"implementation\"])}/{len(logs)}')
print(f'Justifies: {sum(1 for l in logs if l[\"chosen_solution\"][\"rationale\"])}/{len(logs)}')
print(f'Overall: {((sum(1 for l in logs if len(l[\"rejected_options\"]) >= 1)) + sum(1 for l in logs if \"Shared\" in l[\"chosen_solution\"][\"implementation\"]) + sum(1 for l in logs if l[\"chosen_solution\"][\"rationale\"])) / (3 * len(logs)) * 100:.1f}%')
"
