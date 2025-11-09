#!/usr/bin/env python3
"""
Script to help get the DATABASE_URL for Railway PostgreSQL
"""

import subprocess
import json

def get_database_url():
    """Get DATABASE_URL from Railway services"""
    try:
        # Get all services in the project
        result = subprocess.run(['railway', 'service', 'list', '--json'], 
                              capture_output=True, text=True, check=True)
        services = json.loads(result.stdout)
        
        print("Available services:")
        for service in services:
            print(f"- {service['name']} (ID: {service['id']})")
            if 'postgres' in service['name'].lower():
                print(f"  This looks like the PostgreSQL service!")
                
        # Try to get variables from postgres service
        postgres_services = [s for s in services if 'postgres' in s['name'].lower()]
        if postgres_services:
            postgres_service = postgres_services[0]
            print(f"\nTrying to get variables from PostgreSQL service: {postgres_service['name']}")
            
            # Switch to postgres service and get variables
            subprocess.run(['railway', 'service', postgres_service['id']], check=True)
            result = subprocess.run(['railway', 'variables', '--json'], 
                                  capture_output=True, text=True, check=True)
            variables = json.loads(result.stdout)
            
            print("\nPostgreSQL service variables:")
            for var_name, var_value in variables.items():
                if 'DATABASE_URL' in var_name or 'POSTGRES' in var_name:
                    print(f"{var_name}: {var_value}")
                    
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running railway command: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Getting DATABASE_URL information from Railway...")
    success = get_database_url()
    
    if not success:
        print("\nManual steps:")
        print("1. Go to your Railway dashboard")
        print("2. Click on the PostgreSQL service")
        print("3. Go to the Variables tab")
        print("4. Copy the DATABASE_URL value")
        print("5. Add it to your main service using:")
        print("   railway variables --set DATABASE_URL=<the_url_you_copied>")
