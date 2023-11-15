import bluetooth

def bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    bluetooth.advertise_service(server_sock, "WiFiSetupService",
                                service_id=bluetooth.read_local_bdaddr(),
                                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print(f"Waiting for connection on RFCOMM channel {port}")

    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    try:
        wifi_info = client_sock.recv(1024).decode('utf-8')
        print(f"Received Wi-Fi info: {wifi_info}")

    except OSError as e:
        print(f"Error: {e}")

    finally:
        client_sock.close()
        server_sock.close()

if __name__ == "__main__":
    bluetooth_server()
