from PIL import Image
from colorthief import ColorThief
from PIL import Image, ImageSequence
from colorthief import ColorThief

def extract_dominant_color(image_path):
    img = Image.open(image_path)
    colors = []

    for frame in ImageSequence.Iterator(img):
        # Resize each frame to speed up color analysis
        resized_frame = frame.resize((100, 100))

        # Create a ColorThief object for the frame
        color_thief = ColorThief(resized_frame)

        # Get the dominant color as a tuple (R, G, B) for the frame
        dominant_color = color_thief.get_color(quality=1)
        colors.append(dominant_color)

    return colors

# Replace 'your_image.gif' with the path to your GIF file
image_path = 'static/images/astronaut.gif'
dominant_colors = extract_dominant_color(image_path)

print("Dominant Colors in each frame:")
for i, color in enumerate(dominant_colors):
    print(f"Frame {i + 1}: {color}")
