"""Pre-download the local embedding model for demo day."""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

from memory_pod.config import DEFAULT_MODEL_NAME


def main() -> None:
    SentenceTransformer(DEFAULT_MODEL_NAME)
    print(f"Downloaded or verified local cache for {DEFAULT_MODEL_NAME}.")


if __name__ == "__main__":
    main()

