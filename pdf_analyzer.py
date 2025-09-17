#!/usr/bin/env python3
"""
PDF analyzer to understand the structure of Xingrong English lesson PDFs
"""

import pdfplumber
import os
from typing import List, Dict, Any

def analyze_pdf_structure(pdf_path: str) -> Dict[str, Any]:
    """
    Analyze the structure of a PDF file to understand content layout
    """
    print(f"Analyzing PDF: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")
        
        # Analyze first few pages to understand structure
        analysis = {
            'total_pages': total_pages,
            'page_contents': []
        }
        
        # Start from page 2 as mentioned in requirements (0-indexed, so page 1)
        start_page = 1 if total_pages > 1 else 0
        
        for i in range(start_page, min(start_page + 3, total_pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            
            page_info = {
                'page_number': i + 1,
                'text': text,
                'words': page.extract_words(),
                'lines': page.extract_text_simple()
            }
            
            analysis['page_contents'].append(page_info)
            print(f"\n--- Page {i + 1} ---")
            print(f"Text length: {len(text) if text else 0}")
            if text:
                print("First 500 characters:")
                print(text[:500])
    
    return analysis

def main():
    """Main function to analyze PDF structure"""
    pdf_dir = "pdf"
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory '{pdf_dir}' not found")
        return
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the directory")
        return
    
    # Analyze the first PDF to understand structure
    first_pdf = pdf_files[0]
    pdf_path = os.path.join(pdf_dir, first_pdf)
    
    try:
        analysis = analyze_pdf_structure(pdf_path)
        print(f"\nAnalysis complete for {first_pdf}")
        
        # Save analysis to file for reference
        with open('pdf_analysis.txt', 'w', encoding='utf-8') as f:
            f.write(f"PDF Analysis: {first_pdf}\n")
            f.write("=" * 50 + "\n\n")
            
            for page_info in analysis['page_contents']:
                f.write(f"Page {page_info['page_number']}:\n")
                f.write("-" * 30 + "\n")
                f.write(page_info['text'])
                f.write("\n\n")
        
        print("Analysis saved to pdf_analysis.txt")
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")

if __name__ == "__main__":
    main()
