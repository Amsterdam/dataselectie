# Project
from django.db import connection

create_brk_table = """--
--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3 (Debian 10.3-1.pgdg90+1)
-- Dumped by pg_dump version 10.3 (Debian 10.3-1.pgdg90+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

DROP TABLE IF EXISTS public.brk_kadastraalobject;
DROP TABLE IF EXISTS public.brk_eigendom;

DROP TABLE IF EXISTS public.brk_eigendomwijk;
DROP TABLE IF EXISTS public.brk_eigendomstadsdeel;
DROP TABLE IF EXISTS public.brk_eigendomggw;
DROP TABLE IF EXISTS public.brk_eigendomcategorie;
DROP TABLE IF EXISTS public.brk_eigendombuurt;
DROP TABLE IF EXISTS public.brk_eigenaarcategorie;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: brk_eigendombuurt; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_eigendombuurt (
    row_number bigint,
    kadastraal_object_id character varying(60),
    buurt_id character varying(14)
);


ALTER TABLE public.brk_eigendombuurt OWNER TO dataselectie;

--
-- Name: brk_eigendomcategorie; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_eigendomcategorie (
    eigendom_id character varying(183),
    eigendom_cat integer
);


ALTER TABLE public.brk_eigendomcategorie OWNER TO dataselectie;

--
-- Name: brk_eigendomggw; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_eigendomggw (
    row_number bigint,
    kadastraal_object_id character varying(60),
    ggw_id character varying(4)
);


ALTER TABLE public.brk_eigendomggw OWNER TO dataselectie;

--
-- Name: brk_eigendomstadsdeel; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_eigendomstadsdeel (
    row_number bigint,
    kadastraal_object_id character varying(60),
    stadsdeel_id character varying(14)
);


ALTER TABLE public.brk_eigendomstadsdeel OWNER TO dataselectie;

--
-- Name: brk_eigendomwijk; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_eigendomwijk (
    row_number bigint,
    kadastraal_object_id character varying(60),
    buurt_combi_id character varying(14)
);


ALTER TABLE public.brk_eigendomwijk OWNER TO dataselectie;

CREATE TABLE public.brk_eigenaarcategorie (
    id integer,
    categorie character varying
);

ALTER TABLE public.brk_eigenaarcategorie OWNER TO dataselectie;

--
-- Name: brk_kadastraalobject; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE public.brk_kadastraalobject (
    id character varying(60) NOT NULL,
    aanduiding character varying(17) NOT NULL,
    date_modified timestamp with time zone NOT NULL,
    perceelnummer integer NOT NULL,
    indexletter character varying(1) NOT NULL,
    indexnummer integer NOT NULL,
    grootte integer,
    koopsom integer,
    koopsom_valuta_code character varying(50),
    koopjaar character varying(15),
    meer_objecten boolean,
    register9_tekst text NOT NULL,
    status_code character varying(50) NOT NULL,
    toestandsdatum date,
    voorlopige_kadastrale_grens boolean,
    in_onderzoek text,
    poly_geom public.geometry(MultiPolygon,28992),
    point_geom public.geometry(Point,28992),
    cultuurcode_bebouwd_id character varying(50),
    cultuurcode_onbebouwd_id character varying(50),
    kadastrale_gemeente_id character varying(200) NOT NULL,
    sectie_id character varying(200) NOT NULL,
    soort_grootte_id character varying(50),
    voornaamste_gerechtigde_id character varying(60)
);

--
-- Name: brk_eigendom; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brk_eigendom (
    id character varying(183),
    kadastraal_subject_id character varying(60),
    kadastraal_object_id character varying(60),
    aard_zakelijk_recht_akr character varying(3),
    cat_id integer,
    grondeigenaar boolean,
    aanschrijfbaar boolean,
    appartementeigenaar boolean
);

ALTER TABLE public.brk_eigendom OWNER TO dataselectie;
ALTER TABLE public.brk_kadastraalobject OWNER TO dataselectie;


--
-- PostgreSQL database dump complete
--
"""


def create_brk_data():
    with connection.cursor() as cursor:
        cursor.execute(create_brk_table)
