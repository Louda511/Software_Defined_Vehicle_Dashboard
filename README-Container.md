# ADAS Dashboard - Containerized with Podman

This guide explains how to run the ADAS Dashboard application in a container using Podman.

## Prerequisites

1. **Podman**: Make sure Podman is installed on your system
   ```bash
   # Ubuntu/Debian
   sudo apt-get install podman
   
   # CentOS/RHEL/Fedora
   sudo dnf install podman
   ```

2. **X11 Display**: Ensure you're running in a graphical environment with X11 support

3. **X11 Permissions**: The script will automatically set up X11 permissions

## Quick Start

### Option 1: Using the provided script (Recommended)

```bash
./run-container.sh
```

This script will:
- Check if Podman is installed
- Set up X11 permissions
- Build the container image
- Run the application

### Option 2: Manual Podman commands

1. **Build the image**:
   ```bash
   podman build -t adas-dashboard .
   ```

2. **Run the container**:
   ```bash
   # Allow X11 connections
   xhost +local:docker
   
   # Run the container
   podman run --rm \
       --name adas-dashboard \
       --env DISPLAY=$DISPLAY \
       --env QT_X11_NO_MITSHM=1 \
       --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
       --volume .:/app \
       --network host \
       --interactive \
       --tty \
       adas-dashboard
   ```

### Option 3: Using Docker Compose

```bash
# Build and run with docker-compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

## Container Features

- **PyQt6 Support**: Full GUI application support with all necessary X11 libraries
- **Security**: Runs as non-root user inside the container
- **Volume Mounting**: Application code is mounted for easy development
- **X11 Forwarding**: Proper display forwarding for GUI applications
- **Network Access**: Host network mode for full network access

## Troubleshooting

### X11 Display Issues

If you encounter X11 display issues:

1. **Check DISPLAY variable**:
   ```bash
   echo $DISPLAY
   ```

2. **Verify X11 socket**:
   ```bash
   ls -la /tmp/.X11-unix/
   ```

3. **Set X11 permissions manually**:
   ```bash
   xhost +local:docker
   ```

### Permission Issues

If you get permission errors:

1. **Check if you're in the docker group**:
   ```bash
   groups $USER
   ```

2. **Add user to docker group** (if needed):
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

### Container Build Issues

If the build fails:

1. **Check available disk space**:
   ```bash
   df -h
   ```

2. **Clean up unused images**:
   ```bash
   podman system prune -a
   ```

3. **Check Dockerfile syntax**:
   ```bash
   podman build --no-cache -t adas-dashboard .
   ```

## Development Workflow

For development, the container mounts the current directory as a volume, so changes to your code will be reflected immediately. However, you'll need to restart the container to see changes in dependencies.

### Hot Reload Development

1. **Start the container**:
   ```bash
   ./run-container.sh
   ```

2. **Make changes to your code**

3. **Restart the container** to see changes:
   ```bash
   podman stop adas-dashboard
   ./run-container.sh
   ```

## Container Management

### List running containers
```bash
podman ps
```

### Stop the container
```bash
podman stop adas-dashboard
```

### Remove the image
```bash
podman rmi adas-dashboard
```

### View container logs
```bash
podman logs adas-dashboard
```

### Execute commands in running container
```bash
podman exec -it adas-dashboard bash
```

## Security Considerations

- The container runs as a non-root user (appuser)
- X11 permissions are temporarily opened for local connections only
- The container uses host networking for simplicity
- Consider using podman-compose for production deployments

## Performance Tips

- Use `--no-cache` flag when rebuilding if you suspect cache issues
- The container includes all necessary PyQt6 dependencies
- Consider using multi-stage builds for smaller production images
- Use volume mounts for persistent data storage

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your system meets the prerequisites
3. Check the application logs: `podman logs adas-dashboard`
4. Ensure X11 is properly configured on your system 