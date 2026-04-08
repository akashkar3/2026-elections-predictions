from myneta_scraper import MyNetaAssamScraper

scraper = MyNetaAssamScraper()
print('Testing Selenium scraping for BAJALI constituency...')
candidates = scraper.scrape_candidate_for_constituency('BAJALI', '26')
print('Found ' + str(len(candidates)) + ' candidates')

if candidates:
    print('\nSample candidate:')
    cand = candidates[0]
    for key in ['Candidate Name', 'Party', 'Criminal Cases', 'Education', 'Age']:
        print('  ' + key + ': ' + str(cand.get(key, 'N/A')))
else:
    print('No candidates found. Checking if Selenium is working...')
    print('Trying fallback method...')
