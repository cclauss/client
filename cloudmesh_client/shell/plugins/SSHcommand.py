from __future__ import print_function
from cloudmesh_client.shell.cm import command
from cloudmesh_client.shell.console import Console
# from cloudmesh_client.cloud.command_ssh import command_ssh


class SSHCommand (object):

    #def activate_cm_shell_ssh(self):

    def __init__(self, context):
        self.context = context
        if self.context.debug:
            print ("init command ssh")

    @command
    def do_ssh(self, args, arguments):
        """
        ::

            Usage:
                ssh list [--format=FORMAT]
                ssh register NAME PARAMETERS
                ssh NAME [--user=USER] [--key=KEY] [COMMAND]


            conducts a ssh login on a machine while using a set of
            registered machines specified in ~/.ssh/config

            Arguments:

              NAME        Name or ip of the machine to log in
              list        Lists the machines that are registered and
                          the commands to login to them
              PARAMETERS  Register te resource and add the given
                          parameters to the ssh config file.  if the
                          resoource exists, it will be overwritten. The
                          information will be written in /.ssh/config

            Options:

               -v       verbose mode
               --format=FORMAT   the format in which this list is given
                                 formats incluse table, json, yaml, dict
                                 [default: table]

               --user=USER       overwrites the username that is
                                 specified in ~/.ssh/config

               --key=KEY         The keyname as defined in the key list
                                 or a location that contains a pblic key

        """
        # pprint(arguments)
        if arguments["list"]:
            output_format = arguments["--format"]
            Console.ok('list {}'.format(output_format))
        elif arguments["register"]:
            name = arguments["NAME"]
            parameters = arguments["PARAMETERS"]
            Console.ok('register {} {}'.format(name, parameters))
        elif arguments["NAME"]:
            name = arguments["NAME"]
            user = arguments["--user"]
            key = arguments["--key"]
            Console.ok('ssh {} {} {}'.format(name, user, key))
        pass


if __name__ == '__main__':
    command = cm_shell_ssh()
    command.do_ssh("list")
    command.do_ssh("a=x")
    command.do_ssh("x")
