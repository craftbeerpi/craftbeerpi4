import json

import aiosqlite


from cbpi.database.orm_framework import DBModel

DATABASE_FILE = "./craftbeerpi.db"


class ActorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]

    __validation_schema__ = {
        'id': int,
        'name': str,
        'type': str,
        'config': dict
    }


class SensorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]
    __validation_schema__ = {
        'id': int,
        'name': str,
        'type': str,
        'config': dict
    }


class ConfigModel(DBModel):
    __fields__ = ["type", "value", "description", "options"]
    __table_name__ = "config"
    __json_fields__ = ["options"]
    __priamry_key__ = "name"


class KettleModel(DBModel):
    __fields__ = ["name", "sensor", "heater", "automatic", "logic", "config", "agitator", "target_temp"]
    __table_name__ = "kettle"
    __json_fields__ = ["config"]


class StepModel(DBModel):
    __fields__ = ["order", "name", "type", "stepstate", "state", "start", "end", "config", "kettleid"]
    __table_name__ = "step"
    __json_fields__ = ["config", "stepstate"]

    @classmethod
    async def update_step_state(cls, step_id, state):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            cursor = await db.execute("UPDATE %s SET stepstate = ? WHERE id = ?" % cls.__table_name__, (json.dumps(state), step_id))
            await db.commit()

    @classmethod
    async def update_state(cls, step_id, state, end=None):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            if end is not None:
                await db.execute("UPDATE %s SET state = ?, end = ? WHERE id = ?" % cls.__table_name__, (state, end, step_id))
            else:
                await db.execute("UPDATE %s SET state = ? WHERE id = ?" % cls.__table_name__, (state, step_id))
            await db.commit()

    @classmethod
    async def get_by_state(cls, state, order=True):

        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            db.row_factory = DBModel.dict_factory
            async with db.execute("SELECT * FROM %s WHERE state = ? ORDER BY %s.'order'" % (cls.__table_name__, cls.__table_name__,), state) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return cls(row)
                else:
                    return None

    @classmethod
    async def reset_all_steps(cls):

        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute("UPDATE %s SET state = 'I', stepstate = NULL , start = NULL, end = NULL " % cls.__table_name__)
            await db.commit()

    @classmethod
    async def sort(cls, new_order):

        async with aiosqlite.connect(DATABASE_FILE) as db:
            for key, value in new_order.items():
                print("ORDER", key, value)
                await db.execute("UPDATE %s SET '%s' = ? WHERE id = ?" % (cls.__table_name__, "order"), (value, key))
            await db.commit()

    @classmethod
    async def get_max_order(cls):


        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            db.row_factory = DBModel.dict_factory
            async with db.execute("SELECT max(step.'order') as 'order' FROM %s" % cls.__table_name__) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return row.get("order")
                else:
                    return 0


class DashboardModel(DBModel):
    __fields__ = ["name"]
    __table_name__ = "dashboard"
    __json_fields__ = []


class DashboardContentModel(DBModel):
    __fields__ = ["dbid", "type", "element_id", "x", "y","config"]
    __table_name__ = "dashboard_content"
    __json_fields__ = ["config"]

    __validation_schema__ = {
        'dbid': int,
        'element_id': int,
        'type': str,
        'x': int,
        'y': int,
        'config': dict
    }

    @classmethod
    async def get_by_dashboard_id(cls, id, as_array=False):

        result = []
        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = DBModel.dict_factory
            async with db.execute("SELECT * FROM %s WHERE dbid = ?" % (cls.__table_name__), (id,)) as cursor:
                async for row in cursor:
                    result.append(cls(row))
                await cursor.close()
        return result

    @classmethod
    async def update_coordinates(cls, id, x, y):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute("UPDATE %s SET x = ?, y = ? WHERE id = ?" % (cls.__table_name__), (x, y, id,))
            await db.commit()


    @classmethod
    async def delete_by_dashboard_id(cls, id):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute("DELETE FROM %s WHERE dbid = ?" % (cls.__table_name__), (id,))
            await db.commit()


class TranslationModel(DBModel):
    __fields__ = ["key", "text", "language_code"]
    __table_name__ = "translation"
    __json_fields__ = []
    __priamry_key__ = "key"

    @classmethod
    async def get_all(cls):

        result = {}
        async with aiosqlite.connect(DATABASE_FILE) as db:
            sql = "SELECT * FROM %s" % cls.__table_name__
            db.row_factory = DBModel.dict_factory
            async with db.execute(sql) as cursor:
                async for row in cursor:
                    code = row.get("language_code")
                    key = row.get("key")
                    text = row.get("text")
                    if code not in result:
                        result[code] = {}
                    result[code][key] = text
                await cursor.close()

        return result

    @classmethod
    async def add_key(cls, locale, key):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            await db.execute("INSERT INTO %s (language_code, key, text) VALUES (?,?, ' ')" % (cls.__table_name__), (locale, key))
            await db.commit()
