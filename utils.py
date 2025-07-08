#!/usr/bin/env python3
"""
Utility functions for the Monthly Reporting system
"""

import re
import json
import hashlib
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Any


def canonical_id(raw: str) -> str:
    """
    Extract canonical circuit ID using final v0.1.9 rules.
    
    Rules:
    1. Strip everything after first '_', '/', or ' '
    2. For digits-hyphen-letters suffix (e.g., 123-A), trim to digits only
    
    Examples:
    - "123-A_456" → "123"
    - "123-A" → "123" 
    - "VID-1583" → "VID-1583" (no change - doesn't match digits-hyphen-letters pattern)
    
    Args:
        raw: Raw circuit identifier string
        
    Returns:
        str: Canonical circuit identifier
    """
    if not raw or not isinstance(raw, str):
        return str(raw) if raw is not None else ""
    
    s = raw.strip()
    
    # 1) Strip everything after first _, /, or space
    for delimiter in ("_", "/", " "):
        if delimiter in s:
            s = s.split(delimiter, 1)[0]
    
    # 2) Digits-hyphen-letters suffix => trim (e.g., 123-A → 123)
    if re.match(r".*\d{3,}-[A-Za-z]{1,}$", s):
        s = s.split("-", 1)[0]
    
    return s


def warn_low_ticket_median(current_counts: List[int], previous_month_json_path: Optional[Path] = None) -> None:
    """
    Warn if ticket median drops significantly from previous month.
    
    Fires logging.warning if current median ≤ 1 and previous month median > 1.
    
    Args:
        current_counts: List of current month ticket counts
        previous_month_json_path: Path to previous month's JSON summary (optional)
    """
    if not current_counts:
        return
    
    current_median = statistics.median(current_counts)
    
    # Only warn if current median is low
    if current_median > 1:
        return
    
    # Try to get previous month's median
    previous_median = None
    if previous_month_json_path and previous_month_json_path.exists():
        try:
            with open(previous_month_json_path, 'r') as f:
                prev_data = json.load(f)
            
            # Extract raw ticket counts from circuit_ticket_data if available
            circuit_data = prev_data.get('chronic_data', {}).get('circuit_ticket_data', {})
            if circuit_data:
                prev_counts = [
                    data.get('raw_ticket_count_crosstab', 0) 
                    for data in circuit_data.values()
                    if isinstance(data, dict)
                ]
                if prev_counts:
                    previous_median = statistics.median(prev_counts)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.debug(f"Could not extract previous median from {previous_month_json_path}: {e}")
    
    # Fire warning if we have a significant drop
    if previous_median is not None and previous_median > 1:
        logging.warning(
            f"Low ticket median detected: current={current_median:.1f}, "
            f"previous={previous_median:.1f}. Data quality may be compromised."
        )


def validate_metadata(metadata: Dict) -> bool:
    """
    Validate that metadata contains all required keys.
    
    Args:
        metadata: Dictionary to validate
        
    Returns:
        bool: True if all required keys present
    """
    required_keys = {
        'tool_version', 'python_version', 'git_commit', 
        'run_timestamp', 'crosstab_sha256', 'counts_sha256'
    }
    
    missing_keys = required_keys - set(metadata.keys())
    if missing_keys:
        logging.error(f"Missing required metadata keys: {missing_keys}")
        return False
    
    return True


class SHA256Cache:
    """Simple file hash cache to avoid duplicate calculations."""
    
    def __init__(self):
        self._cache = {}
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        Get SHA256 hash of file, using cache if available.
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            str: SHA256 hash in hexadecimal
        """
        str_path = str(file_path)
        
        # Check cache first
        if str_path in self._cache:
            return self._cache[str_path]
        
        # Calculate hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        file_hash = sha256_hash.hexdigest()
        self._cache[str_path] = file_hash
        
        return file_hash


# Global SHA256 cache instance
_sha_cache = SHA256Cache()


def get_file_sha256(file_path: Path) -> str:
    """
    Get SHA256 hash of a file (cached).
    
    Args:
        file_path: Path to file
        
    Returns:
        str: SHA256 hash in hexadecimal
    """
    return _sha_cache.get_file_hash(file_path)


def validate_calculations(metrics: Dict[str, Any]) -> None:
    """
    Validate calculation results to catch impossible values.
    Raises ValueError if any critical validation fails.
    
    Args:
        metrics: Dictionary containing calculated metrics
        
    Raises:
        ValueError: If any availability is outside 0-100% range
    """
    # Check availability values
    if 'bottom5_availability' in metrics:
        for circuit, availability in metrics['bottom5_availability'].items():
            if availability < 0 or availability > 100:
                raise ValueError(f"Invalid availability for {circuit}: {availability:.1f}% (must be 0-100%)")
    
    # Check MTBF values for reasonableness  
    if 'bottom5_mtbf' in metrics:
        for circuit, mtbf_days in metrics['bottom5_mtbf'].items():
            if mtbf_days < 0:
                raise ValueError(f"Invalid MTBF for {circuit}: {mtbf_days:.1f} days (must be positive)")
    
    logging.info("✅ Calculation validation passed")


def filter_test_circuits(df, circuit_column='Config Item Name'):
    """
    Filter out CID_TEST circuits from any DataFrame.
    
    Args:
        df: DataFrame to filter
        circuit_column: Name of the column containing circuit IDs
        
    Returns:
        DataFrame with test circuits removed
    """
    if circuit_column not in df.columns:
        return df
    
    initial_count = len(df)
    # Filter CID_TEST circuits
    test_filter = df[circuit_column].str.startswith('CID_TEST', na=False)
    filtered_df = df[~test_filter]
    
    filtered_count = initial_count - len(filtered_df)
    if filtered_count > 0:
        logging.info(f"Filtered out {filtered_count} test circuits from data")
    
    return filtered_df


def format_circuit_display_name(circuit_id: str) -> str:
    """
    Format circuit ID for display by prepending provider name for abbreviated IDs.
    
    v0.1.9-rc6: Enhanced with authoritative vendor mapping from circuit inventory.
    
    Args:
        circuit_id: Raw circuit identifier
        
    Returns:
        str: Display-formatted circuit identifier with provider prefix if needed
    """
    if not circuit_id or not isinstance(circuit_id, str):
        return str(circuit_id) if circuit_id else ""
    
    # v0.1.9-rc6: Authoritative vendor mappings from circuit inventory
    # These override pattern-based guessing with actual ServiceNow data
    inventory_vendors = {
        'SR216187': 'PCCW',
        'PTH TOK EPL 90030025': 'Telstra',
        'LZA010663': 'NTT',
        '500332738': 'Cirion',
        '500334193': 'Cirion', 
        '500335805': 'Cirion',
        '091NOID1143035717419_889599': 'TATA',
        '091NOID1143035717849_889621': 'TATA',
        'LD017936': 'Orange',
        'IST6041E#3_010G': 'Globenet',
        'IST6022E#2_010G': 'Globenet',
        'W1E32092': 'Verizon',
        'N9675474L': 'Telstra',
        'N2864477L': 'Telstra'
    }
    
    # Check inventory first
    if circuit_id in inventory_vendors:
        vendor = inventory_vendors[circuit_id]
        if not circuit_id.startswith(vendor):
            return f"{vendor} {circuit_id}"
        return circuit_id
    
    # Fallback to pattern-based mapping for circuits not in inventory
    provider_prefixes = {
        'PTH': 'Telstra',       # PTH TOK EPL 90030025 -> Telstra PTH TOK EPL 90030025
        'W1E': 'Verizon',       # W1E32092 -> Verizon W1E32092
        'N96': 'Telstra',       # N9675474L -> Telstra N9675474L
        'N28': 'Telstra',       # N2864477L -> Telstra N2864477L
        'VID': 'Media',         # VID-1583 -> Media VID-1583
        'IST': 'GTT',           # IST6022E#2_010G -> GTT IST6022E#2_010G
        'HI/': 'GTT',           # HI/ADM/00697867 -> GTT HI/ADM/00697867
        'SR2': 'PCCW',          # SR216187 -> PCCW SR216187
        'SSO': 'Sansa',         # SSO-JBTKRHS002F-DWDM10 -> Sansa SSO-JBTKRHS002F-DWDM10
        'FRO': 'Lumen',         # FRO2007133508 -> Lumen FRO2007133508
        'LZA': 'NTT',           # LZA010663 -> NTT LZA010663
        'LD0': 'NTT'            # LD017936 -> NTT LD017936
    }
    
    # Check if circuit starts with any known abbreviation
    for prefix, provider in provider_prefixes.items():
        if circuit_id.startswith(prefix):
            # Only add provider if not already present
            if not circuit_id.startswith(provider):
                return f"{provider} {circuit_id}"
            break
    
    return circuit_id