# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 22:55:12 2022

@author: MUSA
"""

import base64
import re
import socket
import sys


def URLGetter(URL_of_index_file, authentication):
    """
    Parameters:
    URL (string): The URL for the file.
    authentication (String): The name and password separated with a colon.
    Returns index file and the header as a tuple.
.
    """
    host = URL_of_index_file[0:URL_of_index_file.index("/")]
    path = URL_of_index_file[URL_of_index_file.index("/"):]
    encoded = base64.b64encode(authentication.encode('ascii'))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, 80))
    request = "GET {} HTTP/1.1\r\nHost: {}\r\nAuthorization: Basic {}\r\n\r\n".format(path, host, str(encoded)[2:-1])
    client.send(request.encode("ascii"))
    response = client.recv(4096)
    # print(response)
    header, data = response.split(b"\r\n\r\n")
    return header, data


def textExtractor(text):
    """
    Returns the List of URL, authorization information and the bytes to include to the output.

    Uses regex to find bytes, URLs and authorization information.

    Args:
        text (String): The index file

    Returns: (list) The list of lists of URLs and their parameters
    """

    regexForUrls = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regexForUrls, text)
    # print(url)

    regexForParams = "[\w-]{1,100}:[\w-]{1,100}"
    params = re.findall(regexForParams, text)
    # print(params)

    regexForBytes = "[\d-]{1,100}-[\d-]{1,100}"
    byte = re.findall(regexForBytes, text)
    # print(byte)

    the_list_of_params = []
    for i in range(len(params)):
        the_list_of_params.append((params[i], byte[i], url[i][0]))

    return the_list_of_params


def recvall(sock):
    """
    Receives the data in small chunks and merge them to a final data.

    Args:
        sock: socket(socket.AF_INET, socket.SOCK_STREAM)

    Returns: data (bytes)

    """
    buffer_size = 1024
    data = bytearray()
    while True:
        # time.sleep(0.01)
        pack = sock.recv(buffer_size)
        if not pack:
            break
        data += pack
    return data


def listExtractor(listOL):
    """
    Sends get request to all URLs using the socket module.
    Merges responses after separating from the header.

    Args:
        listOL (String): The list of URLs and their parameters

    Returns: final data (bytes)

    """

    end = 0
    finalData = bytes()

    for i in listOL:

        URLs = i[2]
        params = i[0]
        encoded = base64.b64encode(params.encode('ascii'))
        host = URLs[0:URLs.index("/")]
        path = URLs[URLs.index("/"):]
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client.connect((host, 80))

        request = "GET {} HTTP/1.1\r\nHost: {}\r\nAuthorization: Basic {}\r\n\r\n".format(path, host,
                                                                                          str(encoded)[2:-1])

        client.send(request.encode("ascii"))
        # time.sleep(2)
        print(f"Connected to {URLs}")

        response = recvall(client)

        header, data = response.split(b"\r\n\r\n")

        status_codes = header1[header1.find(b" ") + 1:header1.find(b"\r\n")].decode("ascii")

        if int(status_codes[0:3]) > 299:
            print("The status code : ", status_codes)
            # time.sleep(5)
            exit()

        start = int(i[1][0:i[1].find('-')])
        old_start = start
        if start < end:
            start = end
        end = old_start + (len(data))

        print(f"Downloaded bytes {start} to {end - 1} (size = {end - start})")

        data = data[start - old_start: end - old_start]
        finalData += data
        client.close()
    print(f"Download of the file is complete (size = {end-1})")
    return finalData


# Getting arguments
URL = sys.argv[1]
parameters = sys.argv[2]

print("Command--‐line:")

print("URL of the index file: ", URL)

(header1, index_file) = URLGetter(URL, parameters)

index_list = index_file.decode("ascii").split("\n")


status_code = header1[header1.find(b" ") + 1:header1.find(b"\r\n")].decode("ascii")

# Checking the status code
if int(status_code[0:3]) > 299:
    print("The status code : ", status_code)
    # time.sleep(1)
    exit()

# getting name of the file
file_name = index_list[0]

print("File Name: ", file_name)

print("File size is ", index_list[1], " bytes")

print("Index file is downloaded")

print("There are " , (len(index_list) - 1) // 3 , " servers in the index")

print("Status Code: ", status_code)

# decoding the response to send text extractor
received = index_file.decode("ascii")
theList = textExtractor(received)

final = listExtractor(theList)

# the file is named after the name given in the index file
f = open(file_name, 'wb')
f.write(final)
f.close()
