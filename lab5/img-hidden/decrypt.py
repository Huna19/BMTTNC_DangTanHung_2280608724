import sys
from PIL import Image

def decode_image(encoded_image_path):
    img = Image.open(encoded_image_path)
    width, height = img.size
    binary_message = ""
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))

            for color_channel in range(3):
                binary_message += format(pixel[color_channel], '08b')[-1]

    message = ""
    # The image shows '1111111111111110' as an end marker.
    # The code below is trying to decode based on a null character ('\0').
    # I will adapt it to search for the end marker from the encoding function.
    end_marker = '1111111111111110'
    end_marker_found = False

    # Process binary message in 8-bit chunks (bytes)
    for i in range(0, len(binary_message) - len(end_marker) + 1, 8):
        # Check if the end marker is found
        if binary_message[i:i + len(end_marker)] == end_marker:
            end_marker_found = True
            break
        
        # Extract 8 bits and convert to character
        byte_chunk = binary_message[i:i+8]
        if len(byte_chunk) == 8: # Ensure we have a full byte
            char_code = int(byte_chunk, 2)
            message += chr(char_code)
        else:
            # Handle cases where the last chunk might be incomplete (if no end marker)
            # or if the loop runs past the actual message end.
            break # Stop if it's not a full byte and no end marker was found before

    return message

def main():
    if len(sys.argv) != 2:
        print("Usage: python decrypt.py <encoded_image_path>")
        return

    encoded_image_path = sys.argv[1]
    decoded_message = decode_image(encoded_image_path)
    print("Decoded message:", decoded_message)

if __name__ == "__main__":
    main()