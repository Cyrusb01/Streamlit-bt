import re
import decorator
import numpy as np
import pandas as pd
try:
    import cPickle as pickle
except ImportError:
    import pickle




def fmtp(number):
    """
    Formatting helper - percent
    """
    if np.isnan(number):
        return '-'
    return format(number, '.2%')



def fmtpn(number):
    """
    Formatting helper - percent no % sign
    """
    if np.isnan(number):
        return '-'
    return format(number * 100, '.2f')



