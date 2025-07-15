FROM debian:bullseye

# Add contrib + non-free for bullseye
#RUN echo "deb http://deb.debian.org/debian bullseye main contrib non-free" > /etc/apt/sources.list && \
#    echo "deb http://security.debian.org/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
#    echo "deb http://deb.debian.org/debian bullseye-updates main contrib non-free" >> /etc/apt/sources.list

# Install Asterisk and build tools
RUN apt-get update && \
    apt-get install -y \
    asterisk \
    asterisk-dev \
    asterisk-dahdi \
    git \
    nano \
    build-essential \
    autoconf \
    automake \
    libtool \
    libusb-1.0-0-dev \
    pkg-config \
    libsqlite3-dev \
    libjansson-dev \
    usbutils 

# Build chan_dongle & install inside astersik
WORKDIR /usr/src
RUN git clone https://github.com/wdoekes/asterisk-chan-dongle.git && \
    cd asterisk-chan-dongle && \
    ./bootstrap && \
    ./configure --with-astversion=$(asterisk -V | grep -oP '\d+\.\d+\.\d+') && \
    make && \
    make install

# Install python and other tools
RUN apt-get install -y \
    python3-pip \
    supervisor
#     && rm -rf /var/lib/apt/lists/*

# SIPConnect server
WORKDIR /app
COPY requirements.txt /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY . /app

# Start Asterisk and FastAPI with supervisord
CMD ["/usr/bin/supervisord", "-n"]
