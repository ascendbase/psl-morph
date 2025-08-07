# RunPod Setup Guide for Face Morphing App

This guide explains how to set up RunPod Stable Diffusion XL serverless endpoint for cloud GPU processing in the Face Morphing Web App.

## Prerequisites

1. RunPod account with credits
2. Basic understanding of Stable Diffusion and LoRA models
3. Your custom LoRA file (`chad_sd1.5.safetensors`)

## Step 1: Create RunPod Serverless Endpoint

### 1.1 Login to RunPod
- Go to [RunPod.io](https://runpod.io)
- Login to your account
- Navigate to "Serverless" section

### 1.2 Create New Endpoint
- Click "New Endpoint"
- Choose "Stable Diffusion XL" template
- Configure the following settings:
  - **Name**: `face-morphing-sdxl`
  - **GPU Type**: RTX 4090 or A100 (recommended)
  - **Max Workers**: 1-3 (based on your needs)
  - **Idle Timeout**: 5 seconds
  - **Flash Boot**: Enabled (for faster cold starts)

### 1.3 Environment Variables
Add these environment variables to your endpoint:
```
MODEL_NAME=stabilityai/stable-diffusion-xl-base-1.0
ENABLE_LORA=true
LORA_WEIGHTS=your-custom-lora-url
```

## Step 2: Upload Your Custom LoRA

### 2.1 Upload LoRA to Cloud Storage
Upload your `chad_sd1.5.safetensors` file to:
- Hugging Face Hub (recommended)
- Google Drive with public link
- AWS S3 bucket
- Any publicly accessible URL

### 2.2 Get LoRA URL
Copy the direct download URL for your LoRA file.

Example URLs:
```
# Hugging Face
https://huggingface.co/username/repo/resolve/main/chad_sd1.5.safetensors

# Google Drive (convert share link to direct download)
https://drive.google.com/uc?id=FILE_ID&export=download
```

## Step 3: Configure Your Application

### 3.1 Environment Variables
Set these environment variables in your application:

```bash
# Enable cloud GPU
USE_CLOUD_GPU=true

# RunPod Configuration
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here

# Optional: Custom LoRA URL
RUNPOD_LORA_URL=https://your-lora-url.com/chad_sd1.5.safetensors
```

### 3.2 Get RunPod API Key
1. Go to RunPod Settings
2. Navigate to "API Keys"
3. Create new API key
4. Copy the key and set it as `RUNPOD_API_KEY`

### 3.3 Get Endpoint ID
1. Go to your created endpoint
2. Copy the Endpoint ID from the endpoint details
3. Set it as `RUNPOD_ENDPOINT_ID`

## Step 4: Test the Integration

### 4.1 Test Connection
Run the health check endpoint:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "gpu_type": "runpod",
  "gpu_status": "connected",
  "presets": ["HTN", "Chadlite", "Chad"],
  "cloud_gpu_enabled": true
}
```

### 4.2 Test Generation
1. Upload a face image through the web interface
2. Select a preset (HTN, Chadlite, or Chad)
3. Click "Process"
4. Monitor the processing status
5. Download the result when complete

## Step 5: Optimization Tips

### 5.1 Cost Optimization
- Use **Idle Timeout** of 5-10 seconds to minimize costs
- Set **Max Workers** based on expected concurrent users
- Monitor usage in RunPod dashboard

### 5.2 Performance Optimization
- Enable **Flash Boot** for faster cold starts
- Use RTX 4090 for best price/performance ratio
- Consider A100 for higher throughput needs

### 5.3 Reliability
- Set up monitoring and alerts
- Have fallback to local ComfyUI if needed
- Implement retry logic for failed requests

## Step 6: Troubleshooting

### Common Issues

#### 6.1 Connection Failed
```
Error: Failed to connect to RunPod endpoint
```
**Solutions:**
- Check API key is correct
- Verify endpoint ID is correct
- Ensure endpoint is running and not paused
- Check RunPod service status

#### 6.2 LoRA Not Loading
```
Error: LoRA model not found or failed to load
```
**Solutions:**
- Verify LoRA URL is publicly accessible
- Check LoRA file format (should be .safetensors)
- Ensure LoRA is compatible with SDXL
- Test LoRA URL in browser

#### 6.3 Generation Timeout
```
Error: Generation request timed out
```
**Solutions:**
- Increase timeout settings
- Check if endpoint has enough GPU resources
- Reduce image resolution if too high
- Monitor RunPod logs for errors

#### 6.4 High Costs
**Solutions:**
- Reduce idle timeout
- Optimize max workers setting
- Monitor usage patterns
- Consider switching to cheaper GPU types

## Step 7: Monitoring and Maintenance

### 7.1 Monitor Usage
- Check RunPod dashboard regularly
- Monitor costs and usage patterns
- Set up billing alerts

### 7.2 Update Models
- Keep base model updated
- Test new LoRA versions
- Monitor model performance

### 7.3 Scaling
- Adjust max workers based on demand
- Consider multiple endpoints for different regions
- Implement load balancing if needed

## Example Configuration Files

### Environment Variables (.env)
```bash
# Application Settings
USE_CLOUD_GPU=true
ENVIRONMENT=production

# RunPod Settings
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_LORA_URL=https://your-lora-url.com/chad_sd1.5.safetensors

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Security
SECRET_KEY=your_secret_key_here
```

### Docker Environment
```dockerfile
ENV USE_CLOUD_GPU=true
ENV RUNPOD_API_KEY=your_api_key_here
ENV RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

## Support

For issues with:
- **RunPod Platform**: Contact RunPod support
- **Application Integration**: Check application logs and GitHub issues
- **LoRA Models**: Verify model compatibility and format

## Cost Estimation

Typical costs for face morphing generations:
- **RTX 4090**: ~$0.0004 per second
- **A100**: ~$0.0008 per second
- **Average generation time**: 10-30 seconds
- **Cost per generation**: $0.004 - $0.024

Monthly costs for 1000 generations: $4 - $24

This is significantly more cost-effective than maintaining dedicated GPU infrastructure.

## Cost Analysis

Using RunPod serverless endpoints can significantly reduce costs compared to dedicated pods:
- **Dedicated Pod**: $25/day fixed cost regardless of usage
- **Serverless**: Pay only for compute time (~$0.0003-0.0005 per generation)

For typical usage (100 generations/day), serverless costs ~$120/month vs $750/month for dedicated pods.

## Serverless Migration

To migrate from a dedicated pod to serverless endpoints for cost savings, see [RUNPOD_SERVERLESS_SETUP.md](RUNPOD_SERVERLESS_SETUP.md) for detailed instructions.