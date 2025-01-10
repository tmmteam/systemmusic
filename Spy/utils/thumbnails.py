import os
import re
import textwrap
import random

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from Spy import app
from config import YOUTUBE_IMG_URL



# Existing Helper Functions from Your File
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)

# New Functionality: Adding Circle Profile and Rectangle Thumbnail
def add_circle_profile(background, profile_path, position, circle_size):
    profile = Image.open(profile_path)

    # Create circular mask for the profile picture
    mask = Image.new("L", profile.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, profile.size[0], profile.size[1]), fill=255)
    profile_circle = ImageOps.fit(profile, mask.size, centering=(0.5, 0.5))
    profile_circle.putalpha(mask)

    # Resize and paste profile circle on background
    profile_circle = profile_circle.resize(circle_size, Image.ANTIALIAS)
    background.paste(profile_circle, position, profile_circle)
    return background

def add_video_thumbnail(background, thumbnail_path, position, size):
    thumbnail = Image.open(thumbnail_path)
    thumbnail = thumbnail.resize(size)
    background.paste(thumbnail, position)
    return background

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        bg = Image.open(f"Spy/assets/dil.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(9))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)

        image3 = changeImageSize(1280, 720, bg)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250

        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((360, 360), Image.Resampling.LANCZOS)

        border_size = 13
        border_color = get_random_color()

        bordered_logo = Image.new("RGBA", (logo.width + 2 * border_size, logo.height + 2 * border_size), (0, 0, 0, 0))
        bordered_logo.paste(logo, (border_size, border_size))

        draw = ImageDraw.Draw(bordered_logo)
        draw.rectangle(
            [(0, 0), (bordered_logo.width - 1, bordered_logo.height - 1)],
            outline=border_color,
            width=border_size
        )

        background.paste(bordered_logo, (750, 160), bordered_logo)
        background.paste(image3, (0, 0), mask=image3)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("Spy/assets/font2.ttf", 45)
        font2 = ImageFont.truetype("Spy/assets/font2.ttf", 70)
        arial = ImageFont.truetype("Spy/assets/font2.ttf", 30)
        name_font = ImageFont.truetype("Spy/assets/font.ttf", 30)
        para = textwrap.wrap(title, width=30)
        j = 0
        draw.text((5, 5), f"SYSTEM MUSIC", fill="white", font=name_font)
        for line in para:
            if j == 1:
                j += 1
                draw.text(
                    (60, 260),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if j == 0:
                j += 1
                draw.text(
                    (60, 210),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
        draw.text(
            (20, 675),
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (60, 400),
            "00:00",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (610, 400),
            f"{duration[:23]}",
            (255, 255, 255),
            font=arial,
        )
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL

# Example of Adding Circle Profile and Video Thumbnail
def create_custom_thumbnail(background_path, video_thumbnail_path, profile_path, output_path):
    background = Image.open(background_path)
    background = add_video_thumbnail(background, video_thumbnail_path, (600, 200), (500, 250))  # Adjust position
    background = add_circle_profile(background, profile_path, (100, 150), (150, 150))  # Adjust position
    background.save(output_path)
    print(f"Custom thumbnail saved as {output_path}")

