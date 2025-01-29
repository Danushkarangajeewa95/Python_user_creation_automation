import csv
import requests
import logging
from typing import List, Dict
from time import sleep
import os
import argparse


# Configuration Parameters
DEFAULT_ENDPOINT_URL = "https://example.com/api/create_user"
MAX_RETRIES = 5     # Maximum retry attempts
RETRY_INTERVAL = 2  # Base retry interval in seconds
LOG_FILENAME = "error_log.txt"


# Set up logging configuration
def setup_logging():
    """Set up logging configuration to log errors to a file."""
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Logging setup complete.")
    print(f"Errors and logs are being written to: {LOG_FILENAME}")


# Parse the CSV file into a list of dictionaries
def parse_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Load and parse data from a CSV file into a list of dictionaries.

    :param file_path: Path to the input CSV file.
    :return: List of dictionaries containing row data.
    """
    try:
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if not rows:
                logging.warning(f"CSV file is empty: {file_path}")
                print(f"Error: The file '{file_path}' is empty.")
                return []
            return rows
    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_path}")
        print(f"Error: Unable to locate the file '{file_path}'.")
    except PermissionError:
        logging.error(f"Permission denied: {file_path}")
        print(f"Error: Permission denied for accessing '{file_path}'.")
    except Exception as e:
        logging.error(f"Unexpected error while reading CSV: {e}")
        print("Error: An unexpected error occurred while reading the file.")
    return []


# Validate that the required fields are present and not empty
def check_row_validity(row: Dict[str, str]) -> bool:
    """
    Validate user data to ensure all required fields are provided.

    :param row: Dictionary containing user information.
    :return: True if valid, otherwise False.
    """
    required_columns = ["name", "email", "role"]
    missing_columns = [col for col in required_columns if not row.get(col) or not row[col].strip()]

    if missing_columns:
        logging.error(f"Validation failed. Missing fields: {missing_columns}. Data: {row}")
        return False
    return True


# Handle the HTTP request to create the user
def send_user_creation_request(user_data: Dict[str, str], endpoint_url: str, headers: Dict[str, str]) -> bool:
    """
    Submit an HTTP POST request to create a user.

    :param user_data: Dictionary containing user details.
    :param endpoint_url: URL for the API endpoint.
    :param headers: HTTP headers to include in the request.
    :return: True if the request succeeds, otherwise False.
    """
    try:
        response = requests.post(endpoint_url, json=user_data, headers=headers, timeout=10)
        return handle_http_response(response, user_data)
    except requests.Timeout:
        logging.error(f"Request timed out for user {user_data.get('email')}")
        print(f"Error: Request timed out while processing user {user_data.get('email')}.")
    except requests.ConnectionError:
        logging.error(f"Connection error for user {user_data.get('email')}")
        print(f"Error: Connection error while processing user {user_data.get('email')}.")
    except requests.RequestException as e:
        logging.error(f"Request error for user {user_data.get('email')}: {e}")
        print(f"Error: An unexpected error occurred while processing user {user_data.get('email')}.")
    return False


# Handle the HTTP response with different status codes
def handle_http_response(response, user_data: Dict[str, str]) -> bool:
    """
    Handle the response from the HTTP request to create a user.

    :param response: HTTP response object.
    :param user_data: Dictionary containing user details.
    :return: True if the request succeeds, otherwise False.
    """
    if response.status_code == 201:
        return True

# Handle different HTTP errors more specifically                                                    
    if response.status_code == 400:
        logging.error(f"Bad Request for user {user_data.get('email')}: {response.text}")
        print(f"Error: Bad Request for user {user_data.get('email')}. Check the data format.")
    elif response.status_code == 401:
        logging.error(f"Unauthorized request for user {user_data.get('email')}: {response.text}")
        print(f"Error: Unauthorized request for user {user_data.get('email')}. Check your API token.")
    elif response.status_code == 404:
        logging.error(f"Endpoint not found for user {user_data.get('email')}: {response.text}")
        print(f"Error: Endpoint not found for user {user_data.get('email')}. Check the URL.")
    elif response.status_code == 500:
        logging.error(f"Internal Server Error for user {user_data.get('email')}: {response.text}")
        print(f"Error: Server issue while processing user {user_data.get('email')}. Try again later.")
    elif response.status_code == 503:
        logging.error(f"Service Unavailable for user {user_data.get('email')}: {response.text}")
        print(f"Error: Service temporarily unavailable for user {user_data.get('email')}. Try again later.")
    else:
        logging.error(f"Unexpected error for user {user_data.get('email')}: {response.status_code}, {response.text}")
        print(f"Error: Unexpected error occurred while processing user {user_data.get('email')}.")
    
    return False


# Retry a function with exponential backoff in case of failure
def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, base_interval=RETRY_INTERVAL):
    """
    Retry a function with exponential backoff.

    :param func: Function to retry.
    :param args: Arguments to pass to the function.
    :param max_retries: Maximum number of retries.
    :param base_interval: Base retry interval in seconds.
    :return: Result of the function or None if all retries fail.
    """
    for attempt in range(max_retries):
        if func(*args):
            return True
        sleep(base_interval * (2 ** attempt))  # Exponential backoff
        logging.info(f"Retrying attempt {attempt + 1}/{max_retries}...")
    return False


# Process user data from the CSV file and attempt to create users
def process_user_file(file_path: str, endpoint_url: str, api_token: str):
    """
    Read user data from a file, validate it, and process user account creation.

    :param file_path: Path to the CSV file.
    :param endpoint_url: URL for the API endpoint.
    :param api_token: API token for authorization.
    """
    # Setup logging
    setup_logging()

    # Parse the CSV file into a list of user records
    user_records = parse_csv(file_path)
    if not user_records:
        print("No records found in the provided file.")
        return

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    # Iterate over each record and process it
    for record in user_records:
        # Skip invalid rows
        if not check_row_validity(record):
            print(f"Skipping invalid record: {record}")
            continue

        # Retry user creation with exponential backoff
        if retry_with_backoff(send_user_creation_request, record, endpoint_url, headers):
            print(f"Successfully created user: {record['email']}")
        else:
            print(f"Failed to create user after {MAX_RETRIES} attempts: {record['email']}")
            logging.error(f"Exhausted retries for user: {record}")


# Main entry point of the script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a CSV file to create users via API.")
    parser.add_argument("file_path", help="Path to the CSV file containing user data.")
    parser.add_argument("--endpoint_url", default=DEFAULT_ENDPOINT_URL, help="API endpoint URL.")
    parser.add_argument("--api_token", required=True, help="API token for authorization.")

    args = parser.parse_args()

    process_user_file(args.file_path, args.endpoint_url, args.api_token)
