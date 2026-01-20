import re

class DataCleaner:
    def __init__(self):
        self.total_records = 0
        self.invalid_records = 0
        self.valid_records = 0
        self.invalid_reasons = []
    
    def is_valid_record(self, fields):
        """
        Check if record is valid based on criteria
        Returns (is_valid, reason)
        """
        # Check if we have expected number of fields
        if len(fields) < 8:
            return False, "Insufficient fields"
        
        # Extract fields based on YOUR column structure
        # TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region
        transaction_id = fields[0].strip() if len(fields) > 0 else ""
        customer_id = fields[6].strip() if len(fields) > 6 else ""
        region = fields[7].strip() if len(fields) > 7 else ""
        quantity = fields[4].strip() if len(fields) > 4 else ""
        unit_price = fields[5].strip() if len(fields) > 5 else ""
        
        # Rule 1: Missing CustomerID or Region → Remove
        if not customer_id or not region:
            return False, "Missing CustomerID or Region"
        
        # Rule 2: Quantity <= 0 → Remove
        try:
            qty = self.clean_numeric(quantity)
            if qty <= 0:
                return False, "Quantity <= 0"
        except (ValueError, AttributeError):
            return False, "Invalid Quantity format"
        
        # Rule 3: UnitPrice <= 0 → Remove
        try:
            price = self.clean_numeric(unit_price)
            if price <= 0:
                return False, "UnitPrice <= 0"
        except (ValueError, AttributeError):
            return False, "Invalid UnitPrice format"
        
        # Rule 4: TransactionID not starting with 'T' → Remove
        if not transaction_id.startswith('T'):
            return False, "TransactionID not starting with 'T'"
        
        return True, "Valid"
    
    def clean_numeric(self, value):
        """
        Remove commas from numbers and convert to float
        Example: '1,500' -> 1500.0
        """
        if not value:
            raise ValueError("Empty value")
        # Remove commas
        cleaned = value.replace(',', '')
        return float(cleaned)
    
    def clean_field(self, field):
        """
        Clean individual field - remove commas from numeric-looking fields
        """
        # If field looks like a number (contains only digits, dots, commas, minus)
        if re.match(r'^[\d,.\-]+$', field):
            return field.replace(',', '')
        return field
    
    def clean_product_name(self, product_name):
        """
        Remove commas from product names
        Example: 'Mouse,Wireless' -> 'Mouse Wireless'
        """
        return product_name.replace(',', ' ')
    
    def clean_record(self, fields):
        """
        Clean a valid record
        TransactionID|Date|ProductID|ProductName|Quantity|UnitPrice|CustomerID|Region
        """
        cleaned_fields = []
        
        for i, field in enumerate(fields):
            field = field.strip()
            
            # Index 3: ProductName - remove commas
            if i == 3:
                cleaned_fields.append(self.clean_product_name(field))
            # Index 4: Quantity - remove commas from numbers
            elif i == 4:
                cleaned_fields.append(self.clean_field(field))
            # Index 5: UnitPrice - remove commas from numbers
            elif i == 5:
                cleaned_fields.append(self.clean_field(field))
            else:
                cleaned_fields.append(field)
        
        return cleaned_fields
    
    def process_records(self, lines):
        """
        Main processing function
        Returns (valid_lines, invalid_lines)
        """
        valid_lines = []
        invalid_lines = []
        
        # Keep header
        if lines:
            header = lines[0]
            valid_lines.append(header)
            lines = lines[1:]
        
        self.total_records = len(lines)
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            from utils.file_handler import parse_line
            fields = parse_line(line)
            
            # Check validity
            is_valid, reason = self.is_valid_record(fields)
            
            if is_valid:
                # Clean and keep the record
                cleaned_fields = self.clean_record(fields)
                from utils.file_handler import create_line
                valid_lines.append(create_line(cleaned_fields))
                self.valid_records += 1
            else:
                # Remove invalid record
                self.invalid_records += 1
                self.invalid_reasons.append(f"{reason}: {line.strip()}")
                invalid_lines.append(line)
        
        return valid_lines, invalid_lines
    
    def print_summary(self):
        """
        Print cleaning summary
        """
        print("\n" + "="*50)
        print("DATA CLEANING SUMMARY")
        print("="*50)
        print(f"Total records parsed: {self.total_records}")
        print(f"Invalid records removed: {self.invalid_records}")
        print(f"Valid records after cleaning: {self.valid_records}")
        print("="*50)


# ============================================================================
# Task 2.1: Sales Summary Calculator
# ============================================================================

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions
    
    Returns: float (total revenue)
    
    Expected Output: Single number representing sum of (Quantity * UnitPrice)
    Example: 1545000.50
    """
    total_revenue = 0.0
    
    for transaction in transactions:
        try:
            # Extract and clean quantity
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            # Extract and clean unit price
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            
            # Calculate revenue for this transaction
            revenue = quantity * unit_price
            total_revenue += revenue
            
        except (ValueError, TypeError, AttributeError):
            # Skip transactions with invalid data
            continue
    
    return total_revenue


def region_wise_sales(transactions):
    """
    Analyzes sales by region
    
    Returns: dictionary with region statistics
    
    Expected Output Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 25.13
        },
        'South': {...},
        ...
    }
    
    Requirements:
    - Calculate total sales per region
    - Count transactions per region
    - Calculate percentage of total sales
    - Sort by total_sales in descending order
    """
    
    # Step 1: Aggregate data by region
    region_data = {}
    total_revenue = 0.0
    
    for transaction in transactions:
        try:
            region = transaction.get('Region', 'Unknown')
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            revenue = quantity * unit_price
            
            # Initialize region if not exists
            if region not in region_data:
                region_data[region] = {
                    'total_sales': 0.0,
                    'transaction_count': 0,
                    'percentage': 0.0
                }
            
            # Update region data
            region_data[region]['total_sales'] += revenue
            region_data[region]['transaction_count'] += 1
            total_revenue += revenue
            
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Step 2: Calculate percentages
    for region in region_data:
        if total_revenue > 0:
            region_data[region]['percentage'] = round(
                (region_data[region]['total_sales'] / total_revenue) * 100, 
                2
            )
    
    # Step 3: Sort by total_sales descending
    sorted_regions = dict(
        sorted(
            region_data.items(), 
            key=lambda x: x[1]['total_sales'], 
            reverse=True
        )
    )
    
    return sorted_regions


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    
    Returns: list of tuples
    
    Expected Output Format:
    [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 15000.0),
        ...
    ]
    
    Requirements:
    - Aggregate by ProductName
    - Calculate total quantity sold
    - Calculate total revenue for each product
    - Sort by TotalQuantity descending
    - Return top n products
    """
    
    # Step 1: Aggregate by ProductName
    product_data = {}
    
    for transaction in transactions:
        try:
            product_name = transaction.get('ProductName', 'Unknown')
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            revenue = quantity * unit_price
            
            # Initialize product if not exists
            if product_name not in product_data:
                product_data[product_name] = {
                    'total_quantity': 0,
                    'total_revenue': 0.0
                }
            
            # Update product data
            product_data[product_name]['total_quantity'] += quantity
            product_data[product_name]['total_revenue'] += revenue
            
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Step 2: Convert to list of tuples
    product_list = [
        (name, data['total_quantity'], data['total_revenue'])
        for name, data in product_data.items()
    ]
    
    # Step 3: Sort by total_quantity descending
    product_list.sort(key=lambda x: x[1], reverse=True)
    
    # Step 4: Return top n products
    return product_list[:n]


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    
    Returns: dictionary of customer statistics
    
    Expected Output Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        'C002': {...},
        ...
    }
    
    Requirements:
    - Calculate total amount spent per customer
    - Count number of purchases
    - Calculate average order value
    - List unique products bought
    - Sort by total_spent descending
    """
    
    # Step 1: Aggregate data by CustomerID
    customer_data = {}
    
    for transaction in transactions:
        try:
            customer_id = transaction.get('CustomerID', 'Unknown')
            product_name = transaction.get('ProductName', 'Unknown')
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            amount = quantity * unit_price
            
            # Initialize customer if not exists
            if customer_id not in customer_data:
                customer_data[customer_id] = {
                    'total_spent': 0.0,
                    'purchase_count': 0,
                    'avg_order_value': 0.0,
                    'products_bought': []
                }
            
            # Update customer data
            customer_data[customer_id]['total_spent'] += amount
            customer_data[customer_id]['purchase_count'] += 1
            
            # Add product to list if not already there
            if product_name not in customer_data[customer_id]['products_bought']:
                customer_data[customer_id]['products_bought'].append(product_name)
            
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Step 2: Calculate average order value
    for customer_id in customer_data:
        if customer_data[customer_id]['purchase_count'] > 0:
            customer_data[customer_id]['avg_order_value'] = round(
                customer_data[customer_id]['total_spent'] / customer_data[customer_id]['purchase_count'],
                2
            )
    
    # Step 3: Sort by total_spent descending
    sorted_customers = dict(
        sorted(
            customer_data.items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )
    )
    
    return sorted_customers



from datetime import datetime

# ============================================================================
# Task 2.2: Date-based Analysis
# ============================================================================

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date
    
    Returns: dictionary sorted by date
    
    Expected Output Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        '2024-12-02': {...},
        ...
    }
    
    Requirements:
    - Group by date
    - Calculate daily revenue
    - Count daily transactions
    - Count unique customers per day
    - Sort chronologically
    """
    
    # Step 1: Aggregate data by date
    daily_data = {}
    
    for transaction in transactions:
        try:
            date = transaction.get('Date', '').strip()
            customer_id = transaction.get('CustomerID', '').strip()
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            revenue = quantity * unit_price
            
            # Initialize date if not exists
            if date not in daily_data:
                daily_data[date] = {
                    'revenue': 0.0,
                    'transaction_count': 0,
                    'unique_customers': set()
                }
            
            # Update daily data
            daily_data[date]['revenue'] += revenue
            daily_data[date]['transaction_count'] += 1
            daily_data[date]['unique_customers'].add(customer_id)
            
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Step 2: Convert sets to counts
    result = {}
    for date, data in daily_data.items():
        result[date] = {
            'revenue': round(data['revenue'], 2),
            'transaction_count': data['transaction_count'],
            'unique_customers': len(data['unique_customers'])
        }
    
    # Step 3: Sort chronologically
    sorted_result = dict(sorted(result.items()))
    
    return sorted_result


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue
    
    Returns: tuple (date, revenue, transaction_count)
    
    Expected Output Format:
    ('2024-12-15', 185000.0, 12)
    
    Requirements:
    - Find date with maximum revenue
    - Return date, revenue, and transaction count
    """
    
    # Step 1: Get daily sales data
    daily_sales = daily_sales_trend(transactions)
    
    if not daily_sales:
        return (None, 0.0, 0)
    
    # Step 2: Find peak day
    peak_day = max(daily_sales.items(), key=lambda x: x[1]['revenue'])
    
    date = peak_day[0]
    revenue = peak_day[1]['revenue']
    transaction_count = peak_day[1]['transaction_count']
    
    return (date, revenue, transaction_count)


# ============================================================================
# Task 2.3: Product Performance
# ============================================================================

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales
    
    Returns: list of tuples
    
    Expected Output Format:
    [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Headphones', 7, 10500.0),
        ...
    ]
    
    Requirements:
    - Find products with total quantity < threshold
    - Include total quantity and revenue
    - Sort by TotalQuantity ascending
    """
    
    # Step 1: Aggregate by ProductName
    product_data = {}
    
    for transaction in transactions:
        try:
            product_name = transaction.get('ProductName', 'Unknown')
            quantity = float(str(transaction.get('Quantity', 0)).replace(',', ''))
            unit_price = float(str(transaction.get('UnitPrice', 0)).replace(',', ''))
            revenue = quantity * unit_price
            
            # Initialize product if not exists
            if product_name not in product_data:
                product_data[product_name] = {
                    'total_quantity': 0,
                    'total_revenue': 0.0
                }
            
            # Update product data
            product_data[product_name]['total_quantity'] += quantity
            product_data[product_name]['total_revenue'] += revenue
            
        except (ValueError, TypeError, AttributeError):
            continue
    
    # Step 2: Filter products with quantity < threshold
    low_performing = []
    
    for product_name, data in product_data.items():
        if data['total_quantity'] < threshold:
            low_performing.append((
                product_name,
                int(data['total_quantity']),
                round(data['total_revenue'], 2)
            ))
    
    # Step 3: Sort by TotalQuantity ascending
    low_performing.sort(key=lambda x: x[1])
    
    return low_performing

"""
Generate comprehensive text report as per Task 4.1
"""

from datetime import datetime

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report
    
    Report Must Include (in this order):
    
    1. HEADER
       - Report title
       - Generation date and time
       - Total records processed
    
    2. OVERALL SUMMARY
       - Total Revenue (formatted with commas)
       - Total Transactions
       - Average Order Value
       - Date Range of data
    
    3. REGION-WISE PERFORMANCE
       - Table showing each region with:
         * Total Sales Amount
         * Percentage of Total
         * Transaction Count
         * Sorted by sales amount descending
    
    4. TOP 5 PRODUCTS
       - Table with columns: Rank, Product Name, Quantity Sold, Revenue
    
    5. TOP 5 CUSTOMERS
       - Table with columns: Rank, Customer ID, Total Spent, Order Count
    
    6. DAILY SALES TREND
       - Table showing: Date, Revenue, Transactions, Unique Customers
    
    7. PRODUCT PERFORMANCE ANALYSIS
       - Best selling day
       - Low performing products (if any)
       - Average transaction value per region
    
    8. API ENRICHMENT SUMMARY
       - Total enriched records
       - Success rate percentage
       - List of products that couldn't be enriched
    """
    
    from utils.data_processor import (
        calculate_total_revenue,
        region_wise_sales,
        top_selling_products,
        customer_analysis,
        daily_sales_trend,
        find_peak_sales_day,
        low_performing_products
    )
    
    print(f"\n[Generating Comprehensive Report to {output_file}]")
    
    report_lines = []
    
    # ========================================================================
    # 1. HEADER
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append(" "*20 + "SALES ANALYTICS REPORT\n")
    report_lines.append("="*70 + "\n\n")
    
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines.append(f"Report Generated: {generation_time}\n")
    report_lines.append(f"Total Records Processed: {len(transactions)}\n")
    report_lines.append("\n")
    
    # ========================================================================
    # 2. OVERALL SUMMARY
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("1. OVERALL SUMMARY\n")
    report_lines.append("="*70 + "\n\n")
    
    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Get date range
    dates = [t.get('Date', '') for t in transactions if t.get('Date')]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"
    
    report_lines.append(f"Total Revenue: ${total_revenue:,.2f}\n")
    report_lines.append(f"Total Transactions: {total_transactions:,}\n")
    report_lines.append(f"Average Order Value: ${avg_order_value:,.2f}\n")
    report_lines.append(f"Date Range: {date_range}\n")
    report_lines.append("\n")
    
    # ========================================================================
    # 3. REGION-WISE PERFORMANCE
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("2. REGION-WISE PERFORMANCE\n")
    report_lines.append("="*70 + "\n\n")
    
    region_sales = region_wise_sales(transactions)
    
    report_lines.append(f"{'Region':<15}{'Sales Amount':<20}{'Percentage':<15}{'Trans Count':<15}\n")
    report_lines.append("-"*70 + "\n")
    
    for region, stats in region_sales.items():
        report_lines.append(
            f"{region:<15}"
            f"${stats['total_sales']:>18,.2f}"
            f"{stats['percentage']:>14.2f}%"
            f"{stats['transaction_count']:>14}\n"
        )
    
    report_lines.append("\n")
    
    # ========================================================================
    # 4. TOP 5 PRODUCTS
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("3. TOP 5 PRODUCTS\n")
    report_lines.append("="*70 + "\n\n")
    
    top_products = top_selling_products(transactions, n=5)
    
    report_lines.append(f"{'Rank':<8}{'Product Name':<30}{'Qty Sold':<15}{'Revenue':<17}\n")
    report_lines.append("-"*70 + "\n")
    
    for i, (product, quantity, revenue) in enumerate(top_products, 1):
        report_lines.append(
            f"{i:<8}"
            f"{product[:28]:<30}"
            f"{int(quantity):<15}"
            f"${revenue:,.2f}\n"
        )
    
    report_lines.append("\n")
    
    # ========================================================================
    # 5. TOP 5 CUSTOMERS
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("4. TOP 5 CUSTOMERS\n")
    report_lines.append("="*70 + "\n\n")
    
    customer_stats = customer_analysis(transactions)
    top_5_customers = list(customer_stats.items())[:5]
    
    report_lines.append(f"{'Rank':<8}{'Customer ID':<20}{'Total Spent':<20}{'Order Count':<15}\n")
    report_lines.append("-"*70 + "\n")
    
    for i, (customer_id, stats) in enumerate(top_5_customers, 1):
        report_lines.append(
            f"{i:<8}"
            f"{customer_id:<20}"
            f"${stats['total_spent']:>18,.2f}"
            f"{stats['purchase_count']:>14}\n"
        )
    
    report_lines.append("\n")
    
    # ========================================================================
    # 6. DAILY SALES TREND
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("5. DAILY SALES TREND\n")
    report_lines.append("="*70 + "\n\n")
    
    daily_trend = daily_sales_trend(transactions)
    
    report_lines.append(f"{'Date':<15}{'Revenue':<20}{'Transactions':<18}{'Unique Customers':<17}\n")
    report_lines.append("-"*70 + "\n")
    
    # Show first 10 days
    for i, (date, stats) in enumerate(daily_trend.items()):
        if i < 10:
            report_lines.append(
                f"{date:<15}"
                f"${stats['revenue']:>18,.2f}"
                f"{stats['transaction_count']:>17}"
                f"{stats['unique_customers']:>16}\n"
            )
    
    if len(daily_trend) > 10:
        report_lines.append(f"... ({len(daily_trend) - 10} more days)\n")
    
    report_lines.append(f"\nTotal Days with Sales: {len(daily_trend)}\n")
    report_lines.append("\n")
    
    # ========================================================================
    # 7. PRODUCT PERFORMANCE ANALYSIS
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("6. PRODUCT PERFORMANCE ANALYSIS\n")
    report_lines.append("="*70 + "\n\n")
    
    # Best selling day
    peak_date, peak_revenue, peak_count = find_peak_sales_day(transactions)
    report_lines.append(f"Best Selling Day: {peak_date}\n")
    report_lines.append(f"  Revenue: ${peak_revenue:,.2f}\n")
    report_lines.append(f"  Transactions: {peak_count}\n\n")
    
    # Low performing products
    low_products = low_performing_products(transactions, threshold=10)
    if low_products:
        report_lines.append("Low Performing Products (Quantity < 10):\n")
        for product, quantity, revenue in low_products:
            report_lines.append(f"  - {product}: {quantity} units, ${revenue:,.2f}\n")
    else:
        report_lines.append("No low performing products found.\n")
    
    report_lines.append("\n")
    
    # Average transaction value per region
    report_lines.append("Average Transaction Value by Region:\n")
    for region, stats in region_sales.items():
        avg_value = stats['total_sales'] / stats['transaction_count'] if stats['transaction_count'] > 0 else 0
        report_lines.append(f"  {region}: ${avg_value:,.2f}\n")
    
    report_lines.append("\n")
    
    # ========================================================================
    # 8. API ENRICHMENT SUMMARY
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append("7. API ENRICHMENT SUMMARY\n")
    report_lines.append("="*70 + "\n\n")
    
    if enriched_transactions:
        total_enriched = len(enriched_transactions)
        matched = sum(1 for t in enriched_transactions if t.get('API_Match') == True)
        success_rate = (matched / total_enriched * 100) if total_enriched > 0 else 0
        
        report_lines.append(f"Total Records Enriched: {total_enriched}\n")
        report_lines.append(f"Successfully Matched: {matched}\n")
        report_lines.append(f"Success Rate: {success_rate:.2f}%\n\n")
        
        # List products that couldn't be enriched
        unmatched = [t for t in enriched_transactions if not t.get('API_Match')]
        if unmatched:
            report_lines.append("Products that couldn't be enriched:\n")
            unique_unmatched = {}
            for t in unmatched:
                prod_id = t.get('ProductID', 'Unknown')
                prod_name = t.get('ProductName', 'Unknown')
                if prod_id not in unique_unmatched:
                    unique_unmatched[prod_id] = prod_name
            
            for prod_id, prod_name in unique_unmatched.items():
                report_lines.append(f"  - {prod_id}: {prod_name}\n")
        else:
            report_lines.append("All products were successfully enriched!\n")
    else:
        report_lines.append("No API enrichment data available.\n")
    
    report_lines.append("\n")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    report_lines.append("="*70 + "\n")
    report_lines.append(" "*25 + "END OF REPORT\n")
    report_lines.append("="*70 + "\n")
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(report_lines)
        print(f"✓ Comprehensive report generated: {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error generating report: {e}")
        return False