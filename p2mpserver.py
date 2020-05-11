from socket import *
import random
import sys

def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0"

    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = add_carry_around(s, w)
    return ~s & 0xffff

def add_carry_around(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def is_message_error_free(message):
    data = message[64:]
    to_check = checksum(data)
    while len(str(to_check)) != 16:
        to_check = '0' + str(to_check)
    # print 'The local checksum value is: ' + to_check
    if to_check == message[32:48]:
        return True
    else:
        return False

def write_message_to_file(w_file, message):
    with open(w_file, 'a+') as f:
        f.write(message[64:])
        f.close()
if __name__ == '__main__':

    r_port = int(sys.argv[1])
    w_file = str(sys.argv[2])
    loss = float(sys.argv[3])

    ServerSocket = socket(AF_INET, SOCK_DGRAM)
    address = ('', r_port)
    ServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ServerSocket.bind(address)

    open(w_file, 'w').close()
    print 'Server open now'
    required_sequence = 0
    while 1:
        message, clientAddress = ServerSocket.recvfrom(2048)
        print(clientAddress)
        random_number = random.uniform(0, 1)
        received_sequence = message[0:32]
        if random_number > float(loss):
            if message[48:64] == '0101010101010101':
                if required_sequence == int(received_sequence, 2):
                    if is_message_error_free(message):
                        write_message_to_file(w_file, message)
                        ServerSocket.sendto('ack', clientAddress)
                        required_sequence += 1
                #old packet retransmitted, so just send ack
                elif int(received_sequence, 2) < required_sequence:
                    ServerSocket.sendto('ack', clientAddress)
                    continue
                else:
                #do nothing because we received a sequence number higher than what we exxpected
                    continue
        else:
            print 'dropped sequence: ' + str(received_sequence)


