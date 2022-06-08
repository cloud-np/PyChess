# Dockerfile, Image, Container
FROM python:3.10

ADD chess/ chess/.
ADD main.py .


# List packages here
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        file        \
        gcc         \
        libwww-perl && \
    apt-get autoremove -y && \
    apt-get clean \
    apt-get zsh \
    apt-get vim

# Default powerline10k theme, no plugins installed
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)"
# Upgrade pip
RUN pip install --upgrade pip

ENV SHELL /usr/bin/zsh

ADD requirements.txt .
RUN pip install -r requirements.txt

CMD [ "python", "./main.py"]