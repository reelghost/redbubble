import cfscrape
import requests
keyword = "eagle across the mountains"
url = f'https://api.auuptools.com/redbubble/pure-tags?keyword={keyword}&limit=20'


scraper = cfscrape.create_scraper()



try:
    # Use the scraper to get the response, including the headers
    response = scraper.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    
    # Print the response text
    print(response.json())
    
except Exception as e:
    pass
