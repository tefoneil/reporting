#!/usr/bin/env python3
"""
Monthly Reporting CLI
Command-line interface for chronic circuit monthly reporting
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from monthly_builder import ChronicReportBuilder


def setup_logging(debug=False):
    """Set up logging configuration"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Log to file
    logging.basicConfig(
        filename='monthly_reporting.log',
        level=log_level,
        format=log_format,
        filemode='a'
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(log_level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def validate_files(impacts_file, counts_file):
    """Validate input files exist and are readable"""
    impacts_path = Path(impacts_file)
    counts_path = Path(counts_file)
    
    if not impacts_path.exists():
        raise FileNotFoundError(f"Impacts file not found: {impacts_file}")
    
    if not counts_path.exists():
        raise FileNotFoundError(f"Counts file not found: {counts_file}")
    
    # Check file extensions
    valid_extensions = {'.xlsx', '.csv', '.xls'}
    if impacts_path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Impacts file must be Excel or CSV format: {impacts_file}")
    
    if counts_path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Counts file must be Excel or CSV format: {counts_file}")
    
    return impacts_path, counts_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate monthly chronic circuit reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --impacts impacts.xlsx --counts counts.xlsx --output reports/
  %(prog)s --impacts data.csv --counts data.csv --exclude-regional --debug
  %(prog)s --impacts impacts.xlsx --counts counts.xlsx --month "June 2025"
        """
    )
    
    # Required arguments
    parser.add_argument('--impacts', required=True, 
                       help='Path to impacts crosstab Excel/CSV file')
    parser.add_argument('--counts', required=True,
                       help='Path to counts Excel/CSV file')
    
    # Optional arguments
    parser.add_argument('--output', default='./output',
                       help='Output directory (default: ./output)')
    parser.add_argument('--exclude-regional', action='store_true',
                       help='Exclude regional circuits from new chronic detection')
    parser.add_argument('--show-indicators', action='store_true', default=True,
                       help='Show (C) chronic and (R) regional flags in reports (default: True)')
    parser.add_argument('--no-indicators', dest='show_indicators', action='store_false',
                       help='Hide (C) and (R) indicators in reports')
    parser.add_argument('--month', 
                       help='Report month (e.g., "May 2025") - for display purposes')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging and verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate inputs and show what would be generated without creating files')
    parser.add_argument('--quiet', action='store_true',
                       help='Suppress progress bars and reduce output')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        if not args.quiet:
            print(f"Monthly Reporting CLI v0.1.0")
            print(f"Starting report generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validate input files
        if not args.quiet:
            print("Validating input files...")
        impacts_path, counts_path = validate_files(args.impacts, args.counts)
        logger.info(f"Validated input files: {impacts_path}, {counts_path}")
        
        # Create output directory
        output_dir = Path(args.output)
        if args.dry_run:
            print(f"[DRY RUN] Would create output directory: {output_dir}")
        else:
            output_dir.mkdir(exist_ok=True, parents=True)
            logger.info(f"Created output directory: {output_dir}")
        
        # Initialize report builder
        builder = ChronicReportBuilder(
            exclude_regional=args.exclude_regional,
            show_indicators=args.show_indicators
        )
        
        if args.dry_run:
            print(f"[DRY RUN] Configuration:")
            print(f"  - Exclude regional: {args.exclude_regional}")
            print(f"  - Show indicators: {args.show_indicators}")
            print(f"  - Output directory: {output_dir}")
            print(f"[DRY RUN] Would process files and generate reports")
            return
        
        # Create progress bar context
        progress_context = tqdm.write if not args.quiet else lambda x: None
        
        with tqdm(total=6, desc="Building report", disable=args.quiet) as pbar:
            # Step 1: Load data
            progress_context("Loading and processing data files...")
            impacts_df, counts_df = builder.load_crosstab_data(impacts_path, counts_path)
            pbar.update(1)
            
            # Step 2: Process chronic logic
            progress_context("Processing chronic circuit logic...")
            chronic_data = builder.process_chronic_logic(impacts_df, counts_df)
            pbar.update(1)
            
            # Step 3: Calculate metrics
            progress_context("Calculating performance metrics...")
            metrics = builder.calculate_metrics(chronic_data)
            pbar.update(1)
            
            # Step 4: Generate charts
            progress_context("Generating performance charts...")
            charts = builder.generate_charts(metrics, output_dir / 'charts')
            pbar.update(1)
            
            # Step 5: Generate reports
            progress_context("Generating Word documents...")
            report_outputs = builder.build_monthly_report(
                impacts_path, counts_path, None, output_dir
            )
            pbar.update(1)
            
            # Step 6: Generate text summary
            progress_context("Generating text summary...")
            month_str = args.month.replace(' ', '_') if args.month else datetime.now().strftime("%B_%Y")
            text_summary = builder.generate_text_summary(chronic_data, metrics, output_dir, month_str)
            pbar.update(1)
        
        # Report results
        if not args.quiet:
            print(f"\n✅ Report generation completed successfully!")
            print(f"📁 Output directory: {output_dir}")
            print(f"📊 Found {chronic_data['total_chronic_circuits']} existing chronic circuits")
            print(f"🆕 Identified {chronic_data['new_chronic_count']} new chronic circuits")
            
            print(f"\n📄 Generated files:")
            for file_path in output_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix in {'.docx', '.png', '.txt', '.json', '.pdf'}:
                    print(f"  - {file_path.relative_to(output_dir)}")
        
        logger.info("Report generation completed successfully")
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {e}"
        if args.debug:
            logger.exception(error_msg)
        else:
            logger.error(error_msg)
        print(f"❌ Error: {error_msg}")
        print("💡 Tip: Check that file paths are correct and files exist")
        sys.exit(1)
        
    except ValueError as e:
        error_msg = f"Invalid input: {e}"
        if args.debug:
            logger.exception(error_msg)
        else:
            logger.error(error_msg)
        print(f"❌ Error: {error_msg}")
        sys.exit(2)
        
    except Exception as e:
        error_msg = f"Processing error: {e}"
        if args.debug:
            logger.exception(error_msg)
            import traceback
            traceback.print_exc()
        else:
            logger.error(error_msg)
        print(f"❌ Error: {error_msg}")
        print("💡 Tip: Use --debug flag for detailed error information")
        sys.exit(2)


if __name__ == "__main__":
    main()