# https://gis.stackexchange.com/questions/98146/calculating-percent-area-of-intersection-in-where-clause

dataselection_sql_commands = [
    #
    #  Tables for indexing purposes of dataselection
    #
    "DROP TABLE IF EXISTS brk_eigendomstadsdeel",
    "DROP TABLE IF EXISTS brk_eigendomggw",
    "DROP TABLE IF EXISTS brk_eigendomwijk",
    "DROP TABLE IF EXISTS brk_eigendombuurt",

    "CREATE INDEX ON brk_kadastraalobject USING GIST (point_geom)",
    "CREATE INDEX ON brk_kadastraalobject USING GIST (poly_geom)",
    "CREATE INDEX ON bag_buurt USING GIST (geometrie)",
    "CREATE INDEX ON bag_buurtcombinatie USING GIST (geometrie)",
    "CREATE INDEX ON bag_gebiedsgerichtwerken USING GIST (geometrie)",
    "CREATE INDEX ON bag_stadsdeel USING GIST (geometrie)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_buurt
    """CREATE TABLE brk_eigendombuurt AS (
            SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
            FROM brk_kadastraalobject kot, bag_buurt buurt
            WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, buurt.geometrie) 
            UNION
            SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
            FROM brk_kadastraalobject kot, bag_buurt buurt
            WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, buurt.geometrie)
        )""",
    "CREATE INDEX ON brk_eigendombuurt (kadastraal_object_id, buurt_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_wijk
    """CREATE TABLE brk_eigendomwijk AS (
            SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
            FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
            WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, wijk.geometrie) 
            UNION
            SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
            FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
            WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, wijk.geometrie) 
        )""",
    "CREATE INDEX ON brk_eigendomwijk (kadastraal_object_id, buurt_combi_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_ggw
    """CREATE TABLE brk_eigendomggw AS (
            SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
            FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
            WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, ggw.geometrie)
            UNION
            SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
            FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
            WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, ggw.geometrie)
        )""",
    "CREATE INDEX ON brk_eigendomggw (kadastraal_object_id, ggw_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_stadsdeel
    """CREATE TABLE brk_eigendomstadsdeel AS (
            SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
            FROM brk_kadastraalobject kot, bag_stadsdeel sd
            WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, sd.geometrie) 
            UNION
            SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
            FROM brk_kadastraalobject kot, bag_stadsdeel sd
            WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, sd.geometrie) 
        )""",
    "CREATE INDEX ON brk_eigendomstadsdeel (kadastraal_object_id, stadsdeel_id)",
]

mapselection_sql_commands = [
    #
    #  Tables for selecting dataselections on map
    #

    "DROP TABLE IF EXISTS geo_brk_kot_point_in_poly",

    #   Linkup-table:
    #       all point-geometries from Registered properties grouped into their encompassing polygon-geometries
    """CREATE TABLE geo_brk_kot_point_in_poly AS (SELECT
        poly.id as poly_kot_id, point.id as point_kot_id from brk_kadastraalobject poly, brk_kadastraalobject point 
        where poly.poly_geom is not null and point.point_geom is not NULL
        and st_within(point.point_geom, poly.poly_geom))""",
    "CREATE INDEX ON geo_brk_kot_point_in_poly (poly_kot_id, point_kot_id)",
]

carto_sql_commands = [
    "DROP TABLE IF EXISTS geo_brk_eigendom_poly_all",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_all",

    "DROP TABLE IF EXISTS geo_brk_eigendom_poly_stadsdeel",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_stadsdeel",

    # "DROP TABLE IF EXISTS geo_brk_eigendom_poly_ggw",
    # "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_ggw",
    #
    # "DROP TABLE IF EXISTS geo_brk_eigendom_poly_wijk",
    # "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_wijk",
    #
    # "DROP TABLE IF EXISTS geo_brk_eigendom_poly_buurt",
    # "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_buurt",

    "DROP TABLE IF EXISTS geo_brk_eigendom_poly",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly",
    "DROP TABLE IF EXISTS geo_brk_eigendom_point",

    "DROP TABLE IF EXISTS geo_brk_eigendommen",

    #   Base table for cartographic layers,
    #       categorized registry-objects - only outright ownership
    """CREATE TABLE geo_brk_eigendommen AS (SELECT
    row_number() over () AS id,
    eigendom.kadastraal_object_id,
    eigendom.cat_id,
    kot.poly_geom,
    kot.point_geom
    FROM
    (SELECT kadastraal_object_id, cat_id
    FROM brk_eigendom
    WHERE aard_zakelijk_recht_akr = 'VE'
    GROUP BY 1, 2) eigendom, brk_kadastraalobject kot
    WHERE kot.id = eigendom.kadastraal_object_id)""",
    "CREATE INDEX ON geo_brk_eigendommen (kadastraal_object_id)",
    "CREATE INDEX eigendommen_poly ON geo_brk_eigendommen USING GIST (poly_geom)",
    "CREATE INDEX eigendommen_point ON geo_brk_eigendommen USING GIST (point_geom)",

    #   Base table for cartographic layers
    #       Landplots without outright ownership - encompassing registry-objects with outright ownership
    #       Select plot - category combo if not already exists and within that plot the non-plot - category combo does
    """CREATE TABLE geo_brk_niet_eigendom_poly AS (SELECT
        row_number() over () AS id, niet_eigendom.kadastraal_object_id, possible_cats.cat_id, niet_eigendom.poly_geom 
        FROM geo_brk_eigendommen niet_eigendom, 
            (select distinct kpp.poly_kot_id, eigendom.cat_id from geo_brk_eigendommen eigendom, geo_brk_kot_point_in_poly kpp
              where kpp.point_kot_id = eigendom.kadastraal_object_id) possible_cats
        WHERE possible_cats.poly_kot_id = niet_eigendom.kadastraal_object_id
        AND niet_eigendom.kadastraal_object_id = possible_cats.poly_kot_id 
        AND not exists 
            (select * from geo_brk_eigendommen eigendom where eigendom.cat_id = possible_cats.cat_id 
            and eigendom.kadastraal_object_id = niet_eigendom.kadastraal_object_id)
        )""",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly (kadastraal_object_id)",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly USING GIST (poly_geom)",

    #   Based on outright ownership categorized base table:
    #       Table for cartographic layers, grouped polygons (as unnested multipolygons) per categorie
    #       Used for showing lines around grouped counts of point-geom properties
    #           (appartements and the like) per poly-geom (land plots) which have a mixed ownership
    """CREATE TABLE geo_brk_eigendom_poly AS Select
    row_number() over () AS id,
    cat_id,
    ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
    FROM (SELECT st_union(poly_geom) geom, cat_id from geo_brk_eigendommen group by cat_id) as subquery""",
    "CREATE INDEX eigendom_poly ON geo_brk_eigendom_poly USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Aggregated registry-objects per land plots
    """CREATE TABLE geo_brk_eigendom_point AS (Select
        kpp.poly_kot_id as kadastraal_object_id,
        eigendom.cat_id,
        st_centroid(st_union(eigendom.point_geom)) as geometrie,
        count(eigendom.point_geom) as aantal
        from geo_brk_kot_point_in_poly kpp, geo_brk_eigendommen eigendom, brk_kadastraalobject kot 
        where kpp.poly_kot_id = kot.id and kpp.point_kot_id = eigendom.kadastraal_object_id
        group by 1, 2)""",
    "CREATE INDEX ON geo_brk_eigendom_point (kadastraal_object_id)",
    "CREATE INDEX eigendom_point ON geo_brk_eigendom_point USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Land-plots in full ownership, aggregated as unnested multi-polygons
    """CREATE TABLE geo_brk_eigendom_poly_all AS (SELECT
            row_number() over () AS id,
            cat_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(poly_geom) geom, eigendom.cat_id
                        FROM geo_brk_eigendommen eigendom
                        WHERE poly_geom is not null
                        GROUP BY eigendom.cat_id
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_eigendom_point USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Land-plots not in ownership, but with property, aggregated as unnested multi-polygons
    """CREATE TABLE geo_brk_niet_eigendom_poly_all AS (SELECT
            row_number() over () AS id,
            cat_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(poly_geom) geom, eigendom.cat_id
                        FROM geo_brk_niet_eigendom_poly eigendom
                        WHERE eigendom.kadastraal_object_id = stadsdeel.kadastraal_object_id
                        GROUP BY eigendom.cat_id, stadsdeel.stadsdeel_id 
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly_stadsdeel USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Land-plots in full ownership, aggregated as unnested multi-polygons per 'stadsdeel'
    """CREATE TABLE geo_brk_eigendom_poly_stadsdeel AS (SELECT
            row_number() over () AS id,
            cat_id,
            stadsdeel_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(poly_geom) geom, eigendom.cat_id, stadsdeel.stadsdeel_id 
                        FROM geo_brk_eigendommen eigendom, brk_eigendomstadsdeel stadsdeel
                        WHERE poly_geom is not null AND eigendom.kadastraal_object_id = stadsdeel.kadastraal_object_id
                        GROUP BY eigendom.cat_id, stadsdeel.stadsdeel_id 
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_eigendom_point USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Land-plots not in ownership, but with property, aggregated as unnested multi-polygons per 'stadsdeel'
    """CREATE TABLE geo_brk_niet_eigendom_poly_stadsdeel AS (SELECT
            row_number() over () AS id,
            cat_id,
            stadsdeel_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(poly_geom) geom, eigendom.cat_id, stadsdeel.stadsdeel_id 
                        FROM geo_brk_niet_eigendom_poly eigendom, brk_eigendomstadsdeel stadsdeel
                        WHERE eigendom.kadastraal_object_id = stadsdeel.kadastraal_object_id
                        GROUP BY eigendom.cat_id, stadsdeel.stadsdeel_id 
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly_stadsdeel USING GIST (geometrie)",
]