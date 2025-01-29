# User Creation Script  

This script processes a CSV file containing user data and attempts to create user accounts via an API endpoint. It includes error handling, logging, validation, and retry mechanisms with exponential backoff to improve reliability.  

## Features  
- Reads user data from a CSV file.  
- Validates required fields (`name`, `email`, `role`).  
- Sends HTTP POST requests to an API endpoint to create users.  
- Implements exponential backoff retry for failed requests.  
- Logs errors and retry attempts to a file (`error_log.txt`).  

## Requirements  
- Python 3.x  
- Required Python packages: `requests`  

Install dependencies using:  
```sh
pip install requests
```  

## Usage  
Run the script from the command line:  
```sh
python script.py <file_path> --api_token <your_api_token>
```  

### Arguments  
- `file_path` (required): Path to the CSV file containing user data.  
- `--endpoint_url` (optional): API endpoint URL (default: `https://example.com/api/create_user`).  
- `--api_token` (required): API token for authorization.  

### Example  
```sh
python script.py users.csv --api_token YOUR_SECRET_TOKEN
```  

## CSV Format  
The CSV file must contain the following columns:  
```csv
name,email,role
John Doe,john.doe@example.com,admin
Jane Smith,jane.smith@example.com,user
```  

## Logging  
Errors and retry attempts are logged in `error_log.txt`.  

## Error Handling  
- Handles file errors (missing or empty files, permission issues).  
- Logs and prints errors for invalid data.  
- Handles API errors (timeout, bad request, unauthorized, server errors).  

## Retry Mechanism  
If a request fails, it is retried up to 5 times with exponential backoff.  

## License  
This script is open-source and available under the MIT License.  
