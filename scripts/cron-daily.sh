#!/bin/bash
# Daily cron job script for automated post generation
# Add to crontab: 0 8 * * * /path/to/project/scripts/cron-daily.sh
#
# This script:
# 1. Activates the virtual environment (if using one)
# 2. Generates a post
# 3. Logs output to a file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/$(date +%Y%m%d).log"

# Create logs directory
mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

# Optional: activate virtual environment
# source .venv/bin/activate

echo "========================================" >> "$LOG_FILE"
echo "Starting at $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Run the generator
stock-writer generate >> "$LOG_FILE" 2>&1

echo "Completed at $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
