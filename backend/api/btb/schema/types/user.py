from graphene import ID, String, ObjectType, List
from .company import Company
from btb.schema.resolvers import companies_by_principal

class User(ObjectType):
    id = ID(required=True)
    external_id = ID(required=True)

    email = String(required=True)
    name = String(required=False)
    
    companies = List(Company, resolver=companies_by_principal)
