"""
Entity Resolution and Address Standardization Module.
Standardizes street addresses and calculates similarity scores to link
unlicensed sober living residences, group home dockets, and corporate LLCs
to licensed DHCS/OHA treatment centers.
"""

import re
from typing import Dict, Any, Tuple
from fuzzywuzzy import fuzz

# Common street suffixes and standardization map
STREET_ABBREVIATIONS = {
    "AVENUE": "AVE",
    "BOULEVARD": "BLVD",
    "DRIVE": "DR",
    "STREET": "ST",
    "ROAD": "RD",
    "LANE": "LN",
    "COURT": "CT",
    "CIRCLE": "CIR",
    "HIGHWAY": "HWY",
    "PARKWAY": "PKWY",
    "PLACE": "PL",
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
    "SUITE": "STE",
    "APARTMENT": "APT",
    "UNIT": "UNIT",
    "BUILDING": "BLDG",
}


class AddressStandardizer:
    """Cleans and standardizes US street addresses for exact and fuzzy joins."""

    @staticmethod
    def normalize_address(address_str: str) -> str:
        if not address_str:
            return ""
        # Uppercase, remove punctuation
        clean = address_str.upper()
        clean = re.sub(r"[#\.,]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        tokens = clean.split()
        normalized_tokens = [STREET_ABBREVIATIONS.get(t, t) for t in tokens]
        return " ".join(normalized_tokens)


class EntityMatcher:
    """Calculates fuzzy matching confidence across facility names and operators."""

    @staticmethod
    def match_names(name1: str, name2: str) -> int:
        """Token sort ratio for robust legal entity matching (e.g. 'Pacifica Recovery LLC' vs 'Pacifica Recovery Inc')."""
        if not name1 or not name2:
            return 0
        return fuzz.token_sort_ratio(name1.upper(), name2.upper())

    @staticmethod
    def is_match(name1: str, addr1: str, name2: str, addr2: str, threshold: int = 85) -> Tuple[bool, int]:
        """Evaluate whether two records represent the same or affiliated facility."""
        clean_addr1 = AddressStandardizer.normalize_address(addr1)
        clean_addr2 = AddressStandardizer.normalize_address(addr2)

        name_score = EntityMatcher.match_names(name1, name2)
        addr_match = (clean_addr1 == clean_addr2) and (clean_addr1 != "")

        if addr_match and name_score >= 70:
            return True, max(name_score, 95)
        if name_score >= threshold:
            return True, name_score
        return False, name_score

