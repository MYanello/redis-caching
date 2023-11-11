FROM python:3.12-bookworm

WORKDIR /opt/
ADD ./src /opt/src
ADD ./tests /opt/tests

RUN useradd --shell /bin/bash -m bookworm 
RUN chown -R bookworm:bookworm /opt/
USER bookworm

RUN pip3 install --upgrade pip
ADD ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt


EXPOSE 9999
ENTRYPOINT [ "python3" ]
CMD [ "src/app.py"]
