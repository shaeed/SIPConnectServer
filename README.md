[![Build Status](https://github.com/shaeed/SIPConnectServer/actions/workflows/python-app.yml/badge.svg)](https://github.com/shaeed/SIPConnectServer/actions/workflows/python-app.yml)

# SIPConnectServer

**SIPConnectServer** is a lightweight SIP (Session Initiation Protocol) server designed to handle SIP registrations, proxy calls, and integrate easily with VoIP clients and gateways.  
This project aims to provide a simple, configurable solution for SIP-based voice communication in a local environment (to be used with VPN).

---

## Features

✅ SIP registration handling  
✅ Call proxying and routing  
✅ Simple configuration  
✅ Compatible with standard SIP clients (Zoiper, Linphone, softphones, etc.)  
✅ Extensible for integration with Asterisk, FreeSWITCH, or other VoIP infrastructure

---

## Table of Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Getting Started

These instructions will help you get a copy of **SIPConnectServer** up and running on your local machine or server.

---

## Prerequisites

- **Python 3.8+**
- **Docker** (for containerized deployment)
- Dongle with SIM card

---

## Installation

Clone the repository:

```bash
git clone https://github.com/shaeed/SIPConnectServer.git
cd SIPConnectServer
```
Install dependencies:
```bash
pip install -r requirements.txt
```
---

## Usage

To start the server, run:

```bash
uvicorn app/main:app --reaload
```
Or use the provided Dockerfile to build and run a container:

```bash
docker build -t sipconnectserver .
docker run -d -p 5060:5060/udp sipconnectserver
```
By default, the server listens on UDP port 5060 — the standard SIP port.

---

## Contributing

Contributions, issues, and feature requests are welcome!

    Fork the repository

    Create your feature branch (git checkout -b feature/awesome-feature)

    Commit your changes (git commit -m 'Add some feature')

    Push to the branch (git push origin feature/awesome-feature)

    Open a Pull Request

## License

This project is licensed under the MIT License — see LICENSE for details.

## Author

Maintained by Shaeed Khan.

