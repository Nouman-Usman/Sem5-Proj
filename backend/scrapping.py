import requests
from bs4 import BeautifulSoup
import csv
import os

# Function to download PDFs from a URL with conditional headers
def download_pdf(url, save_directory, last_modified=None, etag=None):
    try:
        # Set up headers for conditional requests
        headers = {}
        if last_modified:
            headers['If-Modified-Since'] = last_modified
        if etag:
            headers['If-None-Match'] = etag
        
        # Send GET request to the URL
        response = requests.get(url, headers=headers)
        
        # If not modified, skip downloading
        if response.status_code == 304:
            print(f"No updates found for {url}. Skipping download.")
            return None, None  # No updates, return None for last_modified and etag
        
        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find all the PDF links (assuming the PDFs are linked with <a> tags)
            for link in soup.find_all("a", href=True):
                if link['href'].endswith('.pdf'):  # Check if the link is a PDF
                    pdf_url = link['href']
                    if not pdf_url.startswith("http"):
                        pdf_url = requests.compat.urljoin(url, pdf_url)  # Handle relative URLs
                    
                    # Get the PDF content
                    pdf_response = requests.get(pdf_url)
                    
                    # Check if PDF request was successful
                    if pdf_response.status_code == 200:
                        # Get the PDF name from the URL
                        pdf_name = os.path.basename(pdf_url)
                        
                        # Define the complete file path for saving the PDF
                        save_path = os.path.join(save_directory, pdf_name)
                        
                        # Save the PDF locally at the specified directory
                        with open(save_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)
                            print(f"Downloaded: {pdf_name} to {save_path}")
                        
                        # Get Last-Modified and ETag headers for next request
                        new_last_modified = pdf_response.headers.get('Last-Modified')
                        new_etag = pdf_response.headers.get('ETag')
                        
                        # Return the updated Last-Modified and ETag values
                        return new_last_modified, new_etag
                    else:
                        print(f"Failed to download PDF: {pdf_url}. Status code: {pdf_response.status_code}")
        else:
            print(f"Failed to access: {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while processing {url}: {e}")

    return None, None  # In case of failure

# Function to read URLs and headers from a CSV file
def read_urls_from_csv(csv_file):
    urls_data = []
    try:
        with open(csv_file, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Ensure the row is not empty
                    url = row[0].strip()
                    last_modified = row[1].strip() if len(row) > 1 else None
                    etag = row[2].strip() if len(row) > 2 else None
                    urls_data.append((url, last_modified, etag))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return urls_data

# Function to update CSV file with new Last-Modified and ETag values
def update_csv(csv_file, urls_data):
    try:
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(urls_data)
    except Exception as e:
        print(f"Error updating CSV file: {e}")

# Specify the CSV file containing URLs, Last-Modified, and ETag columns
csv_file_path = "rules.csv"  # Adjust this path as per your CSV file location

# Specify the directory where PDFs will be saved
save_directory = "scrapping.csv"  # Change this to your desired directory

# Ensure the save directory exists
os.makedirs(save_directory, exist_ok=True)

# Get the list of URLs, Last-Modified, and ETag from the CSV file
urls_data = read_urls_from_csv(csv_file_path)

# Loop through the list of URLs and download PDFs if updated
for i, (url, last_modified, etag) in enumerate(urls_data):
    if url:  # Ensure the URL is not empty
        new_last_modified, new_etag = download_pdf(url, save_directory, last_modified, etag)
        
        # Update CSV data if there was a change
        if new_last_modified or new_etag:
            urls_data[i] = (url, new_last_modified or last_modified, new_etag or etag)
    else:
        print("Empty URL found, skipping.")

# Update CSV with new Last-Modified and ETag values
update_csv(csv_file_path, urls_data)

print("All downloads completed.")