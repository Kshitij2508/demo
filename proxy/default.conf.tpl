server {
    listen ${LISTEN_PORT};
    server_name localhost;

    location /static/ {
        alias /vol/static/; 
    }

    location / {
        include uwsgi_params;
        uwsgi_pass app:9000;
    }
}