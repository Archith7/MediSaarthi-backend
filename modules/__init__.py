# Modules package
try:
    from .ocr_module import extract_ocr_data, process_image_file
except ImportError:
    extract_ocr_data = None
    process_image_file = None

from .normalization_engine import NormalizationEngine, normalize_ocr_output
from .database import DatabaseManager, get_db_manager
from .query_engine import QueryEngine, process_natural_query
# from .response_generator import ResponseGenerator, generate_response  # Temporarily disabled due to syntax error

__all__ = [
    'extract_ocr_data',
    'process_image_file',
    'NormalizationEngine',
    'normalize_ocr_output',
    'DatabaseManager',
    'get_db_manager',
    'QueryEngine',
    'process_natural_query',
    'ResponseGenerator',
    'generate_response'
]

