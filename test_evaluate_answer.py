#!/usr/bin/env python3
"""
Test script for the /evaluate_answer endpoint
"""

import requests
import json

def test_evaluate_answer():
    """Test the /evaluate_answer endpoint"""
    base_url = "http://localhost:5000"
    
    print("=== TESTING /evaluate_answer ENDPOINT ===")
    
    # First, login to get a session
    login_data = {
        'username': 'testuser_atss',
        'password': 'testpass123'
    }
    
    print("1. Logging in...")
    session = requests.Session()
    login_response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    print("✅ Login successful")
    
    # Test the /evaluate_answer endpoint
    print("\n2. Testing /evaluate_answer endpoint...")
    
    # Test data
    test_data = {
        'answer': 'I have 5 years of experience in Python development, working on web applications using Django and Flask. I have experience with databases like PostgreSQL and MySQL, and I am familiar with cloud platforms like AWS.',
        'question_index': 0
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = session.post(f"{base_url}/evaluate_answer", 
                              data=json.dumps(test_data), 
                              headers=headers)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ /evaluate_answer endpoint working!")
                print(f"   Evaluation: {result.get('evaluation', 'N/A')}")
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
                print(f"   Response content: {response.text[:200]}...")
        else:
            print(f"❌ /evaluate_answer endpoint failed with status {response.status_code}")
            print(f"   Response content: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error making request: {e}")

if __name__ == "__main__":
    test_evaluate_answer()
