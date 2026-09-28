#!/usr/bin/env python3
"""Analyze all documents in a folder using Document QA Agent."""

import json
import sys
from pathlib import Path

sys.path.insert(0, 'D:\\TWT_AI')

from claude_mcp_docqa_agent.document_processing.content_processor import ContentProcessor
from claude_mcp_docqa_agent.analysis.document_quality_analyzer import DocumentQualityAnalyzer
from claude_mcp_docqa_agent.utils.logger import get_logger

logger = get_logger(__name__)

folder_path = Path(r'D:\TWT_AI\TWT_AI_Course\Ksh files')
supported_extensions = {'.docx', '.pdf', '.md', '.txt'}

# Find all documents
documents = []
for ext in supported_extensions:
    documents.extend(folder_path.glob(f'*{ext}'))

print(f"Found {len(documents)} documents in {folder_path}\n")

if not documents:
    print("No documents found.")
    sys.exit(0)

# Analyze each document
results = []
for i, doc_path in enumerate(sorted(documents), 1):
    print(f"[{i}/{len(documents)}] Analyzing: {doc_path.name}")
    try:
        processor = ContentProcessor(str(doc_path))
        doc_data = processor.process_document()

        analyzer = DocumentQualityAnalyzer(doc_data)
        analysis_result = analyzer.analyze_complete()

        results.append({
            'file': doc_path.name,
            'path': str(doc_path),
            'file_type': doc_data.get('file_type'),
            'language': doc_data.get('language'),
            'text_length': len(doc_data.get('full_text', '')),
            'total_issues': len(analysis_result['all_issues']),
            'formatting_issues': len(analysis_result['formatting_issues']),
            'language_issues': len(analysis_result['language_issues']),
            'summary': analysis_result['summary'],
            'issues': analysis_result['all_issues'],
            'status': 'success'
        })
        print(f"  ✓ {len(analysis_result['all_issues'])} issues found\n")
    except Exception as e:
        logger.error(f"Error analyzing {doc_path.name}: {e}")
        results.append({
            'file': doc_path.name,
            'path': str(doc_path),
            'status': 'error',
            'error': str(e)
        })
        print(f"  ✗ Error: {e}\n")

# Generate summary report
print("\n" + "="*80)
print("FOLDER ANALYSIS SUMMARY REPORT")
print("="*80 + "\n")

print(f"Folder: {folder_path}")
print(f"Total Documents Analyzed: {len(results)}")
print(f"Successful: {sum(1 for r in results if r.get('status') == 'success')}")
print(f"Failed: {sum(1 for r in results if r.get('status') == 'error')}\n")

# Summary table
print("Document Analysis Overview:")
print("-" * 100)
print(f"{'File Name':<40} {'Language':<12} {'Issues':<8} {'Type':<12}")
print("-" * 100)

for result in results:
    if result.get('status') == 'success':
        file_name = result['file'][:37] + "..." if len(result['file']) > 40 else result['file']
        lang = result.get('language', 'Unknown')
        issues = result.get('total_issues', 0)
        file_type = result.get('file_type', 'Unknown').upper()
        print(f"{file_name:<40} {lang:<12} {issues:<8} {file_type:<12}")
    else:
        file_name = result['file'][:37] + "..." if len(result['file']) > 40 else result['file']
        print(f"{file_name:<40} {'ERROR':<12} {'-':<8} {'-':<12}")

print("-" * 100)

# Detailed issues per document
print("\n" + "="*80)
print("DETAILED ISSUES BY DOCUMENT")
print("="*80 + "\n")

for result in sorted(results, key=lambda x: x.get('total_issues', 0), reverse=True):
    if result.get('status') == 'error':
        print(f"\n❌ {result['file']}")
        print(f"   Error: {result.get('error', 'Unknown error')}\n")
        continue

    total = result.get('total_issues', 0)
    if total == 0:
        print(f"\n✅ {result['file']} ({result.get('language', 'Unknown')})")
        print(f"   No issues found - Document is well-formatted!\n")
        continue

    print(f"\n⚠️ {result['file']} ({result.get('language', 'Unknown')})")
    print(f"   File Type: {result.get('file_type', 'Unknown').upper()}")
    print(f"   Total Issues: {total} (Formatting: {result.get('formatting_issues', 0)}, Language: {result.get('language_issues', 0)})")

    # Show issues
    for j, issue in enumerate(result.get('issues', [])[:5], 1):
        if hasattr(issue, '__dict__'):
            issue_type = getattr(issue, 'issue_type', 'Unknown')
            severity = getattr(issue, 'severity', 'info')
            description = getattr(issue, 'issue_description', '')
            print(f"   {j}. [{severity.upper()}] {issue_type}: {description}")

    if len(result.get('issues', [])) > 5:
        print(f"   ... and {len(result.get('issues', [])) - 5} more issues")
    print()

# Statistics
print("\n" + "="*80)
print("STATISTICS")
print("="*80 + "\n")

successful_results = [r for r in results if r.get('status') == 'success']
if successful_results:
    total_issues = sum(r.get('total_issues', 0) for r in successful_results)
    avg_issues = total_issues / len(successful_results) if successful_results else 0

    # Group by language
    languages = {}
    for r in successful_results:
        lang = r.get('language', 'Unknown')
        if lang not in languages:
            languages[lang] = {'count': 0, 'issues': 0}
        languages[lang]['count'] += 1
        languages[lang]['issues'] += r.get('total_issues', 0)

    print(f"Total Issues Across All Documents: {total_issues}")
    print(f"Average Issues per Document: {avg_issues:.1f}\n")

    print("Issues by Language:")
    for lang, stats in sorted(languages.items()):
        print(f"  {lang}: {stats['count']} documents, {stats['issues']} total issues")

    print(f"\nClean Documents (0 issues): {sum(1 for r in successful_results if r.get('total_issues', 0) == 0)}")
    print(f"Documents with Issues: {sum(1 for r in successful_results if r.get('total_issues', 0) > 0)}")
