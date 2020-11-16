
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

# # Set the executable path and initialize the chrome browser in splinter
# # Windows users


def scrape_all():
    # Initiate headless driver for deployment
    # browser = Browser("chrome", executable_path="chromedriver", headless=True)
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "image_url" : hemisphere_image()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_image():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    bs = soup(html, 'html.parser')
    try:
        button = browser.find_by_id("product-section")
        bs = soup(browser.html)

        result = bs.find("div", class_="collapsible results")
    except BaseException:
        return None
    href = []
    for x in result.find_all("a"):
        image = x.get("href")
        href.append(image)
    base_url = "https://astrogeology.usgs.gov"
    images = [base_url + x for x in set(href)]
    browser.visit(images[0])

    img_url =[]
    for img in images:
        browser.visit(img)
        html = browser.html 
        BS = soup(html, "html.parser")
        img_to_use= BS.find("ul").find("li").find("a").get("href")
        img_url.append(img_to_use)

    hrefs = list(set(href))
    title = [" ".join(h.split('/')[-1].split('_')).title() for h in hrefs]
    hemisphere_image_urls = []
    for i in range(0,4):
        hemisphere = {}
        hemisphere["url"] = img_url[i]
        hemisphere["title"] = title[i]
        hemisphere_image_urls.append(hemisphere)
    return hemisphere_image_urls

if __name__ == "__main__":
    print(scrape_all()["image_url"])
    # If running as script, print scraped data
    # print(scrape_all())
