#!/usr/bin/env python3
"""
Test script for the /check_ats endpoint
"""

import requests
import os
from io import BytesIO

def test_check_ats():
    """Test the /check_ats endpoint"""
    base_url = "http://localhost:5000"
    
    print("=== TESTING /check_ats ENDPOINT ===")
    
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
    
    # Create a simple PDF content (this is just a test - in real usage, you'd upload a real PDF)
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(John Doe - Software Engineer) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
    
    # Test the /check_ats endpoint
    print("\n2. Testing /check_ats endpoint...")
    
    files = {
        'resume': ('test_resume.pdf', BytesIO(pdf_content), 'application/pdf')
    }
    
    data = {
        'job_role': 'Software Engineer'
    }
    
    try:
        response = session.post(f"{base_url}/check_ats", files=files, data=data)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ /check_ats endpoint working!")
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   Feedback: {result.get('feedback', 'N/A')[:100]}...")
                print(f"   Skill gaps: {result.get('skill_gaps', 'N/A')[:50]}...")
                print(f"   Recommendations: {result.get('recommendations', 'N/A')[:50]}...")
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
                print(f"   Response content: {response.text[:200]}...")
        else:
            print(f"❌ /check_ats endpoint failed with status {response.status_code}")
            print(f"   Response content: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error making request: {e}")

if __name__ == "__main__":
    test_check_ats()
