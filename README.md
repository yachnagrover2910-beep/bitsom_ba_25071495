The Sales Analytics System is a Python-based application developed to demonstrate end-to-end data handling, analytics, and reporting capabilities on structured sales data. The project focuses on data cleaning, validation, analytical processing, external API integration, and automated report generation to support business decision-making.

The system processes raw sales data, ensures data quality through predefined validation rules, performs multiple levels of analytical computation, enriches records using external product information, and generates a consolidated analytical report.

Objectives

The key objectives of this assignment are:

To clean and validate raw transactional data using business rules

To perform descriptive and analytical computations on sales data

To integrate external API data for enrichment

To generate structured and interpretable analytical reports

To demonstrate modular and maintainable Python code design

Project Structure
sales-analytics-system/
├── data/
│   ├── sales_data.txt
│   └── enriched_sales_data.txt
│
├── output/
│   ├── sales_data_cleaned.txt
│   ├── invalid_records.txt
│   ├── enriched_sales_data.txt
│   └── sales_report.txt
│
├── utils/
│   ├── file_handler.py
│   ├── data_processor.py
│   └── api_handler.py
│
├── main.py
├── requirements.txt
└── README.md

System Components
1. Data Cleaning and Validation

Raw sales data is validated and cleaned based on predefined business rules. Records with missing mandatory fields, invalid quantities or prices, or incorrect transaction identifiers are removed. Data formatting issues such as commas in numeric fields and product names are corrected, and encoding inconsistencies are handled automatically.

2. Data Processing and Analytics

The system performs multiple analytical operations, including:

Total revenue computation

Region-wise sales analysis with percentage contribution

Identification of top-selling products by quantity and revenue

Customer-level purchase behavior analysis

Daily sales trend analysis and peak sales day identification

Detection of low-performing products

3. API Integration and Data Enrichment

External product data is fetched using a public product API. Sales records are enriched with additional attributes such as product category, brand, and rating. The system tracks successful and failed enrichments and handles API errors gracefully.

4. Report Generation

All analytical results are consolidated into a structured text-based report. The report includes an executive summary, detailed analytical sections, and enrichment statistics, making it suitable for academic evaluation and business interpretation.

Setup and Execution

Python version: 3.7 or higher

Required libraries are listed in requirements.txt

To execute the complete workflow:

python main.py


This command performs data cleaning, analytics, API enrichment, and report generation in a single run.

Output Artifacts

sales_data_cleaned.txt: Validated and cleaned sales records

invalid_records.txt: Records excluded during validation

enriched_sales_data.txt: Cleaned data enhanced with API attributes

sales_report.txt: Comprehensive analytical report

Data Flow Summary

Raw sales data is first cleaned and validated, followed by analytical processing and external API enrichment. The enriched dataset and analytical results are then combined to produce a final structured report.

Learning Outcomes

Through this assignment, the following concepts and skills were applied:

Data validation and cleansing techniques

Modular Python programming and file I/O operations

Aggregation and analytical computations

API integration and exception handling

Report generation and result interpretation

Professional project structuring and documentation
