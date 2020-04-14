from sqlalchemy import create_engine, text
from os import environ
import pathlib
import posixpath

def run_file(stage, filename, conn):
    path = posixpath.join(pathlib.Path(__file__).parent.absolute(), filename)
    user = "lambda_b2b_{}".format(stage)

    print("Running script {} as {}".format(path, user))

    file = open(path, "r")
    sql = file.read()
    sql = sql.replace("lambda_b2b_dev", user)

    result = conn.execute(sql)


SCRIPTS = [
    "../../pgsql/01 clean.pgsql",
    "../../pgsql/10 tables.pgsql",
    "../../pgsql/20 views.pgsql",
    "../../pgsql/30 postalcodes.pgsql",
    "../../pgsql/31 real-data.pgsql",
]

STAGE_SCRIPTS = {
    "dev": ["../../pgsql/dev/01 clean.pgsql"] + SCRIPTS,
    "test": SCRIPTS,
    "prod": SCRIPTS
}

TEST_DATA = ["../../pgsql/dev/80 test-data.pgsql"]

def handler(event, context):
    engine = create_engine(environ["SQLALCHEMY_DATABASE_URI"])
    stage = environ["STAGE"] if "STAGE" in environ else "dev"

    with engine.begin() as conn:            
        if "action" in event:
            if event["action"] == "test-data":
                for filename in TEST_DATA:
                    run_file(stage, filename, conn)
                    
            else:
                raise Exception("Unknown event")

        else:
            for filename in STAGE_SCRIPTS[stage]:
                run_file(stage, filename, conn)

