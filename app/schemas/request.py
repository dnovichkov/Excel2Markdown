"""Request schemas for API endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ConversionOptions(BaseModel):
    """Options for file conversion."""

    use_headers: bool = Field(
        default=True,
        description="Treat first row as headers",
    )
    output_format: Literal["markdown", "json"] = Field(
        default="markdown",
        description="Output format for conversion",
    )
