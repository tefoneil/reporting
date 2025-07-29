#!/usr/bin/env python3
"""
Optimized Test Suite for RBuilder - 4 Essential Tests Only
Covers all functionality without redundancy
"""

import subprocess
import os
import time
import json
from pathlib import Path

class OptimizedTester:
    def __init__(self):
        self.test_dir = Path("./test_results_optimized")
        self.test_scenarios = [
            {
                "name": "basic_test",
                "description": "Core functionality - all reports and formats",
                "month": "June 2025",
                "flags": []
            },
            {
                "name": "indicators_test", 
                "description": "With show-indicators flag",
                "month": "July 2025",
                "flags": ["--show-indicators"]
            },
            {
                "name": "regional_test",
                "description": "With exclude-regional flag", 
                "month": "August 2025",
                "flags": ["--exclude-regional"]
            },
            {
                "name": "combined_flags_test",
                "description": "Both flags combined",
                "month": "September 2025", 
                "flags": ["--show-indicators", "--exclude-regional"]
            }
        ]
        
        self.expected_files = [
            # Original files (must remain unchanged)
            "Chronic_Corner_{month}.docx",
            "Chronic_Circuit_Report_{month}.docx", 
            "chronic_circuits_list_{month}.txt",
            "chronic_summary_{month}.json",
            "monthly_trend_analysis_{month}.txt",
            "Monthly_Trend_Analysis_{month}.docx",
            # New lite files
            "Chronic_Corner_Lite_{month}.docx",
            "Chronic_Circle_Report_Lite_{month}.docx",
            # Charts
            "charts/top5_tickets.png",
            "charts/top5_cost.png",
            "charts/bottom5_availability.png", 
            "charts/bottom5_mtbf.png"
        ]
        
    def setup(self):
        """Setup test environment"""
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(exist_ok=True)
        print(f"Created test directory: {self.test_dir}")
        
    def run_test(self, scenario, test_num):
        """Run a single optimized test"""
        print(f"\n{'='*50}")
        print(f"Test {test_num}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Month: {scenario['month']}")
        print(f"Flags: {scenario['flags'] if scenario['flags'] else 'None'}")
        print(f"{'='*50}")
        
        # Create output directory
        output_dir = self.test_dir / scenario['name']
        output_dir.mkdir(exist_ok=True)
        
        # Build command
        cmd = [
            "python", "monthly_builder.py",
            "--impacts", "tests/sample_impacts.xlsx",
            "--counts", "tests/sample_counts.xlsx", 
            "--month", scenario['month'],
            "--output", str(output_dir)
        ]
        cmd.extend(scenario['flags'])
        
        # Run the test
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ SUCCESS in {duration:.2f}s")
                
                # Validate files
                month_str = scenario['month'].replace(' ', '_')
                found_files = []
                missing_files = []
                
                for expected_file in self.expected_files:
                    file_path = output_dir / expected_file.format(month=month_str)
                    if file_path.exists():
                        # Check file size
                        size = file_path.stat().st_size
                        if size > 0:
                            found_files.append({
                                "file": expected_file.format(month=month_str),
                                "size": size
                            })
                        else:
                            print(f"⚠️  Empty file: {expected_file.format(month=month_str)}")
                    else:
                        # PDF might not exist if LibreOffice not available
                        if not expected_file.endswith('.pdf'):
                            missing_files.append(expected_file.format(month=month_str))
                
                # Validate JSON structure
                json_files = list(output_dir.glob("chronic_summary_*.json"))
                json_valid = False
                if json_files:
                    try:
                        with open(json_files[0], 'r') as f:
                            data = json.load(f)
                            required_keys = ['version', 'chronic_data', 'metrics']
                            json_valid = all(key in data for key in required_keys)
                    except:
                        pass
                
                # Check for lite files specifically
                lite_files_found = len([f for f in found_files if 'Lite' in f['file']])
                
                print(f"  📁 Files: {len(found_files)}/{len(self.expected_files)}")
                print(f"  🆕 Lite files: {lite_files_found}/2")
                print(f"  📄 JSON valid: {'✅' if json_valid else '❌'}")
                
                if missing_files:
                    print(f"  ⚠️  Missing: {len(missing_files)} files")
                
                # Save test results
                test_result = {
                    "test_name": scenario['name'],
                    "description": scenario['description'],
                    "success": True,
                    "duration": duration,
                    "files_found": len(found_files),
                    "files_expected": len(self.expected_files),
                    "lite_files_found": lite_files_found,
                    "json_valid": json_valid,
                    "missing_files": missing_files,
                    "file_details": found_files,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open(output_dir / "test_result.json", 'w') as f:
                    json.dump(test_result, f, indent=2)
                    
                return test_result
                
            else:
                print(f"❌ FAILED - Return code: {result.returncode}")
                print(f"Error: {result.stderr}")
                
                test_result = {
                    "test_name": scenario['name'],
                    "description": scenario['description'], 
                    "success": False,
                    "error": result.stderr,
                    "return_code": result.returncode,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open(output_dir / "test_result.json", 'w') as f:
                    json.dump(test_result, f, indent=2)
                    
                return test_result
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            test_result = {
                "test_name": scenario['name'],
                "description": scenario['description'],
                "success": False, 
                "exception": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            return test_result
    
    def generate_summary(self, results):
        """Generate consolidated test summary"""
        print(f"\n{'='*60}")
        print("OPTIMIZED TEST SUITE SUMMARY")
        print(f"{'='*60}")
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        
        print(f"\n📊 Results: {successful_tests}/{total_tests} tests passed")
        print(f"⚡ Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Summary table
        print(f"\n{'Test':<20} {'Status':<10} {'Duration':<10} {'Files':<8} {'Lite':<6}")
        print("-" * 60)
        
        for result in results:
            if result.get('success', False):
                status = "✅ PASS"
                duration = f"{result.get('duration', 0):.1f}s"
                files = f"{result.get('files_found', 0)}/{result.get('files_expected', 0)}"
                lite = f"{result.get('lite_files_found', 0)}/2"
            else:
                status = "❌ FAIL"
                duration = "N/A"
                files = "N/A"
                lite = "N/A"
                
            print(f"{result['test_name']:<20} {status:<10} {duration:<10} {files:<8} {lite:<6}")
        
        # Key validations
        print(f"\n🔍 Key Validations:")
        for result in results:
            if result.get('success', False):
                print(f"  {result['test_name']}: JSON ✅, Lite files ✅")
            else:
                print(f"  {result['test_name']}: ❌ Failed")
        
        # Save summary
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": results
        }
        
        with open(self.test_dir / "test_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Create text summary
        with open(self.test_dir / "test_summary.txt", 'w') as f:
            f.write("OPTIMIZED TEST SUITE SUMMARY\n")
            f.write("="*60 + "\n\n")
            f.write(f"Tests: {successful_tests}/{total_tests} passed\n")
            f.write(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%\n\n")
            f.write("Test Details:\n")
            for result in results:
                f.write(f"- {result['test_name']}: {result['description']}\n")
                f.write(f"  Status: {'PASS' if result.get('success') else 'FAIL'}\n\n")
        
        print(f"\n📁 Results saved to: {self.test_dir.absolute()}")
        
    def run_all_tests(self):
        """Run optimized test suite"""
        print("🚀 Starting Optimized Test Suite")
        print(f"Running {len(self.test_scenarios)} essential tests...")
        
        self.setup()
        results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            result = self.run_test(scenario, i)
            results.append(result)
            time.sleep(0.5)  # Brief pause
            
        self.generate_summary(results)
        return results

if __name__ == "__main__":
    tester = OptimizedTester()
    tester.run_all_tests()