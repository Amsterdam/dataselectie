# https://gis.stackexchange.com/questions/98146/calculating-percent-area-of-intersection-in-where-clause

bagimport_sql_commands = [

]

dataselection_sql_commands = [
    "DROP TABLE IF EXISTS test_table_foo",

    """CREATE TABLE test_table_foo (
        col1 INTEGER PRIMARY KEY,
        col2 INTEGER
    );""",
    "CREATE INDEX ON brk_eigendombuurt (col1, col2)",

]

mapselection_sql_commands = [

]
