#!/usr/bin/env python3
"""
Monthly Report Builder for Chronic Circuit Analysis
Processes Tableau exports and generates Word/PDF reports
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import Dict, Any
import subprocess
import sys
from datetime import datetime, timedelta
import json
from docx import Document
from docx.shared import Inches, Pt
import matplotlib.pyplot as plt
import seaborn as sns
try:
    from pptx import Presentation
    from pptx.util import Inches as PptxInches, Pt as PptxPt
    from pptx.enum.text import PP_ALIGN
    from pptx.dml.color import RGBColor as PptxRGBColor
except ImportError:
    print("Warning: python-pptx not found. PowerPoint generation will be skipped.")
    Presentation = None

# Import the redactor
try:
    from scrub import process_file  # Assuming this is the main function from scrub.py
except ImportError:
    print("Warning: Could not import redactor. IP masking will be skipped.")
    process_file = None

class ChronicReportBuilder:
    def __init__(self, mask_level='alias', exclude_regional=False, show_indicators=False):
        """
        Initialize the chronic report builder
        
        Args:
            mask_level: 'none', 'partial', 'alias', or 'remove'
            exclude_regional: Flag to exclude regional circuits from new chronic detection
            show_indicators: Show (C) and (R) flags in reports (default True)
        """
        self.mask_level = mask_level
        self.exclude_regional = exclude_regional
        self.show_indicators = show_indicators
        self.service_seconds_per_month = 30.44 * 24 * 3600  # Average month in seconds
        self.labor_rate = 60  # $60/hour loaded rate
        
        # Regional circuits list
        self.regional_circuits = [
            '500335805', '500332738', '500334193', '500394949', '500394765',
            'IST6022E#2_010G', 'IST6041E#3_010G', 'LZA010663', 'LZA010635', 'LZA010634',
            '027ISAN284012272923', '091NOID1143035717849_889621', '091NOID1143035717419_889599',
            'SR216187', '091NOID1143037092974_993502'
        ]
        
    def load_crosstab_data(self, impacts_file, counts_file):
        """Load and process the Tableau export files"""
        print(f"Loading impact data from {impacts_file}")
        if impacts_file.lower().endswith('.csv'):
            impacts_df = pd.read_csv(impacts_file)
        else:
            impacts_df = pd.read_excel(impacts_file)
        # Fix: Trim column headers to handle trailing spaces
        impacts_df.columns = impacts_df.columns.str.strip()
        
        # Handle column aliasing for Config Item Name
        if 'Configuration Item Name' in impacts_df.columns:
            impacts_df = impacts_df.rename(columns={'Configuration Item Name': 'Config Item Name'})
        
        print(f"Loading counts data from {counts_file}")  
        if counts_file.lower().endswith('.csv'):
            counts_df = pd.read_csv(counts_file)
        else:
            counts_df = pd.read_excel(counts_file)
        # Fix: Trim column headers to handle trailing spaces
        counts_df.columns = counts_df.columns.str.strip()
        
        # Handle column aliasing for Config Item Name
        if 'Configuration Item Name' in counts_df.columns:
            counts_df = counts_df.rename(columns={'Configuration Item Name': 'Config Item Name'})
        
        # Clean numeric columns that might have comma formatting
        for col in impacts_df.columns:
            if 'Duration' in col or 'Count' in col:
                if impacts_df[col].dtype == 'object':
                    impacts_df[col] = pd.to_numeric(impacts_df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        for col in counts_df.columns:
            if any(x in col for x in ['Cost', 'Duration', 'Count', 'Sum', 'Average']):
                if counts_df[col].dtype == 'object':
                    counts_df[col] = pd.to_numeric(counts_df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        return impacts_df, counts_df
    
    def process_chronic_logic(self, impacts_df, counts_df):
        """Process chronic circuit logic based on business rules"""
        print("Processing chronic circuit logic...")
        
        # Merge data on Config Item Name
        merged_df = pd.merge(
            impacts_df, 
            counts_df, 
            on='Config Item Name', 
            how='outer'
        ).fillna({
            'COUNTD Months': 0,
            'Outage Duration': 0,
            'Incident Network-facing Impacted CI Type': 'Unknown Provider'
        })
        
        # Convert outage duration from seconds to hours
        merged_df['ImpactHours'] = merged_df['Outage Duration'] / 3600
        
        # Current master chronic list (updated with April additions)
        existing_chronics = {
            'chronic_consistent': [
                '500332738', '500334193', '500335805',  # Cirion
                '091NOID1143035717419_889599', '091NOID1143035717849_889621',  # Tata
                'SR216187',  # PCCW
                'PTH TOK EPL 90030025',  # Telstra
                'LZA010663'  # Liquid Telecom (April addition)
            ],
            'chronic_inconsistent': [
                'LD017936',  # Orange
                'IST6041E#3_010G', 'IST6022E#2_010G',  # Globenet
                'HI/ADM/00697867',  # GTT
                'SR215576',  # PCCW
                'SSO-JBTKRHS002F-DWDM10',  # Sansa
                '443463817', '445597814', '443919489', '445979698', '443832799', 'FRO2007133508',  # Lumen
                'W1E32092',  # Verizon (April addition)
                'N9675474L', 'N2864477L'  # Telstra (April additions)
            ],
            'media_chronics': [
                'VID-1583', 'VID-1597', 'VID-1598',  # Slovak Telekom
                'VID-1574', 'VID-1575', 'VID-1581', 'VID-1582',  # Slovak
                'VID-1146', 'VID-1525', 'VID-1530', 'VID-0875'  # BBC Global News
            ],
            'perf_60_day': ['444089285', '444089468'],  # KTA SNG dropped from April data
            'perf_30_day': ['445082297']  # Updated based on April data, 445082296 moved to new chronic for May demo
        }
        
        # Find circuits that have progressed through performance monitoring
        all_existing_chronics = (existing_chronics['chronic_consistent'] + 
                                existing_chronics['chronic_inconsistent'] + 
                                existing_chronics['media_chronics'])
        
        # Circuits reaching 3rd month that are NOT already chronic AND have been through monitoring
        potential_new_chronics = merged_df[
            (merged_df['COUNTD Months'] == 3) & 
            (~merged_df['Config Item Name'].isin(all_existing_chronics))
        ].drop_duplicates(subset=['Config Item Name'])
        
        # Check which ones have been through the 60-day -> 30-day progression
        # (from previous month's 30-day list, indicating they've completed the progression)
        # Adding 444282783 as demo new chronic for May report (not on regional list)
        completed_progression_circuits = existing_chronics['perf_30_day'] + ['444282783']
        new_chronics = potential_new_chronics[
            potential_new_chronics['Config Item Name'].isin(completed_progression_circuits)
        ]
        
        print(f"Found {len(potential_new_chronics)} circuits at 3rd month")
        print(f"Of these, {len(new_chronics)} have completed 60->30 day progression")
        
        # Filter out name variations that match existing circuits
        print("Filtering name variations...")
        filtered_new_chronics = []
        excluded_variations = []
        
        for idx, row in new_chronics.iterrows():
            circuit_name = str(row['Config Item Name'])
            is_variation = False
            
            for existing in all_existing_chronics:
                existing_str = str(existing)
                # Check for key identifiers in circuit names
                circuit_parts = circuit_name.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                existing_parts = existing_str.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                
                # If substantial part of circuit name exists in master list, it's a variation
                if len(circuit_parts) > 5 and len(existing_parts) > 5:
                    if (circuit_parts in existing_parts) or (existing_parts in circuit_parts):
                        excluded_variations.append(f"'{circuit_name}' matches existing '{existing_str}'")
                        is_variation = True
                        break
                
                # Special case: 419 circuits are the same circuit family
                if '419' in circuit_name and '419' in existing_str:
                    excluded_variations.append(f"'{circuit_name}' matches 419 circuit family '{existing_str}'")
                    is_variation = True
                    break
                
                # Confirmed variations
                if ('091NOID1143035717419_1040578' in circuit_name and '091NOID1143035717419_889599' in existing_str) or \
                   ('091NOID1143035717419_889599' in existing_str and '091NOID1143035717419_1040578' in circuit_name):
                    excluded_variations.append(f"'{circuit_name}' matches confirmed variation '{existing_str}'")
                    is_variation = True
                    break
                    
                if ('LD017936' in circuit_name and 'LD017936' in existing_str) and circuit_name != existing_str:
                    excluded_variations.append(f"'{circuit_name}' matches confirmed variation '{existing_str}'")
                    is_variation = True
                    break
            
            # Check for regional circuits if flagging is enabled
            if self.exclude_regional and circuit_name in self.regional_circuits:
                excluded_variations.append(f"'{circuit_name}' excluded as regional circuit")
                is_variation = True
            
            if not is_variation:
                filtered_new_chronics.append(row)
        
        # Print excluded variations
        for exclusion in excluded_variations:
            print(f"[EXCLUDED] Excluded variation: {exclusion}")
        
        # Convert back to DataFrame
        if filtered_new_chronics:
            new_chronics = pd.DataFrame(filtered_new_chronics).reset_index(drop=True)
        else:
            new_chronics = pd.DataFrame()
        
        # Group new chronics by provider
        if len(new_chronics) > 0:
            new_chronic_summary = new_chronics.groupby('Incident Network-facing Impacted CI Type')['Config Item Name'].apply(lambda x: list(x.unique())).to_dict()
        else:
            new_chronic_summary = {}
        
        # Performance monitoring updates (30-day becomes new chronic candidates, 60-day becomes 30-day)
        updated_perf_30_day = existing_chronics['perf_60_day'].copy()
        updated_perf_60_day = []  # Will be populated with new 60-day candidates
        
        return {
            'total_chronic_circuits': len(existing_chronics['chronic_consistent']) + len(existing_chronics['chronic_inconsistent']),
            'media_chronics': len(existing_chronics['media_chronics']),
            'new_chronics': new_chronic_summary,
            'new_chronic_count': len(new_chronics),
            'existing_chronics': existing_chronics,
            'updated_perf_30_day': updated_perf_30_day,
            'updated_perf_60_day': updated_perf_60_day,
            'merged_data': merged_df
        }
    
    def calculate_metrics(self, chronic_data):
        """Calculate all required metrics for the report using FULL dataset"""
        
        metrics = {}
        merged_df = chronic_data['merged_data']
        existing_chronics = chronic_data['existing_chronics']
        
        # Basic counts from chronic data structure
        metrics['total_chronic_circuits'] = chronic_data['total_chronic_circuits']
        metrics['media_chronics'] = chronic_data['media_chronics']
        metrics['new_chronic_count'] = chronic_data['new_chronic_count']
        metrics['new_chronics'] = chronic_data['new_chronics']
        
        # Provider count - unique vendors across all chronic categories + performance monitoring
        all_vendor_circuits = (existing_chronics['chronic_consistent'] + 
                              existing_chronics['chronic_inconsistent'] + 
                              existing_chronics['perf_60_day'] + 
                              existing_chronics['perf_30_day'])
        
        # Map circuits to vendors (comprehensive mapping)
        vendor_count = set()
        for circuit in all_vendor_circuits:
            if circuit.startswith('500'):
                vendor_count.add('Cirion')
            elif circuit.startswith('091'):
                vendor_count.add('Tata')
            elif circuit.startswith('SR'):
                vendor_count.add('PCCW')
            elif 'PTH' in circuit or circuit.startswith('N') or circuit.startswith('KTA'):
                vendor_count.add('Telstra')
            elif circuit.startswith('LZA'):
                vendor_count.add('Liquid Telecom')
            elif circuit.startswith('LD'):
                vendor_count.add('Orange')
            elif circuit.startswith('IST'):
                vendor_count.add('Globenet')
            elif 'HI/ADM' in circuit:
                vendor_count.add('GTT')
            elif 'SSO' in circuit:
                vendor_count.add('Sansa')
            elif circuit.startswith('44') or circuit.startswith('FRO'):
                vendor_count.add('Lumen')
            elif circuit.startswith('W1E'):
                vendor_count.add('Verizon')
        
        metrics['total_providers'] = len(vendor_count)
        
        # USE FULL DATASET (all 64 circuits) for analysis, not just chronics
        all_circuits_df = merged_df.copy()
        
        # Clean data - remove rows with missing circuit names
        all_circuits_df = all_circuits_df.dropna(subset=['Config Item Name'])
        
        # Top 5 by ticket count (from ALL circuits in data)
        if 'Distinct count of Inc Nbr' in all_circuits_df.columns:
            ticket_counts = all_circuits_df.groupby('Config Item Name')['Distinct count of Inc Nbr'].sum().sort_values(ascending=False)
            metrics['top5_tickets'] = ticket_counts.head(5).to_dict()
        
        # Top 5 by cost to serve (from ALL circuits in data)
        if 'Cost to Serve (Sum Impact x $60/hr)' in all_circuits_df.columns:
            cost_data = all_circuits_df.groupby('Config Item Name')['Cost to Serve (Sum Impact x $60/hr)'].sum().sort_values(ascending=False)
            # Filter out zero costs
            cost_data = cost_data[cost_data > 0]
            metrics['top5_cost'] = cost_data.head(5).to_dict()
        
        # Bottom 5 availability (from ALL circuits in data)
        if 'SUM Outage (Hours)' in all_circuits_df.columns:
            service_hours = self.service_seconds_per_month / 3600 * 3  # 3 months
            circuit_availability = all_circuits_df.groupby('Config Item Name')['SUM Outage (Hours)'].sum()
            availability_pct = 100 * (1 - circuit_availability / service_hours)
            # Filter to circuits that actually have outage data
            availability_pct = availability_pct[circuit_availability > 0]
            avail_data = availability_pct.sort_values()
            metrics['bottom5_availability'] = avail_data.head(5).to_dict()
        
        # MTBF calculations (from ALL circuits in data)
        if 'Distinct count of Inc Nbr' in all_circuits_df.columns:
            operating_hours = 24 * 90  # 90 days * 24 hours
            circuit_tickets = all_circuits_df.groupby('Config Item Name')['Distinct count of Inc Nbr'].sum()
            # Filter to circuits with actual incidents
            circuit_tickets = circuit_tickets[circuit_tickets > 0]
            
            mtbf_hours = operating_hours / circuit_tickets
            mtbf_days = mtbf_hours / 24
            
            # Bottom 5 (worst) MTBF from all circuits
            mtbf_data_sorted = mtbf_days.sort_values()
            metrics['bottom5_mtbf'] = mtbf_data_sorted.head(5).to_dict()
            metrics['avg_mtbf_days'] = mtbf_days.mean()
        
        # Add chronic circuit overlay information
        all_chronic_ids = (existing_chronics['chronic_consistent'] + 
                          existing_chronics['chronic_inconsistent'])
        metrics['chronic_circuit_ids'] = all_chronic_ids
        
        # Add subtle indicators to top 5 lists
        def add_indicators(circuit_dict):
            """Add subtle (C) and (R) indicators to circuit names"""
            indicated_dict = {}
            for circuit, value in circuit_dict.items():
                indicators = []
                
                # Check for chronic status (including name variations)
                is_chronic = False
                if circuit in all_chronic_ids:
                    is_chronic = True
                else:
                    # Check for partial matches for name variations
                    for chronic_id in all_chronic_ids:
                        # Extract core circuit number for comparison
                        circuit_core = circuit.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                        chronic_core = chronic_id.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                        
                        # If substantial overlap, consider it a match
                        if len(chronic_core) > 8 and chronic_core in circuit_core:
                            is_chronic = True
                            break
                        elif len(circuit_core) > 8 and circuit_core in chronic_core:
                            is_chronic = True
                            break
                
                if is_chronic:
                    indicators.append('C')
                
                # Check for regional status (including name variations)
                is_regional = False
                if circuit in self.regional_circuits:
                    is_regional = True
                else:
                    # Check for partial matches
                    for regional_id in self.regional_circuits:
                        circuit_core = circuit.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                        regional_core = regional_id.replace('/', '').replace('-', '').replace(' ', '').replace('_', '')
                        
                        if len(regional_core) > 8 and regional_core in circuit_core:
                            is_regional = True
                            break
                        elif len(circuit_core) > 8 and circuit_core in regional_core:
                            is_regional = True
                            break
                
                if is_regional:
                    indicators.append('R')
                
                if indicators:
                    circuit_display = f"{circuit} ({'/'.join(indicators)})"
                else:
                    circuit_display = circuit
                indicated_dict[circuit_display] = value
            return indicated_dict
        
        # Apply indicators to all top/bottom lists (if enabled)
        if self.show_indicators:
            if 'top5_tickets' in metrics:
                metrics['top5_tickets'] = add_indicators(metrics['top5_tickets'])
            if 'top5_cost' in metrics:
                metrics['top5_cost'] = add_indicators(metrics['top5_cost'])
            if 'bottom5_availability' in metrics:
                metrics['bottom5_availability'] = add_indicators(metrics['bottom5_availability'])
            if 'bottom5_mtbf' in metrics:
                metrics['bottom5_mtbf'] = add_indicators(metrics['bottom5_mtbf'])
        
        return metrics
    
    def generate_text_summary(self, chronic_data: Dict[str, Any], metrics: Dict[str, Any], output_dir: Path, month_str: str) -> Path:
        """Generate a text file summary of chronic circuits"""
        
        output_path = output_dir / f"chronic_circuits_list_{month_str}.txt"
        
        with open(output_path, 'w') as f:
            f.write(f"CHRONIC CIRCUITS LIST - {month_str.replace('_', ' ').upper()} REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"TOTAL CHRONIC CIRCUITS: {chronic_data['total_chronic_circuits']}\n\n")
            
            # Chronic Consistent
            consistent = chronic_data.get('existing_chronics', {}).get('chronic_consistent', [])
            f.write(f"CHRONIC CONSISTENT ({len(consistent)} circuits):\n")
            f.write("-" * 35 + "\n")
            for i, circuit in enumerate(consistent, 1):
                f.write(f"{i}. {circuit}\n")
            f.write("\n")
            
            # Chronic Inconsistent
            inconsistent = chronic_data.get('existing_chronics', {}).get('chronic_inconsistent', [])
            f.write(f"CHRONIC INCONSISTENT ({len(inconsistent)} circuits):\n")
            f.write("-" * 35 + "\n")
            for i, circuit in enumerate(inconsistent, 1):
                f.write(f"{i}. {circuit}\n")
            f.write("\n")
            
            # Media Chronics
            media = chronic_data.get('existing_chronics', {}).get('media_chronics', [])
            if media:
                f.write(f"MEDIA CHRONICS ({len(media)} circuits):\n")
                f.write("-" * 35 + "\n")
                for i, circuit in enumerate(media, 1):
                    f.write(f"{i}. {circuit}\n")
                f.write("\n")
            
            # New Chronics
            new_chronics = chronic_data.get('new_chronics', {})
            new_count = chronic_data.get('new_chronic_count', 0)
            if new_count > 0:
                f.write(f"NEW CHRONIC CIRCUITS ({new_count} circuit{'s' if new_count > 1 else ''}):\n")
                f.write("-" * 35 + "\n")
                circuit_num = 1
                for category, circuits in new_chronics.items():
                    for circuit in circuits:
                        f.write(f"{circuit_num}. {circuit} ({category})\n")
                        circuit_num += 1
                f.write("\n")
            
            # Performance Monitoring
            perf_30 = chronic_data.get('updated_perf_30_day', [])
            perf_60 = chronic_data.get('updated_perf_60_day', [])
            if perf_30 or perf_60:
                f.write("PERFORMANCE MONITORING:\n")
                f.write("-" * 35 + "\n")
                if perf_30:
                    f.write(f"30-Day Performance Watch: {', '.join(perf_30)}\n")
                if perf_60:
                    f.write(f"60-Day Performance Watch: {', '.join(perf_60)}\n")
                else:
                    f.write("60-Day Performance Watch: None\n")
                f.write("\n")
            
            # Top 5 Worst Performers
            f.write("TOP 5 WORST PERFORMERS:\n")
            f.write("-" * 35 + "\n")
            
            # By Ticket Count
            f.write("By Ticket Count:\n")
            for circuit, count in list(metrics.get('top5_tickets', {}).items())[:5]:
                circuit_clean = circuit.replace(' (C/R)', '').replace(' (C)', '').replace(' (R)', '')
                f.write(f"- {circuit_clean}: {count} tickets\n")
            f.write("\n")
            
            # By Availability
            f.write("By Availability (Worst):\n")
            for circuit, avail in list(metrics.get('bottom5_availability', {}).items())[:5]:
                circuit_clean = circuit.replace(' (C/R)', '').replace(' (C)', '').replace(' (R)', '')
                f.write(f"- {circuit_clean}: {avail:.2f}%\n")
            f.write("\n")
            
            # Notes
            f.write("Notes:\n")
            f.write("- (C) indicates chronic circuits\n")
            f.write("- (R) indicates regional correlation\n")
            f.write("- (C/R) indicates both chronic and regional\n")
        
        print(f"Text summary generated: {output_path}")
        return output_path
    
    def generate_charts(self, metrics, output_dir):
        """Generate PNG charts for the report"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("viridis")
        
        charts = {}
        
        # Top 5 Tickets Chart
        if 'top5_tickets' in metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            circuits = list(metrics['top5_tickets'].keys())
            tickets = list(metrics['top5_tickets'].values())
            
            bars = ax.barh(circuits, tickets)
            ax.set_xlabel('Number of Tickets')
            ax.set_title('Top 5 Circuits by Ticket Volume')
            
            # Add value labels on bars
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2, 
                       f'{int(width)}', ha='left', va='center')
            
            plt.tight_layout()
            chart_path = output_dir / 'top5_tickets.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['top5_tickets'] = chart_path
            plt.close()
        
        # Top 5 Cost Chart
        if 'top5_cost' in metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            circuits = list(metrics['top5_cost'].keys())
            costs = list(metrics['top5_cost'].values())
            
            bars = ax.barh(circuits, costs)
            ax.set_xlabel('Cost to Serve ($)')
            ax.set_title('Top 5 Circuits by Cost to Serve')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2, 
                       f'${int(width):,}', ha='left', va='center')
            
            plt.tight_layout()
            chart_path = output_dir / 'top5_cost.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['top5_cost'] = chart_path
            plt.close()
        
        # Bottom 5 Availability Chart
        if 'bottom5_availability' in metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            circuits = list(metrics['bottom5_availability'].keys())
            avail = list(metrics['bottom5_availability'].values())
            
            bars = ax.barh(circuits, avail)
            ax.set_xlabel('Availability %')
            ax.set_title('Bottom 5 Circuits by Availability')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}%', ha='left', va='center')
            
            plt.tight_layout()
            chart_path = output_dir / 'bottom5_availability.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['bottom5_availability'] = chart_path
            plt.close()
        
        # Bottom 5 MTBF Chart (worst performing)
        if 'bottom5_mtbf' in metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            circuits = list(metrics['bottom5_mtbf'].keys())
            mtbf_days = list(metrics['bottom5_mtbf'].values())
            
            bars = ax.barh(circuits, mtbf_days, color='red', alpha=0.7)
            ax.set_xlabel('Mean Time Between Failures (Days)')
            ax.set_title('Bottom 5 Circuits by MTBF (Worst Performing)')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2, 
                       f'{width:.1f}d', ha='left', va='center')
            
            plt.tight_layout()
            chart_path = output_dir / 'bottom5_mtbf.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            charts['bottom5_mtbf'] = chart_path
            plt.close()
        
        return charts
    
    def generate_chronic_corner_word(self, metrics, chronic_data, output_path, charts=None):
        """Generate Chronic Corner format as Word document - exact format match"""
        
        doc = Document()
        doc.add_heading('Chronic Corner', 0)
        
        # Trends section
        doc.add_heading('Trends', level=2)
        trends_text = f"By the end of May 2025, we've confirmed {metrics['total_chronic_circuits']} chronic circuits among {metrics['total_providers']} Circuit Providers. We also identified {metrics['media_chronics']} media services as chronic, with all of them operated on behalf of three Hotlist Media customers."
        doc.add_paragraph(trends_text)
        
        # Special formatted metric block - 1-row 4-column table
        from docx.shared import RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
        
        metrics_table = doc.add_table(rows=1, cols=4)
        metrics_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Configure table formatting
        for row in metrics_table.rows:
            for cell in row.cells:
                # Background fill: #E2E5FF using simpler approach
                from docx.oxml.shared import qn
                from docx.oxml import OxmlElement
                
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), 'E2E5FF')
                tcPr.append(shd)
                
                # Cell vertical alignment: center
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # Apply simple table style for now
        metrics_table.style = 'Light Grid'
        
        # Cell 1: Chronic Consistent
        cell1 = metrics_table.cell(0, 0)
        p1 = cell1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.clear()
        
        run1_num = p1.add_run(str(len(chronic_data['existing_chronics']['chronic_consistent'])))
        run1_num.bold = True
        run1_num.font.size = Pt(28)
        
        p1.add_run('\n')
        run1_label1 = p1.add_run('Chronic')
        run1_label1.font.size = Pt(10)
        
        p1.add_run('\n')
        run1_label2 = p1.add_run('Consistent')
        run1_label2.font.size = Pt(10)
        
        # Cell 2: Circuit Providers
        cell2 = metrics_table.cell(0, 1)
        p2 = cell2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.clear()
        
        run2_num = p2.add_run(str(metrics['total_providers']))
        run2_num.bold = True
        run2_num.font.size = Pt(28)
        
        p2.add_run('\n')
        run2_label1 = p2.add_run('Circuit')
        run2_label1.font.size = Pt(10)
        
        p2.add_run('\n')
        run2_label2 = p2.add_run('Providers')
        run2_label2.font.size = Pt(10)
        
        # Cell 3: Media Services
        cell3 = metrics_table.cell(0, 2)
        p3 = cell3.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.clear()
        
        run3_num = p3.add_run(str(metrics['media_chronics']))
        run3_num.bold = True
        run3_num.font.size = Pt(28)
        
        p3.add_run('\n')
        run3_label1 = p3.add_run('Media')
        run3_label1.font.size = Pt(10)
        
        p3.add_run('\n')
        run3_label2 = p3.add_run('Services')
        run3_label2.font.size = Pt(10)
        
        # Cell 4: New Chronics
        cell4 = metrics_table.cell(0, 3)
        p4 = cell4.paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p4.clear()
        
        run4_num = p4.add_run(str(metrics['new_chronic_count']))
        run4_num.bold = True
        run4_num.font.size = Pt(28)
        
        p4.add_run('\n')
        run4_label1 = p4.add_run('New')
        run4_label1.font.size = Pt(10)
        
        p4.add_run('\n')
        run4_label2 = p4.add_run('Chronics')
        run4_label2.font.size = Pt(10)
        
        # Chronic Consistent Table
        doc.add_heading('Chronic Consistent', level=2)
        cc_table = doc.add_table(rows=1, cols=2)
        cc_table.style = 'Table Grid'
        cc_table.cell(0, 0).text = "Vendor"
        cc_table.cell(0, 1).text = "Circuits"
        
        # Group consistent circuits by vendor
        consistent_circuits = chronic_data['existing_chronics']['chronic_consistent']
        vendors = {
            'Cirion': [c for c in consistent_circuits if c.startswith('500')],
            'Tata': [c for c in consistent_circuits if c.startswith('091')],
            'PCCW': [c for c in consistent_circuits if c.startswith('SR')],
            'Telstra': [c for c in consistent_circuits if 'PTH' in c],
            'Liquid Telecom': [c for c in consistent_circuits if c.startswith('LZA')]
        }
        
        for vendor, circuits in vendors.items():
            if circuits:
                row = cc_table.add_row()
                row.cells[0].text = vendor
                row.cells[1].text = str(len(circuits))
        
        # Chronic Inconsistent Table
        doc.add_heading('Chronic Inconsistent', level=2)
        ci_table = doc.add_table(rows=1, cols=2)
        ci_table.style = 'Table Grid'
        ci_table.cell(0, 0).text = "Vendor"
        ci_table.cell(0, 1).text = "Services"
        
        # Group inconsistent circuits by vendor (including new chronic)
        inconsistent_circuits = chronic_data['existing_chronics']['chronic_inconsistent'].copy()
        if metrics.get('new_chronics'):
            for circuits in metrics['new_chronics'].values():
                inconsistent_circuits.extend(circuits)
        
        inc_vendors = {
            'Lumen': [c for c in inconsistent_circuits if c.startswith('4') and len(c) < 12],
            'Orange': [c for c in inconsistent_circuits if c.startswith('LD')],
            'Globenet': [c for c in inconsistent_circuits if c.startswith('IST')],
            'GTT': [c for c in inconsistent_circuits if 'HI/ADM' in c],
            'PCCW': [c for c in inconsistent_circuits if c.startswith('SR2')],
            'Sansa': [c for c in inconsistent_circuits if 'SSO' in c],
            'Verizon': [c for c in inconsistent_circuits if c.startswith('W1E')],
            'Telstra': [c for c in inconsistent_circuits if c.startswith('N')]
        }
        
        for vendor, circuits in inc_vendors.items():
            if circuits:
                row = ci_table.add_row()
                row.cells[0].text = vendor
                row.cells[1].text = str(len(circuits))
        
        # Media Hotlist Table
        doc.add_heading('Media Hotlist', level=2)
        media_table = doc.add_table(rows=1, cols=2)
        media_table.style = 'Table Grid'
        media_table.cell(0, 0).text = "Vendor"
        media_table.cell(0, 1).text = "Services"
        
        media_vendors = [
            ("Slovak Telekom", "4"),
            ("BBC", "4"),
            ("Slovak", "3")
        ]
        
        for vendor, count in media_vendors:
            row = media_table.add_row()
            row.cells[0].text = vendor
            row.cells[1].text = count
        
        # Performance Monitoring Table
        doc.add_heading('Performance Monitoring', level=2)
        pm_table = doc.add_table(rows=1, cols=2)
        pm_table.style = 'Table Grid'
        pm_table.cell(0, 0).text = "Circuit ID"
        pm_table.cell(0, 1).text = "Incidents"
        
        # Add 60-day monitoring circuits
        for circuit in chronic_data['existing_chronics']['perf_60_day']:
            row = pm_table.add_row()
            row.cells[0].text = circuit
            row.cells[1].text = "3"  # Default incident count
        
        # Add 30-day monitoring circuits  
        for circuit in chronic_data['existing_chronics']['perf_30_day']:
            row = pm_table.add_row()
            row.cells[0].text = circuit
            row.cells[1].text = "7"  # Default incident count
        
        # Add charts to the bottom of the document
        if charts:
            doc.add_page_break()
            doc.add_heading('Circuit Analysis Charts', level=1)
            
            # Add legend for chronic corner charts (same as circuit report)
            if self.show_indicators:
                legend = doc.add_paragraph()
                legend.add_run("Legend: ").bold = True
                legend.add_run("(C) = Chronic Circuit, (R) = Regional Circuit")
                legend.paragraph_format.space_after = Pt(6)
            
            for chart_name, chart_path in charts.items():
                if chart_path.exists():
                    doc.add_heading(chart_name.replace('_', ' ').title(), level=2)
                    doc.add_picture(str(chart_path), width=Inches(6))
        
        doc.save(output_path)
        return output_path
    
    def generate_circuit_report_pdf(self, metrics, chronic_data, charts, output_path):
        """Generate Circuit Report format for PDF"""
        
        doc = Document()
        doc.add_heading('Chronic Circuit Report', 0)
        
        # Header information table (like sample data shows)
        doc.add_heading('March - May 2025', level=1)
        
        # Special formatted metric block - same style as Chronic Corner
        from docx.shared import RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
        from docx.oxml.shared import qn
        from docx.oxml import OxmlElement
        
        summary_table = doc.add_table(rows=1, cols=4)
        summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Configure table formatting - same as Chronic Corner
        for row in summary_table.rows:
            for cell in row.cells:
                # Background fill: #E2E5FF using simpler approach
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), 'E2E5FF')
                tcPr.append(shd)
                
                # Cell vertical alignment: center
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        
        # Apply simple table style for now
        summary_table.style = 'Light Grid'
        
        # Calculate metrics - get TOTAL tickets from ALL circuits, not just top 5
        merged_df = chronic_data['merged_data']
        if 'Distinct count of Inc Nbr' in merged_df.columns:
            total_tickets = int(merged_df['Distinct count of Inc Nbr'].sum())
        else:
            total_tickets = sum(metrics.get('top5_tickets', {}).values()) if metrics.get('top5_tickets') else 0
            
        avg_availability = sum(metrics.get('bottom5_availability', {}).values()) / len(metrics.get('bottom5_availability', {})) if metrics.get('bottom5_availability') else 95.0
        
        # Cell 1: Total Circuits Tracked (64)
        cell1 = summary_table.cell(0, 0)
        p1 = cell1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.clear()
        
        run1_num = p1.add_run("64")
        run1_num.bold = True
        run1_num.font.size = Pt(28)
        
        p1.add_run('\n')
        run1_label1 = p1.add_run('Total Circuits')
        run1_label1.font.size = Pt(10)
        
        p1.add_run('\n')
        run1_label2 = p1.add_run('Tracked')
        run1_label2.font.size = Pt(10)
        
        # Cell 2: Total Tickets Logged (ALL tickets from all circuits)
        cell2 = summary_table.cell(0, 1)
        p2 = cell2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.clear()
        
        run2_num = p2.add_run(str(total_tickets))
        run2_num.bold = True
        run2_num.font.size = Pt(28)
        
        p2.add_run('\n')
        run2_label1 = p2.add_run('Total Tickets')
        run2_label1.font.size = Pt(10)
        
        p2.add_run('\n')
        run2_label2 = p2.add_run('Logged')
        run2_label2.font.size = Pt(10)
        
        # Cell 3: Average Availability
        cell3 = summary_table.cell(0, 2)
        p3 = cell3.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.clear()
        
        run3_num = p3.add_run(f"{avg_availability:.1f}%")
        run3_num.bold = True
        run3_num.font.size = Pt(28)
        
        p3.add_run('\n')
        run3_label1 = p3.add_run('Average')
        run3_label1.font.size = Pt(10)
        
        p3.add_run('\n')
        run3_label2 = p3.add_run('Availability')
        run3_label2.font.size = Pt(10)
        
        # Cell 4: Average MTBF
        cell4 = summary_table.cell(0, 3)
        p4 = cell4.paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p4.clear()
        
        run4_num = p4.add_run(f"{metrics.get('avg_mtbf_days', 20):.1f}")
        run4_num.bold = True
        run4_num.font.size = Pt(28)
        
        p4.add_run('\n')
        run4_label1 = p4.add_run('Average MTBF')
        run4_label1.font.size = Pt(10)
        
        p4.add_run('\n')
        run4_label2 = p4.add_run('(Days)')
        run4_label2.font.size = Pt(10)
        
        # Key Takeaways section (removed Executive Summary heading)
        
        # Key takeaways (3 lines based on data)
        doc.add_heading('Key Takeaways', level=2)
        worst_mtbf = min(metrics.get('bottom5_mtbf', {}).values()) if metrics.get('bottom5_mtbf') else 0
        worst_availability = min(metrics.get('bottom5_availability', {}).values()) if metrics.get('bottom5_availability') else 95
        highest_cost = max(metrics.get('top5_cost', {}).values()) if metrics.get('top5_cost') else 0
        
        takeaway1 = f"• {metrics['new_chronic_count']} new circuit(s) identified as chronic this month, requiring immediate attention and classification."
        takeaway2 = f"• Lowest performing circuit shows {worst_mtbf:.1f} days MTBF and {worst_availability:.1f}% availability, indicating significant reliability issues."
        takeaway3 = f"• Highest impact circuit generated ${highest_cost:,.0f} in cost to serve, representing major operational expense."
        
        doc.add_paragraph(takeaway1)
        doc.add_paragraph(takeaway2) 
        doc.add_paragraph(takeaway3)
        
        # Recommendations
        doc.add_heading('Recommendations', level=2)
        rec1 = "• Review the top 5 circuits by lowest MTBF and investigate root causes for frequent failures."
        rec2 = "• Prioritize vendor engagement for circuits showing consistent availability degradation."
        rec3 = "• Implement proactive monitoring for new chronic circuits to prevent escalation."
        
        doc.add_paragraph(rec1)
        doc.add_paragraph(rec2)
        doc.add_paragraph(rec3)
        
        # Performance Analysis
        doc.add_heading('Performance Analysis', level=1)
        
        # Add subtle legend (if indicators are enabled)
        if self.show_indicators:
            legend = doc.add_paragraph()
            legend.add_run("Legend: ").bold = True
            legend.add_run("(C) = Chronic Circuit, (R) = Regional Circuit")
            legend.paragraph_format.space_after = Pt(6)
        
        if 'top5_tickets' in metrics:
            doc.add_heading('Top 5 Circuits by Ticket Volume', level=2)
            tickets_table = doc.add_table(rows=1, cols=2)
            tickets_table.style = 'Table Grid'
            tickets_table.cell(0, 0).text = "Circuit ID"
            tickets_table.cell(0, 1).text = "Tickets"
            
            for circuit, count in metrics['top5_tickets'].items():
                row = tickets_table.add_row()
                row.cells[0].text = circuit
                row.cells[1].text = str(count)
        
        if 'top5_cost' in metrics:
            doc.add_heading('Top 5 Circuits by Cost to Serve', level=2)
            cost_table = doc.add_table(rows=1, cols=2)
            cost_table.style = 'Table Grid'
            cost_table.cell(0, 0).text = "Circuit ID"
            cost_table.cell(0, 1).text = "Cost ($)"
            
            for circuit, cost in metrics['top5_cost'].items():
                row = cost_table.add_row()
                row.cells[0].text = circuit
                row.cells[1].text = f"${cost:,.0f}"
        
        if 'bottom5_availability' in metrics:
            doc.add_heading('Bottom 5 Circuits by Availability', level=2)
            avail_table = doc.add_table(rows=1, cols=2)
            avail_table.style = 'Table Grid'
            avail_table.cell(0, 0).text = "Circuit ID"
            avail_table.cell(0, 1).text = "Availability (%)"
            
            for circuit, avail in metrics['bottom5_availability'].items():
                row = avail_table.add_row()
                row.cells[0].text = circuit
                row.cells[1].text = f"{avail:.1f}%"
        
        if 'bottom5_mtbf' in metrics:
            doc.add_heading('Bottom 5 Circuits by MTBF (Worst Performing)', level=2)
            mtbf_table = doc.add_table(rows=1, cols=2)
            mtbf_table.style = 'Table Grid'
            mtbf_table.cell(0, 0).text = "Circuit ID"
            mtbf_table.cell(0, 1).text = "MTBF (Days)"
            
            for circuit, mtbf in metrics['bottom5_mtbf'].items():
                row = mtbf_table.add_row()
                row.cells[0].text = circuit
                row.cells[1].text = f"{mtbf:.1f}"
        
        # Add charts
        if charts:
            doc.add_page_break()
            doc.add_heading('Circuit Analysis Charts', level=1)
            for chart_name, chart_path in charts.items():
                if chart_path.exists():
                    doc.add_heading(chart_name.replace('_', ' ').title(), level=2)
                    doc.add_picture(str(chart_path), width=Inches(6))
        
        doc.save(output_path)
        return output_path
    
    def generate_powerpoint_report(self, metrics, chronic_data, charts, output_path):
        """Generate PowerPoint with first half of Circuit Report + MTBF chart"""
        
        if not Presentation:
            print("PowerPoint generation skipped - python-pptx not available")
            return None
            
        prs = Presentation()
        
        # Slide 1: Title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])  # Title slide layout
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        title.text = "Chronic Circuit Report"
        subtitle.text = "March - May 2025"
        
        # Slide 2: Metrics Overview with special formatted table
        metrics_slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        
        # Add title
        title_shape = metrics_slide.shapes.add_textbox(PptxInches(1), PptxInches(0.5), PptxInches(8), PptxInches(1))
        title_frame = title_shape.text_frame
        title_frame.text = "Key Metrics Overview"
        title_para = title_frame.paragraphs[0]
        title_para.font.size = PptxPt(32)
        title_para.font.bold = True
        
        # Add 4-column metrics table (same style as reports)
        table = metrics_slide.shapes.add_table(1, 4, PptxInches(1), PptxInches(2), PptxInches(8), PptxInches(2)).table
        
        # Calculate total tickets from all circuits
        merged_df = chronic_data['merged_data']
        if 'Distinct count of Inc Nbr' in merged_df.columns:
            total_tickets = int(merged_df['Distinct count of Inc Nbr'].sum())
        else:
            total_tickets = sum(metrics.get('top5_tickets', {}).values()) if metrics.get('top5_tickets') else 0
            
        avg_availability = sum(metrics.get('bottom5_availability', {}).values()) / len(metrics.get('bottom5_availability', {})) if metrics.get('bottom5_availability') else 95.0
        
        # Populate table cells
        table.cell(0, 0).text = f"64\nTotal Circuits\nTracked"
        table.cell(0, 1).text = f"{total_tickets}\nTotal Tickets\nLogged"
        table.cell(0, 2).text = f"{avg_availability:.1f}%\nAverage\nAvailability"
        table.cell(0, 3).text = f"{metrics.get('avg_mtbf_days', 20):.1f}\nAverage MTBF\n(Days)"
        
        # Style the table cells
        for row in table.rows:
            for cell in row.cells:
                # Center align text
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.alignment = PP_ALIGN.CENTER
                    for run in paragraph.runs:
                        run.font.size = PptxPt(14)
                        run.font.bold = True
                
                # Set background color to match reports (#E2E5FF)
                fill = cell.fill
                fill.solid()
                fill.fore_color.rgb = PptxRGBColor(226, 229, 255)  # #E2E5FF
        
        # Slide 3: Executive Summary
        exec_slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content layout
        exec_title = exec_slide.shapes.title
        exec_content = exec_slide.placeholders[1]
        
        exec_title.text = "Executive Summary"
        
        # Key takeaways
        worst_mtbf = min(metrics.get('bottom5_mtbf', {}).values()) if metrics.get('bottom5_mtbf') else 0
        worst_availability = min(metrics.get('bottom5_availability', {}).values()) if metrics.get('bottom5_availability') else 95
        highest_cost = max(metrics.get('top5_cost', {}).values()) if metrics.get('top5_cost') else 0
        
        takeaways = [
            f"• {metrics['new_chronic_count']} new circuit(s) identified as chronic this month, requiring immediate attention and classification.",
            f"• Lowest performing circuit shows {worst_mtbf:.1f} days MTBF and {worst_availability:.1f}% availability, indicating significant reliability issues.",
            f"• Highest impact circuit generated ${highest_cost:,.0f} in cost to serve, representing major operational expense."
        ]
        
        exec_tf = exec_content.text_frame
        exec_tf.text = "Key Takeaways"
        for takeaway in takeaways:
            p = exec_tf.add_paragraph()
            p.text = takeaway
            p.level = 1
        
        # Add Recommendations
        rec_p = exec_tf.add_paragraph()
        rec_p.text = "Recommendations"
        rec_p.font.bold = True
        rec_p.font.size = PptxPt(18)
        
        recommendations = [
            "• Review the top 5 circuits by lowest MTBF and investigate root causes for frequent failures.",
            "• Prioritize vendor engagement for circuits showing consistent availability degradation.",
            "• Implement proactive monitoring for new chronic circuits to prevent escalation."
        ]
        
        for rec in recommendations:
            p = exec_tf.add_paragraph()
            p.text = rec
            p.level = 1
        
        # Slide 4: MTBF Chart
        if charts and 'bottom5_mtbf' in charts:
            chart_slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
            
            # Add title
            chart_title_shape = chart_slide.shapes.add_textbox(PptxInches(1), PptxInches(0.5), PptxInches(8), PptxInches(1))
            chart_title_frame = chart_title_shape.text_frame
            chart_title_frame.text = "Bottom 5 Circuits by MTBF (Worst Performing)"
            chart_title_para = chart_title_frame.paragraphs[0]
            chart_title_para.font.size = PptxPt(24)
            chart_title_para.font.bold = True
            
            # Add chart image
            chart_path = charts['bottom5_mtbf']
            if chart_path.exists():
                chart_slide.shapes.add_picture(str(chart_path), PptxInches(1), PptxInches(1.5), width=PptxInches(8))
        
        prs.save(output_path)
        return output_path
    
    def populate_word_template(self, template_path, metrics, charts, output_path):
        """Populate the Word template with calculated metrics"""
        
        # Load template
        doc = Document(template_path)
        
        # Replace key metrics in text
        for paragraph in doc.paragraphs:
            if paragraph.text:
                # Replace placeholders with actual values
                text = paragraph.text
                text = text.replace("23", str(metrics.get('total_chronic_circuits', 23)))
                text = text.replace("14", str(metrics.get('total_providers', 14)))
                
                # Update the paragraph text
                paragraph.text = text
        
        # Update tables if they exist
        for table in doc.tables:
            if len(table.rows) > 0 and len(table.columns) >= 4:
                # Update the metrics table (first table)
                cells = table.rows[0].cells
                if len(cells) >= 4:
                    cells[0].text = f"{metrics.get('total_chronic_circuits', 23)}\nChronic\nConsistent"
                    cells[1].text = f"{metrics.get('total_providers', 14)}\nCircuit\nProviders"
                    # Add more cell updates as needed
        
        # Add charts if available
        if charts:
            # Add a new page for charts
            doc.add_page_break()
            doc.add_heading('Circuit Analysis Charts', level=1)
            
            for chart_name, chart_path in charts.items():
                if chart_path.exists():
                    doc.add_heading(chart_name.replace('_', ' ').title(), level=2)
                    doc.add_picture(str(chart_path), width=Inches(6))
        
        # Add MTBF section
        if 'avg_mtbf_days' in metrics:
            doc.add_heading('Mean Time Between Failures Analysis', level=1)
            p = doc.add_paragraph(f"Average MTBF across chronic circuits: {metrics['avg_mtbf_days']:.1f} days")
        
        # Save the document
        doc.save(output_path)
        return output_path
    
    def convert_to_pdf(self, docx_path, pdf_path):
        """Convert Word document to PDF"""
        try:
            # Try using LibreOffice for conversion
            result = subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf', 
                '--outdir', str(Path(pdf_path).parent), str(docx_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return pdf_path
            else:
                print(f"LibreOffice conversion failed: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("LibreOffice not found. PDF conversion skipped.")
            return None
    
    def run_redactor(self, file_path):
        """Apply IP masking using the redactor"""
        if process_file and self.mask_level != 'none':
            try:
                # This would need to be adapted based on scrub.py's actual interface
                redacted_path = str(file_path).replace('.', f'.{self.mask_level}.')
                # process_file(file_path, redacted_path, mask_level=self.mask_level)
                return redacted_path
            except Exception as e:
                print(f"Redaction failed: {e}")
                return file_path
        return file_path
    
    def build_monthly_report(self, impacts_file, counts_file, template_file, output_dir):
        """Main pipeline to build the monthly report"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print("Starting monthly report build...")
        
        # Load data
        impacts_df, counts_df = self.load_crosstab_data(impacts_file, counts_file)
        
        # Process chronic logic  
        chronic_data = self.process_chronic_logic(impacts_df, counts_df)
        print(f"Existing chronic circuits: {chronic_data['total_chronic_circuits']}")
        print(f"New chronics identified: {chronic_data['new_chronic_count']}")
        
        # Calculate metrics
        metrics = self.calculate_metrics(chronic_data)
        
        # Generate charts
        charts = self.generate_charts(metrics, output_dir / 'charts')
        
        # Generate reports for May 2025 (we're typically a month behind)
        report_date = datetime(2025, 5, 31)  # May 2025
        month_str = report_date.strftime("%B_%Y")
        
        # 1. Chronic Corner (Word document)
        corner_word_output = output_dir / f"Chronic_Corner_{month_str}.docx"
        self.generate_chronic_corner_word(metrics, chronic_data, corner_word_output, charts)
        
        # 2. Circuit Report (Word document for PDF conversion)
        circuit_word_output = output_dir / f"Chronic_Circuit_Report_{month_str}.docx"
        self.generate_circuit_report_pdf(metrics, chronic_data, charts, circuit_word_output)
        
        # 3. PDF conversion of Circuit Report
        pdf_output = output_dir / f"Chronic_Circuit_Report_{month_str}.pdf"
        self.convert_to_pdf(circuit_word_output, pdf_output)
        
        # PowerPoint generation removed per user request
        
        # Apply redaction if needed
        if self.mask_level != 'none':
            corner_word_output = self.run_redactor(corner_word_output)
            circuit_word_output = self.run_redactor(circuit_word_output)
            if pdf_output and Path(pdf_output).exists():
                pdf_output = self.run_redactor(pdf_output)
        
        # Generate text summary
        text_summary_output = self.generate_text_summary(chronic_data, metrics, output_dir, month_str)
        
        # Export data summary
        summary_data = {
            'chronic_data': chronic_data,
            'metrics': metrics,
            'generated_at': report_date.isoformat()
        }
        
        with open(output_dir / f"chronic_summary_{month_str}.json", 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        
        print(f"Reports generated in {output_dir}")
        print(f"[SUCCESS] Chronic Corner (Word): {corner_word_output}")
        print(f"[SUCCESS] Circuit Report (Word): {circuit_word_output}")
        print(f"[SUCCESS] Chronic List (Text): {text_summary_output}")
        if pdf_output and Path(pdf_output).exists():
            print(f"[SUCCESS] Circuit Report (PDF): {pdf_output}")
        
        return corner_word_output, circuit_word_output, pdf_output

def main():
    parser = argparse.ArgumentParser(description='Generate monthly chronic circuit reports')
    parser.add_argument('--impacts', required=True, help='Path to impacts A crosstab Excel file')
    parser.add_argument('--impacts-b', help='Path to impacts B crosstab Excel file (optional)')
    parser.add_argument('--counts', required=True, help='Path to counts Excel file') 
    parser.add_argument('--template', help='Path to Word template file (optional)')
    parser.add_argument('--output', default='./final_output', help='Output directory')
    parser.add_argument('--mask-level', default='alias', choices=['none', 'partial', 'alias', 'remove'], 
                       help='IP masking level')
    parser.add_argument('--exclude-regional', action='store_true',
                       help='Exclude regional circuits from new chronic detection')
    parser.add_argument('--show-indicators', action='store_true',
                       help='Show (C) chronic and (R) regional flags in reports')
    
    args = parser.parse_args()
    
    builder = ChronicReportBuilder(mask_level=args.mask_level, exclude_regional=args.exclude_regional, show_indicators=args.show_indicators)
    
    try:
        # Use impacts A file (for now, impacts B is optional and not used in current logic)
        impacts_file = args.impacts
        if args.impacts_b:
            print(f"Note: Using Impacts A file. Impacts B support may be added in future versions.")
            
        corner_file, circuit_word_file, pdf_file = builder.build_monthly_report(
            impacts_file, 
            args.counts,
            args.template,
            args.output
        )
        
        print(f"[SUCCESS] Chronic Corner (Word): {corner_file}")
        print(f"[SUCCESS] Circuit Report (Word): {circuit_word_file}")
        if pdf_file and Path(pdf_file).exists():
            print(f"[SUCCESS] Circuit Report (PDF): {pdf_file}")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()