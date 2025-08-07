# RunPod Serverless Setup Guide

This guide explains how to migrate from a dedicated RunPod pod to RunPod serverless endpoints for cost efficiency.

## Current Cost Analysis

**Dedicated Pod Model:**
- RTX 5090 pod: $25/day fixed cost
- Regardless of usage volume
- Always running, consuming resources

**Serverless Model:**
- Pay only for compute time used
- ~$0.0003-0.0005 per generation (depending on complexity)
- Scales to zero when not in use

## Migration Steps

### 1. Create Custom Docker Image

1. Build a Docker image with your exact setup:
   - ComfyUI with all custom nodes
   - Your LoRA models
   - Your workflow templates
   - All dependencies

2. Push to a container registry (Docker Hub, GitHub Container Registry, etc.)

### 2. Deploy to RunPod Serverless

1. Go to RunPod dashboard
2. Create a new serverless endpoint
3. Select your custom Docker image
4. Configure GPU requirements (RTX 5090 recommended)
5. Set appropriate timeout values

### 3. Update Application Configuration

1. Set `USE_RUNPOD_POD=false` in your environment
2. Set `RUNPOD_ENDPOINT_ID` to your new serverless endpoint ID
3. Set `RUNPOD_API_KEY` with your API key

### 4. Test the Migration

1. Run a few test generations
2. Monitor performance and costs
3. Verify all functionality works as expected

## Cost Savings Example

**Before (Dedicated Pod):**
- $25/day × 30 days = $750/month (fixed)

**After (Serverless):**
- Assuming 100 generations/day at $0.0004 each
- 100 × $0.0004 × 30 = $120/month (variable)

**Savings: $630/month**

## Performance Considerations

- Cold start time: 10-30 seconds for container initialization
- Warm instances: Near-instant response
- For high-volume periods, consider pre-warming instances

## Best Practices

1. Monitor usage patterns to optimize costs
2. Set appropriate timeouts for long-running generations
3. Use caching for frequently requested transformations
4. Implement retry logic for handling cold starts

## Configuration

To switch to serverless mode, update your environment variables:

```bash
# Disable dedicated pod mode
USE_RUNPOD_POD=false

# Enable cloud GPU (required for RunPod)
USE_CLOUD_GPU=true

# Your RunPod API key
RUNPOD_API_KEY=your_api_key_here

# Your serverless endpoint ID
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

## Code Changes

The application automatically uses the serverless client when `USE_RUNPOD_POD=false` and `USE_CLOUD_GPU=true`. No code changes are required in the application itself.

## Testing

1. Restart your application with the new configuration
2. Upload a test image and run a generation
3. Monitor the RunPod dashboard for successful execution
4. Verify the output quality matches your dedicated pod setup

## Troubleshooting

### Common Issues

1. **Authentication errors**: Verify your API key is correct
2. **Timeout errors**: Increase timeout values in config.py
3. **Cold start delays**: Implement retry logic in your frontend

### Monitoring

1. Check RunPod dashboard for execution logs
2. Monitor your application logs for errors
3. Track generation times to optimize performance

## Support

For issues with the migration, contact RunPod support or check the RunPod documentation.