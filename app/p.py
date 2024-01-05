import socket

def get_ip_address():
    try:
        # Get the hostname of the local machine
        hostname = socket.gethostname()

        # Get the IP address associated with the local machine's hostname
        ip_address = socket.gethostbyname(hostname)

        return ip_address
    except socket.error as e:
        print(f"Error: {e}")
        return None

# Get and print the IP address
ip_address = get_ip_address()

if ip_address:
    print(f"IP Address: {ip_address}")
else:
    print("Unable to retrieve IP address.")
