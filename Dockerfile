FROM python:3.11
LABEL authors="Flemyng"
COPY ACC .
WORKDIR /AAC
COPY . .
RUN pip install -r requirements.txt
RUN conda install GDAL
CMD ["python", "multiprocess.py"]