"""
Test the new RunPod endpoint and wait for results
"""

import os
import time
import requests
from dotenv import load_dotenv
from runpod_client import RunPodClient

def test_with_wait():
    """Test generation and wait for completion"""
    
    print("🎯 TESTING NEW ENDPOINT WITH WAIT")
    print("=" * 50)
    
    load_dotenv()
    
    api_key = os.getenv('RUNPOD_API_KEY')
    endpoint_id = os.getenv('RUNPOD_ENDPOINT_ID')
    
    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"Endpoint ID: {endpoint_id}")
    
    if not api_key or not endpoint_id:
        print("❌ Missing credentials!")
        return
    
    # Initialize client
    client = RunPodClient(api_key, endpoint_id)
    print("✅ Client initialized")
    
    # Test image
    test_image = "test_image.png"
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    print(f"✅ Test image found: {test_image}")
    
    # Submit job
    print(f"\n🚀 Submitting HTN generation...")
    try:
        result, error = client.generate_image(
            image_path=test_image,
            preset_key='HTN',
            denoise_intensity=4
        )
        
        if error:
            print(f"❌ Generation failed: {error}")
            return
        
        job_id = result
        print(f"✅ Job submitted: {job_id}")
        
        # Wait for completion
        print(f"\n⏳ Waiting for job completion...")
        max_wait = 300  # 5 minutes
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                # Check job status
                status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
                headers = {'Authorization': f'Bearer {api_key}'}
                
                response = requests.get(status_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'UNKNOWN')
                    
                    print(f"Status: {status}")
                    
                    if status == 'COMPLETED':
                        print(f"🎉 JOB COMPLETED!")
                        
                        # Get the output
                        output = data.get('output', {})
                        if output:
                            print(f"✅ Output received!")
                            print(f"Output keys: {list(output.keys())}")
                            
                            # Check for image data
                            if 'image' in output:
                                print(f"✅ Generated image found!")
                                return True
                            elif 'images' in output:
                                print(f"✅ Generated images found!")
                                return True
                            else:
                                print(f"⚠️ No image in output: {output}")
                        else:
                            print(f"⚠️ No output data")
                        
                        return True
                        
                    elif status == 'FAILED':
                        print(f"❌ Job failed!")
                        error_msg = data.get('error', 'Unknown error')
                        print(f"Error: {error_msg}")
                        return False
                        
                    elif status in ['IN_QUEUE', 'IN_PROGRESS']:
                        print(f"⏳ Job {status.lower()}...")
                        time.sleep(5)
                        wait_time += 5
                        continue
                    else:
                        print(f"⚠️ Unknown status: {status}")
                        time.sleep(5)
                        wait_time += 5
                        continue
                        
                else:
                    print(f"❌ Status check failed: {response.status_code}")
                    time.sleep(5)
                    wait_time += 5
                    continue
                    
            except Exception as e:
                print(f"❌ Error checking status: {e}")
                time.sleep(5)
                wait_time += 5
                continue
        
        print(f"⏰ Timeout after {max_wait} seconds")
        return False
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_wait()
    if success:
        print(f"\n🎉 SUCCESS! Your RunPod endpoint is generating images!")
    else:
        print(f"\n❌ FAILED! Need to investigate the issue.")
