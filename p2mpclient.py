from socket import *
import socket
import sys
import threading
import time

number_of_retransmitted_packets = 0
total_time = 0
servers = []
params = sys.argv
finalParams = []

for i in range(1, len(params)-3):
    servers.append(params[i])

for i in range(len(params) - 3, len(params)):
    finalParams.append(params[i])

port_number = finalParams[0]
name = finalParams[1]
mss = int(finalParams[2])
total_number_of_servers = len(servers)
serverDetails = [[None for x in range(3)] for y in range(total_number_of_servers)]

print("input servers are : " + str(servers))
for i in range(len(servers)):
    serverDetails[i][0] = servers[i]
    serverDetails[i][1] = port_number
    serverDetails[i][2] = 0



def read_data(seek):
    with open(name, 'rb') as fi:
        fi.seek(seek)
        data = fi.read(mss)
        seek = seek + mss
        fi.close()
        return data, seek

def rdt_send():
    global number_of_retransmitted_packets
    seek = 0  # for seeking the file
    seq = -1
    while 1:
        data, seek = read_data(seek)
        seq += 1
        if data != '':
            packet = make_packet(data, seq)
            for i in range(total_number_of_servers):
                thread = threading.Thread(target=send_one_segment, args=(serverDetails[i][0], serverDetails[i][1], packet))
                thread.daemon = True
                thread.start()
            waitForOtherServers = True
            while waitForOtherServers:
                received = 0
                for i in range(total_number_of_servers):
                    if serverDetails[i][0] is not None:
                        if serverDetails[i][2] == 1:
                            received += 1
                if received == total_number_of_servers:
                    for i in range(total_number_of_servers):
                        if serverDetails[i][0] is not None:
                            if serverDetails[i][2] == 1:
                                serverDetails[i][2] = 0
                    waitForOtherServers = False
        else:
            return

def append_zeroes(input, requiredLength):
    while len(str(input))!= requiredLength:
        input = '0' + str(input)
    return input

def make_packet(data, seq):
    check_sum = checksum(data)
    current_sequence = bin(seq)
    current_sequence = current_sequence.lstrip('0b')
    #appending zeroes in the front
    current_sequence = append_zeroes(current_sequence, 32)
    check_sum = append_zeroes(check_sum, 16)

    packet = str(current_sequence) + str(check_sum) + '0101010101010101' + data

    return packet



def add_carry_around(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0"
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i + 1]) << 8)
        s = add_carry_around(s, w)
    return ~s & 0xffff

def send_one_segment(server_ip, server_port, data):
    global total_time
    global number_of_retransmitted_packets
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time_start = time.time()
    received_ack = False
    client.settimeout(0.08)
    while received_ack is False:
        client.sendto(data, (server_ip, int(server_port)))
        try:
            ack, address = client.recvfrom(1024)
            if ack:
                time_end = time.time()
                time_diff = time_end - time_start
                total_time += time_diff
                received_ack = True
                for k in range(total_number_of_servers):
                    if serverDetails[k][0] == server_ip:
                        if serverDetails[k][1] == server_port:
                            serverDetails[k][2] = 1
        except socket.timeout:
            print 'Packet with Sequence Number = ' + data[0:32] + ' has timed out'
            number_of_retransmitted_packets += 1


if __name__ == '__main__':

    rdt_send()
    print'Total number of packets retransmitted:' + str(number_of_retransmitted_packets)
    print'Total time taken:' + str(total_time)
    with open('completion_times.txt', 'a+') as f:
        f.write(str(total_time) + '\n')
        f.close()
    print 'Finish'
