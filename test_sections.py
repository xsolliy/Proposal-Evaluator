import sys
sys.path.insert(0, 'd:/All-of-projects/RayaHosh/First/Step2-Preprocessing/src')
from preprocessing.pipeline import PreprocessingPipeline

p = PreprocessingPipeline()
r = p.process('d:/All-of-projects/RayaHosh/First/test_proposal.docx')
fo = r.get('final_output', {})

import json
with open('test_sections_output.json', 'w', encoding='utf-8') as f:
    # sections from pipeline (sections_result)
    sec_result = r.get('sections', {})
    json.dump({
        'final_output_sections': fo.get('sections', {}),
        'sections_result_sections': sec_result.get('sections', {}),
        'detected_sections': sec_result.get('detected_sections', []),
        'missing_required': sec_result.get('missing_required', []),
        'completeness_score': sec_result.get('completeness_score', 0),
        'normalized_text_preview': fo.get('normalized_text', '')[:500],
        'raw_text_preview': fo.get('raw_text', '')[:500],
    }, f, ensure_ascii=False, indent=2)

print("Done - check test_sections_output.json")
