import sys
sys.path.insert(0, 'd:/All-of-projects/RayaHosh/First/Step2-Preprocessing/src')
from preprocessing.text_extractor import TextExtractor

ext = TextExtractor()

# Try to find the actual Proposal.docx
import glob
files = glob.glob('d:/All-of-projects/RayaHosh/First/**/*.docx', recursive=True)
print("DOCX files found:")
for f in files:
    print(f"  {f}")

# Extract from first real docx if exists
for f in files:
    if 'test_proposal' not in f:
        result = ext.extract(f)
        text = result.get('text', '')
        print(f"\nFile: {f}")
        print(f"Text length: {len(text)} chars")
        print(f"First 800 chars:\n{text[:800]}")
        break
