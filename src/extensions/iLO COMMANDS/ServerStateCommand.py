###
# Copyright 2019 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" Server State Command for rdmc """

import sys

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class ServerStateCommand(RdmcCommandBase):
    """ Returns the current state of the server that  is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='serverstate',\
            usage='serverstate [OPTIONS]\n\n\treturns the current state of the'\
            ' server\n\n\tShow the current server state.\n\texample: serverstate',\
            summary='Returns the current state of the server.',\
            aliases=['serverstate'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """Main serverstate function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if args:
            raise InvalidCommandLineError("Invalid number of parameters, "\
                            "serverstate command does not take any parameters.")

        self.serverstatevalidation(options)

        path = self.typepath.defs.systempath
        results = self._rdmc.app.get_handler(path, silent=True, uncache=True).dict

        if results:
            results = results['Oem'][self.typepath.defs.oemhp]['PostState']
            sys.stdout.write("The server is currently in state: " + results + '\n')
        else:
            raise NoContentsFoundForOperationError("Unable to retrieve server state")

        return ReturnCodes.SUCCESS

    def serverstatevalidation(self, options):
        """ Server state method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.current_client
        except Exception:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    if options.encode:
                        options.user = Encryption.decode_credentials(options.user)
                    inputline.extend(["-u", options.user])
                if options.password:
                    if options.encode:
                        options.password = Encryption.decode_credentials(options.password)
                    inputline.extend(["-p", options.password])
                if options.https_cert:
                    inputline.extend(["--https", options.https_cert])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])
                if self._rdmc.app.config.get_ssl_cert():
                    inputline.extend(["--https", self._rdmc.app.config.get_ssl_cert()])

        if inputline:
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials" \
                                          " to complete the operation.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)
