#!/usr/bin/env bash

PROJECTS_DIR="$HOME/projects"

echo "Scanning for projects in: $PROJECTS_DIR"

# Build array of directories
dirs=()
i=1
declare -A dir_map

for d in "$PROJECTS_DIR"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    # Skip common non-project dirs
    case "$name" in
        .|..|Desktop|Documents|Downloads|Music|Pictures|Public|Templates|Videos|5|4|3|2|1) continue ;;
    esac
    dirs+=("$name")
    dir_map[$i]="$d"
    echo "$i. $name"
    ((i++))
done

echo "$i. Create a new project"
dirs+=("NEW")

read -p "Enter number: " choice

if [ "$choice" = "$i" ]; then
    read -p "New project name: " new_name
    if [ -z "$new_name" ]; then
        echo "Project name is required."
        exit 1
    fi
    mkdir -p "~/$new_name"
    cd "~/$new_name"

    # Launch Code Puppy with Brain AI intro
    echo ""
    echo "🧠💻 Code Puppy + Brain AI Auto-Integration Enabled"
    echo "===================================================="
    echo ""
    echo "Every prompt automatically uses Brain+OpenRouter coordination:"
    echo "  • OpenRouter generates fast (5s)"
    echo "  • Brain AI analyzes deeply (30-60s)"
    echo "  • Brain critiques → OpenRouter refines → Better code"
    echo ""
    echo "Usage in Code Puppy:"
    echo "  bp <your prompt>"
    echo ""
    echo "Examples:"
    echo "  bp ollama .py 3"
    echo "  bp 'add error handling to JSON parser'"
    echo "  bp 'how to implement caching' .rs 2"
    echo ""
    echo "===================================================="
    echo ""

    uvx code-puppy -i
else
    if [ -z "${dir_map[$choice]}" ]; then
        echo "Invalid choice"
        exit 1
    fi
    cd "${dir_map[$choice]}"

    # Auto-index if project has index_repo.py
    if [ -f "index_repo.py" ]; then
        echo "Indexing codebase with LanceDB+Ollama..."
        ./venv/bin/python index_repo.py --index
    fi

    # Launch Code Puppy with Brain AI intro
    echo ""
    echo "🧠💻 Code Puppy + Brain AI Auto-Integration Enabled"
    echo "===================================================="
    echo ""
    echo "Every prompt automatically uses Brain+OpenRouter coordination:"
    echo "  • OpenRouter generates fast (5s)"
    echo "  • Brain AI analyzes deeply (30-60s)"
    echo "  • Brain critiques → OpenRouter refines → Better code"
    echo ""
    echo "Usage in Code Puppy:"
    echo "  bp <your prompt>"
    echo ""
    echo "Examples:"
    echo "  bp ollama .py 3"
    echo "  bp 'add error handling to JSON parser'"
    echo "  bp 'how to implement caching' .rs 2"
    echo ""
    echo "===================================================="
    echo ""

    uvx code-puppy -i
fi
