# RunPod Serverless Deployment Instructions

This document provides step-by-step instructions for deploying the Face Morphing SaaS application with RunPod serverless endpoints.

## Prerequisites

1. Docker installed on your system
2. A Docker Hub account
3. A RunPod account with billing set up
4. The Docker image built (ascendbase/face-morphing-comfyui:latest)

## Deployment Steps

### 1. Build the Docker Image

Make sure the Docker image is built:

```bash
docker build -f Dockerfile.runpod -t ascendbase/face-morphing-comfyui:latest .
```

### 2. Log in to Docker Hub

```bash
docker login
```

### 3. Push the Image to Docker Hub

```bash
docker push ascendbase/face-morphing-comfyui:latest
```

Or use the provided scripts:
- On Linux/Mac: `./push_to_dockerhub.sh`
- On Windows: `push_to_dockerhub.bat`

### 4. Deploy to RunPod Serverless

1. Go to [RunPod.io](https://www.runpod.io/)
2. Navigate to "Serverless" in the dashboard
3. Click "Create Endpoint"
4. Fill in the endpoint details:
   - Endpoint Name: `face-morphing-comfyui`
   - Container Image: `ascendbase/face-morphing-comfyui:latest`
   - GPU Type: Select RTX 5090 or better
   - Ports: `8188`
   - Startup Command: `python main.py --listen 0.0.0.0 --port 8188`
5. Click "Create Endpoint"

### 5. Update Application Configuration

Update your application's `.env` file with the RunPod serverless configuration:

```bash
# RunPod Serverless Configuration
USE_CLOUD_GPU=true
USE_RUNPOD_POD=false
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
RUNPOD_API_KEY=your_api_key_here
```

### 6. Test the Connection

Start your application and verify it can connect to the RunPod serverless endpoint.

## Cost Considerations

With RunPod serverless, you only pay for the compute time used:
- Per second billing with a minimum of 1 second
- No idle costs
- Approximately 80% cost reduction compared to dedicated pods

## Troubleshooting

### Common Issues

1. **Image not found**: Ensure the image was pushed to Docker Hub successfully
2. **Connection timeout**: Check that the endpoint is configured correctly
3. **GPU allocation failed**: Try selecting a different GPU type

### Support

For issues with the Docker image or RunPod deployment:
1. Check the RunPod documentation
2. Review the serverless endpoint logs in the RunPod dashboard
3. Contact RunPod support if needed