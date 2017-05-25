FROM python:3.5
MAINTAINER osayamen <mailbuddie@gmail.com>

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

RUN mkdir -p /app
RUN apt-get clean &&  apt-get autoremove
# Update APT repository
RUN apt-get -y update

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt

VOLUME ["/data"]

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*