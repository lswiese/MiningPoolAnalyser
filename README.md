# Coinbase Data Processing Script

This repository contains a Python script designed to process multiple CSV files containing hex-encoded CoinBase transaction data (Transaction Input Scripts). `MiningPoolMatcher.py` decodes the coinbase scripts, matches them to known mining pool names and links, sanitizes the data, and outputs the results in both Excel (.xlsx) and CSV (.csv) formats.

The dataset contains mining transaction data for Coinbase transactions, which can be processed to identify mining pool names and related information from encoded script data.

The included Dataset contains 868991 Coinbase Transactions ranging from:

**Start Date:**  
`January 3, 2009, 6:15:05 PM` 

**End Date:**  
`November 6, 2024, 4:01:59 AM`


## Features & Overview

The script performs the following tasks:

- **Hex Decoding**: Converts hex-encoded coinbase scripts into UTF-8, ASCII, and Hex formats.
- **Mining Pool Matching**: Matches decoded coinbase scripts with mining pool names and links from the `coinbase_tags_clean.json` configuration file.
- **Sanitization**: Removes illegal characters for Excel compatibility (e.g., non-printable characters).
- **Flexible Output**: Outputs the results to both Excel and CSV formats for easy usage in different environments.
- **Error Handling**: Handles errors gracefully, including missing columns and issues with decoding.

## Requirements

- `Python 3.x`
- `pandas` library
- `openpyxl` library (for Excel file handling)

You can install the necessary dependencies with the following command:

```sh
pip install pandas openpyxl
```

## File Structure

The repository should have the following file structure:

```
.
├── script_converter.py           # The main script that processes the data
├── YearlyCoinbaseTransactions/   # Folder containing the input CSV files with hex-encoded coinbase data
│   ├── transaction_data_1.csv    # Example input CSV file
│   ├── transaction_data_2.csv    # Example input CSV file
│   └── ...                       # Additional CSV files
├── coinbase_tags_clean.json      # JSON file containing pool name and link information
├── Export/                       # Folder where output files will be saved
│   ├── allcoinbase_final.xlsx    # Output Excel file (processed data)
│   └── allcoinbase_final.csv     # Output CSV file (processed data)
└── README.md                     # This README file
```

## Example of `coinbase_tags_clean.json`

The `coinbase_tags_clean.json` file contains the mining pool data, with pool names and corresponding links. Example format:

```json
{
    "coinbase_tags": {
        "Pool Tag": {
            "name": "Pool Name 1",
            "link": "https://pool1.com"
        },
        "Pool Tag 2": {
            "name": "Pool Name 2",
            "link": "https://pool2.com"
        }
    }
}
```

## How to Use

### Input CSV Files

The input CSV files, located in the `YearlyCoinbaseTransactions` folder, should contain the following columns:

- **Input script**: Hex-encoded coinbase script data.
- **TX hash**: Transaction hash.
- **Timestamp**: Timestamp of the transaction.
- **Date**: Date of the transaction.

Example of a `transaction_data_1.csv`:

```csv
Input script,Timestamp,TX hash,Date
"68656c6c6f",2023-10-01,abc123,2023-10-01
"74657374",2023-10-02,def456,2023-10-02
```

### Running the Script

To process the data, run the `script_converter.py` using Python:

```sh
python MiningPoolMatcher.py
```

The script will automatically:

1. Merge all CSV files from the `YearlyCoinbaseTransactions` folder.
2. Decode the `Input script` column from hex to UTF-8, ASCII, and Hex formats.
3. Match the decoded script with a mining pool name and link from the `coinbase_tags_clean.json` file.
4. Remove any illegal characters that are incompatible with Excel.
5. Save the processed data in both an Excel file (.xlsx) and a CSV file (.csv).

### Output Files

After running the script, the processed data will be saved in the `Export/` folder:

- **Excel File**: The processed data is saved as `allcoinbase_final.xlsx` in the `Export/` directory.
- **CSV File**: The processed data is also saved as `allcoinbase_final.csv` in the `Export/` directory.

Both output files will contain the following columns:

- **Mining Pool Name**: The name of the mining pool matched from the decoded coinbase script.
- **Mining Pool Link**: The link to the mining pool.
- **TX hash**: The transaction hash.
- **Timestamp**: The timestamp of the transaction.
- **Date**: The date of the transaction.

Example Output in Excel:

| Mining Pool Name | Mining Pool Link     | TX hash | Timestamp           | Date       |
|------------------|----------------------|---------|---------------------|------------|
| Pool Name 1      | https://pool1.com    | abc123  | 2023-10-01 10:00:00 | 2023-10-01 |
| Pool Name 2      | https://pool2.com    | def456  | 2023-10-02 11:00:00 | 2023-10-02 |

Example Output in CSV:

```csv
Mining Pool Name,Mining Pool Link,TX hash,Timestamp,Date
Pool Name 1,https://pool1.com,abc123,2023-10-01 10:00:00,2023-10-01
Pool Name 2,https://pool2.com,def456,2023-10-02 11:00:00,2023-10-02
```

### Where Are Files Saved?

- **Input CSV Files**: The input CSV files should be located in the `YearlyCoinbaseTransactions/` folder.
- **Output Files**: The processed data will be saved in the `Export/` folder:
  - `Export/allcoinbase_final.xlsx` (Excel format)
  - `Export/allcoinbase_final.csv` (CSV format)

If the `Export/` folder does not exist, the script will create it automatically.

## Troubleshooting

### Common Errors

- **Missing Columns in CSV**: If the input CSV does not contain one of the required columns (`Input script`, `TX hash`, `Timestamp`, `Date`), a warning will be printed, and those rows will be skipped.
- **Illegal Characters for Excel**: If non-printable or illegal characters for Excel are found in the decoded strings, they will be removed automatically during the sanitization process.
- **No Matching Pool Found**: If no mining pool is found in the decoded string, the columns for Mining Pool Name and Mining Pool Link will be left empty.

## Contributing

Feel free to fork the repository, create a branch, and submit pull requests for improvements, bug fixes, or additional features.

## Contributors

- [Lucas Wiese](https://github.com/lswiese)
- [Petr Korab](https://github.com/PetrKorab)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
