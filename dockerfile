FROM python:3.12.0-bookworm

WORKDIR /opt/
ADD ./src /opt/src
ADD ./tests /opt/tests

RUN useradd -m bookworm
RUN chown -R bookworm:bookworm /opt/
USER bookworm

RUN pip3 install --upgrade pip
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
ADD ./requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt


EXPOSE 9999
ENTRYPOINT [ "python3" ]
CMD ["src/app.py"]