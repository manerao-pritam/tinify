from pydantic import BaseModel, AnyHttpUrl

class URLToShorten(BaseModel):
    """Schema for shortening a URL."""
    url: AnyHttpUrl