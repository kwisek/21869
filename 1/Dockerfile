FROM continuumio/miniconda3:latest

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY conda-env.yml ./conda-env.yml
RUN conda env create -f ./conda-env.yml

COPY app ./app
COPY main.py ./main.py

EXPOSE 8000

CMD ["conda", "run", "--no-capture-output", "-n", "kalimba", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]