#!/usr/bin/env python3
"""
PDF parser for Xingrong English lesson PDFs
Extracts Chinese, English, and phonetic content from page 2 onwards
"""

import pdfplumber
import re
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class VocabularyCard:
    """Represents a vocabulary card with Chinese, English, and phonetic"""
    chinese: str
    english: str
    phonetic: Optional[str] = None
    
    def __str__(self):
        return f"Chinese: {self.chinese}, English: {self.english}, Phonetic: {self.phonetic}"

class XingrongPDFParser:
    """Parser for Xingrong English lesson PDFs"""
    
    def __init__(self):
        self.cards: List[VocabularyCard] = []
        
    def extract_text_from_pdf(self, pdf_path: str, start_page: int = 1) -> str:
        """
        Extract text from PDF starting from specified page
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) <= start_page:
                    print(f"PDF has only {len(pdf.pages)} pages, cannot start from page {start_page + 1}")
                    return ""
                
                # Extract text from pages starting from start_page (0-indexed)
                full_text = ""
                for i in range(start_page, len(pdf.pages)):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                return full_text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def parse_vocabulary_content(self, text: str) -> List[VocabularyCard]:
        """
        Parse vocabulary content from text
        Look for patterns of Chinese, English, and phonetic text
        """
        cards = []
        lines = text.split('\n')
        
        # Remove empty lines and clean up
        lines = [line.strip() for line in lines if line.strip()]
        
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip headers and non-vocabulary content
            if self._is_header_line(line):
                i += 1
                continue
            
            # Look for Chinese text (contains Chinese characters)
            if self._contains_chinese(line):
                # First, try to parse the line as a complete vocabulary entry
                # Format: "中文 英文 /音标/" or "中文 英文"
                if self._contains_english(line) and self._contains_phonetic(line):
                    # Single line format: "中文 英文 /音标/"
                    chinese, english, phonetic = self._parse_single_line_vocabulary(line)
                    if chinese and english:
                        card = VocabularyCard(
                            chinese=chinese,
                            english=english,
                            phonetic=phonetic if phonetic else None
                        )
                        cards.append(card)
                        print(f"Found single-line card: {card}")
                        i += 1
                        continue
                
                # If single line parsing didn't work, try multi-line format
                chinese = line.strip()
                english = ""
                phonetic = ""
                
                # Check next few lines for English and phonetic
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j]
                    
                    # Skip header lines
                    if self._is_header_line(next_line):
                        continue
                    
                    # If we hit another Chinese line, stop
                    if self._contains_chinese(next_line) and not english:
                        break
                    
                    # Check if line contains English (Latin characters)
                    if self._contains_english(next_line) and not english:
                        english = next_line.strip()
                    
                    # Check if line contains phonetic symbols (brackets or slashes)
                    elif self._contains_phonetic(next_line):
                        phonetic = next_line.strip()
                
                if chinese and english:
                    card = VocabularyCard(
                        chinese=chinese,
                        english=english,
                        phonetic=phonetic if phonetic else None
                    )
                    cards.append(card)
                    print(f"Found multi-line card: {card}")
                
                # Move to next potential vocabulary item
                i += 1
            else:
                i += 1
        
        return cards
    
    def _parse_single_line_vocabulary(self, line: str) -> tuple:
        """
        Parse a single line that contains Chinese, English, and phonetic
        Format: "中文 英文 /音标/" or "中文 英文"
        """
        try:
            # Split by spaces and extract components
            parts = line.split()
            
            chinese_parts = []
            english_parts = []
            phonetic_parts = []
            
            for part in parts:
                # Check if part contains Chinese characters
                if self._contains_chinese(part):
                    chinese_parts.append(part)
                # Check if part contains phonetic symbols
                elif self._contains_phonetic(part):
                    phonetic_parts.append(part)
                # Otherwise, treat as English
                else:
                    english_parts.append(part)
            
            chinese = ' '.join(chinese_parts) if chinese_parts else ""
            english = ' '.join(english_parts) if english_parts else ""
            phonetic = ' '.join(phonetic_parts) if phonetic_parts else ""
            
            return chinese, english, phonetic
            
        except Exception as e:
            print(f"Error parsing single line vocabulary '{line}': {e}")
            return "", "", ""
    
    def _is_header_line(self, line: str) -> bool:
        """Check if line is a header or non-vocabulary content"""
        # More specific header patterns to avoid filtering vocabulary lines
        header_patterns = [
            '第.*课',  # 第X课
            'lesson', 
            'page',
            '星荣英语笔记',
            '你好，我是星荣',
            '微信：xingrong-english',
            '公众号：Hi要大声说出来',
            '祝好运！',
            '中文 英文 K.K.音标',  # Table header
            '这是零基础学英语系列',
            '上一节课的内容',
            '非常感谢大家的订阅',
            '你们的支持是我更新的动力'
        ]
        
        # Check for header patterns
        for pattern in header_patterns:
            if pattern in line:
                return True
        
        # Skip lines that are too long (likely paragraphs)
        if len(line) > 100:
            return True
            
        # Skip lines that are just numbers
        if line.strip().isdigit():
            return True
            
        return False
    
    def _contains_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        return bool(chinese_pattern.search(text))
    
    def _contains_english(self, text: str) -> bool:
        """Check if text contains English characters"""
        english_pattern = re.compile(r'[a-zA-Z]')
        return bool(english_pattern.search(text))
    
    def _contains_phonetic(self, text: str) -> bool:
        """Check if text contains phonetic symbols"""
        phonetic_indicators = ['/', '[', ']', 'ˈ', 'ˌ', 'ː']
        return any(indicator in text for indicator in phonetic_indicators)
    
    def parse_pdf(self, pdf_path: str) -> List[VocabularyCard]:
        """
        Parse a single PDF file and extract vocabulary cards
        """
        print(f"Parsing PDF: {pdf_path}")
        
        # Extract text from page 2 onwards (0-indexed, so page 1)
        text = self.extract_text_from_pdf(pdf_path, start_page=1)
        
        if not text:
            print(f"No text extracted from {pdf_path}")
            return []
        
        # Parse vocabulary content
        cards = self.parse_vocabulary_content(text)
        
        print(f"Extracted {len(cards)} vocabulary cards from {pdf_path}")
        return cards
    
    def parse_all_pdfs(self, pdf_directory: str) -> Dict[str, List[VocabularyCard]]:
        """
        Parse all PDF files in a directory
        Returns a dictionary mapping PDF filename to list of cards
        """
        results = {}
        
        if not os.path.exists(pdf_directory):
            print(f"Directory {pdf_directory} does not exist")
            return results
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
            return results
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in sorted(pdf_files):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            try:
                cards = self.parse_pdf(pdf_path)
                results[pdf_file] = cards
            except Exception as e:
                print(f"Error parsing {pdf_file}: {e}")
                results[pdf_file] = []
        
        return results

def main():
    """Main function for testing the parser"""
    parser = XingrongPDFParser()
    
    # Test with a single PDF first
    pdf_dir = "pdf"
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if pdf_files:
        test_pdf = os.path.join(pdf_dir, pdf_files[0])
        print(f"Testing with: {test_pdf}")
        
        cards = parser.parse_pdf(test_pdf)
        
        print(f"\nExtracted {len(cards)} cards:")
        for i, card in enumerate(cards, 1):
            print(f"{i}. {card}")
        
        # Save results to file
        with open('parsed_cards.txt', 'w', encoding='utf-8') as f:
            f.write(f"Parsed cards from {test_pdf}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, card in enumerate(cards, 1):
                f.write(f"{i}. Chinese: {card.chinese}\n")
                f.write(f"   English: {card.english}\n")
                f.write(f"   Phonetic: {card.phonetic}\n\n")
        
        print("\nResults saved to parsed_cards.txt")

if __name__ == "__main__":
    main()
