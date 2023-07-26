import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_product_listing(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_list = []
    
    for product in soup.select('.s-result-item'):
        product_url_elem = product.find('a', class_='a-link-normal')
        if product_url_elem:
            product_url = product_url_elem['href']
            if not product_url.startswith('http'):
                product_url = 'https://www.amazon.in' + product_url
            product_name = product.find('h2').text.strip()
            product_price = product.find('span', class_='a-price').find('span', class_='a-offscreen').text.strip()
            product_rating = product.find('span', class_='a-icon-alt')
            rating = product_rating.text.split()[0] if product_rating else 'Not available'
            num_reviews = product.find('span', class_='a-size-base').text.strip() if product.find('span', class_='a-size-base') else '0'
            product_list.append([product_url, product_name, product_price, rating, num_reviews])
    
    return product_list

def scrape_product_details(product_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_asin = soup.find('th', text='ASIN').find_next_sibling('td').text.strip()
    product_desc = soup.find('div', id='productDescription').text.strip()
    manufacturer = soup.find('a', class_='a-link-normal', href=lambda href: href and 'manufacturers' in href).text.strip()
    
    return product_asin, product_desc, manufacturer

def scrape_amazon_products(pages=20, max_products=200):
    base_url = 'https://www.amazon.in/s'
    search_query = 'bags'
    product_urls = []
    all_product_data = []
    
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
            product_url_elem = product.find('a', class_='a-link-normal')
            if product_url_elem:
                product_url = product_url_elem['href']
                if not product_url.startswith('http'):
                    product_url = 'https://www.amazon.in' + product_url
                product_urls.append(product_url)
            if len(product_urls) >= max_products:
                break
        
        if len(product_urls) >= max_products:
            break
    
    print(f'Scraping {len(product_urls)} product URLs...')
    
    for idx, url in enumerate(product_urls):
        product_data = scrape_product_listing(url)
        
        for item in product_data:
            product_asin, product_desc, manufacturer = scrape_product_details(item[0])
            item.extend([product_asin, product_desc, manufacturer])
        
        all_product_data.extend(product_data)
        
        # To avoid overloading the server with requests, we'll introduce a small delay
        if idx % 20 == 0 and idx > 0:
            print(f'Finished scraping {idx} URLs. Pausing for 5 seconds...')
            time.sleep(5)
    
    return all_product_data

def export_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'ASIN', 'Product Description', 'Manufacturer'])
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    scraped_data = scrape_amazon_products(pages=20, max_products=200)
    export_to_csv(scraped_data, 'amazon_products_part2.csv')
    print("Scraping completed and data exported to amazon_products_part2.csv")

