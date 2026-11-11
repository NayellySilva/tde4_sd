FROM python:3.12-slim

WORKDIR /lb
COPY algorithms.py balancer.py ./

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

CMD ["python", "balancer.py"]
