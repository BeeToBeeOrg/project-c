from graphene import ID, String, ObjectType
from db import Company as DB_Company


def demands_by_company(root, info):
    context: Context = info.context
    principal = context.get_principal()

    return []


#
