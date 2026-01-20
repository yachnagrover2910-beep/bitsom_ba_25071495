"""
File Handler for Sales Analytics System
Handles file I/O, validation, and filtering operations
"""

import codecs

def read_file(file_path):
    """
    Read pipe-delimited file with proper encoding handling
    Returns list of lines
    """
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✓ File read successfully with UTF-8 encoding")
        return lines
    except UnicodeDecodeError:
        # Fallback to other encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                print(f"✓ File read successfully with {encoding} encoding")
                return lines
            except UnicodeDecodeError:
                continue
        raise Exception("Unable to decode file with any known encoding")

def write_file(file_path, lines):
    """
    Write cleaned data to file in UTF-8 encoding
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✓ File written successfully to {file_path}")

def parse_line(line):
    """
    Parse pipe-delimited line into fields
    """
    return [field.strip() for field in line.strip().split('|')]

def create_line(fields):
    """
    Create pipe-delimited line from fields
    """
    return '|'.join(fields) + '\n'


# ============================================================================
# TASK 11c: Data Validation and Filtering
# ============================================================================

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    
    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)
    
    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    
    Expected Output Format:
    (
        [list of valid filtered transactions],
        5,  # count of invalid transactions
        {
            'total_input': 100,
            'invalid': 5,
            'filtered_by_region': 20,
            'filtered_by_amount': 10,
            'final_count': 65
        }
    )
    
    Validation Rules:
    - Quantity must be > 0
    - UnitPrice must be > 0
    - All required fields must be present
    - TransactionID must start with 'T'
    - ProductID must start with 'P'
    - CustomerID must start with 'C'
    
    Filter Display:
    - Print available regions to user before filtering
    - Print transaction amount range (min/max) to user
    - Show count of records after each filter applied
    """
    
    valid_transactions = []
    invalid_count = 0
    
    # Initialize filter summary
    filter_summary = {
        'total_input': len(transactions),
        'invalid': 0,
        'filtered_by_region': 0,
        'filtered_by_amount': 0,
        'final_count': 0
    }
    
    # Step 1: Validate transactions
    print("\n" + "="*50)
    print("VALIDATION AND FILTERING")
    print("="*50)
    
    validated_transactions = []
    
    for transaction in transactions:
        is_valid, reason = validate_transaction(transaction)
        
        if is_valid:
            validated_transactions.append(transaction)
        else:
            invalid_count += 1
            print(f"Invalid: {reason} - {transaction.get('TransactionID', 'Unknown')}")
    
    filter_summary['invalid'] = invalid_count
    print(f"\n✓ Valid transactions after validation: {len(validated_transactions)}")
    
    # Step 2: Display available regions (before filtering)
    if region is not None:
        available_regions = get_available_regions(validated_transactions)
        print(f"\nAvailable regions: {', '.join(available_regions)}")
    
    # Step 3: Display transaction amount range
    if min_amount is not None or max_amount is not None:
        amount_range = get_transaction_amount_range(validated_transactions)
        print(f"\nTransaction amount range: ${amount_range['min']:.2f} - ${amount_range['max']:.2f}")
    
    # Step 4: Apply region filter
    if region is not None:
        before_count = len(validated_transactions)
        validated_transactions = filter_by_region(validated_transactions, region)
        filtered_count = before_count - len(validated_transactions)
        filter_summary['filtered_by_region'] = filtered_count
        print(f"\n✓ After region filter ('{region}'): {len(validated_transactions)} records")
    
    # Step 5: Apply amount filter
    if min_amount is not None or max_amount is not None:
        before_count = len(validated_transactions)
        validated_transactions = filter_by_amount(validated_transactions, min_amount, max_amount)
        filtered_count = before_count - len(validated_transactions)
        filter_summary['filtered_by_amount'] = filtered_count
        print(f"✓ After amount filter: {len(validated_transactions)} records")
    
    filter_summary['final_count'] = len(validated_transactions)
    
    return (validated_transactions, invalid_count, filter_summary)


def validate_transaction(transaction):
    """
    Validate a single transaction
    Returns (is_valid, reason)
    """
    # Check required fields
    required_fields = ['TransactionID', 'ProductID', 'CustomerID', 'Quantity', 'UnitPrice']
    
    for field in required_fields:
        if field not in transaction or not transaction[field]:
            return False, f"Missing required field: {field}"
    
    # Validate Quantity > 0
    try:
        quantity = float(str(transaction['Quantity']).replace(',', ''))
        if quantity <= 0:
            return False, "Quantity must be > 0"
    except (ValueError, TypeError):
        return False, "Invalid Quantity format"
    
    # Validate UnitPrice > 0
    try:
        unit_price = float(str(transaction['UnitPrice']).replace(',', ''))
        if unit_price <= 0:
            return False, "UnitPrice must be > 0"
    except (ValueError, TypeError):
        return False, "Invalid UnitPrice format"
    
    # Validate TransactionID starts with 'T'
    if not str(transaction['TransactionID']).startswith('T'):
        return False, "TransactionID must start with 'T'"
    
    # Validate ProductID starts with 'P'
    if not str(transaction['ProductID']).startswith('P'):
        return False, "ProductID must start with 'P'"
    
    # Validate CustomerID starts with 'C'
    if not str(transaction['CustomerID']).startswith('C'):
        return False, "CustomerID must start with 'C'"
    
    return True, "Valid"


def filter_by_region(transactions, region):
    """
    Filter transactions by specific region
    """
    return [t for t in transactions if t.get('Region', '').lower() == region.lower()]


def filter_by_amount(transactions, min_amount=None, max_amount=None):
    """
    Filter transactions by amount range (Quantity * UnitPrice)
    """
    filtered = []
    
    for transaction in transactions:
        try:
            quantity = float(str(transaction['Quantity']).replace(',', ''))
            unit_price = float(str(transaction['UnitPrice']).replace(',', ''))
            amount = quantity * unit_price
            
            # Check min_amount
            if min_amount is not None and amount < min_amount:
                continue
            
            # Check max_amount
            if max_amount is not None and amount > max_amount:
                continue
            
            filtered.append(transaction)
        except (ValueError, TypeError, KeyError):
            continue
    
    return filtered


def get_available_regions(transactions):
    """
    Get list of unique regions from transactions
    """
    regions = set()
    for transaction in transactions:
        region = transaction.get('Region', '')
        if region:
            regions.add(region)
    return sorted(list(regions))


def get_transaction_amount_range(transactions):
    """
    Get min and max transaction amounts
    Returns dict with 'min' and 'max' keys
    """
    amounts = []
    
    for transaction in transactions:
        try:
            quantity = float(str(transaction['Quantity']).replace(',', ''))
            unit_price = float(str(transaction['UnitPrice']).replace(',', ''))
            amount = quantity * unit_price
            amounts.append(amount)
        except (ValueError, TypeError, KeyError):
            continue
    
    if not amounts:
        return {'min': 0, 'max': 0}
    
    return {
        'min': min(amounts),
        'max': max(amounts)
    }


def print_filter_summary(filter_summary):
    """
    Print detailed filter summary
    """
    print("\n" + "="*50)
    print("FILTER SUMMARY")
    print("="*50)
    print(f"Total input: {filter_summary['total_input']}")
    print(f"Invalid: {filter_summary['invalid']}")
    print(f"Filtered by region: {filter_summary['filtered_by_region']}")
    print(f"Filtered by amount: {filter_summary['filtered_by_amount']}")
    print(f"Final count: {filter_summary['final_count']}")
    print("="*50)