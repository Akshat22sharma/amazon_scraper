import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_amazon_products(pages=20):
    base_url = 'https://www.amazon.in/s'
    search_query = 'bags'
    product_data_list = []

    for page_num in range(1, pages + 1):
        query_params = {
            'k': search_query,
            'crid': '2M096C61O4MLT',
            'qid': '1653308124',
            'sprefix': 'ba,aps,283',
            'ref': f'sr_pg_{page_num}',
            'page': page_num
        }

        response = requests.get(base_url, params=query_params)
        soup = BeautifulSoup(response.text, 'html.parser')

        for product in soup.select('.s-result-item'):
            product_url = product.find('a', class_='a-link-normal')
            product_name = product.find('h2')
            product_price = product.find('span', class_='a-price')
            product_rating = product.find('span', class_='a-icon-alt')
            num_reviews = product.find('span', class_='a-size-base')

            if product_url and product_name and product_price and product_rating and num_reviews:
                product_url = product_url['href']
                product_name = product_name.text.strip()
                product_price = product_price.find('span', class_='a-offscreen').text.strip()
                rating = product_rating.text.split()[0]
                num_reviews = num_reviews.text.strip()
                product_data_list.append([product_url, product_name, product_price, rating, num_reviews])

    return product_data_list

def export_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews'])
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    scraped_data = scrape_amazon_products(pages=20)
    export_to_csv(scraped_data, 'amazon_products.csv')
    print("Scraping completed and data exported to amazon_products.csv")






