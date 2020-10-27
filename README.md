# Device Info

device info

# Install

    pip install -r requirements.txt

# Run

### server

    daphne device_info.asgi:application -b 127.0.0.1 -p 9000

### client

    python -m client.client 127.0.0.1 testtoken --port 9000