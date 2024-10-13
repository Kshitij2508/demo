FROM python:3.9-alpine3.13

LABEL key="kshitij"
ENV PYTHONUNBUFFERED 1

# Install system dependencies and tools
RUN apk add --update --no-cache \
    python3-dev \
    postgresql-client \
    postgresql-dev jpeg-dev \
    build-base zlib zlib-dev linux-headers\
    musl-dev \
    py3-setuptools \
    && python3 -m ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools wheel

# Create a virtual environment
RUN python3 -m venv /py

# Set the virtual environment in the path
ENV PATH="/scripts:/py/bin:$PATH"

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Install Python dependencies as root
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Conditional install for development dependencies
ARG DEV=false
RUN if [ "$DEV" = "true" ]; then pip install -r /tmp/requirements.dev.txt; fi

# Copy the application code
COPY ./app /app
COPY ./scripts /scripts
WORKDIR /app

# Create a non-root user for security
RUN adduser --disabled-password django-user

# Create necessary directories and adjust ownership
RUN mkdir -p /vol/web/media /vol/web/static && \
    chown -R django-user:django-user /vol/web/media /vol/web/static && \
    chmod -R +x /scripts
# Switch to the non-root user
USER django-user

# Expose the necessary port
EXPOSE 8000

# Default command
CMD ["run.sh"]
