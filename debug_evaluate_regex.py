#!/usr/bin/env python3
"""
Debug script to test the regex pattern for evaluate_answer
"""

import re

def test_evaluate_regex():
    # Test with various AI response formats for evaluation
    test_cases = [
        """Score: 8/10
Feedback: This is a good answer that demonstrates relevant experience.""",
        
        """**Score:** 7/10

**Feedback:** The answer shows good technical knowledge but could be more specific.""",
        
        """**Score: 9/10**

**Feedback:** Excellent response with specific examples and clear communication.""",
        
        """8/10

The candidate provided a comprehensive answer with relevant experience.""",
        
        """Score: 6/10
Feedback: The answer is adequate but lacks specific examples and quantifiable results."""
    ]
    
    print("=== TESTING EVALUATE_ANSWER REGEX PATTERNS ===")
    
    for i, test_output in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input: {test_output[:50]}...")
        
        lines = test_output.strip().splitlines()
        print(f"Lines: {lines}")
        
        score = None
        feedback = ""
        
        # Test the main regex
        for j, line in enumerate(lines):
            print(f"Processing line {j}: '{line}'")
            
            # Look for patterns like "Score: 8/10", "**Score:** 8/10", "8/10", etc.
            match = re.search(r'(?:Score:?\s*)?(?:\*\*)?(\d{1,2})\s*/\s*10(?:\*\*)?', line, re.IGNORECASE)
            if match:
                print(f"  ✅ MATCH FOUND! Score: {match.group(1)}")
                score = int(match.group(1))
                
                # Collect feedback from next lines, skip empty lines but continue
                feedback_lines = []
                for feedback_line in lines[j+1:]:
                    # Remove markdown formatting from feedback lines
                    clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                    if clean_line:  # Only add non-empty lines
                        feedback_lines.append(clean_line)
                feedback = ' '.join(feedback_lines).strip()
                # Remove "Feedback:" prefix if present
                if feedback.lower().startswith('feedback:'):
                    feedback = feedback[9:].strip()
                break
            else:
                print(f"  ❌ No match")
        
        # If no match found, try the fallback
        if score is None:
            print("\n=== TRYING FALLBACK REGEX ===")
            for j, line in enumerate(lines):
                print(f"Fallback processing line {j}: '{line}'")
                match = re.search(r'(\d{1,2})\s*/\s*10', line)
                if match:
                    print(f"  ✅ FALLBACK MATCH FOUND! Score: {match.group(1)}")
                    score = int(match.group(1))
                    
                    # Collect feedback from remaining lines, skip empty lines but continue
                    feedback_lines = []
                    for feedback_line in lines[j+1:]:
                        # Remove markdown formatting from feedback lines
                        clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', feedback_line.strip())
                        if clean_line:  # Only add non-empty lines
                            feedback_lines.append(clean_line)
                    feedback = ' '.join(feedback_lines).strip()
                    # Remove "Feedback:" prefix if present
                    if feedback.lower().startswith('feedback:'):
                        feedback = feedback[9:].strip()
                    break
                else:
                    print(f"  ❌ No fallback match")
        
        print(f"\n=== RESULT FOR TEST CASE {i+1} ===")
        print(f"Score: {score}")
        print(f"Feedback: '{feedback}'")
        print(f"Score is None: {score is None}")
        print(f"Feedback is empty: {not feedback}")
        print(f"Would pass validation: {score is not None and feedback}")

if __name__ == "__main__":
    test_evaluate_regex()
