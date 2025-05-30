"""
Helper functions for Music Sync Hub.

This module contains utility functions used across the application.
"""

import re
from typing import Optional


def slugify(value: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        value: The string to slugify
        
    Returns:
        A slugified version of the input string
    """
    value = str(value).strip().lower()
    # Replace non-alphanumeric characters with hyphens
    value = re.sub(r'[^a-z0-9]+', '-', value)
    # Remove leading/trailing hyphens
    value = re.sub(r'^-+|-+$', '', value)
    return value


def format_duration(milliseconds: Optional[int]) -> str:
    """
    Format duration from milliseconds to MM:SS format.
    
    Args:
        milliseconds: Duration in milliseconds
        
    Returns:
        Formatted duration string or 'Unknown' if None
    """
    if milliseconds is None:
        return "Unknown"
    
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def safe_get(data: dict, *keys: str, default: str = "Unknown") -> str:
    """
    Safely get nested dictionary values with a default fallback.
    
    Args:
        data: The dictionary to search
        *keys: The keys to traverse
        default: Default value if key not found
        
    Returns:
        The value if found, otherwise the default
    """
    try:
        for key in keys:
            data = data[key]
        return data if data is not None else default
    except (KeyError, TypeError, AttributeError):
        return default


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: The text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..." 