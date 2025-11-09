# Docker Build Error Fix Guide
## "input/output error" Solution

## Problem

You're seeing this error:
```
ERROR: failed to build: failed to solve: failed to compute cache key: commit failed: input/output error
```

This is a **Docker Desktop storage issue**, not a Dockerfile problem.

## Quick Fixes (Try in Order)

### Fix 1: Clean Docker Build Cache

```cmd
docker system prune -a
```

When prompted, type `y` and press Enter.

This will:
- Remove all stopped containers
- Remove all unused images
- Remove all build cache
- Free up disk space

### Fix 2: Restart Docker Desktop

1. Right-click Docker Desktop icon in system tray
2. Click "Quit Docker Desktop"
3. Wait 10 seconds
4. Start Docker Desktop again
5. Wait for it to fully start
6. Try building again

### Fix 3: Increase Docker Disk Space

1. Open Docker Desktop
2. Go to Settings (gear icon)
3. Click "Resources" → "Advanced"
4. Increase "Disk image size" to at least **64 GB**
5. Click "Apply & Restart"
6. Wait for Docker to restart
7. Try building again

###Fix 4: Reset Docker Desktop to Factory Defaults

⚠️ **Warning:** This will delete all images and containers

1. Open Docker Desktop
2. Go to Settings → "Troubleshoot"
3. Click "Clean / Purge data"
4. Click "Reset to factory defaults"
5. Restart Docker Desktop
6. Try building again

## Recommended Solution

**Do Fix 1 + Fix 3 together:**

1. Clean Docker cache:
   ```cmd
   docker system prune -a
   ```

2. Increase disk space to 64 GB in Docker Settings

3. Run the build script again:
   ```cmd
   build_and_push_comfyui.bat
   ```

## Alternative: Use Pre-built Image

If Docker issues persist, you can:

1. Use an existing ComfyUI base image from someone else
2. Or build on GitHub Actions (free) instead of locally
3. Or use RunPod's web interface to build directly on their platform

## Verify Docker is Healthy

Before building, test Docker:

```cmd
docker run hello-world
```

If this works, Docker is healthy and ready to build.

## Why This Happens

- Docker ran out of disk space during download
- Build cache filled up Docker's allocated space
- The RunPod base image is large (~5 GB)
- Windows tmpfs/Docker storage got corrupted

## After Fixing

Once Docker is healthy:

1. Double-click `build_and_push_comfyui.bat`
2. Enter your DockerHub username: `ascendbase`
3. Wait 15-30 minutes for build
4. Success! ✅

## Still Having Issues?

If problems persist after trying all fixes:

1. Check Windows has enough disk space (need 20+ GB free)
2. Try restarting Windows
3. Reinstall Docker Desktop
4. Or use GitHub Actions to build instead (see below)

## Build with GitHub Actions Instead

If local building keeps failing, push code to GitHub and build there:

```yaml
# .github/workflows/build-docker.yml
# (Already included in your project)
```

Just push to GitHub and it will build automatically for free!
