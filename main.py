#!/usr/bin/env python3
"""
Main script to process Xingrong English PDFs and generate Anki cards
Converts PDF content to Anki decks with Chinese front and English back
"""

import os
import sys
import argparse
from typing import List
from pdf_parser import XingrongPDFParser, VocabularyCard
from anki_generator import XingrongAnkiGenerator

def process_single_pdf(pdf_path: str, output_dir: str = "anki_decks") -> bool:
    """
    Process a single PDF file and generate Anki deck
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} not found")
        return False
    
    print(f"Processing: {pdf_path}")
    
    # Parse PDF
    parser = XingrongPDFParser()
    cards = parser.parse_pdf(pdf_path)
    
    if not cards:
        print(f"No vocabulary cards found in {pdf_path}")
        return False
    
    print(f"Found {len(cards)} vocabulary cards")
    
    # Generate Anki deck
    generator = XingrongAnkiGenerator()
    pdf_filename = os.path.basename(pdf_path)
    pdf_cards = {pdf_filename: cards}
    
    generated_files = generator.generate_all_decks(pdf_cards, output_dir)
    
    if generated_files:
        print(f"Generated Anki deck: {generated_files[0]}")
        return True
    else:
        print("Failed to generate Anki deck")
        return False


def process_unified_deck(pdf_dir: str = "pdf", output_dir: str = "anki_decks", deck_name: str = "星荣英语词汇大全") -> List[str]:
    """
    Process all PDF files and generate a single unified Anki deck with tags
    Returns list of generated deck file paths (should be just one file)
    """
    if not os.path.exists(pdf_dir):
        print(f"Error: PDF directory {pdf_dir} not found")
        return []
    
    print(f"Processing all PDFs in {pdf_dir} for unified deck")
    
    # Parse all PDFs
    parser = XingrongPDFParser()
    pdf_cards = parser.parse_all_pdfs(pdf_dir)
    
    if not pdf_cards:
        print("No PDFs found or no cards extracted")
        return []
    
    # Count total cards
    total_cards = sum(len(cards) for cards in pdf_cards.values())
    print(f"Total vocabulary cards extracted: {total_cards}")
    
    # Generate unified deck
    generator = XingrongAnkiGenerator()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate unified deck file
    output_filename = f"{deck_name}.apkg"
    output_path = os.path.join(output_dir, output_filename)
    
    if generator.generate_unified_deck(pdf_cards, output_path, deck_name):
        print(f"Generated unified deck: {output_path}")
        return [output_path]
    else:
        print("Failed to generate unified deck")
        return []

def print_unified_summary(generated_files: List[str], pdf_dir: str, deck_name: str):
    """
    Print summary of unified deck processing results
    """
    print("\n" + "="*60)
    print("UNIFIED DECK PROCESSING SUMMARY")
    print("="*60)
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory {pdf_dir} not found")
        return
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"Total PDF files processed: {len(pdf_files)}")
    print(f"Unified deck generated: {len(generated_files)}")
    
    if generated_files:
        print(f"\nGenerated unified deck file:")
        print(f"  - {os.path.basename(generated_files[0])}")
        
        print(f"\nOutput directory: {os.path.dirname(generated_files[0])}")
        print("\nTo use this deck:")
        print("1. Open Anki")
        print("2. Go to File -> Import")
        print("3. Select the .apkg file from the output directory")
        print("4. The deck will contain all lessons organized by tags")
        
        print("\nTag organization:")
        print("- Each lesson has its own tag (e.g., 'Lesson_1', 'Lesson_2', etc.)")
        print("- Use Anki's browser to filter by tags")
        print("- You can study specific lessons or mix all cards together")
        
        print("\nCard format:")
        print("- Front: Chinese text")
        print("- Back: English translation + phonetic (if available)")
        print("- Tags: Lesson number and metadata")

def main():
    """
    Main function with command line argument support
    """
    parser = argparse.ArgumentParser(
        description="Convert Xingrong English PDFs to Anki cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Process all PDFs and generate unified deck
  python main.py --deck-name "My English Deck"  # Custom deck name
  python main.py -f lesson1.pdf            # Process single PDF file
  python main.py -d my_pdfs -o my_decks    # Custom directories
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Process a single PDF file'
    )
    
    parser.add_argument(
        '-d', '--pdf-dir',
        default='pdf',
        help='PDF directory path (default: pdf)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='anki_decks',
        help='Output directory for Anki decks (default: anki_decks)'
    )
    
    parser.add_argument(
        '--list-pdfs',
        action='store_true',
        help='List all PDF files in the directory and exit'
    )
    
    parser.add_argument(
        '--deck-name',
        default='星荣英语词汇大全',
        help='Name for the deck (default: 星荣英语词汇大全)'
    )
    
    args = parser.parse_args()
    
    # List PDFs if requested
    if args.list_pdfs:
        if os.path.exists(args.pdf_dir):
            pdf_files = [f for f in os.listdir(args.pdf_dir) if f.endswith('.pdf')]
            if pdf_files:
                print(f"PDF files in {args.pdf_dir}:")
                for pdf_file in sorted(pdf_files):
                    print(f"  - {pdf_file}")
            else:
                print(f"No PDF files found in {args.pdf_dir}")
        else:
            print(f"Directory {args.pdf_dir} not found")
        return
    
    # Process single file or all files
    if args.file:
        success = process_single_pdf(args.file, args.output_dir)
        if success:
            print("\nProcessing completed successfully!")
        else:
            print("\nProcessing failed!")
            sys.exit(1)
    else:
        # Generate unified deck
        generated_files = process_unified_deck(args.pdf_dir, args.output_dir, args.deck_name)
        print_unified_summary(generated_files, args.pdf_dir, args.deck_name)
        
        if generated_files:
            print("\nProcessing completed successfully!")
        else:
            print("\nNo decks were generated!")
            sys.exit(1)

if __name__ == "__main__":
    main()
