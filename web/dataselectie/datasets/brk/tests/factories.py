# Project
from django.db import connection
import logging

l = logging.getLogger('django.db.backends')
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())

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

DROP TABLE IF EXISTS public.brk_kadastraalobject CASCADE;
DROP TABLE IF EXISTS brk_kadastraalobjectverblijfsobjectrelatie CASCADE;
DROP TABLE IF EXISTS public.brk_eigendom CASCADE;
DROP TABLE IF EXISTS public.brk_eigendomwijk CASCADE;
DROP TABLE IF EXISTS public.brk_eigendomstadsdeel CASCADE;
DROP TABLE IF EXISTS public.brk_eigendomggw CASCADE;
DROP TABLE IF EXISTS public.brk_eigendomcategorie CASCADE;
DROP TABLE IF EXISTS public.brk_eigendombuurt CASCADE;
DROP TABLE IF EXISTS public.brk_eigenaarcategorie CASCADE;
DROP TABLE IF EXISTS public.brk_adres CASCADE;
DROP TABLE IF EXISTS public.brk_eigenaar CASCADE;
DROP TABLE IF EXISTS public.brk_gemeente CASCADE;
DROP TABLE IF EXISTS public.brk_kadastralesectie CASCADE;
DROP TABLE IF EXISTS public.brk_kadastralegemeente CASCADE;
DROP TABLE IF EXISTS public.brk_zakelijkrecht CASCADE;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: brk_adres; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_adres (
    id character varying(32) NOT NULL,
    openbareruimte_naam character varying(80),
    huisnummer integer,
    huisletter character varying(1),
    toevoeging character varying(4),
    postcode character varying(6),
    woonplaats character varying(80),
    postbus_nummer integer,
    postbus_postcode character varying(50),
    postbus_woonplaats character varying(80),
    buitenland_adres character varying(100),
    buitenland_woonplaats character varying(100),
    buitenland_regio character varying(100),
    buitenland_naam character varying(100),
    buitenland_land_id character varying(50)
);

ALTER TABLE public.brk_adres OWNER TO dataselectie;

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
    id character varying(60) PRIMARY KEY NOT NULL,
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
-- Name: brk_kadastraalobjectverblijfsobjectrelatie; Type: TABLE; Schema: public; Owner: dataselectie
--

CREATE TABLE brk_kadastraalobjectverblijfsobjectrelatie
(
  id                   uuid                     NOT NULL,
  date_modified        TIMESTAMP with time zone NOT NULL,
  kadastraal_object_id VARCHAR(60)              NOT NULL,
  verblijfsobject_id   VARCHAR(14)
);


--
-- Name: brk_eigendomstadsdeel; Type: TABLE; Schema: public; Owner: dataselectie
--
-- We need to add a foreign key for the model if a ManyRelatedManager uses a through model

CREATE TABLE public.brk_eigendomstadsdeel (
    row_number bigint,
    kadastraal_object_id character varying(60) references brk_kadastraalobject(id),
    stadsdeel_id character varying(14) references bag_stadsdeel(id)
);


ALTER TABLE public.brk_eigendomstadsdeel OWNER TO dataselectie;


--
-- Name: brk_eigenaar; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_eigenaar (
    cat_id integer,
    categorie character varying,
    id character varying(60),
    type smallint,
    date_modified timestamp with time zone,
    voornamen character varying(200),
    voorvoegsels character varying(10),
    naam character varying(200),
    geboortedatum character varying(50),
    geboorteplaats character varying(80),
    overlijdensdatum character varying(50),
    partner_voornamen character varying(200),
    partner_voorvoegsels character varying(10),
    partner_naam character varying(200),
    rsin character varying(80),
    kvknummer character varying(8),
    statutaire_naam character varying(200),
    statutaire_zetel character varying(24),
    bron smallint,
    aanduiding_naam_id character varying(50),
    beschikkingsbevoegdheid_id character varying(50),
    geboorteland_id character varying(50),
    geslacht_id character varying(50),
    land_waarnaar_vertrokken_id character varying(50),
    postadres_id character varying(32),
    rechtsvorm_id character varying(50),
    woonadres_id character varying(32)
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

--
-- Name: brk_gemeente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_gemeente (
    gemeente character varying(50) NOT NULL,
    geometrie public.geometry(MultiPolygon,28992) NOT NULL,
    date_modified timestamp with time zone NOT NULL
);

--
-- Name: brk_kadastralesectie; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_kadastralesectie (
    id character varying(200) NOT NULL,
    sectie character varying(2) NOT NULL,
    geometrie public.geometry(MultiPolygon,28992) NOT NULL,
    date_modified timestamp with time zone NOT NULL,
    kadastrale_gemeente_id character varying(200) NOT NULL
);

--
-- Name: brk_kadastralegemeente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_kadastralegemeente (
    id character varying(200) NOT NULL,
    naam character varying(100) NOT NULL,
    geometrie public.geometry(MultiPolygon,28992) NOT NULL,
    date_modified timestamp with time zone NOT NULL,
    gemeente_id character varying(50) NOT NULL
);


--
-- Name: brk_zakelijkrecht; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brk_zakelijkrecht (
    id character varying(183) NOT NULL,
    date_modified timestamp with time zone NOT NULL,
    zrt_id character varying(60) NOT NULL,
    aard_zakelijk_recht_akr character varying(3),
    teller integer,
    noemer integer,
    kadastraal_object_status character varying(50) NOT NULL,
    _kadastraal_subject_naam character varying(200) NOT NULL,
    _kadastraal_object_aanduiding character varying(100) NOT NULL,
    aard_zakelijk_recht_id character varying(50),
    app_rechtsplitstype_id character varying(50),
    betrokken_bij_id character varying(60),
    kadastraal_object_id character varying(60) NOT NULL,
    kadastraal_subject_id character varying(60) NOT NULL,
    ontstaan_uit_id character varying(60)
);

ALTER TABLE public.brk_eigendom OWNER TO dataselectie;
ALTER TABLE public.brk_eigenaar OWNER TO dataselectie;
ALTER TABLE public.brk_gemeente OWNER TO dataselectie;
ALTER TABLE public.brk_kadastralesectie OWNER TO dataselectie;
ALTER TABLE public.brk_kadastraalobject OWNER TO dataselectie;
ALTER TABLE public.brk_kadastraalobjectverblijfsobjectrelatie OWNER TO dataselectie;
ALTER TABLE public.brk_kadastralegemeente OWNER TO dataselectie;
ALTER TABLE public.brk_zakelijkrecht OWNER TO dataselectie;

ALTER TABLE public.brk_eigendomstadsdeel 
ADD CONSTRAINT kadastraal_object_id_fk FOREIGN KEY (kadastraal_object_id) REFERENCES public.brk_kadastraalobject(id),
ADD CONSTRAINT stadsdeel_id_fk FOREIGN KEY (stadsdeel_id) REFERENCES public.bag_stadsdeel(id);

--
-- PostgreSQL database dump complete
--
"""


def create_brk_data():
    with connection.cursor() as cursor:
        cursor.execute(create_brk_table)
