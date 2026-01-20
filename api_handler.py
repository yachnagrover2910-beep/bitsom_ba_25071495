"""
API Handler for Sales Analytics System
Handles API requests to DummyJSON for product data
"""

import requests
import json

# Base URL for DummyJSON API
BASE_URL = "https://dummyjson.com/products"


# ============================================================================
# Task 3.1: Fetch Product Details
# ============================================================================

def fetch_all_products():
    """
    Fetches all products from DummyJSON API
    
    Returns: list of product dictionaries
    
    Expected Output Format:
    [
        {
            'id': 1,
            'title': 'iPhone 9',
            'category': 'smartphones',
            'brand': 'Apple',
            'price': 549,
            'rating': 4.69
        },
        ...
    ]
    
    Requirements:
    - Fetch all available products (use limit=100)
    - Handle connection errors with try-except
    - Return empty list if API fails
    - Print status message (success/failure)
    """
    
    print("\n[Fetching Products from API]")
    
    try:
        # Fetch products with limit=100 to get all products
        url = f"{BASE_URL}?limit=100"
        response = requests.get(url, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✓ Successfully fetched {len(products)} products from API")
            return products
        else:
            print(f"✗ API request failed with status code: {response.status_code}")
            return []
    
    except requests.exceptions.ConnectionError:
        print("✗ Connection error: Unable to connect to API")
        return []
    
    except requests.exceptions.Timeout:
        print("✗ Timeout error: API request took too long")
        return []
    
    except requests.exceptions.RequestException as e:
        print(f"✗ API request error: {e}")
        return []
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []


def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    
    Parameters: api_products from fetch_all_products()
    
    Returns: dictionary mapping product IDs to info
    
    Expected Output Format:
    {
        1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
        2: {'title': 'iPhone X', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.44},
        ...
    }
    """
    
    product_mapping = {}
    
    for product in api_products:
        product_id = product.get('id')
        
        if product_id is not None:
            product_mapping[product_id] = {
                'title': product.get('title', 'Unknown'),
                'category': product.get('category', 'Unknown'),
                'brand': product.get('brand', 'Unknown'),
                'rating': product.get('rating', 0.0)
            }
    
    return product_mapping


def get_product_by_id(product_id):
    """
    Fetches a single product by ID from DummyJSON API
    
    Parameters: product_id (int)
    
    Returns: product dictionary or None if not found
    
    Example:
    product = get_product_by_id(1)
    # Returns: {'id': 1, 'title': 'iPhone 9', 'category': 'smartphones', ...}
    """
    
    try:
        url = f"{BASE_URL}/{product_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Product ID {product_id} not found")
            return None
    
    except Exception as e:
        print(f"✗ Error fetching product {product_id}: {e}")
        return None


def search_products(query):
    """
    Search products by query string
    
    Parameters: query (string) - search term
    
    Returns: list of matching products
    
    Example:
    results = search_products('phone')
    # Returns list of products matching 'phone'
    """
    
    try:
        url = f"{BASE_URL}/search?q={query}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"✓ Found {len(products)} products matching '{query}'")
            return products
        else:
            print(f"✗ Search failed for query: {query}")
            return []
    
    except Exception as e:
        print(f"✗ Error searching products: {e}")
        return []


def save_products_to_file(products, filename='output/api_products.json'):
    """
    Save fetched products to JSON file
    
    Parameters:
    - products: list of product dictionaries
    - filename: output file path
    """
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"✓ Products saved to {filename}")
    except Exception as e:
        print(f"✗ Error saving products to file: {e}")


def print_product_summary(products):
    """
    Print a summary of fetched products
    
    Parameters: products - list of product dictionaries
    """
    
    if not products:
        print("No products to display")
        return
    
    print("\n" + "="*60)
    print("PRODUCT SUMMARY")
    print("="*60)
    
    # Count by category
    categories = {}
    brands = {}
    
    for product in products:
        category = product.get('category', 'Unknown')
        brand = product.get('brand', 'Unknown')
        
        categories[category] = categories.get(category, 0) + 1
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\nTotal Products: {len(products)}")
    print(f"Categories: {len(categories)}")
    print(f"Brands: {len(brands)}")
    
    print("\nTop 5 Categories:")
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    for category, count in sorted_categories:
        print(f"  {category}: {count} products")
    
    print("\nTop 5 Brands:")
    sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]
    for brand, count in sorted_brands:
        print(f"  {brand}: {count} products")
    
    print("="*60)


# ============================================================================
# Task 3.2: Enrich Sales Data
# ============================================================================

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    
    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()
    
    Returns: list of enriched transaction dictionaries
    
    Expected Output Format (each transaction):
    {
        'TransactionID': 'T001',
        'Date': '2024-12-01',
        'ProductID': 'P101',
        'ProductName': 'Laptop',
        'Quantity': 2,
        'UnitPrice': 45000.0,
        'CustomerID': 'C001',
        'Region': 'North',
        # NEW FIELDS ADDED FROM API:
        'API_Category': 'laptops',
        'API_Brand': 'Apple',
        'API_Rating': 4.7,
        'API_Match': True  # True if enrichment successful, False otherwise
    }
    
    Enrichment Logic:
    - Extract numeric ID from ProductID (P101 -> 101, P5 -> 5)
    - If ID exists in product_mapping, add API fields
    - If ID doesn't exist, set API_Match to False and other fields to None
    - Handle all errors gracefully
    """
    
    enriched_transactions = []
    
    print("\n[Enriching Transactions with API Data]")
    match_count = 0
    no_match_count = 0
    
    for transaction in transactions:
        # Create a copy of the transaction
        enriched = transaction.copy()
        
        try:
            # Extract numeric ID from ProductID (e.g., 'P101' -> 101, 'P5' -> 5)
            product_id_str = transaction.get('ProductID', '')
            
            # Remove 'P' prefix and convert to integer
            if product_id_str.startswith('P'):
                numeric_id = int(product_id_str[1:])
            else:
                numeric_id = int(product_id_str)
            
            # Check if product exists in mapping
            if numeric_id in product_mapping:
                product_info = product_mapping[numeric_id]
                
                # Add API fields
                enriched['API_Category'] = product_info.get('category', None)
                enriched['API_Brand'] = product_info.get('brand', None)
                enriched['API_Rating'] = product_info.get('rating', None)
                enriched['API_Match'] = True
                match_count += 1
            else:
                # Product not found in API
                enriched['API_Category'] = None
                enriched['API_Brand'] = None
                enriched['API_Rating'] = None
                enriched['API_Match'] = False
                no_match_count += 1
        
        except (ValueError, TypeError, AttributeError) as e:
            # Handle errors gracefully
            enriched['API_Category'] = None
            enriched['API_Brand'] = None
            enriched['API_Rating'] = None
            enriched['API_Match'] = False
            no_match_count += 1
        
        enriched_transactions.append(enriched)
    
    print(f"✓ Enriched {len(enriched_transactions)} transactions")
    print(f"  - Matched with API: {match_count}")
    print(f"  - No API match: {no_match_count}")
    
    return enriched_transactions


def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file
    
    Expected File Format:
    TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match
    T001|2024-12-01|P101|Laptop|2|45000.0|C001|North|laptops|Apple|4.7|True
    ...
    
    Requirements:
    - Create output file with all original + new fields
    - Use pipe delimiter
    - Handle None values appropriately
    """
    
    print(f"\n[Saving Enriched Data to {filename}]")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            header = "TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region|API_Category|API_Brand|API_Rating|API_Match\n"
            f.write(header)
            
            # Write data
            for transaction in enriched_transactions:
                # Handle None values
                api_category = transaction.get('API_Category') or ''
                api_brand = transaction.get('API_Brand') or ''
                api_rating = transaction.get('API_Rating') or ''
                api_match = transaction.get('API_Match', False)
                
                line = (
                    f"{transaction.get('TransactionID', '')}|"
                    f"{transaction.get('Date', '')}|"
                    f"{transaction.get('ProductID', '')}|"
                    f"{transaction.get('ProductName', '')}|"
                    f"{transaction.get('Quantity', '')}|"
                    f"{transaction.get('UnitPrice', '')}|"
                    f"{transaction.get('CustomerID', '')}|"
                    f"{transaction.get('Region', '')}|"
                    f"{api_category}|"
                    f"{api_brand}|"
                    f"{api_rating}|"
                    f"{api_match}\n"
                )
                f.write(line)
        
        print(f"✓ Enriched data saved to {filename}")
        return True
    
    except Exception as e:
        print(f"✗ Error saving enriched data: {e}")
        return False


def print_enrichment_summary(enriched_transactions):
    """
    Print summary of enrichment process
    """
    
    print("\n" + "="*60)
    print("ENRICHMENT SUMMARY")
    print("="*60)
    
    total = len(enriched_transactions)
    matched = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
    not_matched = total - matched
    
    print(f"\nTotal Transactions: {total}")
    print(f"Successfully Enriched: {matched}")
    print(f"No API Match: {not_matched}")
    
    if total > 0:
        print(f"Success Rate: {(matched/total*100):.2f}%")
    
    # Show API categories distribution
    categories = {}
    for transaction in enriched_transactions:
        if transaction.get('API_Match'):
            category = transaction.get('API_Category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
    
    if categories:
        print("\nAPI Categories Found:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} transactions")
    
    # Show API brands distribution
    brands = {}
    for transaction in enriched_transactions:
        if transaction.get('API_Match'):
            brand = transaction.get('API_Brand', 'Unknown')
            brands[brand] = brands.get(brand, 0) + 1
    
    if brands:
        print("\nAPI Brands Found:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {brand}: {count} transactions")
    
    print("="*60)