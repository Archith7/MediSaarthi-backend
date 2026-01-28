# -*- coding: utf-8 -*-
"""
Unit Normalization Mappings
Standardizes various unit formats to canonical units
"""

# Unit Mappings: raw_unit (lowercase) -> canonical_unit
UNIT_MAPPINGS = {
    # Volume
    "g/dl": "g/dL",
    "gm/dl": "g/dL",
    "gms/dl": "g/dL",
    "g%": "g/dL",
    "gm%": "g/dL",
    
    # Cell counts
    "mill/cu.mm": "million/µL",
    "million/ul": "million/µL",
    "million/cumm": "million/µL",
    "million/cmm": "million/µL",
    "x10^12/l": "million/µL",
    "x10^9/l": "×10⁹/L",
    
    "cells/cu.mm": "cells/µL",
    "cells/cumm": "cells/µL",
    "cells/cmm": "cells/µL",
    "cells/ul": "cells/µL",
    "/cumm": "cells/µL",
    "/cmm": "cells/µL",
    "/ul": "cells/µL",
    
    # Percentages
    "%": "%",
    "percent": "%",
    
    # Indices
    "fl": "fL",
    "pg": "pg",
    
    # Rate
    "mm/hr": "mm/hr",
    "mm/1st hr": "mm/hr",
    "mm in 1st hour": "mm/hr",
    
    # Concentration
    "mg/dl": "mg/dL",
    "mg/l": "mg/L",
    "mmol/l": "mmol/L",
    "µmol/l": "µmol/L",
    "umol/l": "µmol/L",
    "meq/l": "mEq/L",
    
    # Enzyme units
    "iu/l": "IU/L",
    "u/l": "U/L",
    "iu/ml": "IU/mL",
    "miu/l": "mIU/L",
    "miu/ml": "mIU/mL",
    "µiu/ml": "µIU/mL",
    "uiu/ml": "µIU/mL",
    
    # Thyroid specific
    "ng/dl": "ng/dL",
    "ng/ml": "ng/mL",
    "pg/ml": "pg/mL",
    "µg/dl": "µg/dL",
    "ug/dl": "µg/dL",
}


def normalize_unit(raw_unit: str) -> str:
    """
    Normalize unit to standard format
    Returns the canonical unit or original if not found
    """
    if not raw_unit:
        return ""
    
    cleaned = raw_unit.lower().strip()
    return UNIT_MAPPINGS.get(cleaned, raw_unit)
