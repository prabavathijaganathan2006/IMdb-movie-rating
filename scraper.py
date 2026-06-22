"""
IMDb Movie Rating Scraper
Dynamic scraping using Selenium with error handling and retry logic
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
from datetime import datetime

class IMDbScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome options"""
        self.headless = headless
        self.driver = None
        self.movies_data = []
        
    def setup_driver(self):
        """Set up Chrome WebDriver with options"""
        options = webdriver.ChromeOptions()
        
        # Headless mode for server deployment
        if self.headless:
            options.add_argument('--headless')
        
        # Additional options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Error setting up driver: {e}")
            return False
    
    def scrape_top250(self):
        """Scrape IMDb Top 250 movies"""
        if not self.driver:
            if not self.setup_driver():
                return []
        
        url = "https://www.imdb.com/chart/top/"
        self.movies_data = []
        
        try:
            print(f"Loading IMDb Top 250 page...")
            self.driver.get(url)
            
            # Wait for the chart to load
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for the main container
            chart_container = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ipc-page-content-container"))
            )
            
            # Scroll to load all content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get all movie items
            movie_items = self.driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
            
            print(f"Found {len(movie_items)} movies")
            
            for index, item in enumerate(movie_items[:250], 1):
                try:
                    # Get title
                    title_element = item.find_element(By.CSS_SELECTOR, "h3.ipc-title__text")
                    title_text = title_element.text
                    
                    # Extract rank and title
                    rank = index
                    title = title_text.replace(f"{index}.", "").strip()
                    
                    # Get year
                    try:
                        year_element = item.find_element(By.CSS_SELECTOR, "span.sc-43986a27-8")
                        year = year_element.text.strip()
                    except NoSuchElementException:
                        year = "N/A"
                    
                    # Get rating
                    try:
                        rating_element = item.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating")
                        rating = rating_element.text.strip()
                    except NoSuchElementException:
                        rating = "N/A"
                    
                    # Get number of ratings
                    try:
                        votes_element = item.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--voteCount")
                        votes = votes_element.text.strip()
                    except NoSuchElementException:
                        votes = "N/A"
                    
                    # Get movie URL for additional details
                    try:
                        link_element = item.find_element(By.CSS_SELECTOR, "a.ipc-title-link")
                        movie_url = link_element.get_attribute("href")
                    except NoSuchElementException:
                        movie_url = "N/A"
                    
                    movie_data = {
                        "rank": rank,
                        "title": title,
                        "year": year,
                        "rating": rating,
                        "votes": votes,
                        "url": movie_url,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    self.movies_data.append(movie_data)
                    print(f"Scraped: {rank}. {title} ({year}) - {rating} ⭐")
                    
                except Exception as e:
                    print(f"Error scraping movie {index}: {e}")
                    continue
                    
        except TimeoutException as e:
            print(f"Timeout while loading page: {e}")
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            self.close_driver()
        
        return self.movies_data
    
    def save_to_csv(self, filename="data/imdb_top250.csv"):
        """Save scraped data to CSV"""
        if not self.movies_data:
            print("No data to save")
            return False
        
        try:
            df = pd.DataFrame(self.movies_data)
            
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def get_json_data(self):
        """Return scraped data as JSON"""
        return self.movies_data
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

# Function to scrape and return data
def scrape_imdb_top250(headless=True):
    """Main function to scrape IMDb Top 250"""
    scraper = IMDbScraper(headless=headless)
    data = scraper.scrape_top250()
    scraper.save_to_csv()
    return data

if __name__ == "__main__":
    # Test the scraper
    print("Starting IMDb Top 250 Scraper...")
    data = scrape_imdb_top250(headless=True)
    print(f"Scraped {len(data)} movies successfully!")