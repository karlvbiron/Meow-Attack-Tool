#!/usr/bin/env python3
"""
Script to fetch and display data from MongoDB and Elasticsearch in tabular format.
"""

import pymongo
import requests
from tabulate import tabulate
import json
import sys

# Configuration based on docker-compose.yml
MONGODB_CONFIG = {
    "host": "192.168.1.11",
    "port": 27017,
    "username": "root",
    "password": "example",
    "database": "my_database",
    "collection": "my_table"
}

ELASTICSEARCH_CONFIG = {
    "host": "192.168.1.12",
    "port": 9200,
    "index": "my_index"
}

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def fetch_mongodb_data():
    """Fetch data from MongoDB and return as a list of dictionaries"""
    print_header("MONGODB DATA")
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(
            host=MONGODB_CONFIG["host"],
            port=MONGODB_CONFIG["port"],
            username=MONGODB_CONFIG["username"],
            password=MONGODB_CONFIG["password"],
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        print(f"Connected to MongoDB at {MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}")
        
        # Get database and collection
        db = client[MONGODB_CONFIG["database"]]
        collection = db[MONGODB_CONFIG["collection"]]
        
        # Fetch all documents
        documents = list(collection.find())
        
        if not documents:
            print("No documents found in MongoDB collection")
            return []
        
        # Print table with tabulate
        headers = documents[0].keys()
        # Filter out ObjectId from headers (typically _id)
        headers = [h for h in headers if h != "_id"]
        
        # Prepare rows (exclude _id field)
        rows = []
        for doc in documents:
            row = [doc.get(h, "") for h in headers]
            rows.append(row)
        
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        print(f"Total records: {len(documents)}")
        
        return documents
        
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return []
    except Exception as e:
        print(f"Error fetching MongoDB data: {e}")
        return []

def fetch_elasticsearch_data():
    """Fetch data from Elasticsearch and return as a list of dictionaries"""
    print_header("ELASTICSEARCH DATA")
    
    try:
        # Construct the URL
        base_url = f"http://{ELASTICSEARCH_CONFIG['host']}:{ELASTICSEARCH_CONFIG['port']}"
        index_url = f"{base_url}/{ELASTICSEARCH_CONFIG['index']}/_search"
        
        # Check if Elasticsearch is running
        health_response = requests.get(f"{base_url}/_cluster/health", timeout=5)
        if health_response.status_code != 200:
            print(f"Elasticsearch is not available: Status {health_response.status_code}")
            return []
        
        print(f"Connected to Elasticsearch at {ELASTICSEARCH_CONFIG['host']}:{ELASTICSEARCH_CONFIG['port']}")
        
        # Query all documents (up to 100)
        query = {
            "query": {"match_all": {}},
            "size": 100
        }
        
        # Send the search request
        response = requests.get(
            index_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(query)
        )
        
        if response.status_code != 200:
            print(f"Failed to fetch data from Elasticsearch: Status {response.status_code}")
            return []
        
        # Parse the response
        search_results = response.json()
        hits = search_results.get("hits", {}).get("hits", [])
        
        if not hits:
            print("No documents found in Elasticsearch index")
            return []
        
        # Extract documents from hits
        documents = []
        for hit in hits:
            doc = hit["_source"]
            doc["_id"] = hit["_id"]  # Add the _id field
            documents.append(doc)
        
        # Print table with tabulate
        if documents:
            # Use the first document to determine headers, excluding _id
            headers = [k for k in documents[0].keys() if k != "_id"]
            
            # Prepare rows
            rows = []
            for doc in documents:
                row = [doc.get(h, "") for h in headers]
                rows.append(row)
            
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            print(f"Total records: {len(documents)}")
        
        return documents
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Elasticsearch: {e}")
        return []
    except Exception as e:
        print(f"Error fetching Elasticsearch data: {e}")
        return []

def verify_data_consistency():
    """Compare data between MongoDB and Elasticsearch"""
    print_header("DATA CONSISTENCY CHECK")
    
    mongo_data = fetch_mongodb_data()
    es_data = fetch_elasticsearch_data()
    
    if not mongo_data or not es_data:
        print("Cannot compare data: One or both data sources are empty")
        return
    
    # Get all emails from MongoDB
    mongo_emails = {doc.get("email") for doc in mongo_data if "email" in doc}
    
    # Get all emails from Elasticsearch
    es_emails = {doc.get("email") for doc in es_data if "email" in doc}
    
    # Find differences
    mongo_only = mongo_emails - es_emails
    es_only = es_emails - mongo_emails
    common = mongo_emails.intersection(es_emails)
    
    print(f"Common records: {len(common)}")
    if common:
        print("Common email addresses:")
        for email in common:
            print(f"  - {email}")
    
    if mongo_only:
        print("\nRecords only in MongoDB:")
        for email in mongo_only:
            print(f"  - {email}")
    
    if es_only:
        print("\nRecords only in Elasticsearch:")
        for email in es_only:
            print(f"  - {email}")

def main():
    """Main entry point"""
    try:
        # Check for command-line arguments
        if len(sys.argv) > 1:
            if sys.argv[1].lower() == "mongo":
                fetch_mongodb_data()
            elif sys.argv[1].lower() == "es" or sys.argv[1].lower() == "elasticsearch":
                fetch_elasticsearch_data()
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Usage: python fetch_data.py [mongo|es|all]")
        else:
            # Default: fetch from both and verify consistency
            verify_data_consistency()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()