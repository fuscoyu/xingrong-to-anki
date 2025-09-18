#!/usr/bin/env python3
"""
PDF parser for Xingrong English lesson PDFs
Extracts Chinese, English, and phonetic content from page 2 onwards
"""

import pdfplumber
import camelot
import pandas as pd
import re
import os
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class VocabularyCard:
    """Represents a vocabulary card with Chinese, English, and phonetic"""
    chinese: str
    english: str
    phonetic: Optional[str] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    
    def __str__(self):
        return f"Chinese: {self.chinese}, English: {self.english}, Phonetic: {self.phonetic}"

class XingrongPDFParser:
    """Parser for Xingrong English lesson PDFs"""
    
    def __init__(self):
        self.cards: List[VocabularyCard] = []
        self.use_camelot = True  # Use Camelot by default for better table extraction
        
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing newlines and normalizing whitespace
        """
        if not text or text == 'nan' or pd.isna(text):
            return ''
        
        # Convert to string
        text = str(text)
        
        # Remove various newline characters directly (no replacement)
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        text = text.replace('\r\n', '')
        
        # Replace multiple consecutive spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading and trailing whitespace
        text = text.strip()
        
        return text
    
    def separate_chinese_english(self, mixed_text: str) -> tuple:
        """
        Separate Chinese and English from mixed text
        Returns (chinese_part, english_part)
        """
        if not mixed_text:
            return '', ''
        
        # Split by spaces to handle word boundaries
        words = mixed_text.split()
        
        chinese_part = []
        english_part = []
        found_english = False
        
        for word in words:
            # Check if word contains Chinese characters
            if re.search(r'[\u4e00-\u9fff]', word):
                if not found_english:  # Still in Chinese section
                    chinese_part.append(word)
                else:  # English section has started, this might be mixed
                    # If word is purely Chinese, it might be a new Chinese phrase
                    if re.match(r'^[\u4e00-\u9fff；，。！？]+$', word):
                        chinese_part.append(word)
                    else:
                        english_part.append(word)
            else:
                # Word contains no Chinese, it's English
                found_english = True
                english_part.append(word)
        
        chinese_result = ' '.join(chinese_part).strip()
        english_result = ' '.join(english_part).strip()
        
        return chinese_result, english_result
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[VocabularyCard]:
        """
        Extract vocabulary tables from PDF using Camelot
        """
        print(f"Extracting tables from PDF using Camelot: {pdf_path}")
        
        try:
            # Try lattice method first (better for tables with borders)
            tables = camelot.read_pdf(pdf_path, pages='2-end', flavor='lattice')
            print(f"Lattice method found {len(tables)} tables")
            
            if len(tables) == 0:
                # If no tables found, try stream method
                tables = camelot.read_pdf(pdf_path, pages='2-end', flavor='stream')
                print(f"Stream method found {len(tables)} tables")
            
            all_cards = []
            
            for table_idx, table in enumerate(tables):
                df = table.df
                print(f"Processing table {table_idx + 1}: shape {df.shape}, accuracy {table.accuracy:.2f}")
                
                for row_idx, row in df.iterrows():
                    # Extract three columns: Chinese, English, Phonetic
                    raw_chinese = self.clean_text(row.iloc[0])
                    raw_english = self.clean_text(row.iloc[1])
                    phonetic = self.clean_text(row.iloc[2]) if len(row) > 2 else ''
                    
                    # Handle mixed Chinese-English in the first column
                    if raw_chinese and re.search(r'[a-zA-Z]', raw_chinese):
                        # First column contains mixed Chinese and English
                        chinese_part, english_part = self.separate_chinese_english(raw_chinese)
                        
                        # Combine with second column if it contains more English
                        if raw_english and not re.search(r'[\u4e00-\u9fff]', raw_english):
                            english = (english_part + ' ' + raw_english).strip()
                        else:
                            english = english_part
                        
                        chinese = chinese_part
                    else:
                        # Normal case: Chinese in first column, English in second
                        chinese = raw_chinese
                        english = raw_english
                    
                    # Validate entry
                    if self.is_valid_vocabulary_entry(chinese, english):
                        card = VocabularyCard(
                            chinese=chinese,
                            english=english,
                            phonetic=phonetic if phonetic else None,
                            table_index=table_idx + 1,
                            row_index=row_idx
                        )
                        all_cards.append(card)
                        print(f"Extracted: {chinese} → {english}")
            
            print(f"Total vocabulary cards extracted: {len(all_cards)}")
            return all_cards
            
        except Exception as e:
            print(f"Error extracting tables with Camelot: {e}")
            print("Falling back to text-based parsing...")
            return self.extract_text_from_pdf_fallback(pdf_path)
    
    def is_valid_vocabulary_entry(self, chinese: str, english: str) -> bool:
        """
        Check if the entry is a valid vocabulary entry
        """
        # Skip header rows
        if ('中文' in chinese or '英文' in english or 
            'K.K.音标' in chinese or 'K.K.音标' in english):
            return False
        
        # Skip empty entries
        if not chinese or not english:
            return False
        
        # Skip entries that are just numbers
        if chinese.isdigit() or english.isdigit():
            return False
        
        return True
        
    def extract_text_from_pdf_fallback(self, pdf_path: str, start_page: int = 1) -> List[VocabularyCard]:
        """
        Fallback method: Extract text from PDF and parse using text-based approach
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) <= start_page:
                    print(f"PDF has only {len(pdf.pages)} pages, cannot start from page {start_page + 1}")
                    return []
                
                # Extract text from pages starting from start_page (0-indexed)
                full_text = ""
                for i in range(start_page, len(pdf.pages)):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                # Parse vocabulary content using the old text-based method
                return self.parse_vocabulary_content(full_text)
                
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return []
    
    def parse_vocabulary_content(self, text: str) -> List[VocabularyCard]:
        """
        Parse vocabulary content from text
        Look for patterns of Chinese, English, and phonetic text
        Handle long sentences that are split across multiple lines
        """
        cards = []
        lines = text.split('\n')
        
        # Remove empty lines and clean up
        lines = [line.strip() for line in lines if line.strip()]
        
        # First, merge split lines to handle long sentences
        lines = self._merge_split_lines(lines)
        
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip headers and non-vocabulary content
            if self._is_header_line(line):
                i += 1
                continue
            
            # Look for Chinese text (contains Chinese characters)
            if self._contains_chinese(line):
                # Try to parse the line as a complete vocabulary entry
                # Format: "中文 英文 /音标/" or "中文 英文"
                if self._contains_english(line):
                    chinese, english, phonetic = self._parse_single_line_vocabulary(line)
                    if chinese and english:
                        card = VocabularyCard(
                            chinese=chinese,
                            english=english,
                            phonetic=phonetic if phonetic else None
                        )
                        cards.append(card)
                        print(f"Found vocabulary card: {card}")
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
    
    def _merge_split_lines(self, lines: List[str]) -> List[str]:
        """
        Merge lines that are split in the middle of vocabulary entries
        Handle cases where long sentences are broken across multiple lines
        """
        merged_lines = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i]
            
            # Skip header lines
            if self._is_header_line(current_line):
                merged_lines.append(current_line)
                i += 1
                continue
            
            # Try to detect multi-line vocabulary entries
            merged_entry = self._try_merge_multiline_entry(lines, i)
            if merged_entry:
                merged_lines.append(merged_entry['merged_line'])
                print(f"Merged multi-line entry: {merged_entry['lines_used']} lines -> '{merged_entry['merged_line'][:100]}...'")
                i += merged_entry['lines_used']
                continue
            
            # Check if this line contains Chinese and English but might be incomplete
            if self._contains_chinese(current_line) and self._contains_english(current_line):
                # Look at the next line to see if it's a continuation
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    
                    # Check if next line is a continuation (no Chinese, has English/phonetic)
                    if (not self._contains_chinese(next_line) and 
                        (self._contains_english(next_line) or self._contains_phonetic(next_line)) and
                        not self._is_header_line(next_line)):
                        
                        # Merge the lines
                        merged_line = current_line + " " + next_line
                        merged_lines.append(merged_line)
                        print(f"Merged split line: '{current_line}' + '{next_line}' -> '{merged_line}'")
                        i += 2  # Skip both lines
                        continue
                
                # Not a split line, add as is
                merged_lines.append(current_line)
                i += 1
            else:
                # Line doesn't match pattern for merging, add as is
                merged_lines.append(current_line)
                i += 1
        
        return merged_lines
    
    def _try_merge_multiline_entry(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """
        Try to merge a multi-line vocabulary entry where Chinese, English, and phonetic
        are each split across multiple lines
        
        Pattern example:
        它是重要的对我来说所以我必
        须每天做这件事
        It is important for me so I have to
        do it every day
        /ɪt/ /ɪz/ /ɪm'pɔrtnt/ /fɝ/ /mi/ /so/ /aɪ/ /hæv/
        /tə/ /du/ /ɪt/ /'ɛvri/ /de/
        """
        if start_idx >= len(lines):
            return None
            
        # Look ahead to see if we have a pattern of split Chinese/English/Phonetic
        chinese_lines = []
        english_lines = []
        phonetic_lines = []
        
        i = start_idx
        max_look_ahead = min(8, len(lines) - start_idx)  # Look ahead max 8 lines
        
        # Phase 1: Collect Chinese lines (lines that contain Chinese but may be incomplete)
        while i < start_idx + max_look_ahead:
            line = lines[i].strip()
            if not line or self._is_header_line(line):
                break
            if self._contains_chinese(line) and not self._contains_phonetic(line):
                chinese_lines.append(line)
                i += 1
            else:
                break
        
        # Phase 2: Collect English lines (lines that contain English but no Chinese)
        while i < start_idx + max_look_ahead:
            line = lines[i].strip()
            if not line or self._is_header_line(line):
                break
            if (self._contains_english(line) and 
                not self._contains_chinese(line) and 
                not self._contains_phonetic(line)):
                english_lines.append(line)
                i += 1
            else:
                break
        
        # Phase 3: Collect phonetic lines (lines that contain phonetic symbols)
        while i < start_idx + max_look_ahead:
            line = lines[i].strip()
            if not line or self._is_header_line(line):
                break
            if self._contains_phonetic(line) and not self._contains_chinese(line):
                phonetic_lines.append(line)
                i += 1
            else:
                break
        
        # Check if we found a valid multi-line pattern
        if len(chinese_lines) >= 2 and len(english_lines) >= 2 and len(phonetic_lines) >= 1:
            # Merge all parts
            chinese_part = "".join(chinese_lines)
            english_part = " ".join(english_lines)
            phonetic_part = " ".join(phonetic_lines)
            
            merged_line = f"{chinese_part} {english_part} {phonetic_part}"
            lines_used = len(chinese_lines) + len(english_lines) + len(phonetic_lines)
            
            return {
                'merged_line': merged_line,
                'lines_used': lines_used,
                'chinese_lines': chinese_lines,
                'english_lines': english_lines,
                'phonetic_lines': phonetic_lines
            }
        
        return None
    
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
        Uses Camelot for table extraction by default, falls back to text parsing if needed
        """
        print(f"Parsing PDF: {pdf_path}")
        
        if self.use_camelot:
            # Try Camelot table extraction first
            cards = self.extract_tables_from_pdf(pdf_path)
            if cards:
                print(f"Successfully extracted {len(cards)} vocabulary cards using Camelot")
                return cards
            else:
                print("Camelot extraction failed, falling back to text-based parsing...")
        
        # Fallback to text-based parsing
        cards = self.extract_text_from_pdf_fallback(pdf_path, start_page=1)
        print(f"Extracted {len(cards)} vocabulary cards using text-based parsing")
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
    
    def save_to_json(self, cards: List[VocabularyCard], output_file: str):
        """
        Save vocabulary cards to JSON file
        """
        data = []
        for card in cards:
            data.append({
                'chinese': card.chinese,
                'english': card.english,
                'phonetic': card.phonetic,
                'table_index': card.table_index,
                'row_index': card.row_index
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to: {output_file}")
    
    def save_to_text(self, cards: List[VocabularyCard], output_file: str):
        """
        Save vocabulary cards to text file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Xingrong PDF Parser Results\n")
            f.write(f"Total cards: {len(cards)}\n")
            f.write("=" * 60 + "\n\n")
            
            for i, card in enumerate(cards, 1):
                f.write(f"{i:3d}. Chinese: {card.chinese}\n")
                f.write(f"     English: {card.english}\n")
                if card.phonetic:
                    f.write(f"     Phonetic: {card.phonetic}\n")
                if card.table_index:
                    f.write(f"     Source: Table {card.table_index}, Row {card.row_index}\n")
                f.write("\n")
        
        print(f"Results saved to: {output_file}")

def main():
    """Main function for testing the parser"""
    parser = XingrongPDFParser()
    
    # Test with lesson 10.5 specifically
    pdf_path = "pdf/零基础学英语第10.5课-星荣英语笔记.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    print("Testing enhanced PDF parser with Camelot integration...")
    cards = parser.parse_pdf(pdf_path)
    
    if cards:
        # Save results in multiple formats
        parser.save_to_json(cards, "enhanced_lesson_10_5.json")
        parser.save_to_text(cards, "enhanced_lesson_10_5.txt")
        
        # Show statistics
        print(f"\n=== Enhanced Parser Statistics ===")
        print(f"Total cards: {len(cards)}")
        
        long_sentences = [card for card in cards if len(card.chinese) > 20]
        print(f"Long sentences (>20 chars): {len(long_sentences)}")
        
        # Show method used
        camelot_cards = [card for card in cards if card.table_index is not None]
        text_cards = [card for card in cards if card.table_index is None]
        print(f"Camelot extracted: {len(camelot_cards)}")
        print(f"Text-based extracted: {len(text_cards)}")
        
        # Show some examples
        print(f"\n=== Long sentence examples ===")
        for i, card in enumerate(long_sentences[:5], 1):
            print(f"{i}. {card.chinese}")
            print(f"   → {card.english}")
            print()
    else:
        print("No vocabulary cards extracted!")

if __name__ == "__main__":
    main()
