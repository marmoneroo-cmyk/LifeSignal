"""OCR provider interface for scanned / photographed documents.

The local pdf_parser handles text-layer PDFs. Scanned images need a real OCR
service. This defines the contract; a concrete provider is added when credentials
exist (AZURE_DOCUMENT_INTELLIGENCE_KEY / GOOGLE_APPLICATION_CREDENTIALS).

Status: NOT ACTIVE — raises NotImplementedError until configured.
"""
from __future__ import annotations

from typing import Protocol


class OCRProvider(Protocol):
    def extract_text(self, data: bytes, content_type: str) -> str:
        """Return recognized text from an image/PDF byte blob."""
        ...


class AzureDocumentIntelligence:
    """Skeleton for Azure Document Intelligence.

    To implement:
      pip install azure-ai-documentintelligence
      set AZURE_DI_ENDPOINT and AZURE_DI_KEY
      call begin_analyze_document("prebuilt-read", body=data)
    """

    def __init__(self, endpoint: str | None = None, key: str | None = None) -> None:
        self.endpoint = endpoint
        self.key = key

    def extract_text(self, data: bytes, content_type: str) -> str:  # noqa: ARG002
        raise NotImplementedError(
            "Azure OCR is not configured. Provide AZURE_DI_ENDPOINT and AZURE_DI_KEY "
            "and implement extract_text() to enable scanned-document support."
        )
