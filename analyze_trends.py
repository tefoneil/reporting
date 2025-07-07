#!/usr/bin/env python3
"""
Monthly Chronic Circuit Trend Analysis
Analyzes patterns and changes between monthly reports
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

def load_monthly_data(output_dir: str = './final_output') -> Dict[str, Dict]:
    """Load all available monthly JSON reports"""
    output_path = Path(output_dir)
    monthly_data = {}
    
    if output_path.exists():
        json_files = list(output_path.glob('chronic_summary_*.json'))
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Extract month from filename
                month_key = json_file.name.replace('chronic_summary_', '').replace('.json', '')
                monthly_data[month_key] = data
                
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    return monthly_data

def analyze_ticket_trends(monthly_data: Dict[str, Dict]) -> Dict[str, Any]:
    """Analyze ticket count trends across months"""
    trends = {
        'circuit_changes': {},
        'overall_stats': {},
        'top_movers': {'increased': [], 'decreased': []},
        'threshold_crossings': {'became_consistent': [], 'became_inconsistent': []}
    }
    
    months = sorted(monthly_data.keys())
    
    for i in range(len(months) - 1):
        current_month = months[i]
        next_month = months[i + 1]
        
        current_data = monthly_data[current_month].get('chronic_data', {}).get('circuit_ticket_data', {})
        next_data = monthly_data[next_month].get('chronic_data', {}).get('circuit_ticket_data', {})
        
        comparison_key = f"{current_month}_to_{next_month}"
        trends['circuit_changes'][comparison_key] = []
        
        # Analyze each circuit's changes
        all_circuits = set(current_data.keys()) | set(next_data.keys())
        
        for circuit in all_circuits:
            current_tickets = current_data.get(circuit, {}).get('rolling_ticket_total', 0)
            next_tickets = next_data.get(circuit, {}).get('rolling_ticket_total', 0)
            current_status = current_data.get(circuit, {}).get('status', 'unknown')
            next_status = next_data.get(circuit, {}).get('status', 'unknown')
            
            change = next_tickets - current_tickets
            
            circuit_change = {
                'circuit': circuit,
                'tickets_before': current_tickets,
                'tickets_after': next_tickets,
                'change': change,
                'percent_change': (change / current_tickets * 100) if current_tickets > 0 else 0,
                'status_before': current_status,
                'status_after': next_status,
                'status_changed': current_status != next_status
            }
            
            trends['circuit_changes'][comparison_key].append(circuit_change)
            
            # Track significant movers
            if abs(change) >= 5:  # 5+ ticket change threshold
                if change > 0:
                    trends['top_movers']['increased'].append(circuit_change)
                else:
                    trends['top_movers']['decreased'].append(circuit_change)
            
            # Track threshold crossings (6 ticket consistency threshold)
            if current_status != next_status:
                if current_status == 'inconsistent' and next_status == 'consistent':
                    trends['threshold_crossings']['became_consistent'].append(circuit_change)
                elif current_status == 'consistent' and next_status == 'inconsistent':
                    trends['threshold_crossings']['became_inconsistent'].append(circuit_change)
    
    return trends

def analyze_availability_trends(monthly_data: Dict[str, Dict]) -> Dict[str, Any]:
    """Analyze availability trends across months"""
    availability_trends = {}
    months = sorted(monthly_data.keys())
    
    for i in range(len(months) - 1):
        current_month = months[i]
        next_month = months[i + 1]
        
        current_avail = monthly_data[current_month].get('metrics', {}).get('bottom5_availability', {})
        next_avail = monthly_data[next_month].get('metrics', {}).get('bottom5_availability', {})
        
        comparison_key = f"{current_month}_to_{next_month}"
        availability_trends[comparison_key] = []
        
        # Find circuits in both months for comparison
        common_circuits = set(current_avail.keys()) & set(next_avail.keys())
        
        for circuit in common_circuits:
            current_val = current_avail[circuit]
            next_val = next_avail[circuit]
            change = next_val - current_val
            
            availability_trends[comparison_key].append({
                'circuit': circuit,
                'availability_before': current_val,
                'availability_after': next_val,
                'change': change,
                'improved': change > 0
            })
    
    return availability_trends

def generate_trend_summary(monthly_data: Dict[str, Dict]) -> str:
    """Generate written summary of trends"""
    if len(monthly_data) < 2:
        return "Insufficient data for trend analysis. Need at least 2 months of data."
    
    ticket_trends = analyze_ticket_trends(monthly_data)
    availability_trends = analyze_availability_trends(monthly_data)
    
    months = sorted(monthly_data.keys())
    latest_comparison = f"{months[-2]}_to_{months[-1]}"
    
    summary = []
    summary.append("# MONTHLY CHRONIC CIRCUIT TREND ANALYSIS")
    summary.append("=" * 50)
    summary.append(f"Analysis Period: {months[-2].replace('_', ' ')} → {months[-1].replace('_', ' ')}")
    summary.append("")
    
    # Overall metrics comparison
    prev_metrics = monthly_data[months[-2]].get('metrics', {})
    curr_metrics = monthly_data[months[-1]].get('metrics', {})
    
    total_change = curr_metrics.get('total_chronic_circuits', 0) - prev_metrics.get('total_chronic_circuits', 0)
    
    summary.append("## EXECUTIVE SUMMARY")
    summary.append(f"• Total chronic circuits: {prev_metrics.get('total_chronic_circuits', 0)} → {curr_metrics.get('total_chronic_circuits', 0)} ({total_change:+d})")
    summary.append(f"• New chronics identified: {curr_metrics.get('new_chronic_count', 0)}")
    summary.append(f"• Media chronics: {curr_metrics.get('media_chronics', 0)}")
    summary.append("")
    
    # Ticket count trends
    if latest_comparison in ticket_trends['circuit_changes']:
        changes = ticket_trends['circuit_changes'][latest_comparison]
        
        # Sort by absolute change for most significant movers
        significant_changes = [c for c in changes if abs(c['change']) >= 2]
        significant_changes.sort(key=lambda x: abs(x['change']), reverse=True)
        
        summary.append("## TICKET VOLUME TRENDS")
        
        if significant_changes:
            summary.append("### Most Significant Changes (≥2 tickets):")
            for change in significant_changes[:10]:  # Top 10
                direction = "↑" if change['change'] > 0 else "↓"
                circuit_clean = change['circuit'].split(' ')[0]  # Remove indicators
                summary.append(f"• {circuit_clean}: {change['tickets_before']} → {change['tickets_after']} ({change['change']:+d}) {direction}")
        
        # Status changes
        status_changes = [c for c in changes if c['status_changed']]
        if status_changes:
            summary.append("")
            summary.append("### Status Changes:")
            for change in status_changes:
                circuit_clean = change['circuit'].split(' ')[0]
                summary.append(f"• {circuit_clean}: {change['status_before']} → {change['status_after']} ({change['tickets_after']} tickets)")
        
        # Calculate averages
        total_tickets_before = sum(c['tickets_before'] for c in changes)
        total_tickets_after = sum(c['tickets_after'] for c in changes)
        avg_change = (total_tickets_after - total_tickets_before) / len(changes) if changes else 0
        
        summary.append("")
        summary.append(f"### Overall Ticket Trend: {avg_change:+.1f} tickets per circuit average")
        summary.append("")
    
    # Availability trends
    if latest_comparison in availability_trends:
        avail_changes = availability_trends[latest_comparison]
        avail_changes.sort(key=lambda x: x['change'], reverse=True)
        
        summary.append("## AVAILABILITY TRENDS")
        improved_count = len([c for c in avail_changes if c['improved']])
        degraded_count = len(avail_changes) - improved_count
        
        summary.append(f"• Circuits with improved availability: {improved_count}")
        summary.append(f"• Circuits with degraded availability: {degraded_count}")
        
        if avail_changes:
            summary.append("")
            summary.append("### Notable Availability Changes:")
            for change in avail_changes[:5]:  # Top 5 changes
                direction = "↑" if change['improved'] else "↓"
                circuit_clean = change['circuit'].split(' ')[0]
                summary.append(f"• {circuit_clean}: {change['availability_before']:.1f}% → {change['availability_after']:.1f}% ({change['change']:+.1f}%) {direction}")
        summary.append("")
    
    # Top performers comparison
    prev_top5 = prev_metrics.get('top5_tickets', {})
    curr_top5 = curr_metrics.get('top5_tickets', {})
    
    summary.append("## TOP TICKET GENERATORS COMPARISON")
    summary.append("### Previous Month:")
    for i, (circuit, count) in enumerate(list(prev_top5.items())[:5], 1):
        circuit_clean = circuit.split(' ')[0]
        summary.append(f"{i}. {circuit_clean}: {count} tickets")
    
    summary.append("")
    summary.append("### Current Month:")
    for i, (circuit, count) in enumerate(list(curr_top5.items())[:5], 1):
        circuit_clean = circuit.split(' ')[0]
        summary.append(f"{i}. {circuit_clean}: {count} tickets")
    
    summary.append("")
    
    # Recommendations
    summary.append("## RECOMMENDATIONS")
    
    if significant_changes:
        increasing_circuits = [c for c in significant_changes if c['change'] > 0]
        if increasing_circuits:
            summary.append("### Priority Actions:")
            for circuit in increasing_circuits[:3]:  # Top 3 increasing
                circuit_clean = circuit['circuit'].split(' ')[0]
                summary.append(f"• Investigate {circuit_clean} - ticket volume increased by {circuit['change']} tickets")
    
    status_improvements = [c for c in status_changes if c['status_after'] == 'consistent']
    if status_improvements:
        summary.append("")
        summary.append("### Success Stories:")
        for circuit in status_improvements:
            circuit_clean = circuit['circuit'].split(' ')[0]
            summary.append(f"• {circuit_clean} promoted to Consistent status with {circuit['tickets_after']} tickets")
    
    summary.append("")
    summary.append("### General Recommendations:")
    if avg_change > 1:
        summary.append("• Overall ticket volumes are increasing - consider proactive maintenance review")
    elif avg_change < -1:
        summary.append("• Overall ticket volumes are decreasing - maintenance efforts showing positive impact")
    else:
        summary.append("• Ticket volumes remain stable - continue current monitoring approach")
    
    return "\n".join(summary)

def main():
    """Main analysis function"""
    monthly_data = load_monthly_data()
    
    if not monthly_data:
        print("No monthly data found in ./final_output/")
        return
    
    print(f"Loaded data for months: {', '.join(sorted(monthly_data.keys()))}")
    
    # Generate trend summary
    summary = generate_trend_summary(monthly_data)
    
    # Save to file
    output_path = Path('./final_output/monthly_trend_analysis.txt')
    with open(output_path, 'w') as f:
        f.write(summary)
    
    print(f"\nTrend analysis saved to: {output_path}")
    print("\n" + "="*50)
    print(summary)

if __name__ == "__main__":
    main()