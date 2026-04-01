FROM python:3.11-slim
WORKDIR /app
COPY test.py /app/
RUN pip install flask
CMD ["python", "-m", "flask", "--app", "test.py", "run", "--host=0.0.0.0", "--port=8000"]

