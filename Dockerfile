# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

# PODMAN_SOCKET_PATH will be set at runtime via docker-compose or run-container.sh
# This allows for dynamic user ID detection

# Optionally, you can document in the Dockerfile how to mount the socket when running the container:
# Example:
#   podman run -v /run/user/$(id -u)/podman/podman.sock:/run/user/$(id -u)/podman/podman.sock:rw \
#     -e PODMAN_SOCKET_PATH=/run/user/$(id -u)/podman/podman.sock ...

# Install system dependencies for PyQt6 and X11
RUN apt-get update && apt-get install -y \
    libegl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xkb1 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libxi6 \
    libasound2 \
    libpulse0 \
    libpulse-mainloop-glib0 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgirepository-1.0-1 \
    libnotify4 \
    libnss3 \
    libdrm2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libfontconfig1 \
    libfreetype6 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libxcb-util1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (this layer will be cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytz

# Copy resources directory into container (will be container-local, not mounted from host)
COPY resources/ ./resources/

# Create a non-root user with UID 1000 for proper UID mapping
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

# Expose port (if needed for future web interface)
EXPOSE 8080

# Set the default command
CMD ["python", "main.py"] 