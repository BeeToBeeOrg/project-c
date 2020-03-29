from graphene import ID, String, ObjectType
from btb.models import db
from sqlalchemy import text

from promise import Promise
from promise.dataloader import DataLoader
from flask import current_app, g

class CompanyLoader(DataLoader):
    def batch_load_fn(self, keys):
        # current_app.logger.debug('CompanyLoader', keys)

        with db.engine.begin() as conn:
            sql = text('select * from btb.company where id = any(:keys)')
            data = conn.execute(sql, keys=list(map(lambda k: int(k), keys)))

            d = { str(i["id"]) : i for i in data }

            # must return result in same order
            return Promise.resolve([d.get(str(id), None) for id in keys])


def company_by_id(root, info, id=None):
    id = root["company_id"] if id is None else id
    current_app.logger.debug('company_by_id', id)
    
    return g.company_loader.load(id)
