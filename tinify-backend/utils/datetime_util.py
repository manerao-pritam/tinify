from datetime import datetime

# Format to use for datetime conversion (ISO 8601)
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

def datetime_to_str(dt: datetime) -> str:
    """Convert a datetime object to a string."""
    return dt.strftime(DATETIME_FORMAT) if isinstance(dt, datetime) else None

def str_to_datetime(dt_str: str) -> datetime:
    """Convert a string to a datetime object."""
    return datetime.strptime(dt_str, DATETIME_FORMAT) if dt_str else None