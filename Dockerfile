FROM python:3.11-bookworm

RUN pip install --progress-bar off --upgrade pip

WORKDIR /app
# 将/app添加到PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"
COPY . /app

RUN pip install --progress-bar off --no-cache-dir -r githubgather/requirements.txt

EXPOSE 9000
CMD ["uvicorn", "githubgather.main:app", "--host", "0.0.0.0", "--port", "9000"]