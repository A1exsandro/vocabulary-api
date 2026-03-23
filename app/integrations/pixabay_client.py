import requests
import os
from fastapi import HTTPException

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


def fetch_image_from_pixabay(query: str) -> bytes:
    """
        MELHORIAS
        - [ ] Fornecer um array de imagens para o usuário escolher uma
    """

    if not PIXABAY_API_KEY:
        raise HTTPException(status_code=500, detail="PIXABAY_API_KEY not configured")

    url = "https://pixabay.com/api/"

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 3,
        "safesearch": "true",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch image metadata")

    data = response.json()

    if not data.get("hits"):
        raise HTTPException(status_code=404, detail="No image found")

    image_url = data["hits"][0]["largeImageURL"]

    img_response = requests.get(image_url)

    if img_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download image")

    return img_response.content