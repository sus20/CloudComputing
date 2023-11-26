FROM python:3.9.7

# Use build-time arg to set default values
ARG IMAGE_ANALYSIS_URL="http://image-analysis:80"
ARG FACE_RECOGNITION_URL="http://face-recognition:80"
ARG ALERT_URL="http://alert:80"
ARG SECTION_URL="http://section:80"

# Set runtime environment variables with the default values
ENV IMAGE_ANALYSIS_URL=${IMAGE_ANALYSIS_URL} \
    FACE_RECOGNITION_URL=${FACE_RECOGNITION_URL} \
    ALERT_URL=${ALERT_URL} \
    SECTION_URL=${SECTION_URL}

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "80"]
