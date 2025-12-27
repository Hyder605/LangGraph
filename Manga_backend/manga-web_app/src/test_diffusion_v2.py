import requests
import base64
from PIL import Image
from io import BytesIO

# Your running FastAPI diffusion server endpoint
server_url = "http://203.241.228.97:9000/generate"

def generate_image(prompt: str, server_url: str = server_url):
    """
    Sends a text prompt to a remote diffusion server and returns the generated image (in-memory).

    Args:
        prompt (str): Text description to send to the diffusion model.
        server_url (str): The URL of your diffusion server's API endpoint.

    Returns:
        PIL.Image.Image: The generated image.
    """
    try:
        # Send request to the diffusion server
        response = requests.post(server_url, json={"prompt": prompt})
        response.raise_for_status()

        data = response.json()
        if "image_base64" not in data:
            raise ValueError("No 'image_base64' field found in server response.")

        # Decode the base64 image
        image_data = base64.b64decode(data["image_base64"])
        image = Image.open(BytesIO(image_data))

        print("✅ Image generated successfully (in memory).")
        
        return image  # 👈 return the image instead of saving it

    except Exception as e:
        print(f"❌ Error generating image: {e}")
        raise





# import requests
# import base64
# from PIL import Image
# from io import BytesIO

# server_url = "http://203.241.228.97:9000/generate"  # 👈 replace with your server IP

# prompt = """
# Crowded schoolyard, bright daylight. Ibad_001, A lanky teenage boy with messy black hair tripping over his feet in a schoolyard, blushing. He has wide, expressive brown eyes., sees Aisha_002, A slender teenage girl with long brown hair and sparkling blue eyes smiling gently in a schoolyard. She is wearing a neat school uniform., who is glowing slightly. A large heart with the sound effect "POW!" bursts near Ibad_001's head. Ibad_001 thinks: "She's...an angel!" in consistent manga style
# """

# response = requests.post(server_url, json={"prompt": prompt})
# data = response.json()

# # Decode and save the returned image
# image_data = base64.b64decode(data["image_base64"])
# image = Image.open(BytesIO(image_data))
# image.save("generated_from_server.png")

# print("✅ Image received and saved as generated_from_server.png")

