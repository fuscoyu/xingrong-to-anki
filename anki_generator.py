#!/usr/bin/env python3
"""
Anki deck generator for Xingrong English vocabulary cards
Generates a single unified deck with tags for lesson organization
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

def main():
    """Main function for testing the Anki generator"""
    from pdf_parser import XingrongPDFParser
    
    # Parse PDFs to get vocabulary cards
    parser = XingrongPDFParser()
    pdf_cards = parser.parse_all_pdfs("pdf")
    
    if not pdf_cards:
        print("No PDFs found or parsed")
        return
    
    # Generate Anki decks
    generator = XingrongAnkiGenerator()
    generated_files = generator.generate_all_decks(pdf_cards)
    
    print(f"\nGenerated {len(generated_files)} Anki deck files:")
    for file_path in generated_files:
        print(f"- {file_path}")
    
    print("\nYou can now import these .apkg files into Anki!")

if __name__ == "__main__":
    main()
