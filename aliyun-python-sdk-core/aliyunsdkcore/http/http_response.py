# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# coding=utf-8
__author__ = 'alex jiang'

from http import client
import tornado.httpclient
import tornado.gen

from .http_request import HttpRequest
from . import protocol_type as PT


class HttpResponse(HttpRequest):
    def __init__(
            self,
            host="",
            url="/",
            method="GET",
            headers={},
            protocol=PT.HTTP,
            content=None,
            port=None,
            key_file=None,
            cert_file=None):
        HttpRequest.__init__(
            self,
            host=host,
            url=url,
            method=method,
            headers=headers)
        self.__ssl_enable = False
        if protocol is PT.HTTPS:
            self.__ssl_enable = True
        self.__key_file = key_file
        self.__cert_file = cert_file
        self.__port = port
        self.__connection = None
        self.set_body(content)

    def set_ssl_enable(self, enable):
        self.__ssl_enable = enable

    def get_ssl_enabled(self):
        return self.__ssl_enable

    def get_response(self):
        if self.get_ssl_enabled():
            return self.get_https_response()
        else:
            return self.get_http_response()

    async def get_response_object(self):
        if self.get_ssl_enabled():
            return await self.get_https_response_object()
        else:
            return await self.get_http_response_object()

    def get_http_response(self):
        if self.__port is None or self.__port == "":
            self.__port = 80
        try:
            self.__connection = client.HTTPConnection(
                self.get_host(), self.__port)
            self.__connection.connect()
            self.__connection.request(
                method=self.get_method(),
                url=self.get_url(),
                body=self.get_body(),
                headers=self.get_headers())
            response = self.__connection.getresponse()
            return response.getheaders(), response.read()
        finally:
            self.__close_connection()

    async def get_http_response_object(self):
        if self.__port is None or self.__port == "":
            self.__port = 80

        # by Will        
        http_client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(
            http_client.fetch,
            "{0}://{1}:{2}{3}".format(PT.HTTP,
                                      self.get_host(),
                                      self.__port,
                                      self.get_url()),
            method=self.get_method(),
            headers=self.get_headers(),
            body=self.get_body(),
            validate_cert=False)
        
        return resp.code, resp.headers, resp.body
        # end

        """
        if self.__port is None or self.__port == "":
            self.__port = 80

        try:
            self.__connection = client.HTTPConnection(
                self.get_host(), self.__port)
            self.__connection.connect()
            self.__connection.request(
                method=self.get_method(),
                url=self.get_url(),
                body=self.get_body(),
                headers=self.get_headers())
            response = self.__connection.getresponse()
            return response.status, response.getheaders(), response.read()
        finally:
            self.__close_connection()
        """

    def get_https_response(self):
        if self.__port is None or self.__port == "":
            self.__port = 443
        try:
            self.__port = 443
            self.__connection = client.HTTPSConnection(
                self.get_host(),
                self.__port,
                cert_file=self.__cert_file,
                key_file=self.__key_file)
            self.__connection.connect()
            self.__connection.request(
                method=self.get_method(),
                url=self.get_url(),
                body=self.get_body(),
                headers=self.get_headers())
            response = self.__connection.getresponse()
            return response.getheaders(), response.read()
        finally:
            self.__close_connection()

    async def get_https_response_object(self):
        if self.__port is None or self.__port == "":
            self.__port = 443

        # by Will
        http_client = tornado.httpclient.AsyncHTTPClient()
        resp = await tornado.gen.Task(
            http_client.fetch,
            "{0}://{1}:{2}{3}".format(PT.HTTPS,
                                      self.get_host(),
                                      self.__port,
                                      self.get_url()),
            method=self.get_method(),
            headers=self.get_headers(),
            body=self.get_body(),
            validate_cert=True,
            ca_certs=self.__cert_file,
            client_key=self.__key_file)
        
        return resp.code, resp.headers, resp.body
     
        # end

        """
        try:
            self.__port = 443
            self.__connection = client.HTTPSConnection(
                self.get_host(),
                self.__port,
                cert_file=self.__cert_file,
                key_file=self.__key_file)
            self.__connection.connect()
            self.__connection.request(
                method=self.get_method(),
                url=self.get_url(),
                body=self.get_body(),
                headers=self.get_headers())
            response = self.__connection.getresponse()
            return response.status, response.getheaders(), response.read()
        finally:
            self.__close_connection()
        """

    def __close_connection(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
