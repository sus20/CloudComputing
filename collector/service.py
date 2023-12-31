from datetime import datetime
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
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

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set up Prometheus instrumentation for FastAPI,
#  adding middleware and exposing /metrics endpoint.
Instrumentator().instrument(app).expose(app)

image_analysis_url = os.getenv("IMAGE_ANALYSIS_URL")
face_recognition_url = os.getenv("FACE_RECOGNITION_URL")
alert_url = os.getenv("ALERT_URL")
section_url = os.getenv("SECTION_URL")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def forward_request(url: str, json_data: Dict) -> httpx.Response:
    try:
        timestamp = datetime.today().isoformat()
        json_data["timestamp"] = timestamp
        response = httpx.post(url, json=json_data)
        response.raise_for_status()
        logger.info(f"Request successfully forwarded to {url}")
        return response

    except httpx.HTTPError as e:
        logger.error(f"Service error: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"Service error: {url}")
    except Exception as e:
        logger.error(f"Error during request forwarding: {str(e)}")
        return None


def updated_frame(frame_dict: Dict) -> Dict:

    collector_frame = CollectorFrame(**frame_dict)
    frame_dict = collector_frame.model_dump()

    filtered_fields = {}

    for key, value in frame_dict.items():
        if value is not None and value != "":
            filtered_fields[key] = value

    return filtered_fields


def forward_to_image_analysis(payload):
    updated_payload = updated_frame(payload)
    return forward_request(image_analysis_url + "/frame", updated_payload)


def forward_to_face_recognition(json_dict):
    updated_json_data = updated_frame(json_dict)
    return forward_request(face_recognition_url + "/frame", updated_json_data)


def forward_to_alert(json_dict):
    return forward_request(alert_url + "/alerts", json_dict)


def forward_to_section(json_dict):
    return forward_request(section_url + "/persons", json_dict)


@app.post("/frame", status_code=status.HTTP_201_CREATED)
def create_frames(payload: CollectorFrame):

    frame_dict = payload.model_dump()
    image_res = forward_to_image_analysis(frame_dict)

    if not image_res or image_res.status_code != status.HTTP_200_OK:
        return {"message": "Frame forwarding to image analysis failed"}

    fr_res = forward_to_face_recognition(image_res.json())

    if not fr_res or fr_res.status_code != status.HTTP_200_OK:
        section_res = forward_to_section(image_res.json())

        if section_res and section_res.status_code == status.HTTP_200_OK:
            return {"message": "Person added to section "}
        else:
            return {"message": "Frame forwarding to section service failed"}

    fr_res_data = fr_res.json()

    if "known-persons" in fr_res_data:
        alert_response = forward_to_alert(fr_res_data)

        if alert_response and alert_response.status_code == status.HTTP_200_OK:
            return {"message": "Forwarding to alert successful! "}
        else:
            return {"message": "Forwarding to alert service failed"}

    return {"message": "Frame forwarding to face recognition failed"}
