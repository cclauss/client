from __future__ import print_function

import yaml
import os.path
import json
import re
from cloudmesh_base.ConfigDict import ConfigDict as BaseConfigDict

class todo(object):
    @classmethod
    def implemet(cls):
        raise NotImplementedError("Please implement")

class Config(object):

    @classmethod
    def check_file_for_tabs(cls, filename, verbose=True):
        """identifies if the file contains tabs and returns True if it
        does. It also prints the location of the lines and columns. If
        verbose is set to False, the location is not printed.

        :param filename: the filename
        :type filename: str
        :rtype: True if there are tabs in the file
        """
        file_contains_tabs = False
        with file(filename) as f:
            lines = f.read().split("\n")

        line_no = 1
        for line in lines:
            if "\t" in line:
                file_contains_tabs = True
                location = [
                    i for i in range(len(line)) if line.startswith('\t', i)]
                if verbose:
                    print("Tab found in line", line_no, "and column(s)", location)
            line_no += 1
        return file_contains_tabs

    @classmethod
    def path_expand(cls, path):
        current_dir = "." + os.path.sep
        if path.startswith(current_dir):
            cwd = str(os.getcwd())
            path = path.replace(current_dir, cwd, 1)
        location = os.path.expandvars(os.path.expanduser(path))
        return location

    @classmethod
    def find_file(cls, filename, load_order=None, verbose=False):
        if load_order is None:
            load_order = [".", "~/.cloudmesh"]
        for path in load_order:
            name = Config.path_expand(path + os.path.sep + filename)
            if verbose:
                print ("try finding file", name)
            if os.path.isfile(name):
                if verbose:
                    print ("Found File", name)
                return name
        return None



class ConfigDict(object):

    def __init__(self,
                 filename,
                 load_order=None,
                 verbose=False):
        """
        Creates a dictionary from a yaml configuration file
        while using the filename to load it in the specified load_order.
        The load order is an array of paths in which the file is searched.
        By default the load order is set to . and ~/.cloudmesh

        :param filename: the filename
        :type filename: string
        :param load_order: an array with path names in with the filename is looked for.
        :type load_order: list of strings
        :return: an instance of ConfigDict
        :rtype: ConfigDict
        """
        if load_order is None:
            self.load_order = [".", "~/.cloudmesh"]
        for path in self.load_order:
            name = Config.path_expand(path + os.path.sep + filename)
            if verbose:
                    print ("try Loading ConfigDict", name)
            if os.path.isfile(name):
                if verbose:
                    print ("Loading ConfigDict", name)
                self.load(name)
                self.filename = name
                return

    def load(self, filename):
        """loads the filename"""
        self.data = BaseConfigDict(filename=Config.path_expand(filename))

    def save(self, filename=None):
        """
        saves the configuration in the given filename, if it is none the filename at load time is used.

        :param filename:
        :return:
        """
        content = self.data.yaml()
        with open(Config.path_expand(self.filename),'w') as f:
            f.write(content)

    def __setitem__(self, item, value):
        if "." in item:
            keys = item.split(".")
        else:
            element = self.data[item]

        element = self.data[keys[0]]
        for key in keys[1:]:
            element = element[key]
        element = value

    def __getitem__(self, item):
        if "." in item:
            keys = item.split(".")
        else:
            return self.data[item]
        element = self.data[keys[0]]
        for key in keys[1:]:
            element = element[key]
        return element

    def __str__(self):
        """

        :return:
        """
        return self.data.yaml()

    @property
    def yaml(self):
        return self.data.yaml()

    def info(self):
        """

        :return:
        """
        print (type(self.data))
        print (self.data)

    @property
    def json(self):
        """
        string of the json formated object

        :return: json string version
        """
        return (json.dumps(self.data, indent=4))

    @classmethod
    def check(cls, filename):
        """
        checks the filename if it is syntactically corrrect and does not include tabs

        :param filename:
        :return:
        """
        todo.implement()

def main():
    d = ConfigDict("cloudmesh.yaml")
    print (d, end='')
    d.info()

    print (d["meta"])
    print (d["meta.kind"])
    print (d["meta"]["kind"])

    # this does not yet work
    d.data["cloudmesh"]["profile"]["firstname"] = 'ABC'
    print (d)
    d.save()

    import os
    os.system("cat cmd3.yaml")

    print(d.json)
    print(d.filename)
    print("YAML")
    print(d.yaml)

if __name__ == "__main__":
    main()