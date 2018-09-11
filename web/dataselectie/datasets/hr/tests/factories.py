# Project
from . import fixture_utils
from datasets.bag.tests import fixture_utils as bag_factory
from datasets.hr.models import DataSelectie
from django.db import connection

create_hr_table = """--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.6
-- Dumped by pg_dump version 9.6.6

SET statement_timeout = 0;
SET lock_timeout = 0;
-- SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

DROP TABLE IF EXISTS public.hr_dataselectie;
SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: hr_dataselectie; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE hr_dataselectie (
    id SERIAL,
    uid character varying(21) NOT NULL,
    bag_numid character varying(16),
    api_json jsonb NOT NULL
);


--
-- PostgreSQL database dump complete
--
"""


def dataselectie_hr_factory(nummeraanduiding_obj, from_nr, to_nr):
    for json in fixture_utils.JSON[from_nr:to_nr]:
        dataset = json['dataset']

        if dataset == 'ves':
            uid = f'v{json["vestigingsnummer"]}'
        else:
            uid = f'm{json["id"]}'

        DataSelectie.objects.get_or_create(
            uid=uid,
            api_json=json,
            bag_numid=nummeraanduiding_obj.landelijk_id)


def create_hr_data():
    with connection.cursor() as cursor:
        cursor.execute(create_hr_table)

    nummeraanduidingen = bag_factory.create_nummeraanduiding_fixtures()
    dataselectie_hr_factory(nummeraanduidingen[1], 0, 2)
    dataselectie_hr_factory(nummeraanduidingen[3], 2, 3)
    dataselectie_hr_factory(nummeraanduidingen[4], 3, 4)
    dataselectie_hr_factory(nummeraanduidingen[2], 4, 6)
