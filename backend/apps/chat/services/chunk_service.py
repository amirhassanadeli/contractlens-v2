from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from django.conf import settings


class ChunkService:

    @staticmethod
    def split_documents(documents: list[Document]) -> list[Document]:
        # Separators optimized for legal / contract documents
        # (English + Persian)
        separators = [
            "\n\n\n",
            "\n\n",
            "\n",

            # Common legal section markers
            "Article ",
            "ARTICLE ",
            "Section ",
            "SECTION ",
            "Clause ",
            "CLAUSE ",
            "ماده ",
            "بند ",
            "تبصره ",

            ". ",
            "؟ ",
            "? ",
            "! ",

            ".",
            "؟",
            "?",
            "!",

            "، ",
            ", ",
            "؛ ",
            "; ",
            ": ",

            "،",
            "؛",

            " ",
            "\u200c",  # Zero-width non-joiner (Persian)

            "",
        ]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=separators,
            keep_separator=True,
            is_separator_regex=False,
        )

        chunks = splitter.split_documents(documents)

        for index, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": index,
                "chunk_size": len(chunk.page_content),
            })

        return chunks
