FROM python:3.12-slim

WORKDIR /app
COPY server.py storefront.py ./

ENV PYTHONUNBUFFERED=1 \
    PORT=5000

EXPOSE 5000

CMD ["python", "server.py"]
