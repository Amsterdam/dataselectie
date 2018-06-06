# https://gis.stackexchange.com/questions/98146/calculating-percent-area-of-intersection-in-where-clause

bagimport_sql_commands = [
    #
    #  Indexes on imported tables
    #
    "CREATE INDEX ON brk_kadastraalobject USING GIST (point_geom)",
    "CREATE INDEX ON brk_kadastraalobject USING GIST (poly_geom)",
    "CREATE INDEX ON bag_buurt USING GIST (geometrie)",
    "CREATE INDEX ON bag_buurtcombinatie USING GIST (geometrie)",
    "CREATE INDEX ON bag_gebiedsgerichtwerken USING GIST (geometrie)",
    "CREATE INDEX ON bag_stadsdeel USING GIST (geometrie)",
]

dataselection_sql_commands = [
    #
    #  Tables for indexing purposes of dataselection
    #
    "DROP TABLE IF EXISTS brk_eigendomstadsdeel",
    "DROP TABLE IF EXISTS brk_eigendomggw",
    "DROP TABLE IF EXISTS brk_eigendomwijk",
    "DROP TABLE IF EXISTS brk_eigendombuurt",
    "DROP TABLE IF EXISTS brk_eigendomcategorie",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_buurt
    """CREATE TABLE brk_eigendombuurt AS (
            SELECT row_number() over (), kadastraal_object_id, buurt_id FROM (
                SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
                FROM brk_kadastraalobject kot, bag_buurt buurt
                WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, buurt.geometrie) 
                UNION
                SELECT kot.id as kadastraal_object_id, buurt.id as buurt_id
                FROM brk_kadastraalobject kot, bag_buurt buurt
                WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, buurt.geometrie)
            ) subquery
        )""",
    "CREATE INDEX ON brk_eigendombuurt (kadastraal_object_id, buurt_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_wijk
    """CREATE TABLE brk_eigendomwijk AS (
            SELECT row_number() over (), kadastraal_object_id, buurt_combi_id FROM (
                SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
                FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
                WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, wijk.geometrie) 
                UNION
                SELECT kot.id as kadastraal_object_id, wijk.id as buurt_combi_id
                FROM brk_kadastraalobject kot, bag_buurtcombinatie wijk
                WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, wijk.geometrie) 
            ) subquery
        )""",
    "CREATE INDEX ON brk_eigendomwijk (kadastraal_object_id, buurt_combi_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_ggw
    """CREATE TABLE brk_eigendomggw AS (
            SELECT row_number() over (), kadastraal_object_id, ggw_id FROM (
                SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
                FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
                WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, ggw.geometrie)
                UNION
                SELECT kot.id as kadastraal_object_id, ggw.id as ggw_id
                FROM brk_kadastraalobject kot, bag_gebiedsgerichtwerken ggw
                WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, ggw.geometrie)
            ) subquery
        )""",
    "CREATE INDEX ON brk_eigendomggw (kadastraal_object_id, ggw_id)",

    #   Linkup-table:
    #       all geometries from Registered properties grouped into their encompassing bag_stadsdeel
    """CREATE TABLE brk_eigendomstadsdeel AS (
            SELECT row_number() over (), kadastraal_object_id, stadsdeel_id FROM (
                SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
                FROM brk_kadastraalobject kot, bag_stadsdeel sd
                WHERE kot.poly_geom is not null AND ST_INTERSECTS(kot.poly_geom, sd.geometrie) 
                UNION
                SELECT kot.id as kadastraal_object_id, sd.id as stadsdeel_id
                FROM brk_kadastraalobject kot, bag_stadsdeel sd
                WHERE kot.point_geom is not null AND ST_Within(kot.point_geom, sd.geometrie) 
            ) subquery
        )""",
    "CREATE INDEX ON brk_eigendomstadsdeel (kadastraal_object_id, stadsdeel_id)",

    #   Normalisation-table:
    #       all combinations of eigendom and eigendomcategorie
    """CREATE TABLE brk_eigendomcategorie AS (
        SELECT id AS eigendom_id, 1::INTEGER  as eigendom_cat FROM brk_eigendom WHERE grondeigenaar = true::boolean
        UNION
        SELECT id AS eigendom_id, 2::INTEGER  as eigendom_cat FROM brk_eigendom WHERE aanschrijfbaar = true::boolean
        UNION
        SELECT id AS eigendom_id, 3::INTEGER  as eigendom_cat FROM brk_eigendom WHERE appartementeigenaar = true::boolean
    )""",
    "CREATE INDEX IF NOT EXISTS bag_nummeraanduiding_verblijfsobject_id_idx ON bag_nummeraanduiding(verblijfsobject_id)",
    "CREATE INDEX IF NOT EXISTS bag_verblijfsobject_id_idx ON bag_verblijfsobject(id)",
    "CREATE INDEX IF NOT EXISTS brk_adres_id_idx ON brk_adres(id)",
    "CREATE INDEX IF NOT EXISTS brk_eigenaar_id_idx ON brk_eigenaar(id)",
    "CREATE INDEX IF NOT EXISTS brk_eigendom_id_idx ON brk_eigendom(id)",
    "CREATE INDEX IF NOT EXISTS brk_eigendom_kadastraal_object_id_idx ON brk_eigendom(kadastraal_object_id)",
    "CREATE INDEX IF NOT EXISTS brk_eigendom_kadastraal_subject_id_idx ON brk_eigendom(kadastraal_subject_id)",
    "CREATE INDEX IF NOT EXISTS brk_eigendomcategorie_eigendom_id_eigendom_cat_idx ON brk_eigendomcategorie (eigendom_id, eigendom_cat)",
    "CREATE INDEX IF NOT EXISTS brk_kadastraalobject_id_idx ON brk_kadastraalobject(id)",
    "CREATE INDEX IF NOT EXISTS brk_kadastraalobjectverblijfsobjectrel_id_idx  ON brk_kadastraalobjectverblijfsobjectrelatie(id)",
    "CREATE INDEX IF NOT EXISTS brk_kadastraalobjectverblijfsobjectrelatie_kadastraal_object_id_idx ON brk_kadastraalobjectverblijfsobjectrelatie(kadastraal_object_id)",
    "CREATE INDEX IF NOT EXISTS brk_kadastralegemeente_id_idx ON brk_kadastralegemeente(id)",
    "CREATE INDEX IF NOT EXISTS brk_kadastralesectie_id_idx ON brk_kadastralesectie(id)",
    "CREATE INDEX IF NOT EXISTS brk_zakelijkrecht_id_idx ON brk_zakelijkrecht(id)",
]

mapselection_sql_commands = [
    #
    #  Tables for selecting dataselections on map
    #

    "DROP TABLE IF EXISTS geo_brk_eigendom_poly_index",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_index",

    "DROP TABLE IF EXISTS geo_brk_eigendom_poly_all",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly_all",

    "DROP TABLE IF EXISTS geo_brk_eigendom_poly",
    "DROP TABLE IF EXISTS geo_brk_niet_eigendom_poly",
    "DROP TABLE IF EXISTS geo_brk_eigendom_point",

    "DROP TABLE IF EXISTS geo_brk_eigendommen",
    "DROP TABLE IF EXISTS geo_brk_kot_point_in_poly",

    #   Linkup-table:
    #       all point-geometries from Registered properties grouped into their encompassing polygon-geometries
    """CREATE TABLE geo_brk_kot_point_in_poly AS (SELECT
        poly.id as poly_kot_id, point.id as point_kot_id from brk_kadastraalobject poly, brk_kadastraalobject point 
        where poly.poly_geom is not null and point.point_geom is not NULL
        and st_within(point.point_geom, poly.poly_geom))""",
    "CREATE INDEX ON geo_brk_kot_point_in_poly (poly_kot_id, point_kot_id)",

    #   Base table for cartographic layers,
    #       categorized registry-objects - only outright ownership
    """CREATE TABLE geo_brk_eigendommen AS (SELECT
    row_number() over () AS id,
    eigendom.kadastraal_object_id,
    eigendom.cat_id,
    st_transform(kot.poly_geom, 4326) poly_geom,
    st_transform(kot.point_geom, 4326) point_geom
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
        row_number() over () AS id, niet_eigendom.kadastraal_object_id, 
        possible_cats.cat_id, ST_ForcePolygonCCW(niet_eigendom.poly_geom) as geometrie
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
    "CREATE INDEX ON geo_brk_niet_eigendom_poly USING GIST (geometrie)",

    #   Based on outright ownership categorized base table:
    #       Table for cartographic layers, grouped polygons (as unnested multipolygons) per categorie
    #       Used for showing lines around grouped counts of point-geom properties
    #           (appartements and the like) per poly-geom (land plots) which have a mixed ownership
    """CREATE TABLE geo_brk_eigendom_poly AS (Select
        row_number() over () AS id, 
        eigendom.kadastraal_object_id,
        eigendom.cat_id,
        ST_ForcePolygonCCW(eigendom.poly_geom) as geometrie
        FROM geo_brk_eigendommen eigendom
        WHERE poly_geom is not null
        )""",
    "CREATE INDEX eigendom_poly ON geo_brk_eigendom_poly USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Aggregated registry-objects per land plots
    """CREATE TABLE geo_brk_eigendom_point AS (Select
        kpp.poly_kot_id as kadastraal_object_id,
        eigendom.cat_id,
        st_centroid(st_union(eigendom.point_geom)) as geometrie,
        count(eigendom.point_geom) as aantal,
        row_number() over () AS id
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
                        SELECT st_union(geometrie) geom, eigendom.cat_id
                        FROM geo_brk_eigendom_poly eigendom
                        GROUP BY eigendom.cat_id
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_eigendom_poly_all USING GIST (geometrie)",

    #   Aggregated table for cartographic layers
    #       Land-plots not in ownership, but with property, aggregated as unnested multi-polygons
    """CREATE TABLE geo_brk_niet_eigendom_poly_all AS (SELECT
            row_number() over () AS id,
            cat_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(geometrie) geom, eigendom.cat_id
                        FROM geo_brk_niet_eigendom_poly eigendom
                        GROUP BY eigendom.cat_id 
                    ) inner_query)""",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly_all USING GIST (geometrie)",

    #   Aggregated table for geoselection api
    #       Aggregated registry-objects per land plots
    """CREATE TABLE geo_brk_eigendom_point_index AS (Select
        kadastraal_object_id,
        cat_id,
        geometrie,
        aantal,
        id
        from geo_brk_eigendom_point)""",
    "CREATE SEQUENCE point_index_seq",
    "ALTER TABLE geo_brk_eigendom_point_index ALTER COLUMN id SET NOT NULL, ALTER COLUMN id SET DEFAULT nextval('point_index_seq')",
    "ALTER SEQUENCE point_index_seq OWNED BY geo_brk_eigendom_point_index.id",
    "SELECT setval('point_index_seq', MAX(id)) FROM geo_brk_eigendom_point_index ",
    """INSERT INTO geo_brk_eigendom_point_index (kadastraal_object_id, cat_id, geometrie, aantal) Select
        kpp.poly_kot_id as kadastraal_object_id,
        99::INTEGER as cat_id,
        st_centroid(st_union(eigendom.point_geom)) as geometrie,
        count(eigendom.point_geom) as aantal
        from geo_brk_kot_point_in_poly kpp, geo_brk_eigendommen eigendom, brk_kadastraalobject kot 
        where kpp.poly_kot_id = kot.id and kpp.point_kot_id = eigendom.kadastraal_object_id
        group by 1""",
    "CREATE INDEX ON geo_brk_eigendom_point_index (kadastraal_object_id)",
    "CREATE INDEX ON geo_brk_eigendom_point_index USING GIST (geometrie)",


    #   Aggregated table for geoselection api
    #       Land-plots in full ownership, aggregated as unnested multi-polygons per 'buurt'
    """CREATE TABLE geo_brk_eigendom_poly_index AS (SELECT
            cat_id,
            eigendom_cat,
            'buurt' as gebied,
            buurt_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(in_eigendom.poly_geom) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, buurt.buurt_id
                        FROM geo_brk_eigendommen in_eigendom, brk_eigendombuurt buurt,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE poly_geom is not null AND eigendom.kadastraal_object_id = buurt.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query)""",
    "ALTER TABLE geo_brk_eigendom_poly_index ADD COLUMN id SERIAL PRIMARY KEY",
    """INSERT INTO geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'wijk' as gebied,
            buurt_combi_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(in_eigendom.poly_geom) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, wijk.buurt_combi_id
                        FROM geo_brk_eigendommen in_eigendom, brk_eigendomwijk wijk,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE poly_geom is not null AND eigendom.kadastraal_object_id = wijk.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'ggw' as gebied,
            ggw_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(in_eigendom.poly_geom) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, ggw.ggw_id
                        FROM geo_brk_eigendommen in_eigendom, brk_eigendomggw ggw,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE poly_geom is not null AND eigendom.kadastraal_object_id = ggw.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'stadsdeel' as gebied,
            stadsdeel_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(in_eigendom.poly_geom) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, stadsdeel.stadsdeel_id
                        FROM geo_brk_eigendommen in_eigendom, brk_eigendomstadsdeel stadsdeel,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE poly_geom is not null AND eigendom.kadastraal_object_id = stadsdeel.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
        99::INTEGER as cat_id, eigendom_cat, gebied, gebied_id, ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
        FROM (SELECT st_union(geometrie) geom, eigendom_cat, gebied, gebied_id FROM geo_brk_eigendom_poly_index GROUP BY 2, 3, 4) subquery""",
    """INSERT INTO geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
        cat_id, 9::INTEGER AS eigendom_cat, gebied, gebied_id, ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
        FROM (SELECT st_union(geometrie) geom, cat_id, gebied, gebied_id FROM geo_brk_eigendom_poly_index GROUP BY 2, 3, 4) subquery""",

    #   Aggregated table for geoselection api
    #       Land-plots not in ownership, but with property, aggregated as unnested multi-polygons per 'buurt'
    """CREATE TABLE geo_brk_niet_eigendom_poly_index AS (SELECT
            cat_id,
            eigendom_cat,
            'buurt' as gebied,
            buurt_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(niet_in_eigendom.geometrie) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, buurt.buurt_id
                        FROM geo_brk_niet_eigendom_poly niet_in_eigendom, brk_eigendombuurt buurt,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE eigendom.kadastraal_object_id = buurt.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = niet_in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query)""",
    "ALTER TABLE geo_brk_niet_eigendom_poly_index ADD COLUMN id SERIAL PRIMARY KEY",
    """INSERT INTO geo_brk_niet_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'wijk' as gebied,
            buurt_combi_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(niet_in_eigendom.geometrie) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, wijk.buurt_combi_id
                        FROM geo_brk_niet_eigendom_poly niet_in_eigendom, brk_eigendomwijk wijk,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE eigendom.kadastraal_object_id = wijk.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = niet_in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_niet_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'ggw' as gebied,
            ggw_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(niet_in_eigendom.geometrie) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, ggw.ggw_id
                        FROM geo_brk_niet_eigendom_poly niet_in_eigendom, brk_eigendomggw ggw,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE eigendom.kadastraal_object_id = ggw.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = niet_in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_niet_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
            cat_id,
            eigendom_cat,
            'stadsdeel' as gebied,
            stadsdeel_id as gebied_id,
            ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
            FROM (
                        SELECT st_union(niet_in_eigendom.geometrie) geom, eigendom.cat_id, 
                               eigendom_cat.eigendom_cat, stadsdeel.stadsdeel_id
                        FROM geo_brk_niet_eigendom_poly niet_in_eigendom, brk_eigendomstadsdeel stadsdeel,
                             brk_eigendom eigendom, brk_eigendomcategorie eigendom_cat
                        WHERE eigendom.kadastraal_object_id = stadsdeel.kadastraal_object_id
                        AND eigendom.kadastraal_object_id = niet_in_eigendom.kadastraal_object_id 
                        AND eigendom.id = eigendom_cat.eigendom_id
                        GROUP BY 2, 3, 4
                    ) inner_query""",
    """INSERT INTO geo_brk_niet_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id, geometrie) SELECT
        cat_id, 9::INTEGER AS eigendom_cat, gebied, gebied_id, ST_GeometryN(geom, generate_series(1, ST_NumGeometries(geom))) as geometrie
        FROM (SELECT st_union(geometrie) geom, cat_id, gebied, gebied_id FROM geo_brk_niet_eigendom_poly_index GROUP BY 2, 3, 4) subquery""",

    "CREATE INDEX ON geo_brk_niet_eigendom_poly_index USING GIST (geometrie)",
    "CREATE INDEX ON geo_brk_eigendom_poly_index USING GIST (geometrie)",
    "CREATE INDEX ON geo_brk_niet_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id)",
    "CREATE INDEX ON geo_brk_eigendom_poly_index (cat_id, eigendom_cat, gebied, gebied_id)",

    # Simplify geometries (to the nearest 5, 10, 20 and 50 meters) for faster serving:
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.0000005) where gebied = 'buurt'",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.0000005) where gebied = 'buurt'",
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000001) where gebied = 'wijk'",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000001) where gebied = 'wijk'",
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000002) where gebied = 'ggw'",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000002) where gebied = 'ggw'",
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000005) where gebied = 'stadsdeel'",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_SIMPLIFY(geometrie, 0.000005) where gebied = 'stadsdeel'",

    # Make geometries valid for calculating intersections:
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_MAKEVALID(geometrie)",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_MAKEVALID(geometrie)",

    # Make geometries CW for serializing into valid GeoJSON:
    "UPDATE geo_brk_eigendom_poly_index SET geometrie = ST_ForcePolygonCCW(geometrie)",
    "UPDATE geo_brk_niet_eigendom_poly_index SET geometrie = ST_ForcePolygonCCW(geometrie)",

]