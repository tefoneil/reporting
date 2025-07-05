#!/bin/bash
# Smoke test for monthly reporting CLI
# Tests basic functionality and verifies output generation

set -e  # Exit on any error

echo "🧪 Monthly Reporting Smoke Test"
echo "==============================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
TEST_OUTPUT="$SCRIPT_DIR/test_output"

# Clean up any previous test runs
if [ -d "$TEST_OUTPUT" ]; then
    echo "🧹 Cleaning up previous test output..."
    rm -rf "$TEST_OUTPUT"
fi

# Create test output directory
mkdir -p "$TEST_OUTPUT"

echo "📂 Test directory: $TEST_OUTPUT"
echo "📂 Repository root: $REPO_DIR"

# Change to repo directory for imports to work
cd "$REPO_DIR"

# Test 1: Check if sample data exists
echo ""
echo "📋 Test 1: Verifying sample data files..."
if [ ! -f "$SCRIPT_DIR/sample_impacts.xlsx" ]; then
    echo "❌ Sample impacts file not found. Creating..."
    cd "$SCRIPT_DIR"
    python create_sample_data.py
    cd "$REPO_DIR"
fi

if [ ! -f "$SCRIPT_DIR/sample_counts.xlsx" ]; then
    echo "❌ Sample counts file not found. Creating..."
    cd "$SCRIPT_DIR"
    python create_sample_data.py
    cd "$REPO_DIR"
fi

echo "✅ Sample data files verified"

# Test 2: CLI Help
echo ""
echo "📋 Test 2: Testing CLI help..."
python monthly_reporting_cli.py --help > "$TEST_OUTPUT/help_output.txt"
if [ $? -eq 0 ]; then
    echo "✅ CLI help works"
else
    echo "❌ CLI help failed"
    exit 1
fi

# Test 3: Dry run
echo ""
echo "📋 Test 3: Testing dry run..."
python monthly_reporting_cli.py \
    --impacts "$SCRIPT_DIR/sample_impacts.xlsx" \
    --counts "$SCRIPT_DIR/sample_counts.xlsx" \
    --output "$TEST_OUTPUT" \
    --dry-run \
    --quiet > "$TEST_OUTPUT/dry_run_output.txt"

if [ $? -eq 0 ]; then
    echo "✅ Dry run completed successfully"
else
    echo "❌ Dry run failed"
    exit 1
fi

# Test 4: Full report generation
echo ""
echo "📋 Test 4: Testing full report generation..."
python monthly_reporting_cli.py \
    --impacts "$SCRIPT_DIR/sample_impacts.xlsx" \
    --counts "$SCRIPT_DIR/sample_counts.xlsx" \
    --output "$TEST_OUTPUT" \
    --exclude-regional \
    --show-indicators \
    --month "Test_Run" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ Report generation completed"
else
    echo "❌ Report generation failed"
    exit 1
fi

# Test 5: Verify output files
echo ""
echo "📋 Test 5: Verifying output files..."

required_files=(
    "Chronic_Corner_Test_Run.docx"
    "Chronic_Circuit_Report_Test_Run.docx"
    "chronic_circuits_list_Test_Run.txt"
    "chronic_summary_Test_Run.json"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$TEST_OUTPUT/$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ All required output files generated"
else
    echo "❌ Missing output files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Test 6: Check for charts
echo ""
echo "📋 Test 6: Verifying chart generation..."
chart_count=$(find "$TEST_OUTPUT/charts" -name "*.png" 2>/dev/null | wc -l)
if [ "$chart_count" -gt 0 ]; then
    echo "✅ Charts generated ($chart_count PNG files)"
else
    echo "⚠️  No charts found (may be expected for small dataset)"
fi

# Test 7: File size checks
echo ""
echo "📋 Test 7: Checking output file sizes..."
for file in "${required_files[@]}"; do
    if [ -f "$TEST_OUTPUT/$file" ]; then
        size=$(wc -c < "$TEST_OUTPUT/$file")
        if [ "$size" -gt 0 ]; then
            echo "✅ $file: ${size} bytes"
        else
            echo "❌ $file: Empty file"
            exit 1
        fi
    fi
done

# Success summary
echo ""
echo "🎉 All smoke tests passed!"
echo "📊 Generated files:"
find "$TEST_OUTPUT" -type f -name "*.docx" -o -name "*.txt" -o -name "*.json" -o -name "*.png" | sort

echo ""
echo "🧪 Smoke test completed successfully"
echo "📁 Test output available in: $TEST_OUTPUT"