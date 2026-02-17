# set the base image to create the image for react app
FROM ubuntu:latest

# set the maintainer of the image
LABEL maintainer="Name <me.email@example.com>"

# set the working directory in the container
WORKDIR /app

# install dependencies
RUN apt-get update

# install dependencies for flutter
RUN apt-get install -y curl git unzip zip
# install flutter
RUN curl https://storage.googleapis.com/flutter_infra/releases/stable/linux/flutter_linux_1.22.2-stable.tar.xz | tar -xf -
# add flutter to path
ENV PATH "$PATH:/flutter/bin"

# run flutter doctor to check if everything is set up correctly
RUN flutter doctor

# copy the project files to the container
COPY . /app

# build the flutter app
RUN flutter build apk --release

# set the command to run the app
CMD ["flutter", "run"]