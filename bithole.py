#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import logging

import subprocess
from multiprocessing import Pool
from functools import partial
import cProfile
import pstats
import random
import logging

import datetime


def execute(command, log_path=None):
    """
    Executes a command in a subprocess with output handled similar to tee. Output
    goes to STDOUT and an optional log path.

    :param command: The command to run as a single string. Not split.
    :param log_path: Path of file to log output to.
    :return: The exit code of the subprocess
    """
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        next_line = process.stdout.readline()
        if next_line == b'' and process.poll() is not None:
            break
        sys.stdout.write(str(next_line, encoding='utf-8'))
        sys.stdout.flush()
        if log_path:
            with open(log_path, 'a') as logfile:
                logfile.write(str(next_line, encoding='utf-8'))

    exit_code = process.returncode
    return exit_code


def puzzle(args):
    logger = logging.getLogger()
    log_dir = f'{os.getcwd()}/logs'

    try:
        os.mkdir(log_dir)
        logger.info(f'Created log directory {log_dir}')
    except FileExistsError:
        logger.info(f'Log directory exists: {log_dir}')

    transactions = []
    with open('puzzle_transactions.csv', 'r') as transaction_file:
        reader = csv.DictReader(transaction_file)
        for line in reader:
            transactions.append(line)

    bits_entropy = args.num_bits - 1  # high bit is always on
    bits_batch_size = args.batch_size
    target_addr = transactions[bits_entropy]['address']

    bitcrack_path = f'/home/chris/projects/bithole/cuBitCrack'

    while True:
        # Note the start of the batch
        start = datetime.datetime.now()

        # Choose a random batch
        num_batches = 2 ** (bits_entropy - bits_batch_size)
        batch_num = random.randint(0, num_batches)
        print(f'Selected batch {batch_num} out of {num_batches}')

        # Calculate private key start and finish for the batch
        start_key = (2 ** bits_entropy) + (2 ** bits_batch_size * batch_num)
        end_key = (2 ** bits_entropy) + (2 ** bits_batch_size * (batch_num + 1))

        # Build the bitcrack command
        cmd = f'{bitcrack_path} -b 160 -t 256 -p 512 -f --keyspace {hex(start_key)}:{hex(end_key)} {target_addr}'

        # Execute bitcrack
        execute(cmd, log_path=f'{log_dir}/batch{batch_num}_{bits_entropy}-{bits_batch_size}.log')

        # Note the time when the batch finished
        end = datetime.datetime.now()
        print(f'Took {end - start} to finish.')

    #
    #     with open(f'{log_dir}batches_record_{bits_entropy}-{bits_batch_size}.txt', 'a+') as record:
    #         record.write(f'{batch_number}\n')
    #

    #
    #     cmd = f'/home/chris/projects/fruitbrute/cuBitCrack -b 160 -t 256 -p 512 -f --keyspace {hex(start_key)}:{hex(end_key)} {target_addr}'
    #     print(cmd)
    #
    #     import subprocess
    #     import sys
    #     with open('test.log', 'wb') as f:  # replace 'w' with 'wb' for Python 3
    #         process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #         for line in iter(process.stdout.readline, b''):  # replace '' with b'' for Python 3
    #             sys.stdout.write(str(line, encoding='utf-8'))
    #             f.write(line)
    #
    #     completed = subprocess.run(cmd.split(' '), capture_output=True)
    #     with open(f'{log_dir}batch_{batch_number}_{bits_entropy}-{bits_batch_size}.stderr', 'w') as stderr_log:
    #         stderr_log.write(str(completed.stderr, encoding='ascii'))
    #     with open(f'{log_dir}batch_{batch_number}_{bits_entropy}-{bits_batch_size}.stdout', 'w') as stdout_log:
    #         stdout_log.write(str(completed.stdout, encoding='ascii'))
    #     print(f'Batch {batch_number} took {end - start} to finish.')
    #
    # print(2 ** bits_entropy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    puzzle_parser = subparsers.add_parser('puzzle',
                                          help='Batch up a bitcoin puzzle transaction and execute in bitcrack.',
                                          func=puzzle)
    puzzle_parser.add_argument('--num-bits',
                               required=True,
                               dest='num_bits',
                               type=int,
                               help='Bit length of the key')
    puzzle_parser.add_argument('--batch-size',
                               required=True,
                               dest='batch_size',
                               type=int,
                               help='Power of 2 to use for the batch size, eg. 40 = 2^40.')

    brain_parser = subparsers.add_parser('brain',
                                         help='Search for brain wallets.')

    parsed_args = parser.parse_args()
    parsed_args.func(parsed_args)
