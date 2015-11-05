from __future__ import print_function

import json
import getpass
from pprint import pprint

from sqlalchemy.orm import sessionmaker
from cloudmesh_base.util import banner
from sqlalchemy import inspect
from cloudmesh_base.hostlist import Parameter
from cloudmesh_client.db.model import database, table, tablenames, \
    FLAVOR, DEFAULT, KEY, IMAGE, VM, GROUP, RESERVATION

from cloudmesh_client.common.todo import TODO


class CloudmeshDatabase(object):
    def __init__(self, user=None):
        """
        initializes the CloudmeshDatabase for a specific user.
        The user is used to add entries augmented with it.

        :param cm_user: The username that is used to be added to the objects in teh database
        """

        self.db = database()
        self.db.Base.metadata.create_all()
        self.session = self.connect()

        if user is None:
            self.user = getpass.getuser()
        else:
            self.user = user

    # noinspection PyPep8Naming
    def connect(self):
        """
        before any method is called we need to connect to the database

        :return: the session of the database
        """
        Session = sessionmaker(bind=self.db.engine)
        self.session = Session()
        return self.session

    def save(self):
        self.session.commit()
        self.session.flush()

    def close(self):
        self.session.close()

    def db_table(self, kind):
        _type = kind
        if type(kind) == str:
            _type = self.get_table_from_name(kind)
        return _type

    def delete(self, item):
        """
        :param item:
        :return:
        """
        self.session.delete(item)
        self.save()

    def delete_all(self, kind):
        """
        :param type:
        :return:
        """
        self.session.query(kind).delete()
        self.save()

    def get_table_from_name(self, kind):
        if kind.lower() in ["flavor"]:
            return FLAVOR
        elif kind.lower() in ["default"]:
            return DEFAULT
        elif kind.lower() in ["image"]:
            return IMAGE
        elif kind.lower() in ["vm"]:
            return VM
        elif kind.lower() in ["key"]:
            return KEY
        elif kind.lower() in ["group"]:
            return GROUP
        elif kind.lower() in ["reservation"]:
            return RESERVATION
        else:
            TODO.implement("wrong table type: `{}`".format(kind))

    def find_by_name(self, kind, **kwargs):
        """
        find an object by name in the given table.
         If multiple objects have the same name, the first one is returned.

        :param name: the name
        :return: the object
        """
        def first(result):
            if len(result) == 0:
                return None
            else:
                return result[result.keys()[0]]

        if 'name' not in kwargs:
            raise ValueError("name not specified in find_by_name")

        table_type = self.db_table(kind)

        result = first(self.find(table_type, **kwargs))
        return result

    def find(self, kind, output="dict", **kwargs):
        """
        NOT teted
        :param kind:
        :param kwargs:
        :return:
        """
        table_type = self.db_table(kind)
        result = self.session.query(table_type).filter_by(**kwargs)
        if output == 'dict' and result is not None:
            result = self.object_to_dict(result)
        return result

    def all(self, table):
        table_type = self.db_table(kind)
        d = {}
        elements = self.session.query(table).all()
        for element in elements:
            d[element.id] = {}
            for key in element.__dict__.keys():
                if not key.startswith("_sa"):
                    d[element.id][key] = str(element.__dict__[key])
        return d

    def update(self, kind, args):
        """

        :param kind:
        :param kwargs:
        :return:
        """
        self.find(kind, output="object", name=args["name"]).update(args)
        self.save()

    def delete_by_name(self, kind, name):
        """
        NOTTESTED
        :param kind:
        :param name:
        :return:
        """
        table_type = self.db_table(kind)

        item = self.find(table_type, name=name, output="item").first()
        self.delete(item)

    def object_to_dict(self, obj):
        """
        converst the object to dict

        :param obj:
        :return:
        """
        result = dict()
        for u in obj:
            _id = u.id
            values = {}
            for key in u.__dict__.keys():
                if not key.startswith("_sa"):
                    values[key] = u.__dict__[key]
            result[_id] = values
        return result

    def dict(self, table):
        """
        returns a dict from all elements in the table

        :param table:
        :return:
        """
        return self.object_to_dict(self.session.query(table).all())

    def json(self, table):
        """
        returns a json representation from all elements in the table

        :param table:
        :return:
        """
        d = self.dict(table)
        return json.dumps(d)

    def info(self, what=None, kind=None):
        """
        prints information about the database
        """
        count_result = {}
        if kind is None:
            kinds = tablenames()
        else:
            kinds = Parameter.expand(kind)
        if what is None:
            infos = "table,count"
        else:
            infos = Parameter.expand(what)

        banner("Databse table information", c="-")
        inspector = inspect(self.db.engine)

        if "table" in infos:
            for table_name in inspector.get_table_names():
                if table_name in kinds:
                    print(table_name + ":")
                    for column in inspector.get_columns(table_name):
                        print("  ", column['name'], column['type'])

        sum = 0
        if "count" in infos:
            for table_name in inspector.get_table_names():
                if table_name in kinds:
                    t = table(table_name)
                    rows = self.session.query(t).count()
                    count_result[table_name] = rows
                    print("Count {:}: {:}".format(table_name, rows))
                    sum = sum + rows
            count_result['sum'] = sum

        return count_result

    def query(self, table):
        return self.session.query(table)

    def db_obj_dict(self, kind, obj_dict=None, **kwargs):
        """
        This method is a generic method to populate an object dict.
        The object dict can then be passed to database layer to add/ modify objects.
        :param dict: Dict to add object to
        :param kind: The table name in the db.
        :param kwargs: object parameters
        :return: Dict with object added
        """
        if obj_dict is None:
            obj_dict = dict()

        dict_length = len(obj_dict)

        obj_dict[dict_length] = dict()
        obj_dict[dict_length][kind] = kwargs

        # print(obj_dict)
        return obj_dict

    def add(self, o):
        self.session.add(o)
        self.session.commit()
        self.session.flush()

    def add_obj(self, obj_dict):
        # print("Inside add_obj")
        # print("Object Dict to add: {}".format(obj_dict))

        for obj in obj_dict.values():
            # print(obj)
            for key in obj.keys():
                table_name = self.db_table(key)
                obj_to_persist = table_name(**obj[key])
                self.add(obj_to_persist)

    def get(self, table, **kwargs):
        return self.session.query(table).filter_by(**kwargs).first()


def main():
    cm = CloudmeshDatabase(user="gregor")

    m = DEFAULT("hallo", "world")
    m.newfield__hhh = 13.9
    cm.add(m)

    n = cm.query(DEFAULT).filter_by(name='hallo').first()

    print("\n\n")

    pprint(n.__dict__)

    o = cm.get(DEFAULT, 'hallo')

    print("\n\n")

    pprint(o.__dict__)

    m = DEFAULT("other", "world")
    m.other = "ooo"
    cm.add(m)

    print("\n\n")
    pprint(cm.get(DEFAULT, 'other').__dict__)

    cm.info()

    """


    cm.info()
    # print(cm.list(VM))
    """


if __name__ == "__main__":
    main()
