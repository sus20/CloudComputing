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
face_recognition_url = os.getenv("FACE_RECOGNITION_URL")

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
face_recognition_frames_list = []


def updated_frame(frame_dict: Dict) -> Dict:

    collector_frame = CollectorFrame(**frame_dict)
    frame_dict = collector_frame.model_dump()

    filtered_fields = {}

    for key, value in frame_dict.items():
        if value is not None and value != "":
            filtered_fields[key] = value

    return filtered_fields


def forward_request(url: str, json_data: Dict) -> httpx.Response:
    try:
        timestamp = datetime.today().isoformat()
        json_data["timestamp"] = timestamp
        response = httpx.post(url, json=json_data)
        response.raise_for_status()
        return response
    except httpx.HTTPError as e:
        logger.error(f"Service error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"Service error: {url}")
    except Exception as e:
        logger.error(f"Error during request forwarding: {str(e)}")
        return None


def forward_to_image_analysis(body_dict):
    return forward_request(image_analysis_url + "/frame", body_dict)


def forward_to_face_recognition(json_data):
    updated_json_data = updated_frame(json_data)
    return forward_request(face_recognition_url + "/frame", updated_json_data)


@app.post("/frame", status_code=status.HTTP_201_CREATED)
def create_frames(payload: CollectorFrame):
    frame_dict = payload.model_dump()
    updated_payload = updated_frame(frame_dict)

    collector_frames_list.append(frame_dict)

    response = forward_to_image_analysis(updated_payload)

    # Ensure the response object exists, is not None, and has an okay status code.
    if response and response.status_code == status.HTTP_200_OK:
        image_analysis_frames_list.append(response.json())

        face_recognition_response = forward_to_face_recognition(
            response.json())

        if face_recognition_response and face_recognition_response.status_code == status.HTTP_200_OK:
            face_recognition_frames_list.append(
                face_recognition_response.json())
            return {"message": "Frame added successfully"}
        else:
            return {"message": "Frame forwarding to face recognition failed"}
    else:
        return {"message": "Frame forwarding failed"}


@app.get("/frames", response_model=List[CollectorFrame])
def get_frames():
    return collector_frames_list


@app.get("/imageAnalysisFrames")
def get_frames():
    return image_analysis_frames_list


@app.get("/faceRecognitionFrames")
def get_frames():
    return face_recognition_frames_list
