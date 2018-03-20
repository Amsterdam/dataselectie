# https://gis.stackexchange.com/questions/98146/calculating-percent-area-of-intersection-in-where-clause

dataselection_sql_commands = [
    #
    #  Tables for indexing purposes of dataselection
    #
    "DROP TABLE IF EXISTS brk_eigendomstadsdeel",
    "DROP TABLE IF EXISTS brk_eigendomggw",
    "DROP TABLE IF EXISTS brk_eigendomwijk",
    "DROP TABLE IF EXISTS brk_eigendombuurt",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_buurt
    """CREATE TABLE brk_eigendombuurt AS (
        SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
        FROM brk_kadastraalobject kot, bag_buurt buurt
        WHERE ST_INTERSECTS(kot.poly_geom, buurt.geometrie) and kot.poly_geom is not null
        UNION
        SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
        FROM brk_kadastraalobject kot, bag_buurt buurt
        WHERE ST_INTERSECTS(kot.point_geom, buurt.geometrie) and kot.point_geom is not null)""",
    "CREATE INDEX ON brk_eigendombuurt (kadastraal_object_id, buurt_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_wijk
    """CREATE TABLE brk_eigendomwijk AS (
        SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
        FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
        WHERE ST_INTERSECTS(kot.poly_geom, wijk.geometrie) and kot.poly_geom is not null
        UNION
        SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
        FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
        WHERE ST_INTERSECTS(kot.point_geom, wijk.geometrie) and kot.point_geom is not null)""",
    "CREATE INDEX ON brk_eigendomwijk (kadastraal_object_id, buurt_combi_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_ggw
    """CREATE TABLE brk_eigendomggw AS (
        SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
        FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
        WHERE ST_INTERSECTS(kot.poly_geom, ggw.geometrie) and kot.poly_geom is not null
        UNION
        SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
        FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
        WHERE ST_INTERSECTS(kot.point_geom, ggw.geometrie) and kot.point_geom is not null)""",
    "CREATE INDEX ON brk_eigendomggw (kadastraal_object_id, ggw_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_stadsdeel
    """CREATE TABLE brk_eigendomstadsdeel AS (
        SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
        FROM brk_kadastraalobject kot, bag_stadsdeel sd
        WHERE ST_INTERSECTS(kot.poly_geom, sd.geometrie) and kot.poly_geom is not null
        UNION
        SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
        FROM brk_kadastraalobject kot, bag_stadsdeel sd
        WHERE ST_INTERSECTS(kot.point_geom, sd.geometrie) and kot.point_geom is not null)
        """,
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
]

carto_sql_commands = [
    "DROP TABLE IF EXISTS geo_brk_eigendom_point_gemcluster",
    "DROP TABLE IF EXISTS geo_brk_eigendom_point_sectiecluster",
    "DROP TABLE IF EXISTS geo_brk_eigendom_filled_polygons",
    "DROP TABLE IF EXISTS geo_brk_eigendom_poly",
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
    "CREATE INDEX eigendommen_poly ON geo_brk_eigendommen USING GIST (poly_geom)",
    "CREATE INDEX eigendommen_point ON geo_brk_eigendommen USING GIST (point_geom)",
    #   Based on previous tables:
    #       Table for cartographic layers, grouped point-geometries together per polygon
    #       Used for showing counts of point-geom properties (appartements and the like) per poly-geom
    #       (usually land plots)
    """CREATE TABLE geo_brk_eigendom_point AS Select
        kpp.poly_kot_id as id, eigendom.cat_id, kot.poly_geom, 
        st_centroid(st_union(eigendom.point_geom)) as geometrie, count(eigendom.point_geom) as aantal
        from geo_brk_kot_point_in_poly kpp, geo_brk_eigendommen eigendom, brk_kadastraalobject kot 
        where kpp.poly_kot_id = kot.id and kpp.point_kot_id = eigendom.kadastraal_object_id
        group by 1, 2, 3""",
    "CREATE INDEX eigendom_point ON geo_brk_eigendom_point USING GIST (geometrie)",
    #   Based on outright ownership categorized base table:
    #       Table for cartographic layers, grouped polygons (as unnested multipolygons)
    #       per categorie of the encompassing polygons by which the previous table is grouped by
    """CREATE TABLE geo_brk_eigendom_filled_polygons AS Select
    row_number() over () AS id,
    cat_id,
    ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
    FROM (SELECT st_union(poly_geom) geom, cat_id from geo_brk_eigendom_point group by cat_id) as subquery""",
    "CREATE INDEX eigendom_point_niet_poly ON geo_brk_eigendom_filled_polygons USING GIST (geometrie)",
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
    #   Based on outright ownership categorized base table:
    #       Table for cartographic layers, grouped polygons (as unnested multipolygons) per categorie
    #       Used for showing lines around grouped counts of point-geom properties
    #           (appartements and the like) per poly-geom (land plots) which have a same type of ownership
    """CREATE TABLE geo_brk_eigendom_point_sectiecluster AS SELECT
    pt.cat_id, ks.id, st_centroid(ks.geometrie) as geometrie, count(obj.*) as aantal
    FROM geo_brk_eigendommen pt, brk_kadastraalobject obj, brk_kadastralesectie ks
    where pt.kadastraal_object_id = obj.id and obj.sectie_id = ks.id and pt.point_geom is not null
    GROUP BY 1, 2""",
    #   Based on outright ownership categorized base table:
    #       Table for cartographic layers, grouped points per registry-municipality
    """CREATE TABLE geo_brk_eigendom_point_gemcluster AS SELECT
    pt.cat_id, kg.id, st_centroid(kg.geometrie) as geometrie, count(obj.*) as aantal
    FROM geo_brk_eigendommen pt, brk_kadastraalobject obj, brk_kadastralegemeente kg
    where pt.kadastraal_object_id = obj.id and obj.kadastrale_gemeente_id = kg.id and pt.point_geom is not null
    GROUP BY 1, 2""",
]
