import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    print("⚠️  Selenium not installed. Using requests-only mode (may miss dynamic content).")

class MyNetaAssamScraper:
    def __init__(self):
        self.base_url = "https://www.myneta.info/Assam2026/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.constituencies = {}  # Changed to dict: {name: id}
        self.candidates_data = []
    
    def scrape_constituencies(self):
        """Scrape all constituencies from the main page"""
        print("📍 Fetching constituencies from MyNeta...")
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all constituency links with constituency_id parameter
            constituency_links = soup.find_all('a', href=re.compile(r'action=show_candidates&constituency_id='))
            
            seen = set()
            for link in constituency_links:
                constituency_name = link.get_text().strip()
                href = link.get('href', '')
                
                # Extract constituency_id from href
                match = re.search(r'constituency_id=(\d+)', href)
                if match and constituency_name and constituency_name not in seen and constituency_name != 'ALL CONSTITUENCIES':
                    constituency_id = match.group(1)
                    self.constituencies[constituency_name] = constituency_id
                    seen.add(constituency_name)
            
            print(f"✅ Found {len(self.constituencies)} constituencies")
            return self.constituencies
            
        except Exception as e:
            print(f"❌ Error scraping constituencies: {e}")
            return {}
    
    def scrape_candidate_for_constituency(self, constituency_name, constituency_id):
        """Scrape candidates for a specific constituency using Selenium for dynamic content"""
        try:
            if HAS_SELENIUM:
                return self._scrape_with_selenium(constituency_name, constituency_id)
            else:
                return self._scrape_with_requests(constituency_name, constituency_id)
            
        except Exception as e:
            print(f"❌ Error scraping {constituency_name}: {e}")
            return []
    
    def _scrape_with_selenium(self, constituency_name, constituency_id):
        """Use Selenium to scrape data with JavaScript rendering"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            
            driver = webdriver.Chrome(options=options)
            url = f"{self.base_url}index.php?action=show_candidates&constituency_id={constituency_id}"
            driver.get(url)
            
            # Wait for table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tr td"))
            )
            
            time.sleep(1)  # Additional wait for dynamic content
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            
            candidates = []
            tables = soup.find_all('table', class_='w3-table w3-bordered')
            
            if tables:
                table = tables[0]
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            sno = cols[0].get_text().strip()
                            candidate_name = cols[1].get_text().strip()
                            party = cols[2].get_text().strip()
                            criminal_cases = cols[3].get_text().strip() if len(cols) > 3 else "0"
                            education = cols[4].get_text().strip() if len(cols) > 4 else "N/A"
                            age = cols[5].get_text().strip() if len(cols) > 5 else "N/A"
                            total_assets = cols[6].get_text().strip() if len(cols) > 6 else "N/A"
                            liabilities = cols[7].get_text().strip() if len(cols) > 7 else "N/A"
                            
                            if candidate_name:
                                candidates.append({
                                    'Constituency': constituency_name,
                                    'S.No': sno,
                                    'Candidate Name': candidate_name,
                                    'Party': party,
                                    'Criminal Cases': criminal_cases,
                                    'Education': education,
                                    'Age': age,
                                    'Total Assets': total_assets,
                                    'Liabilities': liabilities
                                })
                        except Exception as e:
                            pass
            
            return candidates
            
        except Exception as e:
            print(f"Selenium error for {constituency_name}: {e}")
            return []
    
    def _scrape_with_requests(self, constituency_name, constituency_id):
        """Fallback scraper using pure requests (may miss dynamic content)"""
        try:
            url = f"{self.base_url}index.php?action=show_candidates&constituency_id={constituency_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            candidates = []
            
            # Extract candidate information from the page
            tables = soup.find_all('table', class_='w3-table w3-bordered')
            
            if tables:
                table = tables[0]
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            sno = cols[0].get_text().strip()
                            candidate_name = cols[1].get_text().strip()
                            party = cols[2].get_text().strip()
                            criminal_cases = cols[3].get_text().strip() if len(cols) > 3 else "0"
                            education = cols[4].get_text().strip() if len(cols) > 4 else "N/A"
                            age = cols[5].get_text().strip() if len(cols) > 5 else "N/A"
                            total_assets = cols[6].get_text().strip() if len(cols) > 6 else "N/A"
                            liabilities = cols[7].get_text().strip() if len(cols) > 7 else "N/A"
                            
                            if candidate_name and candidate_name not in ['', 'Candidate Name']:
                                candidates.append({
                                    'Constituency': constituency_name,
                                    'S.No': sno,
                                    'Candidate Name': candidate_name,
                                    'Party': party,
                                    'Criminal Cases': criminal_cases,
                                    'Education': education,
                                    'Age': age,
                                    'Total Assets': total_assets,
                                    'Liabilities': liabilities
                                })
                        except Exception as e:
                            pass
            
            return candidates
            
        except Exception as e:
            print(f"Error scraping {constituency_name}: {e}")
            return []
    
    def scrape_all_candidates(self):
        """Scrape candidates for all constituencies"""
        if not self.constituencies:
            print("❌ No constituencies found. Run scrape_constituencies() first.")
            return []
        
        print(f"\n📊 Scraping candidates for {len(self.constituencies)} constituencies...")
        
        for i, (constituency_name, constituency_id) in enumerate(self.constituencies.items(), 1):
            print(f"  [{i}/{len(self.constituencies)}] Scraping {constituency_name}...", end=' ')
            candidates = self.scrape_candidate_for_constituency(constituency_name, constituency_id)
            self.candidates_data.extend(candidates)
            print(f"({len(candidates)} candidates)")
            time.sleep(0.3)  # Polite delay between requests
        
        print(f"\n✅ Total candidates scraped: {len(self.candidates_data)}")
        return self.candidates_data
    
    def save_to_excel(self, filename='Assam_Elections_2026.xlsx'):
        """Save all data to Excel with multiple sheets"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                
                # Sheet 1: All candidates (detailed info)
                if self.candidates_data:
                    df_candidates = pd.DataFrame(self.candidates_data)
                    df_candidates = df_candidates.sort_values(['Constituency', 'Candidate Name'])
                    df_candidates.to_excel(writer, sheet_name='All Candidates', index=False)
                    print(f"📄 Saved {len(df_candidates)} candidates to 'All Candidates' sheet")
                
                # Sheet 2: Constituencies summary
                df_constituencies = pd.DataFrame({
                    'Constituency': list(self.constituencies.keys()),
                    'Candidate Count': [
                        len([c for c in self.candidates_data if c['Constituency'] == cons])
                        for cons in self.constituencies.keys()
                    ]
                }).sort_values('Candidate Count', ascending=False)
                df_constituencies.to_excel(writer, sheet_name='Constituencies', index=False)
                print(f"📄 Saved {len(df_constituencies)} constituencies to 'Constituencies' sheet")
                
                # Sheet 3: Party distribution
                if self.candidates_data:
                    df_temp = pd.DataFrame(self.candidates_data)
                    party_dist = df_temp['Party'].value_counts().reset_index()
                    party_dist.columns = ['Party', 'Count']
                    party_dist.to_excel(writer, sheet_name='Party Distribution', index=False)
                    print(f"📄 Saved party distribution to 'Party Distribution' sheet")
                    
                    # Sheet 4: Candidates by party per constituency
                    pivot_data = df_temp.groupby(['Constituency', 'Party']).size().reset_index(name='Count')
                    pivot_table = pivot_data.pivot_table(index='Constituency', columns='Party', values='Count', fill_value=0)
                    pivot_table.to_excel(writer, sheet_name='Party by Constituency')
                    print(f"📄 Saved party distribution by constituency to 'Party by Constituency' sheet")
                    
                    # Sheet 5: Criminal cases analysis
                    df_temp['Criminal Cases'] = pd.to_numeric(df_temp['Criminal Cases'], errors='coerce').fillna(0)
                    criminal_summary = df_temp.groupby('Constituency')['Criminal Cases'].agg(['sum', 'mean', 'max']).reset_index()
                    criminal_summary.columns = ['Constituency', 'Total Criminal Cases', 'Avg Cases per Candidate', 'Max Cases']
                    criminal_summary.to_excel(writer, sheet_name='Criminal Analysis', index=False)
                    print(f"📄 Saved criminal cases analysis to 'Criminal Analysis' sheet")
            
            print(f"\n✅ Data saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving to Excel: {e}")
            return None
    
    def run_full_scrape(self):
        """Execute complete scraping pipeline"""
        print("🚀 Starting MyNeta Assam 2026 Data Scraper\n")
        print("=" * 50)
        
        # Step 1: Get constituencies
        self.scrape_constituencies()
        
        if not self.constituencies:
            print("❌ Failed to retrieve constituencies. Exiting.")
            return
        
        # Step 2: Get all candidates
        self.scrape_all_candidates()
        
        # Step 3: Save to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'Assam_Elections_2026_{timestamp}.xlsx'
        self.save_to_excel(filename)
        
        print("=" * 50)
        print(f"✅ Scraping complete!")
        print(f"   - Constituencies: {len(self.constituencies)}")
        print(f"   - Total Candidates: {len(self.candidates_data)}")


if __name__ == "__main__":
    scraper = MyNetaAssamScraper()
    scraper.run_full_scrape()
