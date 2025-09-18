# Best-practices Dockerfile for MarkSlideGo project
FROM python:3.12-slim

# Install system dependencies, tesseract with English and German training data, and git client
RUN apt-get update && \
    apt-get install -y curl wget sudo gnupg2 git tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Create a non-root user 
RUN useradd -ms /bin/bash msgo
USER msgo



# Install Node.js (current LTS) and MARP CLI as msgo user
ENV NVM_DIR="/home/msgo/.nvm"
ENV HOME="/home/msgo"
ENV NPM_CONFIG_CACHE="/home/msgo/.npm"
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash \
    && bash -c "source $NVM_DIR/nvm.sh && nvm install --lts && nvm install-latest-npm && npm cache clean --force && npm install -g --unsafe-perm @marp-team/marp-cli"

# Switch to root to create symlinks in /usr/bin
USER root
RUN ln -s /home/msgo/.nvm/versions/node/$(ls /home/msgo/.nvm/versions/node/ | sort -V | tail -n 1)/bin/node /usr/bin/node \
    && ln -s /home/msgo/.nvm/versions/node/$(ls /home/msgo/.nvm/versions/node/ | sort -V | tail -n 1)/bin/npm /usr/bin/npm \
    && ln -s /home/msgo/.nvm/versions/node/$(ls /home/msgo/.nvm/versions/node/ | sort -V | tail -n 1)/bin/npx /usr/bin/npx \
    && ln -s /home/msgo/.nvm/nvm.sh /usr/bin/nvm
# Switch back to msgo user for app execution
USER msgo

WORKDIR /app
# Copy only top-level files, not subdirectories
COPY *.py *.sh requirements.txt package.json README.md LICENSE /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy .env file for reference (not used for ENV, but available in container)
COPY .env /app/.env

# Set environment variables (user should override via docker-compose or runtime)
ENV TESSERACT_CMD="/usr/bin/tesseract" \
    NPX_CMD="/usr/bin/npx" \
    MARKSLIDE_DIR="/app/" \
    LOGGING_LEVEL="INFO"

CMD ["bash"]
