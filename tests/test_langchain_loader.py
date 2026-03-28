from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from hads.langchain import HADSLoader, load_hads
from hads.parser import parse


class HADSLoaderIntegrationTest(unittest.TestCase):
    def test_loader_emits_one_document_per_hads_block(self) -> None:
        text = textwrap.dedent(
            """\
            # Example API
            **Version 1.2.3**

            Short description.

            ## AI READING INSTRUCTION

            Use SPEC and BUG blocks for retrieval.

            ## Authentication

            **[SPEC]**
            Use bearer tokens for authenticated requests.

            Operators may keep a local test token for staging.

            **[BUG]**
            Symptom: Tokens expire early under clock skew.
            Fix: Refresh the token before retrying the request.

            ## Limits

            **[SPEC]**
            Rate limits are 10 requests per second.
            """
        )

        parsed = parse(text)

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "example.md"
            path.write_text(text, encoding="utf-8")

            docs = HADSLoader(str(path)).load()

            self.assertEqual(len(docs), len(parsed.blocks))
            self.assertEqual(
                [doc.page_content for doc in docs],
                [block.content for block in parsed.blocks],
            )

            for doc, block in zip(docs, parsed.blocks):
                self.assertEqual(
                    doc.metadata,
                    {
                        "source": str(path),
                        "block_type": block.type,
                        "section": block.section,
                        "hads_version": parsed.version,
                        "document_name": parsed.name,
                        "line_start": block.line_start,
                        "line_end": block.line_end,
                    },
                )

            filtered_docs = load_hads(str(path), block_types=["[SPEC]", "bug"])
            self.assertEqual(
                [doc.metadata["block_type"] for doc in filtered_docs],
                ["SPEC", "BUG", "SPEC"],
            )


if __name__ == "__main__":
    unittest.main()
