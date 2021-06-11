import delegator
import portpicker
import requests


def run(command):
    return delegator.run(command)


def free_port():
    return portpicker.pick_unused_port()


def ip():
    return requests.get('https://checkip.amazonaws.com').text.strip()
