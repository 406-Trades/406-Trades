def log(msg, label=''):
    import datetime, time
    _msg = str(label) + ': ' + str(msg) + '\n'
    with open('tmp\mylog', 'a') as mypylib:
        mypylib.write(_msg)