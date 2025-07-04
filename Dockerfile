# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Build arguments for dynamic user
ARG USER_ID=1000
ARG GROUP_ID=1000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1

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

# Add entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create group and user with dynamic UID/GID
RUN groupadd -g $GROUP_ID appgroup && \
    useradd -m -u $USER_ID -g $GROUP_ID appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expose port (if needed for future web interface)
EXPOSE 8080

# Use entrypoint for dynamic env/user setup
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"] 