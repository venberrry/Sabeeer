FROM python:3.12

WORKDIR /SaberManager

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
