import threading

import pika
import sys
import json


def load_rabbit_config(key, config_path='./configMaster.json'):

    with open(config_path) as fp:
        config = json.load(fp)

    if key not in config:
        raise ValueError("{} is not found in {}".format(key, config_path))

    port = config['port']
    host = config['host']
    required = ['id', 'url', 'data']

    rabbit = {
        'in': Channel(host, port, config[key]['in_q']),
        'out': Channel(host, port, config[key]['out_q']),
        'log': Channel(host, port, config['log_q']),
        'progress': Channel(host, port, config['progress_q']),
        'error': Channel(host, port, config['error_q'])
    }

    return required, rabbit


class Channel:
    def __init__(self, host, port, queue):
        self.host = host
        self.port = port
        self.queue = queue
        self.connection = self.connect()
        self.channel = None
        self.create_channel()
        sys.stdout.write('✓ Channel: {}:{}/{}\n'.format(host, port, queue))
        sys.stdout.flush()
        self.connectionTries = 0

    def connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port, heartbeat=0))
        return connection

    def check_connection(self):
        if self.connection.is_open:
            return True
        else:
            return False

    def create_channel(self):
        if self.check_connection():
            channel = self.connection.channel()
            channel.queue_declare(queue=self.queue, durable=False)
            channel.confirm_delivery()
            channel.basic_qos(prefetch_count=1)
            self.channel = channel
        else:
            self.connection = self.connect()
            self.create_channel()

    def subscribe(self, user_callback):
        def callback_with_ack(ch, method, properties, body):
            print("Received: %r" % ch, method, properties, body)
            if user_callback(body):
                print("Done")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print("Message failed")

        self.channel.basic_consume(queue=self.queue, on_message_callback=callback_with_ack, auto_ack=False)
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()
        thread.join(0)

    def publish(self, body):
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queue, body=str(body),
                                       properties=pika.BasicProperties(
                                           content_type='text/plain',
                                           delivery_mode=2),
                                       mandatory=True)
            self.connectionTries = 0
        except Exception as e:
            sys.stdout.write(str(e) + '\n')
            sys.stdout.write(F'Try number: {str(self.connectionTries)}\n')
            sys.stdout.flush()
            if self.create_channel():
                self.put(body)

    def close_channel(self):
        self.channel.close_channel()

