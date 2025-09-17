#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pdfplumber
        print("✓ pdfplumber imported successfully")
    except ImportError as e:
        print(f"✗ pdfplumber import failed: {e}")
        return False
    
    try:
        import genanki
        print("✓ genanki imported successfully")
    except ImportError as e:
        print(f"✗ genanki import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✓ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    return True

def test_pdf_directory():
    """Test if PDF directory exists and contains files"""
    print("\nTesting PDF directory...")
    
    pdf_dir = "pdf"
    if not os.path.exists(pdf_dir):
        print(f"✗ PDF directory '{pdf_dir}' not found")
        return False
    
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"✗ No PDF files found in '{pdf_dir}'")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files in '{pdf_dir}'")
    for pdf_file in pdf_files[:3]:  # Show first 3 files
        print(f"  - {pdf_file}")
    
    if len(pdf_files) > 3:
        print(f"  ... and {len(pdf_files) - 3} more")
    
    return True

def test_output_directory():
    """Test if output directory can be created"""
    print("\nTesting output directory...")
    
    output_dir = "anki_decks"
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ Created output directory '{output_dir}'")
        else:
            print(f"✓ Output directory '{output_dir}' already exists")
        return True
    except Exception as e:
        print(f"✗ Failed to create output directory: {e}")
        return False

def test_module_imports():
    """Test if our custom modules can be imported"""
    print("\nTesting custom modules...")
    
    try:
        from pdf_parser import XingrongPDFParser
        print("✓ pdf_parser module imported successfully")
    except ImportError as e:
        print(f"✗ pdf_parser import failed: {e}")
        return False
    
    try:
        from anki_generator import XingrongAnkiGenerator
        print("✓ anki_generator module imported successfully")
    except ImportError as e:
        print(f"✗ anki_generator import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("xingrong-to-anki - Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_pdf_directory,
        test_output_directory,
        test_module_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Setup is ready.")
        print("\nYou can now run:")
        print("  python main.py")
        return True
    else:
        print("✗ Some tests failed. Please check the setup.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
