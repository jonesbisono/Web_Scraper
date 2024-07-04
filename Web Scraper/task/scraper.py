import requests
from bs4 import BeautifulSoup
import os
import string

def get_title(url):
    try:
        page = requests.get(url)

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            title = soup.find('title').text
            summary = soup.find('meta', attrs={'name': 'description'})['content']
            return {"title": title, "description": summary}
        else:
            return "Invalid page!"
    except requests.exceptions.RequestException:
        return "Invalid page!"
    except TypeError:
        return "Invalid page!"



def get_quote(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'content' in data:
                return data['content']
            else:
                return "Invalid quote resource!"

        else:
            return "Invalid quote resource!"

    except requests.exceptions.RequestException:
        return "Invalid URL!"


def save_content(url):
    try:
        response = requests.get(url)
        page_content = requests.get(url).content
        if response.status_code == 200:
            with open('source.html', 'wb') as f:
                f.write(page_content)
                return "Content saved."
        else:
            return f"The URL returned {response.status_code}"
    except requests.exceptions.RequestException:
        return f"The URL returned {response.status_code}"


'''-----------------------------------------'''

def clean_filename(title):
    # Remove punctuation and replace spaces with underscores
    translator = str.maketrans("", "", string.punctuation)
    return "_".join(title.translate(translator).split()).strip()

def save_article_to_file(title, content, page_number):
    # Clean title for use as filename
    cleaned_title = clean_filename(title)
    filename = f"Page_{page_number}/{cleaned_title}.txt"

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Save article content to file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        print(f"Error creating directory or saving file: {e}")

def scrape_nature_articles(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find all articles
        articles = soup.find_all('article')

        for article in articles:
            # Extract article type
            article_type = article.find('span', attrs={'data-test': 'article.type'}).text

            # Check if article type is "News"
            if article_type.lower() == 'news':
                # Extract article title
                article_title = article.find('h3').text.strip()

                # Extract link to full article content
                article_link = article.find('a', attrs={'data-track-action': 'view article'})['href']
                full_article_url = f"https://www.nature.com{article_link}"

                # Retrieve full article content
                full_article_page = requests.get(full_article_url)
                full_article_soup = BeautifulSoup(full_article_page.content, 'html.parser')
                article_body = full_article_soup.find('p', class_='article__teaser').text.strip()

                # Save article content to a file
                save_article_to_file(article_title, article_body)

    except requests.exceptions.RequestException:
        print("Error fetching the page or article data.")


def multiple_pages_scrape(num_pages, article_type):
    base_url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page="

    for page_number in range(1, num_pages + 1):
        url = f"{base_url}{page_number}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find all articles
        articles = soup.find_all('article')

        found_article = False

        for article in articles:
            # Extract article type
            article_type_found = article.find('span', attrs={'data-test': 'article.type'}).text.lower()

            # Check if article type matches user input
            if article_type_found == article_type.lower():
                # Extract article title
                article_title = article.find('h3').text.strip()

                # Extract link to full article content
                article_link = article.find('a', attrs={'data-track-action': 'view article'})['href']
                full_article_url = f"https://www.nature.com{article_link}"

                # Retrieve full article content
                full_article_page = requests.get(full_article_url)
                full_article_soup = BeautifulSoup(full_article_page.content, 'html.parser')
                article_body = full_article_soup.find('p', class_='article__teaser').text.strip()

                # Save article content to a file
                save_article_to_file(article_title, article_body, page_number)

            if not found_article:
                os.makedirs(f"Page_{page_number}", exist_ok=True)



# Example usage:
if __name__ == "__main__":
    num_pages = int(input())
    article_type = input()
    multiple_pages_scrape(num_pages, article_type)
    print("Saved all articles.")