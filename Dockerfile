FROM python:3.6.4-stretch

WORKDIR /usr/artis

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["chmod", "+x", "run.sh"]
CMD ./run.sh