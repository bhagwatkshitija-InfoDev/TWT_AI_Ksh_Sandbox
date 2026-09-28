#!/usr/bin/env python3
"""Analyze document using Document QA Agent."""

import json
import sys
from pathlib import Path

sys.path.insert(0, 'D:\\TWT_AI')

from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer

file_path = r'D:\TWT_AI\TWT_AI_Course\Ksh files\XYZ_AirFryer_User_Guide_Chinese.docx'

# Process document
processor = ContentProcessor(file_path)
doc_data = processor.process_document()
print('=== DOCUMENT PROCESSING ===')
print(f'File Type: {doc_data.get("file_type")}')
print(f'Language: {doc_data.get("language")}')
print(f'Text Length: {len(doc_data.get("full_text", ""))} characters')

# Analyze document
analyzer = DocumentQualityAnalyzer(doc_data)
result = analyzer.analyze_complete()

print('\n=== ANALYSIS RESULTS ===')
print(f'Total Issues Found: {len(result["all_issues"])}')
print(f'Formatting Issues: {len(result["formatting_issues"])}')
print(f'Language Issues: {len(result["language_issues"])}')

print('\n=== SUMMARY ===')
print(result['summary'])

print('\n=== TOP 10 ISSUES BY SEVERITY ===')
for i, issue in enumerate(result['all_issues'][:10], 1):
    print(f"\n{i}. Issue object details:")
    print(f"   Type: {type(issue).__name__}")
    if hasattr(issue, '__dict__'):
        for attr, value in issue.__dict__.items():
            if not attr.startswith('_'):
                print(f"   {attr}: {value}")
    else:
        print(f"   Value: {issue}")
