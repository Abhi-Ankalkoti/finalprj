#!/usr/bin/env python3
"""
Debug script to test the regex pattern
"""

import re

def test_regex():
    # Test with the actual output we're getting
    test_output = """**Score:** 82/100  

**Feedback:** The resume demonstrates strong technical skills (Python, Java, AWS) and a relevant Computer Science degree. However, it lacks quantifiable achievements and specific project details. Strengths: Technical skills (40%), Education (30%). Weaknesses: Missing quantifiable results (20%), Limited project scope (10%). Score breakdown: Skills-40%, Education-30%, Experience-20%, Formatting-10% = 100%."""
    
    print("=== TESTING REGEX PATTERNS ===")
    print(f"Input: {test_output[:100]}...")
    
    lines = test_output.strip().splitlines()
    print(f"Lines: {lines}")
    
    score = None
    feedback = ""
    
    for i, line in enumerate(lines):
        print(f"Processing line {i}: '{line}'")
        
        # Test the main regex
        match = re.search(r'(?:Score:?\s*)?(?:\*\*)?(\d{1,3})\s*/\s*100(?:\*\*)?', line, re.IGNORECASE)
        if match:
            print(f"  ✅ MATCH FOUND! Score: {match.group(1)}")
            score = int(match.group(1))
            
            # Collect feedback from next lines
            feedback_lines = []
            for feedback_line in lines[i+1:]:
                if feedback_line.strip() == "":
                    break
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                feedback_lines.append(clean_line)
            feedback = ' '.join(feedback_lines).strip()
            break
        else:
            print(f"  ❌ No match")
    
    # If no match found, try the fallback
    if score is None:
        print("\n=== TRYING FALLBACK REGEX ===")
        for i, line in enumerate(lines):
            print(f"Fallback processing line {i}: '{line}'")
            match = re.search(r'(\d{1,3})\s*/\s*100', line)
            if match:
                print(f"  ✅ FALLBACK MATCH FOUND! Score: {match.group(1)}")
                score = int(match.group(1))
                
                feedback_lines = []
                for feedback_line in lines[i+1:]:
                    if feedback_line.strip() == "":
                        break
                    clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                    feedback_lines.append(clean_line)
                feedback = ' '.join(feedback_lines).strip()
                break
            else:
                print(f"  ❌ No fallback match")
    
    print(f"\n=== FINAL RESULT ===")
    print(f"Score: {score}")
    print(f"Feedback: '{feedback}'")
    print(f"Feedback length: {len(feedback)}")
    print(f"Score is None: {score is None}")
    print(f"Feedback is empty: {not feedback}")

if __name__ == "__main__":
    test_regex()
