from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.get("https://www.imdb.com/chart/top/")
time.sleep(5)

# Scroll down to load more movies
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

movies = driver.find_elements(
    "xpath",
    "//li[contains(@class,'ipc-metadata-list-summary-item')]"
)

print("Movies Found:", len(movies))

data = []

for movie in movies:
    try:
        lines = movie.text.split("\n")

        title = lines[1] if len(lines) > 1 else ""
        year = ""
        rating = ""

        for item in lines:
            if len(item) >= 4 and item[:4].isdigit():
                year = item[:4]

            try:
                value = float(item)
                if value <= 10:
                    rating = item
            except:
                pass

        data.append([title, year, rating])

    except:
        pass

df = pd.DataFrame(
    data,
    columns=["Movie Name", "Year", "IMDb Rating"]
)

df.to_csv("movies.csv", index=False)

print("Total Movies Scraped:", len(data))
print("Data Saved Successfully!")

driver.quit()