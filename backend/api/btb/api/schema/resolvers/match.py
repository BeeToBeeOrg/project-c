from graphene import ID, String, ObjectType
from btb.api.models import db
from sqlalchemy import text

from promise import Promise
from promise.dataloader import DataLoader

from flask import current_app, g


class MatchQuery:
    def __init__(self, table, skills, location):
        self.table = table

        self.params = {
            "principal": g.principal.get_id(),
            "offset": 0,
        }

        self.select = []
        self.orders = {}
        self.conditions = []

        self.page_size = 10
        self.radius = 30

        self.limit = "limit {} offset :offset".format(self.page_size + 1)

        self.match_skills(skills)
        self.match_location(location)

    def set_offset(self, offset):
        self.params["offset"] = offset

    def set_radius(self, radius):
        self.params["radius"] = (radius if radius is not None else self.radius) * 1000

    def match_location(self, postal_code, radius=None):
        self.select.append(
            "st_distance(point, btb.get_postalcode_position(:postal_code)) as distance"
        )
        self.conditions.append(
            "st_dwithin(point, btb.get_postalcode_position(:postal_code), :radius)"
        )
        self.orders["distance"] = "point <-> btb.get_postalcode_position(:postal_code)"

        self.params["postal_code"] = postal_code
        self.params["radius"] = (radius if radius is not None else self.radius) * 1000

    def match_skills(self, skills):
        # number of matching elements
        self.select.append("icount(skills & :skills) as matchingskills")

        # have one element in common
        self.conditions.append("skills && :skills")
        self.orders["skills"] = "{} desc".format(len(self.select))

        self.params["skills"] = skills

    def match_salary(self, salary=None):
        self.select.append(":max_salary - hourly_salary as diffsalary")
        self.orders["salary"] = "{} desc".format(len(self.select))

        self.params["max_salary"] = salary if salary is not None else 0

    def match_quantity(self, quantity=None):
        self.select.append(":min_quantity - quantity as diffquantity")
        self.params["min_quantity"] = quantity if quantity is not None else 0
        self.orders["quantity"] = "{} desc".format(len(self.select))

    def calculate_percentage(self, record, orderby):
        matchingskills = record["matchingskills"] if "matchingskills" in record else 0
        diffsalary = record["diffsalary"] if "diffsalary" in record else 0
        diffquantity = record["diffquantity"] if "diffquantity" in record else 0

        amountskills = len(self.params["skills"]) if "skills" in self.params else 0
        salary = self.params["max_salary"] if "max_salary" in self.params else 0
        quantity = self.params["min_quantity"] if "min_quantity" in self.params else 0

        optionscount = amountskills
        matches = matchingskills

        if "salary" in orderby and salary > 0:
            optionscount += 1

            if diffsalary >= 0:
                matches += 1

        if "quantity" in orderby and quantity > 0:
            optionscount += 1

            if diffquantity >= 0:
                matches += 1

        return round(matches / optionscount * 100, 0)

    def map_default_result(self, tag, loader, record, orderby):
        return {
            "distance": round(record["distance"], 0),
            "percentage": self.calculate_percentage(record, orderby),
            tag: loader.load(record["record_id"]),
        }

    def map_result(self, record, orderby):
        return record

    # ["skills", "salary", "quantity", "distance"] we neglegt salary for now
    def execute(self, orderby = ["skills", "quantity", "distance"]): 
        select = self.select
        conditions = self.conditions

        orders = list(filter(
            lambda x: x is not None,
            map(lambda k: self.orders[k] if k in self.orders else None, orderby)
        ))

        current_app.logger.debug('orderby %s', orders)

        orders.append("company_name")
        select.append("record_id")

        conditions.append("external_id <> :principal")

        with db.engine.begin() as conn:
            result = conn.execute(
                text(
                    """
select {}
from {}
WHERE {}
order by {}
{}
                """.format(
                        ",".join(select),
                        self.table,
                        " and ".join(conditions),
                        ",".join(orders),
                        self.limit,
                    )
                ),
                **self.params
            )

            data = result.fetchall()
            nextCursor = {
                "has_next_page": False,
                "offset": self.params["offset"],
                "page_size": self.page_size,
            }

            if len(data) > self.page_size:
                data = data[:-1]
                nextCursor["has_next_page"] = True
                nextCursor["offset"] = self.params["offset"] + self.page_size

            elif self.params["offset"] > 0:
                nextCursor["offset"] = self.params["offset"] + len(data)

            if data is None or len(data) == 0:
                return {
                    "page_info": {**nextCursor},
                    "matches": [],
                }

            return {
                "page_info": {**nextCursor},
                "matches": map(lambda row: self.map_result(row, orderby), data),
            }
