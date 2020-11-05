import os
from datetime import datetime

def register_log(log_msg, log_dir, filename):
    log_output_dir = log_dir + filename

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    with open(log_output_dir, 'a') as log_f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f'[{now}]: {log_msg}'
        log_f.write(log_msg + '\n')
        print(log_msg)


# def foooo():
#     print('here!!')