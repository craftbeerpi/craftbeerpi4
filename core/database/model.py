import json
import aiosqlite
from core.database.orm_framework import DBModel
DATABASE_FILE = "./craftbeerpi.db"

class ActorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]


class SensorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]

class ConfigModel(DBModel):
    __fields__ = ["type", "value", "description", "options"]
    __table_name__ = "config"
    __json_fields__ = ["options"]
    __priamry_key__ = "name"

class KettleModel(DBModel):
    __fields__ = ["name","sensor", "heater", "automatic", "logic", "config", "agitator", "target_temp"]
    __table_name__ = "kettle"
    __json_fields__ = ["config"]


class StepModel(DBModel):
    __fields__ = ["order", "name", "type", "stepstate", "state", "start", "end",  "config",  "kettleid"]
    __table_name__ = "step"
    __json_fields__ = ["config", "stepstate"]

    @classmethod
    async def update_step_state(cls, step_id, state):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            cursor = await db.execute("UPDATE %s SET stepstate = ? WHERE id = ?" % cls.__table_name__, (json.dumps(state), step_id))
            await db.commit()

    @classmethod
    async def get_by_state(cls, state, order=True):


        async with aiosqlite.connect(DATABASE_FILE) as db:
            db.row_factory = aiosqlite.Row
            db.row_factory = DBModel.dict_factory
            async with db.execute("SELECT * FROM %s WHERE state = ? ORDER BY %s.'order'" %  (cls.__table_name__, cls.__table_name__,), state) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return cls(row)
                else:
                    return None

    @classmethod
    async def reset_all_steps(cls):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            cursor = await db.execute("UPDATE %s SET state = 'I', stepstate = NULL , start = NULL, end = NULL " % cls.__table_name__)
            await db.commit()

