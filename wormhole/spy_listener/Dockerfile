FROM python:3.9

# Create a non-root user and set permissions
RUN useradd -ms /bin/bash dockeruser && \
    mkdir -p /wh_spy_listener && \
    chown -R dockeruser:dockeruser /wh_spy_listener

# Switch to non-root user
USER dockeruser

WORKDIR /wh_spy_listener

# Copy only the requirements.txt first to leverage Docker cache
COPY --chown=dockeruser:dockeruser ./requirements.txt /wh_spy_listener/requirements.txt

# Install Python dependencies and switch to non-root user
RUN pip install --no-cache-dir --upgrade -r /wh_spy_listener/requirements.txt

COPY --chown=dockeruser:dockeruser ./app /wh_spy_listener/app

# Environment Variables
# Server
ENV SERVER_PORT=8000
ENV OPENAPI_URL=inject_at_deployment
ENV ENVIRONMENT=development

# Wormhole
ENV GUARDIAN_SPY_URL=inject_at_deployment
ENV SPY_SERVICE_FILTERS=inject_at_deployment
ENV RECONNECT_WAIT_TIME=2

# Database 
ENV DB_URL=inject_at_deployment

# REDIS
ENV REDIS_ZSET=inject_at_deployment
ENV REDIS_URL=inject_at_deployment

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]


