from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from pypdf import PdfWriter
from rest_framework.exceptions import ValidationError

from ..serializers import ContractCreateSerializer


class ContractPDFValidationTests(SimpleTestCase):
    def setUp(self):
        self.serializer = ContractCreateSerializer()

    def make_pdf(self, with_page=True):
        buffer = BytesIO()
        writer = PdfWriter()

        if with_page:
            writer.add_blank_page(width=595, height=842)

        writer.write(buffer)

        return SimpleUploadedFile(
            "contract.pdf",
            buffer.getvalue(),
            content_type="application/pdf",
        )

    def test_accepts_valid_pdf_and_resets_pointer(self):
        uploaded = self.make_pdf()

        result = self.serializer.validate_file(uploaded)

        self.assertIs(result, uploaded)
        self.assertEqual(result.tell(), 0)

    def test_rejects_empty_file(self):
        uploaded = SimpleUploadedFile(
            "empty.pdf",
            b"",
            content_type="application/pdf",
        )

        with self.assertRaisesMessage(
                ValidationError,
                "File is empty.",
        ):
            self.serializer.validate_file(uploaded)

    def test_rejects_large_file(self):
        uploaded = self.make_pdf()

        # بدون تخصیص واقعی بیش از ۵۰ مگابایت حافظه.
        uploaded.size = 50 * 1024 * 1024 + 1

        with self.assertRaisesMessage(
                ValidationError,
                "Maximum file size is 50 MB.",
        ):
            self.serializer.validate_file(uploaded)

    def test_rejects_non_pdf_extension(self):
        uploaded = SimpleUploadedFile(
            "contract.txt",
            b"Some text",
            content_type="text/plain",
        )

        with self.assertRaisesMessage(
                ValidationError,
                "Only PDF files are allowed.",
        ):
            self.serializer.validate_file(uploaded)

    def test_rejects_invalid_pdf_content(self):
        uploaded = SimpleUploadedFile(
            "contract.pdf",
            b"This is not a PDF.",
            content_type="application/pdf",
        )

        with self.assertRaisesMessage(
                ValidationError,
                "Invalid PDF file.",
        ):
            self.serializer.validate_file(uploaded)

    def test_rejects_pdf_without_pages(self):
        uploaded = self.make_pdf(with_page=False)

        with self.assertRaises(ValidationError):
            self.serializer.validate_file(uploaded)
