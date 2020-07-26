import os

from flask import Flask, request
from queutils import load_rabbit_config
from callbacks import return_output, transfer_in_out
from sys import stdout

# create a threadpool with 4 threads, for the 4 channels we have
# pool = ThreadPoolExecutor(max_workers=4)
app = Flask(__name__)

file_name = os.path.basename(__file__[:-3])
required_fields, rabbit = load_rabbit_config(file_name)


@app.route('/', methods=['GET'])
def get_request():
    return "Server Alive!"


@app.route('/', methods=['POST'])
def post_request():
    data_dict = request.get_json()

    # validate required fields
    response_error = ''
    for key in required_fields:
        if key not in data_dict:
            response_error += "key '" + key + "' is missing\n"

    if response_error != '':
        # pool.submit(rabbit['error'].put, "Invalid request\n" + response_error)
        rabbit['error'].publish("Invalid request\n" + response_error)
        stdout.write("request rejected\n")
        stdout.flush()
        return "Invalid request\n" + response_error, 422

    # send the message to rabbitMQ in_q
    rabbit['in'].publish(data_dict)
    stdout.write("request accepted\n")
    stdout.flush()
    return "Request accepted, Result will be sent to: {} when ready".format(data_dict['url'])


@app.route('/callback', methods=['GET', 'POST'])
def get_callback():
    data_dict = request.get_json()
    stdout.write("callback: " + str(data_dict))
    stdout.flush()
    return "callback: " + str(data_dict)


@app.route('/flush', methods=['GET'])
def get_flush():
    rabbit['in'].subscribe(transfer_in_out)
    return "flushing"


def transfer_in_out(body):
    rabbit['out'].publish(body)
    return True


if __name__ == '__main__':

    # listen to messages from output channel and progress channel
    rabbit['out'].subscribe(return_output)
    # rabbit['progress'].subscribe(return_progress)

    # start the server
    app.run(port=5000)
