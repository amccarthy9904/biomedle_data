import redis
import os
import io
import json
import tkinter as tk
from PIL import Image, ImageTk

# Connect to the Redis server
redis_host = 'localhost'
redis_port = 6379
redis_password = 'pass1232'
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

redis_client.delete("my_key")
# Directory containing images
img_directory = 'img'

# Function to read and add images to Redis cache
def add_images_to_redis(directory):
    for filename in os.listdir(directory):
        # Read image
        image_path = os.path.join(directory, filename)
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        # Additional JSON information
        json_info = {
            'filename': filename,
            'description': 'This is a sample description.'
        }

        # Combine image data and JSON info
        redis_value = json.dumps({'image_data': image_data.decode('latin-1'), 'json_info': json_info})

        # Add image data to Redis
        redis_key = os.path.splitext(filename)[0]  # Use filename without extension as the key
        redis_client.set(redis_key, redis_value)

        print(f"Added image '{filename}' to Redis with key '{redis_key}'")


# Function to get image from Redis cache and display in a window
def display_image_from_redis(redis_key):
    # Get data from Redis
    redis_value = redis_client.get(redis_key)

    if redis_value:
        # Parse JSON data
        data = json.loads(redis_value)

        # Extract image data and convert it back to binary
        image_data = data.get('image_data', '').encode('latin-1')
        
        if image_data:
            # Create an Image object from binary data
            image = Image.open(io.BytesIO(image_data))

            # Create a Tkinter window
            window = tk.Tk()
            window.title(f"Image for Key: {redis_key}")

            # Convert the Image object to a Tkinter PhotoImage object
            photo = ImageTk.PhotoImage(image)

            # Display the image in a label
            label = tk.Label(window, image=photo)
            label.image = photo
            label.pack()

            # Start the Tkinter main loop
            window.mainloop()
        else:
            print(f"Image data not found for key '{redis_key}' in Redis.")
    else:
        print(f"Key '{redis_key}' not found in Redis.")


# Add images to Redis cache
add_images_to_redis(img_directory)
# Example: Display image for a specific key
display_image_from_redis('country_key')