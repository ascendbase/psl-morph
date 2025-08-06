# Complete Integration Guide: Railway ↔ RunPod Serverless

## 🎯 Overview
This guide connects your Railway web app to RunPod serverless, replacing the expensive hourly GPU rental with pay-per-use serverless.

## 📋 Complete Migration Checklist

### Phase 1: Docker Image (Current Step)
- [ ] Build Docker image with ComfyUI + FaceDetailer
- [ ] Push to Docker Hub
- [ ] Test image locally

### Phase 2: RunPod Serverless Setup
- [ ] Create RunPod serverless endpoint
- [ ] Configure with your Docker image
- [ ] Get API credentials
- [ ] Test serverless endpoint

### Phase 3: Railway App Integration
- [ ] Update runpod_client.py for serverless API
- [ ] Add environment variables
- [ ] Test integration locally
- [ ] Deploy to Railway

### Phase 4: Testing & Optimization
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Cost monitoring
- [ ] User experience validation

## 🔧 Phase 1: Docker Image (In Progress)

### Current Status
You have the Docker image ready. Next steps:

1. **Build the image**:
   ```cmd
   build_now.bat
   ```

2. **Push to Docker Hub**:
   ```cmd
   push_to_dockerhub.bat
   ```

## 🚀 Phase 2: RunPod Serverless Setup

### Step 1: Create Serverless Endpoint
1. Go to [RunPod Console](https://www.runpod.io/console/serverless)
2. Click "New Endpoint"
3. Configure:
   - **Name**: `face-morphing-comfyui`
   - **Docker Image**: `ascendbase/face-morphing-comfyui:latest`
   - **GPU Type**: RTX 4090 or A100 (for speed)
   - **Container Disk**: 20GB
   - **Max Workers**: 3-5 (adjust based on usage)

### Step 2: Configure Environment
```json
{
  "CONTAINER_DISK_SIZE_GB": "20",
  "PYTHONUNBUFFERED": "1"
}
```

### Step 3: Get API Credentials
After creation, you'll get:
- **Endpoint ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **API Key**: Your RunPod API key

## 🔗 Phase 3: Railway App Integration

### Step 1: Update Environment Variables
Add to your Railway app:
```env
RUNPOD_SERVERLESS_ENDPOINT=your-endpoint-id
RUNPOD_API_KEY=your-api-key
RUNPOD_SERVERLESS_URL=https://api.runpod.ai/v2/your-endpoint-id
```

### Step 2: Update runpod_client.py
Replace the current pod connection with serverless API:

```python
import requests
import time
import os
import base64

class RunPodServerlessClient:
    def __init__(self):
        self.endpoint_id = os.getenv('RUNPOD_SERVERLESS_ENDPOINT')
        self.api_key = os.getenv('RUNPOD_API_KEY')
        self.base_url = f"https://api.runpod.ai/v2/{self.endpoint_id}"
        
    def generate_image(self, workflow_data, input_image=None):
        """Submit job to RunPod serverless"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare input data
        input_data = {
            "workflow": workflow_data
        }
        
        if input_image:
            # Convert image to base64
            input_data["input_image"] = base64.b64encode(input_image).decode()
        
        # Submit job
        response = requests.post(
            f"{self.base_url}/run",
            json={"input": input_data},
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to submit job: {response.text}")
        
        job_data = response.json()
        job_id = job_data["id"]
        
        # Poll for completion
        return self._wait_for_completion(job_id, headers)
    
    def _wait_for_completion(self, job_id, headers):
        """Wait for job completion and return result"""
        while True:
            response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get job status: {response.text}")
            
            status_data = response.json()
            status = status_data["status"]
            
            if status == "COMPLETED":
                return status_data["output"]
            elif status == "FAILED":
                raise Exception(f"Job failed: {status_data.get('error', 'Unknown error')}")
            
            # Wait before polling again
            time.sleep(2)

# Usage in your app
def process_face_morphing(input_image, workflow_type="facedetailer"):
    client = RunPodServerlessClient()
    
    # Load appropriate workflow
    workflow_path = f"comfyui_workflows/workflow_{workflow_type}.json"
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Generate image
    result = client.generate_image(workflow, input_image)
    
    return result
```

### Step 3: Update Your Main App Logic
In your main app file (app.py), update the image generation calls:

```python
from runpod_client import process_face_morphing

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        # Get user input
        input_image = request.files['image'].read()
        workflow_type = request.form.get('workflow_type', 'facedetailer')
        
        # Check user credits
        if not user_has_credits(current_user):
            return jsonify({"error": "Insufficient credits"}), 400
        
        # Generate image using serverless
        result = process_face_morphing(input_image, workflow_type)
        
        # Deduct credit
        deduct_user_credit(current_user)
        
        # Return result
        return jsonify({"success": True, "image_url": result["image_url"]})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## 📊 Phase 4: Cost Monitoring

### Add Cost Tracking
```python
import time

class CostTracker:
    def __init__(self):
        self.generation_costs = []
    
    def track_generation(self, start_time, end_time, cost_per_second=0.0004):
        duration = end_time - start_time
        cost = duration * cost_per_second
        self.generation_costs.append({
            'duration': duration,
            'cost': cost,
            'timestamp': time.time()
        })
        return cost
    
    def get_daily_cost(self):
        today = time.time() - 86400  # 24 hours ago
        daily_costs = [c['cost'] for c in self.generation_costs if c['timestamp'] > today]
        return sum(daily_costs)
```

## 🎯 Expected Cost Savings

### Before (Hourly)
- **Cost**: $0.90/hour × 24 hours = $21.60/day
- **Monthly**: $648
- **Efficiency**: ~5% (most time idle)

### After (Serverless)
- **Cost**: $0.0004/second × actual usage
- **Per generation**: ~$0.004 (10 seconds)
- **Monthly**: $4-40 depending on usage
- **Efficiency**: 100%

### Profit Analysis
- **Revenue per credit**: $0.25
- **Cost per generation**: $0.004
- **Profit per generation**: $0.246 (98.4% margin!)

## 🚀 Deployment Steps

1. **Complete Docker build** (current step)
2. **Set up RunPod serverless endpoint**
3. **Update Railway app code**
4. **Test integration**
5. **Deploy to production**
6. **Monitor costs and performance**

## 📈 Scaling Strategy

With serverless, you can:
- **Handle unlimited users** without fixed costs
- **Scale automatically** based on demand
- **Add premium features** for higher margins
- **Expand to new markets** without infrastructure concerns

Your app will go from losing $600+/month to making $100+/month profit!
