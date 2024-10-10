FROM locustio/locust
RUN pip3 install websockets locust-plugins locust-plugins[websocket]