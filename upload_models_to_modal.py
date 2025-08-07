"""
Upload models, LoRAs, and workflows to Modal.com persistent storage
Run this script to prepare your Modal deployment
"""

import modal
import os
import shutil

# Create Modal app for uploading
app = modal.App("face-morph-setup")

# Create persistent volume for models
volume = modal.Volume.from_name("face-models", create_if_missing=True)

@app.function(
    volumes={"/models": volume},
    timeout=3600  # 1 hour timeout for large uploads
)
def upload_models():
    """Upload all models, LoRAs, and workflows to Modal storage"""
    
    print("🚀 Starting model upload to Modal.com...")
    
    uploaded_files = []
    
    # Upload LoRAs
    if os.path.exists("./lora"):
        print("📁 Uploading LoRAs...")
        os.makedirs("/models/lora", exist_ok=True)
        
        for file in os.listdir("./lora"):
            if file.endswith(('.safetensors', '.ckpt', '.pt')):
                src_path = f"./lora/{file}"
                dst_path = f"/models/lora/{file}"
                
                print(f"⬆️ Uploading {file}...")
                shutil.copy(src_path, dst_path)
                uploaded_files.append(f"LoRA: {file}")
                print(f"✅ Uploaded: {file}")
    else:
        print("⚠️ No ./lora directory found")
    
    # Upload base models
    if os.path.exists("./base_models"):
        print("📁 Uploading base models...")
        os.makedirs("/models/base_models", exist_ok=True)
        
        for file in os.listdir("./base_models"):
            if file.endswith(('.safetensors', '.ckpt')):
                src_path = f"./base_models/{file}"
                dst_path = f"/models/base_models/{file}"
                
                print(f"⬆️ Uploading {file}...")
                shutil.copy(src_path, dst_path)
                uploaded_files.append(f"Base Model: {file}")
                print(f"✅ Uploaded: {file}")
    else:
        print("⚠️ No ./base_models directory found")
    
    # Upload workflows
    if os.path.exists("./comfyui_workflows"):
        print("📁 Uploading workflows...")
        os.makedirs("/models/comfyui_workflows", exist_ok=True)
        
        for file in os.listdir("./comfyui_workflows"):
            if file.endswith('.json'):
                src_path = f"./comfyui_workflows/{file}"
                dst_path = f"/models/comfyui_workflows/{file}"
                
                print(f"⬆️ Uploading {file}...")
                shutil.copy(src_path, dst_path)
                uploaded_files.append(f"Workflow: {file}")
                print(f"✅ Uploaded: {file}")
    else:
        print("⚠️ No ./comfyui_workflows directory found")
    
    # List uploaded files
    print("\n📋 Upload Summary:")
    if uploaded_files:
        for file in uploaded_files:
            print(f"  ✅ {file}")
        print(f"\n🎉 Successfully uploaded {len(uploaded_files)} files!")
    else:
        print("⚠️ No files were uploaded. Please check your directories.")
    
    # List contents of Modal storage
    print("\n📁 Modal Storage Contents:")
    for root, dirs, files in os.walk("/models"):
        level = root.replace("/models", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    return f"Upload completed: {len(uploaded_files)} files"

@app.function(volumes={"/models": volume})
def list_modal_storage():
    """List all files in Modal storage"""
    
    print("📁 Modal Storage Contents:")
    
    if not os.path.exists("/models"):
        print("❌ No models directory found in Modal storage")
        return
    
    total_files = 0
    for root, dirs, files in os.walk("/models"):
        level = root.replace("/models", "").count(os.sep)
        indent = " " * 2 * level
        folder_name = os.path.basename(root) if root != "/models" else "models"
        print(f"{indent}{folder_name}/")
        
        subindent = " " * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            print(f"{subindent}{file} ({size_mb:.1f} MB)")
            total_files += 1
    
    print(f"\n📊 Total files in storage: {total_files}")

@app.local_entrypoint()
def main():
    """Main function to run upload"""
    
    print("🚀 Modal.com Model Upload Tool")
    print("=" * 50)
    
    # Check local directories
    print("🔍 Checking local directories...")
    
    local_dirs = ["./lora", "./base_models", "./comfyui_workflows"]
    found_dirs = []
    
    for dir_path in local_dirs:
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) 
                            if f.endswith(('.safetensors', '.ckpt', '.pt', '.json'))])
            print(f"✅ {dir_path}: {file_count} files")
            found_dirs.append(dir_path)
        else:
            print(f"❌ {dir_path}: Not found")
    
    if not found_dirs:
        print("\n⚠️ No model directories found!")
        print("Please ensure you have:")
        print("  - ./lora/ (for LoRA files)")
        print("  - ./base_models/ (for checkpoint files)")
        print("  - ./comfyui_workflows/ (for workflow JSON files)")
        return
    
    print(f"\n📁 Found {len(found_dirs)} directories with models")
    
    # Upload models
    print("\n⬆️ Starting upload...")
    result = upload_models.remote()
    print(f"📊 Upload result: {result}")
    
    # List storage contents
    print("\n📋 Listing Modal storage...")
    list_modal_storage.remote()
    
    print("\n🎉 Upload process completed!")
    print("\nNext steps:")
    print("1. Deploy your Modal app: modal deploy modal_face_morph.py")
    print("2. Test the setup: python modal_face_morph.py")
    print("3. Update your app config: USE_MODAL=true")

if __name__ == "__main__":
    main()
