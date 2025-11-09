#!/usr/bin/env python
"""
Script to check if Google Gemini API is accessible and has quota available.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_api():
    print("\n" + "="*80)
    print("🔍 CHECKING GOOGLE GEMINI API")
    print("="*80 + "\n")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key found!")
        print("Please add GOOGLE_API_KEY or GEMINI_API_KEY to your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Try a simple API call
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("\n🧪 Testing API with a simple request...")
        response = model.generate_content("Say 'API is working!' in one word")
        
        print(f"✅ API Response: {response.text}")
        print("\n" + "="*80)
        print("✅ GEMINI API IS READY!")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ API Error: {error_msg}")
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print("\n⚠️  QUOTA EXCEEDED!")
            print("="*80)
            print("The free tier has a limit of 10 requests per minute.")
            print("Please wait 1-2 minutes and try again.")
            print("="*80)
        else:
            print("\n⚠️  UNEXPECTED ERROR!")
            print("="*80)
            print("Please check your API key and internet connection.")
            print("="*80)
        
        print()
        return False

if __name__ == "__main__":
    check_api()
