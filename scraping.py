# Import Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

# Set up scraping function
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data



def mars_news(browser):
    # Scrap mars news
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handing
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit JPL Space Images URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # Add try/except error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


def mars_facts():
    # Add try/except for error handling    
    try:
        # Use read_html to scrape the data into a table
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None
    
    # Assign columns and set index
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    classes = 'table table-striped table-condensed'

    return df.to_html(classes=classes)

def hemispheres(browser):
    # Use the browser to visit the hemisphere image url
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere.
    for i in range(4):
        hemispheres = {}
        browser.find_by_css("a.product-item img", wait_time=1)[i].click()
        title = browser.find_by_css('h2.title', wait_time=1).text
        img_url = browser.find_by_text('Sample', wait_time=1)['href']
        hemispheres['img_url'] = img_url
        hemispheres['title'] = title
        hemisphere_image_urls.append(hemispheres)
        browser.back()
    
    # Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

 
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())