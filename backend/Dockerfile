FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY . ${LAMBDA_TASK_ROOT}/

# Pre-download YuNet model into the container for fast cold starts
RUN python -c "from services.face_detector import ensure_model; ensure_model()"

CMD ["handler.handler"]
