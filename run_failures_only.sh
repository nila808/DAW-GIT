#!/bin/bash

# Run the full test suite and save the output
./run_tests.sh | tee test_output.log

# Extract from the first failure block to the end
awk '/=+ FAILURES =+/,0' test_output.log | pbcopy

echo "✅ Copied failure block (to end) to clipboard."
