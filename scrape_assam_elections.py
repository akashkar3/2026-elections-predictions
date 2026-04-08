#!/usr/bin/env python
"""
MyNeta Assam 2026 Election Data Scraper
Scrapes all constituencies and candidates data and saves to Excel
"""

from myneta_scraper import MyNetaAssamScraper

def main():
    print("=" * 60)
    print("ASSAM 2026 ELECTION DATA SCRAPER")
    print("=" * 60)
    
    # Initialize scraper
    scraper = MyNetaAssamScraper()
    
    # Step 1: Get all constituencies
    print("\nSTEP 1: Scraping Constituencies")
    print("-" * 60)
    scraper.scrape_constituencies()
    
    if not scraper.constituencies:
        print("Failed to retrieve constituencies. Exiting.")
        return False
    
    print(f"Found {len(scraper.constituencies)} constituencies")
    print(f"   Districts: {', '.join(set([c.split('(')[0].strip() for c in scraper.constituencies.keys() if '(' in c][:10]))}")
    
    # Step 2: Get all candidates
    print("\nSTEP 2: Scraping Candidates Data")
    print("-" * 60)
    scraper.scrape_all_candidates()
    
    if not scraper.candidates_data:
        print(" No candidate data found")
        return False
    
    # Step 3: Save to Excel
    print("\nSTEP 3: Saving Data to Excel")
    print("-" * 60)
    filename = scraper.save_to_excel()
    
    if filename:
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"Summary:")
        print(f"   ✓ Constituencies: {len(scraper.constituencies)}")
        print(f"   ✓ Total Candidates: {len(scraper.candidates_data)}")
        print(f"   ✓ Output File: {filename}")
        print(f"\nExcel Sheets Generated:")
        print(f"   1. All Candidates - Complete candidate data")
        print(f"   2. Constituencies - Summary by constituency")
        print(f"   3. Party Distribution - Party wise statistics")
        print(f"   4. Party by Constituency - Cross-tabulation")
        print(f"   5. Criminal Analysis - Criminal cases summary")
        print("=" * 60)
        return True
    else:
        print("Failed to save Excel file")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
