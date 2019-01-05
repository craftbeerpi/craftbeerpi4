import json
import aiosqlite
import os

from cbpi.api import *
from voluptuous import MultipleInvalid, Schema

DATABASE_FILE = "./craftbeerpi.db"


class DBModel(object):
    __priamry_key__ = "id"
    __as_array__ = False
    __order_by__ = None
    __json_fields__ = []
    __validation_schema__ = None

    def __init__(self, args):
        self.__setattr__(self.__priamry_key__, args[self.__priamry_key__])
        for f in self.__fields__:

            if f in self.__json_fields__:
                if args.get(f) is not None:

                    if isinstance(args[f], dict) or isinstance(args[f], list):
                        self.__setattr__(f, args.get(f))
                    else:
                        self.__setattr__(f, json.loads(args.get(f, "{}")))
                else:
                    self.__setattr__(f, None)
            else:

                self.__setattr__(f, args.get(f))

    @classmethod
    async def setup(self):

        async with aiosqlite.connect(DATABASE_FILE) as db:
            assert isinstance(db, aiosqlite.Connection)
            this_directory = os.path.dirname(__file__)
            qry = open(os.path.join(this_directory, "../config/create_database.sql"), 'r').read()
            cursor = await db.executescript(qry)

    @classmethod
    def validate(cls, data):
        if cls.__validation_schema__ is not None:
            try:
                schema = Schema(cls.__validation_schema__)
                schema(data)
            except MultipleInvalid as e:
                raise CBPiException(str(e))

    @classmethod
    async def get_all(cls):

        if cls.__as_array__ is True:
            result = []
        else:
            result = {}
        async with aiosqlite.connect(DATABASE_FILE) as db:

            if cls.__order_by__ is not None:
                sql = "SELECT * FROM %s ORDER BY %s.'%s'" % (cls.__table_name__, cls.__table_name__, cls.__order_by__)
            else:
                sql = "SELECT * FROM %s" % cls.__table_name__

            db.row_factory = DBModel.dict_factory
            async with db.execute(sql) as cursor:
                async for row in cursor:

                    if cls.__as_array__ is True:
                        result.append(cls(row))
                    else:

                        result[row.get(cls.__priamry_key__)] = cls(row)
                await cursor.close()

        return result

    @classmethod
    async def get_one(cls, id):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            db.row_factory = DBModel.dict_factory
            async with db.execute("SELECT * FROM %s WHERE %s = ?" % (cls.__table_name__, cls.__priamry_key__), (id,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return cls(row)
                else:
                    return None

    @classmethod
    async def delete(cls, id):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute("DELETE FROM %s WHERE %s = ? " % (cls.__table_name__, cls.__priamry_key__), (id,))
            await db.commit()

    @classmethod
    async def insert(cls, **kwargs):


        cls.validate(kwargs)

        async with aiosqlite.connect(DATABASE_FILE) as db:
            if cls.__priamry_key__ is not None and cls.__priamry_key__ in kwargs:
                query = "INSERT INTO %s (%s, %s) VALUES (?, %s)" % (
                    cls.__table_name__,
                    cls.__priamry_key__,
                    ', '.join("'%s'" % str(x) for x in cls.__fields__),
                    ', '.join(['?'] * len(cls.__fields__)))
                data = ()
                data = data + (kwargs.get(cls.__priamry_key__),)
                for f in cls.__fields__:
                    if f in cls.__json_fields__:
                        data = data + (json.dumps(kwargs.get(f)),)
                    else:
                        data = data + (kwargs.get(f),)
            else:

                query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                    cls.__table_name__,
                    ', '.join("'%s'" % str(x) for x in cls.__fields__),
                    ', '.join(['?'] * len(cls.__fields__)))

                data = ()
                for f in cls.__fields__:
                    if f in cls.__json_fields__:
                        data = data + (json.dumps(kwargs.get(f)),)
                    else:
                        data = data + (kwargs.get(f),)


            cursor = await db.execute(query, data)
            await db.commit()

            i = cursor.lastrowid
            kwargs["id"] = i

            return cls(kwargs)

    @classmethod
    async def update(cls, **kwargs):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            query = 'UPDATE %s SET %s WHERE %s = ?' % (cls.__table_name__, ', '.join("'%s' = ?" % str(x) for x in cls.__fields__), cls.__priamry_key__)

            data = ()
            for f in cls.__fields__:
                if f in cls.__json_fields__:
                    data = data + (json.dumps(kwargs.get(f)),)
                else:
                    data = data + (kwargs.get(f),)

            data = data + (kwargs.get(cls.__priamry_key__),)
            cursor = await db.execute(query, data)
            await db.commit()
            return cls(kwargs)

    @classmethod
    def dict_factory(cls, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
