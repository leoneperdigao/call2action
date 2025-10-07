"""Debug script to test the summarizer with batch processing."""

from call2action.config import Settings
from call2action.summarizer import Summarizer

# Create a simple test transcript
test_transcript = """
This is a test meeting transcript. We discussed the architecture of our new system.
John mentioned that we need to implement a REST API. Sarah suggested using FastAPI framework.
The team agreed to use PostgreSQL for the database. We need to start development next week.
Mike will be responsible for the backend, and Lisa will handle the frontend.
""" * 5  # Repeat to make it longer

settings = Settings()
summarizer = Summarizer(settings)

print("Testing summarizer with batch processing...")
print(f"Transcript length: {len(test_transcript)} characters")

summary = summarizer.generate_summary(test_transcript)

print(f"\n{'='*60}")
print(f"Summary length: {len(summary)} characters")
print(f"Summary content:")
print(f"{'='*60}")
print(summary)
print(f"{'='*60}")
