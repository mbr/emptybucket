#!/usr/bin/env python
# coding=utf8

import argparse
from getpass import getpass
from Queue import Queue
from threading import Thread
import sys
import time

import boto
import progressbar

parser = argparse.ArgumentParser()
parser.add_argument('bucket')
parser.add_argument('--key', default=None)
parser.add_argument('--secret-key', default=None)
parser.add_argument('--num-threads', default=64, type=int)

args = parser.parse_args()

key = args.key
secret_key = args.secret_key

if not key:
    sys.stdout.write('Enter AWS Key: ')
    sys.stdout.flush()
    key = sys.stdin.readline()[:-1]
    print "Using key", key

if not secret_key:
    secret_key = getpass('Enter secret key for %s: ' % key)

print 'Connecting to bucket "%s"' % args.bucket
s3 = boto.connect_s3(key, secret_key)
bucket = s3.get_bucket(args.bucket)

key_queue = Queue()
pbar = progressbar.ProgressBar(
    widgets=['Retrieving keys: ', progressbar.Counter()],
    maxval=progressbar.UnknownLength
)

pbar.start()
total_keys = 0
last_refresh = time.time()
for k in bucket.list():
    key_queue.put(k)
    total_keys += 1

    # update progress
    cur_time = time.time()
    if cur_time - last_refresh > 0.1:
        last_refresh = cur_time
        pbar.update(total_keys)
pbar.finish()

print 'Bucket has %d keys, deleting with %d threads' % (total_keys,
                                                        args.num_threads)
def delete_keys():
    while True:
        k = key_queue.get()
        k.delete()

threads = []
for i in xrange(args.num_threads):
    t = Thread(target=delete_keys)
    t.daemon = True
    t.start()

pbar = progressbar.ProgressBar(
    widgets=['Deleting keys: ', progressbar.SimpleProgress(),
             progressbar.Bar(marker='#', left='[', right=']'),
             progressbar.ETA()],
    maxval=total_keys)

if total_keys:
    pbar.start()
    while True:
        remain = key_queue.qsize()
        pbar.update(total_keys-remain)
        time.sleep(0.5)

        if not remain:
            break

    pbar.finish()

print "Deleting bucket"
bucket.delete()
