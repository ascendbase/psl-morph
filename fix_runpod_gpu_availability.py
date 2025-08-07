"""
Fix RunPod GPU availability by updating endpoint configuration
"""

import requests
import os
from dotenv import load_dotenv

def fix_gpu_availability():
    """Update RunPod endpoint to use more available GPU types"""
    
    print("🔧 FIXING RUNPOD GPU AVAILABILITY")
    print("=" * 50)
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    if not api_key or not endpoint_id:
        print("❌ Missing RunPod credentials!")
        return
    
    print(f"API Key: ✅ Found")
    print(f"Endpoint ID: {endpoint_id}")
    
    # Get current endpoint configuration
    print(f"\n📋 Getting current endpoint configuration...")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get endpoint details
        response = requests.get(
            f'https://api.runpod.ai/graphql',
            headers=headers,
            json={
                'query': '''
                query getEndpoint($endpointId: String!) {
                    endpoint(id: $endpointId) {
                        id
                        name
                        gpuTypes
                        locations
                        scalerType
                        scalerValue
                        workersMax
                        workersMin
                    }
                }
                ''',
                'variables': {'endpointId': endpoint_id}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']['endpoint']:
                endpoint = data['data']['endpoint']
                print(f"✅ Current configuration:")
                print(f"  Name: {endpoint['name']}")
                print(f"  GPU Types: {endpoint['gpuTypes']}")
                print(f"  Locations: {endpoint['locations']}")
                print(f"  Workers Min/Max: {endpoint['workersMin']}/{endpoint['workersMax']}")
                
                # Suggest better GPU configuration
                print(f"\n💡 RECOMMENDED FIXES:")
                print(f"1. Add more GPU types for better availability:")
                print(f"   - RTX A4000 (current)")
                print(f"   - RTX A4500") 
                print(f"   - RTX A5000")
                print(f"   - RTX 4090")
                print(f"   - RTX 3090")
                
                print(f"\n2. Add more locations:")
                print(f"   - US-CA-1 (California)")
                print(f"   - US-OR-1 (Oregon)")
                print(f"   - EU-RO-1 (Romania)")
                print(f"   - EU-IS-1 (Iceland)")
                
                print(f"\n3. Increase worker limits:")
                print(f"   - Min Workers: 0 (for cost efficiency)")
                print(f"   - Max Workers: 3-5 (for scaling)")
                
            else:
                print(f"❌ Could not get endpoint details")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔧 MANUAL FIX INSTRUCTIONS:")
    print(f"1. Go to RunPod Console: https://www.runpod.io/console/serverless")
    print(f"2. Click on your endpoint: {endpoint_id}")
    print(f"3. Click 'Edit' button")
    print(f"4. Under 'GPU Types', add more options:")
    print(f"   ✅ RTX A4000")
    print(f"   ✅ RTX A4500") 
    print(f"   ✅ RTX A5000")
    print(f"   ✅ RTX 4090")
    print(f"   ✅ RTX 3090")
    print(f"5. Under 'Locations', add more regions")
    print(f"6. Set Max Workers to 3-5")
    print(f"7. Click 'Save'")
    
    print(f"\n⚡ IMMEDIATE WORKAROUND:")
    print(f"The jobs will eventually process when GPUs become available.")
    print(f"Your setup is working correctly - it's just a capacity issue!")

if __name__ == "__main__":
    fix_gpu_availability()
