import io

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """Read a PDF file (from Streamlit's file uploader) and return its plain text.

    Safe to call on repeated Streamlit reruns: the stream is rewound before
    reading, so a second call does not silently return empty text.
    """
    try:
        uploaded_file.seek(0)
    except (AttributeError, OSError, ValueError):
        # Not a seekable stream - carry on and read whatever is available.
        pass

    data = uploaded_file.read()

    if not data:
        raise ValueError(
            "The uploaded PDF could not be read (empty file). Please re-upload the file."
        )

    reader = PdfReader(io.BytesIO(data))
    pages = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(pages).strip()

    if not text:
        raise ValueError(
            "No selectable text found in this PDF - it looks like a scanned image. "
            "Please upload a text-based PDF, or run OCR on it first."
        )

    return text