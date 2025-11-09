"""
RunPod ComfyUI Client for Morph App
Handles ComfyUI workflow execution on RunPod serverless GPUs
"""

import requests
import json
import base64
import time
import os
from typing import Dict, Any, Optional

class RunPodComfyUIClient:
    """Client for running ComfyUI workflows on RunPod serverless"""
    
    def __init__(self, api_key: str, endpoint_id: str):
        """
        Initialize RunPod ComfyUI client
        
        Args:
            api_key: Your RunPod API key
            endpoint_id: Your RunPod endpoint ID
        """
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _load_workflow(self, workflow_path: str) -> Dict:
        """Load workflow JSON"""
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    def run_workflow(
        self, 
        workflow_path: str,
        input_image: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> Dict:
        """
        Run a ComfyUI workflow on RunPod
        
        Args:
            workflow_path: Path to workflow JSON file
            input_image: Path to input image (optional)
            params: Additional parameters to inject into workflow
            timeout: Maximum time to wait for result (seconds)
            
        Returns:
            Dict containing status and output
        """
        # Load workflow
        workflow = self._load_workflow(workflow_path)
        
        # Prepare payload
        payload = {
            "input": {
                "workflow": workflow
            }
        }
        
        # Add input image if provided
        if input_image and os.path.exists(input_image):
            # Update workflow with image
            if "5" in workflow:  # Node 5 is typically LoadImage
                workflow["5"]["inputs"]["image"] = os.path.basename(input_image)
            
            # Encode image
            payload["input"]["images"] = [{
                "name": os.path.basename(input_image),
                "image": self._encode_image(input_image)
            }]
        
        # Inject parameters into workflow
        if params:
            for node_id, node_params in params.items():
                if node_id in workflow:
                    workflow[node_id]["inputs"].update(node_params)
        
        # Run synchronous request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.base_url}/runsync",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"RunPod API error: {response.status_code}",
                "details": response.text
            }
        
        result = response.json()
        
        # Check if execution was successful
        if result.get("status") == "COMPLETED":
            return {
                "status": "success",
                "output": result.get("output"),
                "execution_time": result.get("executionTime")
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Unknown error"),
                "details": result
            }
    
    def run_facedetailer(
        self,
        input_image: str,
        prompt: str = "chad, male model, face portrait",
        negative_prompt: str = "(worst quality, low quality:1.4), (bad anatomy), text, error",
        denoise: float = 0.50,
        steps: int = 20,
        cfg: float = 8.0
    ) -> Dict:
        """
        Run FaceDetailer workflow
        
        Args:
            input_image: Path to input image
            prompt: Positive prompt
            negative_prompt: Negative prompt
            denoise: Denoising strength (0.0-1.0)
            steps: Number of sampling steps
            cfg: CFG scale
            
        Returns:
            Dict containing status and output
        """
        params = {
            "3": {"text": prompt},
            "4": {"text": negative_prompt},
            "8": {
                "denoise": denoise,
                "steps": steps,
                "cfg": cfg
            }
        }
        
        return self.run_workflow(
            "comfyui_workflows/workflow_facedetailer.json",
            input_image=input_image,
            params=params
        )
    
    def health_check(self) -> Dict:
        """Check if RunPod endpoint is healthy"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"status": "healthy", "details": response.json()}
            else:
                return {"status": "unhealthy", "code": response.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Example usage
if __name__ == "__main__":
    # Load credentials from environment or config
    API_KEY = os.getenv("RUNPOD_API_KEY", "YOUR_API_KEY")
    ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "YOUR_ENDPOINT_ID")
    
    # Create client
    client = RunPodComfyUIClient(API_KEY, ENDPOINT_ID)
    
    # Check health
    print("Checking endpoint health...")
    health = client.health_check()
    print(f"Health: {health}")
    
    # Run FaceDetailer workflow
    print("\nRunning FaceDetailer workflow...")
    result = client.run_facedetailer(
        input_image="path/to/your/image.jpg",
        prompt="chad, male model, perfect face",
        denoise=0.55,
        steps=25
    )
    
    print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if result["status"] == "success":
        print("\n✓ Workflow executed successfully!")
        print(f"Execution time: {result.get('execution_time', 'N/A')} seconds")
    else:
        print(f"\n✗ Error: {result.get('message')}")
