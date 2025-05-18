from PIL import Image, ImageDraw, ImageFont
import os

# Készítsünk egy 1024x1024-es képet
img = Image.new('RGB', (1024, 1024), color='white')
d = ImageDraw.Draw(img)

# Rajzoljunk egy egyszerű szerver ikont
# Háttér
d.rectangle([(100, 100), (924, 924)], fill='#4a90e2', outline='#2171c7', width=20)

# Szerver "képernyő"
d.rectangle([(200, 200), (824, 824)], fill='#ffffff', outline='#2171c7', width=10)

# Szerver "gombok"
for y in range(300, 800, 100):
    d.ellipse([(250, y), (350, y+50)], fill='#4CAF50', outline='#2171c7', width=5)
    d.ellipse([(400, y), (500, y+50)], fill='#FFC107', outline='#2171c7', width=5)
    d.ellipse([(550, y), (650, y+50)], fill='#F44336', outline='#2171c7', width=5)

# Mentsük el
img.save('icon.png')
print("Az ikon elkészült: icon.png") 