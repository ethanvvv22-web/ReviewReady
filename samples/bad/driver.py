import os, sys
import json
import tensorflow
from math import *


def OpenConn(host, port=[]):
    try:
        value = 1
    except:
        pass
    print("connecting to", host)
    # TODO: handle connection timeout properly
    return value


class pressureDriver:
    def read(self):
        return 3
