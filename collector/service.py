from datetime import datetime
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
from dotenv import load_dotenv
from typing import List
from typing import Dict
from schema import CollectorFrame


app = FastAPI()

load_dotenv()
logger = logging.getLogger(__name__)

image_analysis_url = os.getenv("IMAGE_ANALYSIS_URL")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

collector_frames_list = []
image_analysis_frames_list = []


def updated_frame(frame_dict: Dict) -> Dict:

    collector_frame = CollectorFrame(**frame_dict)
    frame_dict = collector_frame.model_dump()

    filtered_fields = {}

    for key, value in frame_dict.items():
        if value is not None and value != "":
            filtered_fields[key] = value

    return filtered_fields


def forward_to_image_analysis(body_dict):
    try:
        timestamp = datetime.today().isoformat()
        body_dict["timestamp"] = timestamp
        response = httpx.post(image_analysis_url + "/frame", json=body_dict)
        response.raise_for_status()
        return response

    except httpx.HTTPError as e:
        logger.error("Image analysis service error: %s", e.response.text)
        raise HTTPException(status_code=e.response.status_code,
                            detail="Image analysis service error")

    except Exception as e:
        logger.error("Error during frame forwarding: %s", str(e))
        return None  # Return None in case of an exception


@app.post("/frame", status_code=status.HTTP_201_CREATED)
def create_frames(payload: CollectorFrame):

    frame_dict = payload.model_dump()
    updated_payload = updated_frame(frame_dict)

    collector_frames_list.append(frame_dict)

    response = forward_to_image_analysis(updated_payload)
    print(response.json())

    if response.status_code == status.HTTP_200_OK:
        image_analysis_frames_list.append(response.json())
        return {"message": "Frame added successfully"}
    else:
        return {"message": "Frame forwarding failed"}


@app.get("/frames", response_model=List[CollectorFrame])
def get_frames():
    return collector_frames_list


@app.get("/imageAnalysisFrames")
def get_frames():
    return image_analysis_frames_list
