FROM python:3.9

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    wget \
    nginx \
    ca-certificates

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN pip install gunicorn
RUN pip install Flask==2.1.2
RUN pip install Flask_SQLAlchemy==2.5.1
RUN pip install python-dotenv==0.20.0
RUN pip install SQLAlchemy==1.4.36
RUN pip install psycopg2==2.9.3


# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Set up the program in the image
COPY app.py /opt/program/app.py
WORKDIR /opt/program

EXPOSE 5000

CMD ["gunicorn", "--timeout", "200", "-b", "0.0.0.0:5000", "app:app"]