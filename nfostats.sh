#!/bin/sh

# Default to not logging
LOG_TO_FILE=0

# Parse command line arguments
while [ "$1" != "" ]; do
    case $1 in
        -l | --log )    LOG_TO_FILE=1
                        ;;
        * )             echo "Unknown option: $1"
                        exit 1
    esac
    shift
done

if [ "$LOG_TO_FILE" -eq 1 ]; then
    # Run silently with file logging
    nohup python3 -u NFOStats.py > NFOStats.out 2>&1 &
    echo "Process started in background. Check NFOStats.out for output."
else
    # Run on screen without logging
    echo "Running with console output (use --log or -l to log to file instead)"
    python3 -u NFOStats.py
fi
