#!/usr/bin/env python3
"""
Upload Chad 1.5 LoRA to Modal persistent storage
"""

import modal
import os
import shutil

# Get the Modal app and volume
app = modal.App.lookup("face-morph-simple", create_if_missing=False)
models_volume = modal.Volume.from_name("face-models", create_if_missing=True)

@app.function(
    volumes={"/models": models_volume}
)
def upload_lora_files():
    """Upload LoRA files to Modal persistent storage"""
    print("📁 Setting up LoRA directory structure...")
    
    # Create lora directory if it doesn't exist
    os.makedirs("/models/lora", exist_ok=True)
    
    # List current contents
    if os.path.exists("/models/lora"):
        current_loras = os.listdir("/models/lora")
        print(f"📋 Current LoRAs in storage: {current_loras}")
    else:
        print("📋 No LoRA directory found, creating...")
        os.makedirs("/models/lora", exist_ok=True)
    
    print("✅ LoRA directory ready for upload")
    return "LoRA directory prepared"

@app.function(
    volumes={"/models": models_volume}
)
def list_uploaded_loras():
    """List all LoRAs in Modal storage"""
    print("📁 Checking LoRAs in Modal storage...")
    
    if os.path.exists("/models/lora"):
        loras = os.listdir("/models/lora")
        print(f"📋 Available LoRAs: {loras}")
        
        for lora in loras:
            lora_path = f"/models/lora/{lora}"
            if os.path.isfile(lora_path):
                size = os.path.getsize(lora_path)
                print(f"   📄 {lora}: {size:,} bytes")
        
        return loras
    else:
        print("❌ No LoRA directory found")
        return []

if __name__ == "__main__":
    print("🚀 UPLOADING CHAD 1.5 LORA TO MODAL")
    print("=" * 50)
    
    # First, prepare the directory
    with app.run():
        result = upload_lora_files.remote()
        print(f"Setup result: {result}")
    
    # Upload the local LoRA file
    print("\n📤 Uploading local LoRA file...")
    local_lora_path = "lora/chad_sd1.5.safetensors"
    
    if os.path.exists(local_lora_path):
        print(f"✅ Found local LoRA: {local_lora_path}")
        
        # Upload to Modal volume
        with models_volume.batch_upload() as batch:
            batch.put_file(local_lora_path, "/lora/chad_sd1.5.safetensors")
        
        print("✅ Chad 1.5 LoRA uploaded to Modal storage!")
        
        # Verify upload
        print("\n🔍 Verifying upload...")
        with app.run():
            uploaded_loras = list_uploaded_loras.remote()
            
        if "chad_sd1.5.safetensors" in uploaded_loras:
            print("🎉 SUCCESS! Chad 1.5 LoRA is now available in Modal!")
        else:
            print("❌ Upload verification failed")
    else:
        print(f"❌ Local LoRA file not found: {local_lora_path}")
        print("Please make sure the file exists in the lora directory")
