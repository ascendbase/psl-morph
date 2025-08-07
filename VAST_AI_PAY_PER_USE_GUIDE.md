# 💰 Vast.ai Pay-Per-Use Setup Guide

## 🎯 **Goal: Pay Only for Generation Time**

Instead of paying hourly rates, you want to pay **only when generating images**. Here's how to achieve this with Vast.ai:

## 🚀 **Method 1: On-Demand Instance Management (Recommended)**

### **How It Works**
1. **Start instance** only when generation is requested
2. **Process image** (takes 30-60 seconds)
3. **Stop instance** immediately after completion
4. **Pay only** for actual usage time (~1-2 minutes per generation)

### **Cost Breakdown**
```
Traditional Hourly: $0.20-0.50/hour × 1 hour = $0.20-0.50
Pay-Per-Use: $0.20-0.50/hour × 0.02 hours = $0.004-0.01

SAVINGS: 98-99% cost reduction!
```

### **Implementation Steps**

#### **1. Enhanced Vast.ai Client**
Create an advanced client that manages instances automatically:

```python
# vast_on_demand_client.py
import requests
import time
import json
import os
from typing import Optional, Tuple

class VastOnDemandClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://console.vast.ai/api/v0"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.current_instance_id = None
    
    def find_cheapest_gpu(self, min_gpu_ram: int = 8) -> Optional[dict]:
        """Find the cheapest available GPU instance"""
        url = f"{self.base_url}/bundles/"
        params = {
            "q": json.dumps({
                "verified": {"eq": True},
                "external": {"eq": False},
                "rentable": {"eq": True},
                "gpu_ram": {"gte": min_gpu_ram},
                "type": "on-demand"
            }),
            "order": [["dph_total", "asc"]],  # Order by price ascending
            "limit": 10
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            offers = response.json()["offers"]
            return offers[0] if offers else None
        return None
    
    def start_instance(self, offer_id: int, image: str = "pytorch/pytorch:latest") -> Optional[int]:
        """Start a new instance"""
        url = f"{self.base_url}/asks/{offer_id}/"
        data = {
            "client_id": "vast_on_demand",
            "image": image,
            "args": [],
            "env": {},
            "onstart": "bash -c 'pip install torch torchvision && echo Instance ready'"
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        if response.status_code == 200:
            result = response.json()
            self.current_instance_id = result.get("new_contract")
            return self.current_instance_id
        return None
    
    def wait_for_instance_ready(self, instance_id: int, timeout: int = 300) -> bool:
        """Wait for instance to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_instance_status(instance_id)
            if status == "running":
                return True
            time.sleep(10)
        return False
    
    def get_instance_status(self, instance_id: int) -> str:
        """Get instance status"""
        url = f"{self.base_url}/instances/"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            instances = response.json()["instances"]
            for instance in instances:
                if instance["id"] == instance_id:
                    return instance["actual_status"]
        return "unknown"
    
    def stop_instance(self, instance_id: int) -> bool:
        """Stop instance"""
        url = f"{self.base_url}/instances/{instance_id}/"
        response = requests.delete(url, headers=self.headers)
        return response.status_code == 200
    
    def generate_image_on_demand(self, image_path: str, preset: str = "tier1") -> Tuple[Optional[bytes], Optional[str]]:
        """Generate image with on-demand instance"""
        try:
            # 1. Find cheapest GPU
            offer = self.find_cheapest_gpu()
            if not offer:
                return None, "No available GPU instances"
            
            # 2. Start instance
            instance_id = self.start_instance(offer["id"])
            if not instance_id:
                return None, "Failed to start instance"
            
            # 3. Wait for ready
            if not self.wait_for_instance_ready(instance_id):
                self.stop_instance(instance_id)
                return None, "Instance failed to start"
            
            # 4. Process image (implement your ComfyUI workflow here)
            result_image = self.process_on_instance(instance_id, image_path, preset)
            
            # 5. Stop instance immediately
            self.stop_instance(instance_id)
            
            return result_image, None
            
        except Exception as e:
            if self.current_instance_id:
                self.stop_instance(self.current_instance_id)
            return None, str(e)
    
    def process_on_instance(self, instance_id: int, image_path: str, preset: str) -> Optional[bytes]:
        """Process image on the running instance"""
        # This would implement your ComfyUI workflow
        # For now, return placeholder
        time.sleep(30)  # Simulate processing time
        return b"fake_image_data"
```

#### **2. Update Your App Configuration**
```python
# In config.py, add:
VAST_ON_DEMAND_MODE = True
VAST_AUTO_STOP_INSTANCES = True
VAST_MAX_INSTANCE_LIFETIME = 300  # 5 minutes max
```

#### **3. Integration with Your App**
```python
# In app.py, update the GPU client initialization:
if USE_CLOUD_GPU and VAST_ON_DEMAND_MODE:
    from vast_on_demand_client import VastOnDemandClient
    gpu_client = VastOnDemandClient(os.getenv('VAST_API_KEY'))
```

## 🔧 **Method 2: Instance Auto-Stop with Monitoring**

### **How It Works**
1. **Keep instance running** during active periods
2. **Monitor idle time** (no generations for X minutes)
3. **Auto-stop** when idle threshold reached
4. **Auto-start** when new generation requested

### **Implementation**
```python
# vast_auto_stop_client.py
import threading
import time
from datetime import datetime, timedelta

class VastAutoStopClient:
    def __init__(self, api_key: str, idle_timeout: int = 300):  # 5 minutes
        self.api_key = api_key
        self.idle_timeout = idle_timeout
        self.last_activity = datetime.now()
        self.instance_id = None
        self.monitor_thread = None
        self.running = False
    
    def start_monitoring(self):
        """Start the idle monitoring thread"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_idle)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_idle(self):
        """Monitor for idle instances and stop them"""
        while self.running:
            if self.instance_id:
                idle_time = datetime.now() - self.last_activity
                if idle_time.total_seconds() > self.idle_timeout:
                    print(f"Instance idle for {idle_time}, stopping...")
                    self.stop_current_instance()
            time.sleep(60)  # Check every minute
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def generate_image(self, image_path: str, preset: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Generate image with auto-stop management"""
        self.update_activity()
        
        # Start instance if not running
        if not self.instance_id:
            self.instance_id = self.start_new_instance()
            if not self.instance_id:
                return None, "Failed to start instance"
        
        # Process image
        result = self.process_image(image_path, preset)
        self.update_activity()
        
        return result, None
```

## 💡 **Method 3: Scheduled Instance Management**

### **How It Works**
1. **Predict usage patterns** (peak hours, etc.)
2. **Start instances** before expected usage
3. **Stop instances** during low-usage periods
4. **Scale up/down** based on demand

### **Usage Patterns**
```python
# Example usage schedule
USAGE_SCHEDULE = {
    "weekdays": {
        "start": "08:00",  # Start at 8 AM
        "stop": "22:00",   # Stop at 10 PM
        "timezone": "UTC"
    },
    "weekends": {
        "start": "10:00",  # Start at 10 AM
        "stop": "20:00",   # Stop at 8 PM
        "timezone": "UTC"
    }
}
```

## 📊 **Cost Comparison**

### **Traditional Hourly Billing**
```
RTX 4090: $0.50/hour × 24 hours = $12/day
Monthly cost: $360
Yearly cost: $4,320
```

### **Pay-Per-Use (Method 1)**
```
100 generations/day × 1 minute each = 100 minutes
100 minutes ÷ 60 = 1.67 hours/day
1.67 hours × $0.50 = $0.83/day
Monthly cost: $25
Yearly cost: $300

SAVINGS: 93% cost reduction!
```

### **Auto-Stop (Method 2)**
```
Active 4 hours/day × $0.50 = $2/day
Monthly cost: $60
Yearly cost: $720

SAVINGS: 83% cost reduction!
```

## 🛠 **Setup Instructions**

### **1. Install Dependencies**
```bash
pip install requests threading datetime
```

### **2. Get Vast.ai API Key**
```bash
# Go to: https://console.vast.ai/account/
# Generate API key
# Add to .env:
VAST_API_KEY=your_api_key_here
VAST_ON_DEMAND_MODE=true
```

### **3. Test On-Demand Setup**
```bash
python test_vast_on_demand.py
```

### **4. Monitor Costs**
- Check Vast.ai dashboard regularly
- Set spending alerts
- Track cost per generation

## 🚨 **Important Considerations**

### **Startup Time**
- **Cold start**: 2-5 minutes to start new instance
- **Warm start**: 30 seconds if instance already running
- **Trade-off**: Cost savings vs response time

### **Reliability**
- **Instance availability**: May need to wait for GPU
- **Fallback options**: Have backup providers ready
- **Error handling**: Implement robust retry logic

### **Optimization Tips**
1. **Batch processing**: Process multiple images per instance
2. **Smart scheduling**: Predict usage patterns
3. **Instance pooling**: Keep 1-2 instances warm during peak hours
4. **Cost monitoring**: Set daily/monthly spending limits

## 🎯 **Recommended Approach**

For your use case, I recommend **Method 1 (On-Demand)** because:
- ✅ **Maximum cost savings** (98-99%)
- ✅ **True pay-per-use** billing
- ✅ **No idle costs**
- ✅ **Scales to zero** when not used

The 2-5 minute startup time is acceptable for most users, and the massive cost savings make it worthwhile.

## 🚀 **Next Steps**

1. **Implement** the VastOnDemandClient
2. **Test** with small workloads
3. **Monitor** costs and performance
4. **Optimize** based on usage patterns
5. **Scale up** once proven

Your GPU costs will drop from $300-600/month to $25-60/month - a **90-95% reduction**!
