#!/usr/bin/env python3

#--------------------------------------------------------------------------------
# MIT License

# Copyright (c) 2018 Peter Stenger

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#--------------------------------------------------------------------------------

import zeep, requests, logging
import zeep.helpers

class PywerschoolError(Exception):
    ''' An error within pywerschool '''

class Client:
    ''' The client for connecting to powerschool
    
    Client(base_url, api_username="pearson", api_password="m0bApP5")

    A client for using powerschool methods '''
    def __init__(self, base_url, api_username="pearson", api_password="m0bApP5"):
        logging.basicConfig(level=logging.CRITICAL)
        session = requests.session()
        session.auth = requests.auth.HTTPDigestAuth(api_username, api_password)
        if base_url[:-1] != "/":
            base_url += "/"
        self.url = base_url + "pearson-rest/services/PublicPortalServiceJSON"
        try:
            self.client = zeep.Client(wsdl=self.url + "?wsdl",transport=zeep.transports.Transport(session=session))
        except requests.exceptions.ConnectionError:
            raise PywerschoolError("Could not connect to {}.".format(base_url))
        except requests.exceptions.HTTPError:
            raise PywerschoolError("Incorrect api credentials ({}, {})".format(api_username, api_password))
    def getStudent(self, username, password,toDict=False):
        service = self.client.create_service('{http://publicportal.rest.powerschool.pearson.com}PublicPortalServiceJSONSoap12Binding',self.url)
        result = service.loginToPublicPortal(username, password)["userSessionVO"]
        if result["userId"] == None:
            raise PywerschoolError("Could not log in to ({}, {})".format(username, password))
        userSessionVO = {
                "userId": result["userId"],
                "serviceTicket": result["serviceTicket"],
                "serverInfo": {
                    "apiVersion": result["serverInfo"]["apiVersion"]
                },
                "serverCurrentTime": result["serverCurrentTime"],
                "userType": result["userType"]
        }
        student = service.getStudentData(userSessionVO, result["studentIDs"][0], {"includes": "1"})["studentDataVOs"][0]
        if toDict:
            return zeep.helpers.serialize_object(student,target_cls=dict)
        return student

