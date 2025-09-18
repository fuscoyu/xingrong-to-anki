#!/usr/bin/env python3
"""
Anki deck generator for Xingrong English vocabulary cards
Generates a main deck with subdecks for each lesson
"""

import genanki
import os
import re
from typing import List, Dict
from pdf_parser import VocabularyCard

class XingrongAnkiGenerator:
    """Generator for Anki decks from Xingrong vocabulary cards"""
    
    def __init__(self):
        # Define card model for vocabulary cards with tags support
        self.model = genanki.Model(
            1607392319,  # Unique model ID
            'Xingrong English Vocabulary',
            fields=[
                {'name': 'Chinese'},
                {'name': 'English'},
                {'name': 'Phonetic'},
                {'name': 'Tags'},
            ],
            templates=[
                {
                    'name': 'Chinese to English',
                    'qfmt': '<div style="font-size: 24px; text-align: center; font-family: Arial;">{{Chinese}}</div>',
                    'afmt': '<div style="font-size: 20px; text-align: center; font-family: Arial;">{{English}}</div>'
                           '<hr>'
                           '<div style="font-size: 16px; text-align: center; font-family: Arial; color: #666;">{{Phonetic}}</div>'
                           '<hr style="margin-top: 20px;">'
                           '<div style="font-size: 12px; text-align: left; color: #888;">{{Tags}}</div>',
                },
            ],
            css='''
            .card {
                font-family: Arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
            '''
        )
    
    def create_deck_name(self, pdf_filename: str) -> str:
        """
        Create a deck name from PDF filename, keeping the original format
        """
        # Remove .pdf extension but keep the original Chinese name
        name = pdf_filename.replace('.pdf', '')
        
        # Keep the original name as is, no prefix or character removal
        return name
    
    def extract_lesson_number(self, pdf_filename: str) -> str:
        """
        Extract lesson number from PDF filename for tagging
        """
        # Remove .pdf extension
        name = pdf_filename.replace('.pdf', '')
        
        # Extract lesson number using regex
        lesson_match = re.search(r'第(\d+(?:\.\d+)?)课', name)
        if lesson_match:
            return f"Lesson_{lesson_match.group(1).replace('.', '_')}"
        
        # Fallback: use the whole filename
        return re.sub(r'[^\w\s-]', '', name).replace(' ', '_')
    
    def deduplicate_cards(self, pdf_cards: Dict[str, List[VocabularyCard]]) -> Dict[str, List[VocabularyCard]]:
        """
        Remove duplicate cards based on Chinese text, keeping the first occurrence
        """
        seen_chinese = set()
        deduplicated_pdf_cards = {}
        
        print("Deduplicating cards...")
        
        for pdf_filename, cards in pdf_cards.items():
            if not cards:
                deduplicated_pdf_cards[pdf_filename] = []
                continue
            
            unique_cards = []
            duplicates_count = 0
            
            for card in cards:
                if card.chinese not in seen_chinese:
                    seen_chinese.add(card.chinese)
                    unique_cards.append(card)
                else:
                    duplicates_count += 1
            
            if duplicates_count > 0:
                print(f"  {pdf_filename}: {len(cards)} -> {len(unique_cards)} cards (removed {duplicates_count} duplicates)")
            
            deduplicated_pdf_cards[pdf_filename] = unique_cards
        
        return deduplicated_pdf_cards
    
    def create_unified_deck(self, pdf_cards: Dict[str, List[VocabularyCard]], deck_name: str = "星荣英语词汇大全") -> genanki.Deck:
        """
        Create a single unified deck with all cards from all PDFs, using tags to organize by lesson
        """
        # First deduplicate cards
        deduplicated_cards = self.deduplicate_cards(pdf_cards)
        
        deck_id = abs(hash("Xingrong_Unified_Deck")) % (10 ** 10)  # Generate unique deck ID
        deck = genanki.Deck(deck_id, deck_name)
        
        total_cards = 0
        for pdf_filename, cards in deduplicated_cards.items():
            if not cards:
                continue
            
            lesson_tag = self.extract_lesson_number(pdf_filename)
            lesson_name = pdf_filename.replace('.pdf', '').replace('零基础学英语', '').replace('-星荣英语笔记', '')
            
            print(f"Adding {len(cards)} cards from {lesson_name} with tag: {lesson_tag}")
            
            for card in cards:
                # Create note with vocabulary data and tags
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        card.chinese, 
                        card.english, 
                        card.phonetic or '', 
                        f"{lesson_tag} {lesson_name}"
                    ],
                    tags=[lesson_tag, "Xingrong", "English", "Vocabulary"]
                )
                deck.add_note(note)
                total_cards += 1
        
        print(f"Created unified deck with {total_cards} total unique cards")
        return deck
    
    def create_main_deck_with_subdecks(self, pdf_cards: Dict[str, List[VocabularyCard]], main_deck_name: str = "星荣英语") -> List[genanki.Deck]:
        """
        Create a main deck with subdecks for each lesson
        Returns a list of decks: [main_deck, subdeck1, subdeck2, ...]
        """
        print(f"Creating main deck with subdecks...")
        
        # First deduplicate cards
        deduplicated_cards = self.deduplicate_cards(pdf_cards)
        
        # Create main deck
        main_deck_id = abs(hash("Xingrong_Main_Deck")) % (10 ** 10)
        main_deck = genanki.Deck(main_deck_id, main_deck_name)
        
        # Create subdecks for each lesson
        all_decks = [main_deck]
        total_cards = 0
        
        # Sort lessons by lesson number for proper ordering
        def extract_lesson_number_for_sort(pdf_filename: str) -> float:
            """Extract lesson number for sorting"""
            import re
            match = re.search(r'第(\d+(?:\.\d+)?)课', pdf_filename)
            if match:
                return float(match.group(1))
            return 999  # Put unmatched items at the end
        
        # Sort the lessons by lesson number
        sorted_lessons = sorted(deduplicated_cards.items(), key=lambda x: extract_lesson_number_for_sort(x[0]))
        
        for pdf_filename, cards in sorted_lessons:
            if not cards:
                continue
            
            # Extract lesson info
            lesson_tag = self.extract_lesson_number(pdf_filename)
            lesson_name = self.extract_clean_lesson_name(pdf_filename)
            
            # Extract lesson number for proper sorting
            import re
            lesson_match = re.search(r'第(\d+(?:\.\d+)?)课', lesson_name)
            if lesson_match:
                lesson_num = float(lesson_match.group(1))
                # Format with leading zeros for proper sorting: "01" "02" "10.5" etc
                if lesson_num == int(lesson_num):
                    formatted_num = f"{int(lesson_num):02d}"
                else:
                    formatted_num = f"{lesson_num:04.1f}".replace('.', '_')
                subdeck_name = f"{main_deck_name}::{formatted_num}_{lesson_name}"
            else:
                subdeck_name = f"{main_deck_name}::{lesson_name}"
            subdeck_id = abs(hash(f"Xingrong_Subdeck_{lesson_tag}")) % (10 ** 10)
            subdeck = genanki.Deck(subdeck_id, subdeck_name)
            
            print(f"Creating subdeck: {subdeck_name} with {len(cards)} cards")
            
            for card in cards:
                # Create note with vocabulary data
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        card.chinese, 
                        card.english, 
                        card.phonetic or '', 
                        f"{lesson_tag} {lesson_name}"
                    ],
                    tags=[lesson_tag, "Xingrong", "English", "Vocabulary"]
                )
                
                # Add note to both main deck and subdeck
                main_deck.add_note(note)
                subdeck.add_note(note)
                total_cards += 1
            
            all_decks.append(subdeck)
        
        print(f"Created main deck with {total_cards} cards and {len(all_decks)-1} subdecks")
        return all_decks
    
    def extract_clean_lesson_name(self, pdf_filename: str) -> str:
        """
        Extract clean lesson name for subdeck naming
        """
        # Remove .pdf extension
        name = pdf_filename.replace('.pdf', '')
        
        # Extract just the lesson part: "第X课" or "第X.Y课"
        lesson_match = re.search(r'(第\d+(?:\.\d+)?课)', name)
        if lesson_match:
            return lesson_match.group(1)
        
        # Fallback: clean up the name
        clean_name = name.replace('零基础学英语', '').replace('-星荣英语笔记', '').strip()
        return clean_name if clean_name else name
    
    def generate_deck_file(self, deck: genanki.Deck, output_path: str) -> bool:
        """
        Generate .apkg file for the deck
        """
        try:
            genanki.Package(deck).write_to_file(output_path)
            return True
        except Exception as e:
            print(f"Error generating deck file {output_path}: {e}")
            return False
    
    
    def generate_unified_deck(self, pdf_cards: Dict[str, List[VocabularyCard]], output_path: str, deck_name: str = "星荣英语词汇大全") -> bool:
        """
        Generate a single unified .apkg file with all cards from all PDFs
        """
        try:
            # Create unified deck
            deck = self.create_unified_deck(pdf_cards, deck_name)
            
            # Generate .apkg file
            genanki.Package(deck).write_to_file(output_path)
            return True
        except Exception as e:
            print(f"Error generating unified deck file {output_path}: {e}")
            return False
    
    def generate_big_deck_with_subdecks(self, pdf_cards: Dict[str, List[VocabularyCard]], output_path: str = "anki_decks/星荣英语大全.apkg") -> bool:
        """
        Generate a big deck with subdecks for each lesson
        """
        try:
            # Create all decks (main + subdecks)
            all_decks = self.create_main_deck_with_subdecks(pdf_cards)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Package all decks together
            package = genanki.Package(all_decks)
            package.write_to_file(output_path)
            
            print(f"✅ Generated big deck with subdecks: {output_path}")
            print(f"   Main deck: {all_decks[0].name}")
            print(f"   Subdecks: {len(all_decks)-1}")
            
            return True
            
        except Exception as e:
            print(f"Error generating big deck: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function for generating Anki decks"""
    from pdf_parser import XingrongPDFParser
    
    print("=== 星荣英语 Anki 大deck生成器 ===")
    print()
    
    # Parse all PDFs to get vocabulary cards
    parser = XingrongPDFParser()
    print("正在解析所有PDF文件...")
    pdf_cards = parser.parse_all_pdfs("pdf")
    
    if not pdf_cards:
        print("❌ 没有找到或解析任何PDF文件")
        return
    
    # Show parsing statistics
    total_lessons = len([k for k, v in pdf_cards.items() if v])
    total_cards = sum(len(cards) for cards in pdf_cards.values())
    print(f"📚 解析完成: {total_lessons} 个课程, {total_cards} 个词汇卡片")
    
    # Generate big deck with subdecks
    generator = XingrongAnkiGenerator()
    
    print("\n正在生成大deck和subdecks...")
    success = generator.generate_big_deck_with_subdecks(pdf_cards)
    
    if success:
        print("\n🎉 生成成功!")
        print("📦 输出文件: anki_decks/星荣英语大全.apkg")
        print()
        print("📖 使用说明:")
        print("  1. 将 .apkg 文件导入到 Anki 中")
        print("  2. 你会看到一个主deck '星荣英语'")
        print("  3. 每节课都有对应的subdeck: '星荣英语::第X课'")
        print("  4. 可以选择学习整个大deck或单独的课程")
        print()
        print("🏷️  标签说明:")
        print("  • Lesson_X: 课程标签")
        print("  • Xingrong: 星荣系列标签")
        print("  • English: 英语学习标签")
        print("  • Vocabulary: 词汇类型标签")
    else:
        print("❌ 生成失败，请检查错误信息")

if __name__ == "__main__":
    main()
