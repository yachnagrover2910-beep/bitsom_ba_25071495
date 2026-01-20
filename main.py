"""
Sales Analytics System - Complete Integrated Main Script
Includes: Data Cleaning, Data Processing, API Integration, and Comprehensive Reporting
"""

import os
from utils.file_handler import read_file, write_file, parse_line
from utils.data_processor import (
    DataCleaner,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
    generate_sales_report
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data,
    print_enrichment_summary
)


def convert_to_transactions(lines):
    """Convert pipe-delimited lines to transaction dictionaries"""
    transactions = []
    
    for line in lines:
        if not line.strip():
            continue
        
        fields = parse_line(line)
        
        if len(fields) >= 8:
            transaction = {
                'TransactionID': fields[0],
                'Date': fields[1],
                'ProductID': fields[2],
                'ProductName': fields[3],
                'Quantity': fields[4],
                'UnitPrice': fields[5],
                'CustomerID': fields[6],
                'Region': fields[7]
            }
            transactions.append(transaction)
    
    return transactions


def main():
    """Main execution function - runs all tasks"""
    
    print("\n" + "="*70)
    print(" "*15 + "SALES ANALYTICS SYSTEM")
    print(" "*20 + "Complete Integration")
    print("="*70 + "\n")
    
    # ========================================================================
    # PART 1: DATA CLEANING
    # ========================================================================
    print("="*70)
    print("PART 1: DATA CLEANING")
    print("="*70 + "\n")
    
    # File paths
    input_file = 'data/sales_data.txt'
    output_file = 'output/sales_data_cleaned.txt'
    invalid_file = 'output/invalid_records.txt'
    
    # Step 1: Read the file
    print("[Step 1] Reading input file...")
    try:
        lines = read_file(input_file)
        print(f"✓ Read {len(lines)} lines from {input_file}")
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return
    
    # Step 2: Process and clean data
    print("\n[Step 2] Processing and cleaning data...")
    cleaner = DataCleaner()
    valid_lines, invalid_lines = cleaner.process_records(lines)
    
    # Step 3: Write cleaned data
    print("\n[Step 3] Writing cleaned data...")
    write_file(output_file, valid_lines)
    
    if invalid_lines:
        write_file(invalid_file, invalid_lines)
    
    # Step 4: Print summary
    cleaner.print_summary()
    
    # Convert to transactions for further processing
    transactions = convert_to_transactions(valid_lines[1:])  # Skip header
    
    print("\n✓ Part 1: Data Cleaning Completed!")
    
    # ========================================================================
    # PART 2: DATA PROCESSING & ANALYTICS
    # ========================================================================
    print("\n" + "="*70)
    print("PART 2: DATA PROCESSING & ANALYTICS")
    print("="*70 + "\n")
    
    print("[Running Analytics Functions...]")
    
    # Run all analytics (silently for now, will be in report)
    total_revenue = calculate_total_revenue(transactions)
    region_sales = region_wise_sales(transactions)
    top_products = top_selling_products(transactions, n=5)
    customer_stats = customer_analysis(transactions)
    daily_trend = daily_sales_trend(transactions)
    peak_date, peak_revenue, peak_count = find_peak_sales_day(transactions)
    low_products = low_performing_products(transactions, threshold=10)
    
    print(f"✓ Total Revenue: ${total_revenue:,.2f}")
    print(f"✓ Analyzed {len(region_sales)} regions")
    print(f"✓ Identified top {len(top_products)} products")
    print(f"✓ Analyzed {len(customer_stats)} customers")
    print(f"✓ Processed {len(daily_trend)} days of sales data")
    print(f"✓ Peak sales day: {peak_date}")
    
    print("\n✓ Part 2: Data Processing Completed!")
    
    # ========================================================================
    # PART 3: API INTEGRATION
    # ========================================================================
    print("\n" + "="*70)
    print("PART 3: API INTEGRATION")
    print("="*70 + "\n")
    
    # Task 3.1: Fetch products from API
    print("[Task 3.1] Fetching products from API...")
    api_products = fetch_all_products()
    
    enriched_transactions = None
    
    if api_products:
        # Create product mapping
        print("\n[Task 3.1] Creating product mapping...")
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Created mapping for {len(product_mapping)} products")
        
        # Task 3.2: Enrich sales data
        print("\n[Task 3.2] Enriching sales data with API information...")
        enriched_transactions = enrich_sales_data(transactions, product_mapping)
        
        # Save enriched data
        save_enriched_data(enriched_transactions, 'data/enriched_sales_data.txt')
        save_enriched_data(enriched_transactions, 'output/enriched_sales_data.txt')
        
        # Print enrichment summary
        print_enrichment_summary(enriched_transactions)
        
        print("\n✓ Part 3: API Integration Completed!")
    else:
        print("\n⚠ Part 3: API Integration Skipped (API not available)")
        print("  Continuing with non-enriched data...")
    
    # ========================================================================
    # PART 4: COMPREHENSIVE REPORT GENERATION
    # ========================================================================
    print("\n" + "="*70)
    print("PART 4: COMPREHENSIVE REPORT GENERATION")
    print("="*70 + "\n")
    
    print("[Task 4.1] Generating comprehensive sales report...")
    
    # Generate the comprehensive report
    success = generate_sales_report(
        transactions, 
        enriched_transactions,
        output_file='output/sales_report.txt'
    )
    
    if success:
        print("\n✓ Part 4: Report Generation Completed!")
    else:
        print("\n✗ Part 4: Report Generation Failed!")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70 + "\n")
    
    print("Files Generated:")
    print("  Data Cleaning:")
    print("    ✓ output/sales_data_cleaned.txt")
    print("    ✓ output/invalid_records.txt")
    print("\n  API Integration:")
    if api_products:
        print("    ✓ data/enriched_sales_data.txt")
        print("    ✓ output/enriched_sales_data.txt")
    else:
        print("    ⚠ Skipped (API unavailable)")
    print("\n  Final Report:")
    print("    ✓ output/sales_report.txt")
    
    print("\n" + "="*70)
    print(" "*20 + "🎉 ALL TASKS COMPLETED! 🎉")
    print("="*70 + "\n")
    
    print("Next Steps:")
    print("  1. Review the comprehensive report: output/sales_report.txt")
    print("  2. Check enriched data: output/enriched_sales_data.txt")
    print("  3. Analyze cleaned data: output/sales_data_cleaned.txt")
    print("\nThank you for using Sales Analytics System!\n")


if __name__ == "__main__":
    main()