import sys
import time
import threading
import pandas as pd
import binascii
import json
import re
import os

# ============================
# Script Overview:
# ============================
# This script processes multiple CSV files containing hex-encoded mining transaction data.
# It decodes the input scripts from hex to UTF-8, ASCII, and hex representations, 
# then attempts to match the decoded values to known mining pool names and links 
# from a provided JSON configuration. It outputs the processed data in both Excel 
# and CSV formats.
# ============================

# Spinner function that runs indefinitely in a separate thread
def loading_spinner(stop_event):
    """
    This function runs a spinner in the terminal until `stop_event` is set.
    """
    spinner = ['|', '/', '-', '\\']
    while not stop_event.is_set():
        for symbol in spinner:
            sys.stdout.write(f'\rProcessing... {symbol} (This may take a couple of minutes, coffee time!)')
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\rProcessing... Done!      \n')

# Function to convert hex-encoded script into UTF-8, ASCII, and Hex representations
def convert_script(input_script):
    try:
        # Decode the hex-encoded script to bytes
        decoded_bytes = binascii.unhexlify(input_script)

        # Decode as UTF-8 (may fail if the content is not valid UTF-8)
        try:
            utf8_decoded = decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            utf8_decoded = f"Error decoding as UTF-8: {e}"

        # Convert to ASCII (only printable ASCII characters)
        ascii_decoded = ''.join([chr(b) if 32 <= b < 127 else '.' for b in decoded_bytes])

        # Original Hex representation (retain the original data)
        hex_decoded = binascii.hexlify(decoded_bytes).decode('utf-8')

        return {
            "UTF-8": utf8_decoded,
            "ASCII": ascii_decoded,
            "Hex": hex_decoded
        }

    except Exception as e:
        return {
            "UTF-8": f"Error: {e}",
            "ASCII": "Error",
            "Hex": "Error"
        }

# Function to load pool data from a JSON file
def load_pool_data(json_file):
    """Load pool configuration from a JSON file containing pool names and links."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data['coinbase_tags']

# Function to match decoded strings with pool name and link
def match_pool_in_columns(decoded_str, pool_data):
    """
    Searches for a mining pool name in the decoded string.
    
    Args:
    decoded_str (str): The decoded UTF-8 or ASCII string.
    pool_data (dict): Dictionary containing pool names and links.
    
    Returns:
    tuple: Mining pool name and link, or empty strings if no match is found.
    """
    if not isinstance(decoded_str, str):
        decoded_str = str(decoded_str) if decoded_str is not None else ""

    for key, pool in pool_data.items():
        # Check if pool name appears in the decoded string (case-insensitive)
        if pool['name'].lower() in decoded_str.lower():
            return pool['name'], pool['link']
    return "", ""  # Return empty strings if no match is found

# Function to sanitize strings (remove illegal characters for Excel)
def sanitize_string(value):
    """
    Removes characters that are not printable ASCII characters (e.g., control characters)
    which are not compatible with Excel.
    
    Args:
    value (str): The string to sanitize.
    
    Returns:
    str: The sanitized string.
    """
    if isinstance(value, str):
        # Remove non-printable ASCII characters (except space and standard punctuation)
        return re.sub(r'[^\x20-\x7E]', '', value)
    return value

# Function to merge multiple CSV files into one DataFrame
def merge_csv_files(input_folder):
    """
    Merges all CSV files in the given directory into a single DataFrame, ordered by file name.
    
    Args:
    input_folder (str): Path to the directory containing CSV files.
    
    Returns:
    pd.DataFrame: A DataFrame containing the combined data from all CSV files.
    """
    # Get all CSV files in the folder and sort them (lexicographical order)
    all_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    all_files.sort()  # Sort the files alphabetically
    
    combined_df = pd.DataFrame()

    for file in all_files:
        file_path = os.path.join(input_folder, file)
        print(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    print(f"Merged {len(all_files)} files into a single DataFrame with {len(combined_df)} records.")
    return combined_df

# Main function to process the merged DataFrame, match pools, and save to Excel and CSV
def process_data(merged_df, output_excel, output_csv, pool_json):
    """
    Processes the merged DataFrame, decodes the scripts, matches mining pools,
    and saves the results to both Excel and CSV formats.
    
    Args:
    merged_df (pd.DataFrame): DataFrame containing the merged transaction data.
    output_excel (str): Path to the output Excel file.
    output_csv (str): Path to the output CSV file.
    pool_json (str): Path to the JSON file containing mining pool data.
    """
    # Load pool data from the provided JSON file
    pool_data = load_pool_data(pool_json)

    # Start the spinner in a background thread
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event,))
    spinner_thread.start()

    # Decode input script and add new columns for UTF-8, ASCII, and Hex representations
    merged_df[['UTF-8', 'ASCII', 'Hex']] = merged_df['Input script'].apply(lambda x: pd.Series(convert_script(x)))

    # Initialize lists to store pool names and links
    pool_names = []
    pool_links = []

    # Process each row to find the mining pool from decoded strings
    for _, row in merged_df.iterrows():
        utf8_decoded = row['UTF-8']
        ascii_decoded = row['ASCII']
        
        # First, try to match the pool using UTF-8 decoded string
        pool_name, pool_link = match_pool_in_columns(utf8_decoded, pool_data)
        
        if not pool_name:  # If no match, try the ASCII decoded string
            pool_name, pool_link = match_pool_in_columns(ascii_decoded, pool_data)
        
        pool_names.append(pool_name)
        pool_links.append(pool_link)

    # Add the mining pool name and link columns to the DataFrame
    merged_df['Mining Pool Name'] = pool_names
    merged_df['Mining Pool Link'] = pool_links

    # Sanitize all string columns to remove illegal characters for Excel
    merged_df = merged_df.applymap(sanitize_string)

    # Define the columns to extract
    columns_to_extract = [
        'Mining Pool Name', 'Mining Pool Link', 'TX hash', 'Timestamp', 'Date'
    ]
    
    # Check for missing columns in the input data
    missing_columns = [col for col in columns_to_extract if col not in merged_df.columns]
    if missing_columns:
        print(f"Warning: The following columns are missing from the input CSV: {', '.join(missing_columns)}")
    
    # Filter the DataFrame to include only the selected columns
    extracted_df = merged_df[columns_to_extract]

    # Stop the spinner when processing is complete
    stop_event.set()
    spinner_thread.join()

    # Save the processed data to Excel
    extracted_df.to_excel(output_excel, index=False, engine='openpyxl')
    print(f"Processed data saved to {output_excel}")

    # Save the processed data to CSV
    extracted_df.to_csv(output_csv, index=False)
    print(f"Processed data saved to {output_csv}")

# Running in local directory
input_folder = './YearlyCoinbaseTransactions'  # Path to directory containing CSV files
output_excel = './Export/allcoinbase_final.xlsx'  # Path to output Excel file
output_csv = './Export/allcoinbase_final.csv'  # Path to output CSV file
pool_json = './coinbase_tags_clean.json'  # Path to JSON file containing pool data

# Merge all CSV files in the input folder
merged_df = merge_csv_files(input_folder)

# Process the merged data and save to Excel and CSV
process_data(merged_df, output_excel, output_csv, pool_json)
