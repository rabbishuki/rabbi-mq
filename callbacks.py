from sys import stdout
import requests


# callback function for messages from output channel
def return_output(body):
    response = requests.post(body.url, json=body)
    stdout.write(response.text)
    stdout.flush()
    return True


# callback function for messages from update channel
def return_progress(body):
    response = requests.post(body.url, json=body)
    stdout.write(response.text)
    stdout.flush()
    return True

def transfer_in_out(body):
    return True