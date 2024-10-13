# Use the unprivileged Nginx base image
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="kshitij"

# Copy configuration files and scripts
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /scripts/run.sh

# Set environment variables
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# Switch to root to perform administrative tasks
USER root

# Create necessary directories, set permissions, and adjust ownership
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /scripts/run.sh


# Define a volume for static files
VOLUME /vol/static

# Switch back to the nginx user
USER nginx

# Define the default command to run the script
CMD ["scripts/run.sh"]


