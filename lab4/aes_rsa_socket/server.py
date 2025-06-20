from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import socket
import threading

# Khởi tạo socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

# Tạo cặp khóa RSA cho server
server_key = RSA.generate(2048)

# Danh sách client đã kết nối
clients = []

# Mã hóa tin nhắn bằng AES
def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv + ciphertext

# Giải mã tin nhắn AES
def decrypt_message(key, encrypted_message):
    iv = encrypted_message[:AES.block_size]
    ciphertext = encrypted_message[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_message.decode()

# Xử lý từng client
def handle_client(client_socket, client_address):
    print(f" Kết nối từ {client_address}")

    try:
        # Gửi public key của server cho client
        client_socket.send(server_key.publickey().export_key(format='PEM'))

        # Nhận public key của client
        client_received_key = RSA.import_key(client_socket.recv(2048))

        # Tạo khóa AES ngẫu nhiên
        aes_key = get_random_bytes(16)

        # Mã hóa khóa AES bằng public key của client
        cipher_rsa = PKCS1_OAEP.new(client_received_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)
        client_socket.send(encrypted_aes_key)

        # Lưu client
        clients.append((client_socket, aes_key))

        while True:
            try:
                encrypted_message = client_socket.recv(4096)
                if not encrypted_message:
                    break

                decrypted_message = decrypt_message(aes_key, encrypted_message)
                print(f" {client_address} gửi: {decrypted_message}")

                # Gửi lại tin nhắn cho các client khác
                for client, key in clients:
                    if client != client_socket:
                        encrypted = encrypt_message(key, decrypted_message)
                        client.send(encrypted)

                if decrypted_message.strip().lower() == "exit":
                    break

            except (ConnectionResetError, ConnectionAbortedError):
                print(f"Mất kết nối với {client_address}")
                break

    finally:
        # Xoá client ra khỏi danh sách và đóng socket
        clients.remove((client_socket, aes_key))
        client_socket.close()
        print(f" Kết thúc kết nối với {client_address}")

# Nhận kết nối từ client
print("Server đang chạy tại localhost:12345...")
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
