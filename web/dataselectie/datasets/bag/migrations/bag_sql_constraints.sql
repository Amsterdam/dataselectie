--
-- TOC entry 3764 (class 2606 OID 645523)
-- Name: bag_bouwblok bag_bouwblok_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_bouwblok
    ADD CONSTRAINT bag_bouwblok_code_key UNIQUE (code);


--
-- TOC entry 3768 (class 2606 OID 645525)
-- Name: bag_bouwblok bag_bouwblok_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_bouwblok
    ADD CONSTRAINT bag_bouwblok_pkey PRIMARY KEY (id);


--
-- TOC entry 3771 (class 2606 OID 645384)
-- Name: bag_bron bag_bron_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_bron
    ADD CONSTRAINT bag_bron_pkey PRIMARY KEY (code);


--
-- TOC entry 3776 (class 2606 OID 645455)
-- Name: bag_buurt bag_buurt_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurt
    ADD CONSTRAINT bag_buurt_code_key UNIQUE (code);


--
-- TOC entry 3780 (class 2606 OID 645457)
-- Name: bag_buurt bag_buurt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurt
    ADD CONSTRAINT bag_buurt_pkey PRIMARY KEY (id);


--
-- TOC entry 3786 (class 2606 OID 645393)
-- Name: bag_buurtcombinatie bag_buurtcombinatie_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurtcombinatie
    ADD CONSTRAINT bag_buurtcombinatie_pkey PRIMARY KEY (id);


--
-- TOC entry 3791 (class 2606 OID 645387)
-- Name: bag_eigendomsverhouding bag_eigendomsverhouding_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_eigendomsverhouding
    ADD CONSTRAINT bag_eigendomsverhouding_pkey PRIMARY KEY (code);


--
-- TOC entry 3794 (class 2606 OID 645390)
-- Name: bag_financieringswijze bag_financieringswijze_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_financieringswijze
    ADD CONSTRAINT bag_financieringswijze_pkey PRIMARY KEY (code);


--
-- TOC entry 3797 (class 2606 OID 645402)
-- Name: bag_gebiedsgerichtwerken bag_gebiedsgerichtwerken_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gebiedsgerichtwerken
    ADD CONSTRAINT bag_gebiedsgerichtwerken_pkey PRIMARY KEY (id);


--
-- TOC entry 3802 (class 2606 OID 645399)
-- Name: bag_gebruik bag_gebruik_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gebruik
    ADD CONSTRAINT bag_gebruik_pkey PRIMARY KEY (code);


--
-- TOC entry 3804 (class 2606 OID 645574)
-- Name: bag_gebruiksdoel bag_gebruiksdoel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gebruiksdoel
    ADD CONSTRAINT bag_gebruiksdoel_pkey PRIMARY KEY (id);


--
-- TOC entry 3809 (class 2606 OID 645407)
-- Name: bag_gemeente bag_gemeente_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gemeente
    ADD CONSTRAINT bag_gemeente_code_key UNIQUE (code);


--
-- TOC entry 3812 (class 2606 OID 645409)
-- Name: bag_gemeente bag_gemeente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gemeente
    ADD CONSTRAINT bag_gemeente_pkey PRIMARY KEY (id);


--
-- TOC entry 3815 (class 2606 OID 645413)
-- Name: bag_grootstedelijkgebied bag_grootstedelijkgebied_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_grootstedelijkgebied
    ADD CONSTRAINT bag_grootstedelijkgebied_pkey PRIMARY KEY (id);


--
-- TOC entry 3818 (class 2606 OID 645416)
-- Name: bag_ligging bag_ligging_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligging
    ADD CONSTRAINT bag_ligging_pkey PRIMARY KEY (code);


--
-- TOC entry 3832 (class 2606 OID 645419)
-- Name: bag_ligplaats bag_ligplaats_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3834 (class 2606 OID 645424)
-- Name: bag_ligplaats bag_ligplaats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats_pkey PRIMARY KEY (id);


--
-- TOC entry 3839 (class 2606 OID 645449)
-- Name: bag_locatieingang bag_locatieingang_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_locatieingang
    ADD CONSTRAINT bag_locatieingang_pkey PRIMARY KEY (code);


--
-- TOC entry 3846 (class 2606 OID 646580)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3852 (class 2606 OID 646633)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_pkey PRIMARY KEY (id);


--
-- TOC entry 3863 (class 2606 OID 646572)
-- Name: bag_openbareruimte bag_openbareruimte_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_code_key UNIQUE (code);


--
-- TOC entry 3868 (class 2606 OID 646582)
-- Name: bag_openbareruimte bag_openbareruimte_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3870 (class 2606 OID 646584)
-- Name: bag_openbareruimte bag_openbareruimte_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_pkey PRIMARY KEY (id);


--
-- TOC entry 3881 (class 2606 OID 646568)
-- Name: bag_pand bag_pand_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_pand
    ADD CONSTRAINT bag_pand_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3883 (class 2606 OID 646570)
-- Name: bag_pand bag_pand_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_pand
    ADD CONSTRAINT bag_pand_pkey PRIMARY KEY (id);


--
-- TOC entry 3888 (class 2606 OID 645532)
-- Name: bag_redenafvoer bag_redenafvoer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_redenafvoer
    ADD CONSTRAINT bag_redenafvoer_pkey PRIMARY KEY (code);


--
-- TOC entry 3891 (class 2606 OID 645535)
-- Name: bag_redenopvoer bag_redenopvoer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_redenopvoer
    ADD CONSTRAINT bag_redenopvoer_pkey PRIMARY KEY (code);


--
-- TOC entry 3894 (class 2606 OID 645538)
-- Name: bag_stadsdeel bag_stadsdeel_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_stadsdeel
    ADD CONSTRAINT bag_stadsdeel_code_key UNIQUE (code);


--
-- TOC entry 3900 (class 2606 OID 645540)
-- Name: bag_stadsdeel bag_stadsdeel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_stadsdeel
    ADD CONSTRAINT bag_stadsdeel_pkey PRIMARY KEY (id);


--
-- TOC entry 3914 (class 2606 OID 645547)
-- Name: bag_standplaats bag_standplaats_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3916 (class 2606 OID 645549)
-- Name: bag_standplaats bag_standplaats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats_pkey PRIMARY KEY (id);


--
-- TOC entry 3921 (class 2606 OID 645565)
-- Name: bag_status bag_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_status
    ADD CONSTRAINT bag_status_pkey PRIMARY KEY (code);


--
-- TOC entry 3924 (class 2606 OID 645568)
-- Name: bag_toegang bag_toegang_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_toegang
    ADD CONSTRAINT bag_toegang_pkey PRIMARY KEY (code);


--
-- TOC entry 3927 (class 2606 OID 645571)
-- Name: bag_unesco bag_unesco_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_unesco
    ADD CONSTRAINT bag_unesco_pkey PRIMARY KEY (id);


--
-- TOC entry 3947 (class 2606 OID 646647)
-- Name: bag_verblijfsobject bag_verblijfsobject_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3953 (class 2606 OID 646692)
-- Name: bag_verblijfsobject bag_verblijfsobject_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_pkey PRIMARY KEY (id);


--
-- TOC entry 3966 (class 2606 OID 645750)
-- Name: bag_verblijfsobjectpandrelatie bag_verblijfsobjectpandrelatie_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobjectpandrelatie
    ADD CONSTRAINT bag_verblijfsobjectpandrelatie_pkey PRIMARY KEY (id);


--
-- TOC entry 3974 (class 2606 OID 646553)
-- Name: bag_woonplaats bag_woonplaats_landelijk_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_woonplaats
    ADD CONSTRAINT bag_woonplaats_landelijk_id_key UNIQUE (landelijk_id);


--
-- TOC entry 3976 (class 2606 OID 646555)
-- Name: bag_woonplaats bag_woonplaats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_woonplaats
    ADD CONSTRAINT bag_woonplaats_pkey PRIMARY KEY (id);


--
-- TOC entry 3977 (class 2606 OID 647005)
-- Name: bag_bouwblok bag_bouwblok_buurt_id_ff870647_fk_bag_buurt_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_bouwblok
    ADD CONSTRAINT bag_bouwblok_buurt_id_ff870647_fk_bag_buurt_id FOREIGN KEY (buurt_id) REFERENCES bag_buurt(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3978 (class 2606 OID 646940)
-- Name: bag_buurt bag_buurt_buurtcombinatie_id_e4f5ff64_fk_bag_buurtcombinatie_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurt
    ADD CONSTRAINT bag_buurt_buurtcombinatie_id_e4f5ff64_fk_bag_buurtcombinatie_id FOREIGN KEY (buurtcombinatie_id) REFERENCES bag_buurtcombinatie(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3979 (class 2606 OID 647040)
-- Name: bag_buurt bag_buurt_stadsdeel_id_0e62f99f_fk_bag_stadsdeel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurt
    ADD CONSTRAINT bag_buurt_stadsdeel_id_0e62f99f_fk_bag_stadsdeel_id FOREIGN KEY (stadsdeel_id) REFERENCES bag_stadsdeel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3980 (class 2606 OID 647045)
-- Name: bag_buurtcombinatie bag_buurtcombinatie_stadsdeel_id_06f6a98f_fk_bag_stadsdeel_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_buurtcombinatie
    ADD CONSTRAINT bag_buurtcombinatie_stadsdeel_id_06f6a98f_fk_bag_stadsdeel_id FOREIGN KEY (stadsdeel_id) REFERENCES bag_stadsdeel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3981 (class 2606 OID 647050)
-- Name: bag_gebiedsgerichtwerken bag_gebiedsgerichtwe_stadsdeel_id_9ad56674_fk_bag_stads; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gebiedsgerichtwerken
    ADD CONSTRAINT bag_gebiedsgerichtwe_stadsdeel_id_9ad56674_fk_bag_stads FOREIGN KEY (stadsdeel_id) REFERENCES bag_stadsdeel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3982 (class 2606 OID 647175)
-- Name: bag_gebruiksdoel bag_gebruiksdoel_verblijfsobject_id_b756d53f_fk_bag_verbl; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_gebruiksdoel
    ADD CONSTRAINT bag_gebruiksdoel_verblijfsobject_id_b756d53f_fk_bag_verbl FOREIGN KEY (verblijfsobject_id) REFERENCES bag_verblijfsobject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3984 (class 2606 OID 646950)
-- Name: bag_ligplaats bag_ligplaats__gebiedsgerichtwerke_7921ca73_fk_bag_gebie; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats__gebiedsgerichtwerke_7921ca73_fk_bag_gebie FOREIGN KEY (_gebiedsgerichtwerken_id) REFERENCES bag_gebiedsgerichtwerken(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3985 (class 2606 OID 646975)
-- Name: bag_ligplaats bag_ligplaats__grootstedelijkgebie_b1924b41_fk_bag_groot; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats__grootstedelijkgebie_b1924b41_fk_bag_groot FOREIGN KEY (_grootstedelijkgebied_id) REFERENCES bag_grootstedelijkgebied(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3983 (class 2606 OID 646905)
-- Name: bag_ligplaats bag_ligplaats_bron_id_9916456f_fk_bag_bron_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats_bron_id_9916456f_fk_bag_bron_code FOREIGN KEY (bron_id) REFERENCES bag_bron(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3986 (class 2606 OID 647010)
-- Name: bag_ligplaats bag_ligplaats_buurt_id_596acb57_fk_bag_buurt_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats_buurt_id_596acb57_fk_bag_buurt_id FOREIGN KEY (buurt_id) REFERENCES bag_buurt(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3987 (class 2606 OID 647060)
-- Name: bag_ligplaats bag_ligplaats_status_id_2c8abc61_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_ligplaats
    ADD CONSTRAINT bag_ligplaats_status_id_2c8abc61_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3988 (class 2606 OID 646910)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_bron_id_69a6a637_fk_bag_bron_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_bron_id_69a6a637_fk_bag_bron_code FOREIGN KEY (bron_id) REFERENCES bag_bron(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3989 (class 2606 OID 646995)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_ligplaats_id_ccf19788_fk_bag_ligplaats_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_ligplaats_id_ccf19788_fk_bag_ligplaats_id FOREIGN KEY (ligplaats_id) REFERENCES bag_ligplaats(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3992 (class 2606 OID 647115)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_openbare_ruimte_id_70ec9873_fk_bag_openb; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_openbare_ruimte_id_70ec9873_fk_bag_openb FOREIGN KEY (openbare_ruimte_id) REFERENCES bag_openbareruimte(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3990 (class 2606 OID 647055)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_standplaats_id_e4275a89_fk_bag_stand; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_standplaats_id_e4275a89_fk_bag_stand FOREIGN KEY (standplaats_id) REFERENCES bag_standplaats(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3991 (class 2606 OID 647065)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_status_id_cca87526_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_status_id_cca87526_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3993 (class 2606 OID 647180)
-- Name: bag_nummeraanduiding bag_nummeraanduiding_verblijfsobject_id_ffa54442_fk_bag_verbl; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_nummeraanduiding
    ADD CONSTRAINT bag_nummeraanduiding_verblijfsobject_id_ffa54442_fk_bag_verbl FOREIGN KEY (verblijfsobject_id) REFERENCES bag_verblijfsobject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3994 (class 2606 OID 646915)
-- Name: bag_openbareruimte bag_openbareruimte_bron_id_cbea113b_fk_bag_bron_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_bron_id_cbea113b_fk_bag_bron_code FOREIGN KEY (bron_id) REFERENCES bag_bron(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3995 (class 2606 OID 647070)
-- Name: bag_openbareruimte bag_openbareruimte_status_id_2129d363_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_status_id_2129d363_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3996 (class 2606 OID 647095)
-- Name: bag_openbareruimte bag_openbareruimte_woonplaats_id_487c4f06_fk_bag_woonplaats_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_openbareruimte
    ADD CONSTRAINT bag_openbareruimte_woonplaats_id_487c4f06_fk_bag_woonplaats_id FOREIGN KEY (woonplaats_id) REFERENCES bag_woonplaats(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3997 (class 2606 OID 647025)
-- Name: bag_pand bag_pand_bouwblok_id_bd200ca2_fk_bag_bouwblok_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_pand
    ADD CONSTRAINT bag_pand_bouwblok_id_bd200ca2_fk_bag_bouwblok_id FOREIGN KEY (bouwblok_id) REFERENCES bag_bouwblok(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3998 (class 2606 OID 647075)
-- Name: bag_pand bag_pand_status_id_1855bcfd_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_pand
    ADD CONSTRAINT bag_pand_status_id_1855bcfd_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3999 (class 2606 OID 646965)
-- Name: bag_stadsdeel bag_stadsdeel_gemeente_id_3f93513f_fk_bag_gemeente_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_stadsdeel
    ADD CONSTRAINT bag_stadsdeel_gemeente_id_3f93513f_fk_bag_gemeente_id FOREIGN KEY (gemeente_id) REFERENCES bag_gemeente(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4001 (class 2606 OID 646955)
-- Name: bag_standplaats bag_standplaats__gebiedsgerichtwerke_82c43a3b_fk_bag_gebie; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats__gebiedsgerichtwerke_82c43a3b_fk_bag_gebie FOREIGN KEY (_gebiedsgerichtwerken_id) REFERENCES bag_gebiedsgerichtwerken(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4002 (class 2606 OID 646980)
-- Name: bag_standplaats bag_standplaats__grootstedelijkgebie_c782a144_fk_bag_groot; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats__grootstedelijkgebie_c782a144_fk_bag_groot FOREIGN KEY (_grootstedelijkgebied_id) REFERENCES bag_grootstedelijkgebied(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4000 (class 2606 OID 646920)
-- Name: bag_standplaats bag_standplaats_bron_id_0f958d87_fk_bag_bron_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats_bron_id_0f958d87_fk_bag_bron_code FOREIGN KEY (bron_id) REFERENCES bag_bron(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4003 (class 2606 OID 647015)
-- Name: bag_standplaats bag_standplaats_buurt_id_efa5da1b_fk_bag_buurt_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats_buurt_id_efa5da1b_fk_bag_buurt_id FOREIGN KEY (buurt_id) REFERENCES bag_buurt(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4004 (class 2606 OID 647080)
-- Name: bag_standplaats bag_standplaats_status_id_7aa01805_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_standplaats
    ADD CONSTRAINT bag_standplaats_status_id_7aa01805_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4009 (class 2606 OID 646960)
-- Name: bag_verblijfsobject bag_verblijfsobject__gebiedsgerichtwerke_45ee3c7a_fk_bag_gebie; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject__gebiedsgerichtwerke_45ee3c7a_fk_bag_gebie FOREIGN KEY (_gebiedsgerichtwerken_id) REFERENCES bag_gebiedsgerichtwerken(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4010 (class 2606 OID 646985)
-- Name: bag_verblijfsobject bag_verblijfsobject__grootstedelijkgebie_197094b4_fk_bag_groot; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject__grootstedelijkgebie_197094b4_fk_bag_groot FOREIGN KEY (_grootstedelijkgebied_id) REFERENCES bag_grootstedelijkgebied(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4005 (class 2606 OID 646925)
-- Name: bag_verblijfsobject bag_verblijfsobject_bron_id_6983ff76_fk_bag_bron_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_bron_id_6983ff76_fk_bag_bron_code FOREIGN KEY (bron_id) REFERENCES bag_bron(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4013 (class 2606 OID 647020)
-- Name: bag_verblijfsobject bag_verblijfsobject_buurt_id_147c7220_fk_bag_buurt_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_buurt_id_147c7220_fk_bag_buurt_id FOREIGN KEY (buurt_id) REFERENCES bag_buurt(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4006 (class 2606 OID 646930)
-- Name: bag_verblijfsobject bag_verblijfsobject_eigendomsverhouding__6efcb6a5_fk_bag_eigen; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_eigendomsverhouding__6efcb6a5_fk_bag_eigen FOREIGN KEY (eigendomsverhouding_id) REFERENCES bag_eigendomsverhouding(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4007 (class 2606 OID 646935)
-- Name: bag_verblijfsobject bag_verblijfsobject_financieringswijze_i_ada0c4fc_fk_bag_finan; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_financieringswijze_i_ada0c4fc_fk_bag_finan FOREIGN KEY (financieringswijze_id) REFERENCES bag_financieringswijze(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4008 (class 2606 OID 646945)
-- Name: bag_verblijfsobject bag_verblijfsobject_gebruik_id_750be72a_fk_bag_gebruik_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_gebruik_id_750be72a_fk_bag_gebruik_code FOREIGN KEY (gebruik_id) REFERENCES bag_gebruik(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4011 (class 2606 OID 646990)
-- Name: bag_verblijfsobject bag_verblijfsobject_ligging_id_85bab2d0_fk_bag_ligging_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_ligging_id_85bab2d0_fk_bag_ligging_code FOREIGN KEY (ligging_id) REFERENCES bag_ligging(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4012 (class 2606 OID 647000)
-- Name: bag_verblijfsobject bag_verblijfsobject_locatie_ingang_id_d3df4a0c_fk_bag_locat; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_locatie_ingang_id_d3df4a0c_fk_bag_locat FOREIGN KEY (locatie_ingang_id) REFERENCES bag_locatieingang(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4014 (class 2606 OID 647030)
-- Name: bag_verblijfsobject bag_verblijfsobject_reden_afvoer_id_d63ad9d4_fk_bag_reden; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_reden_afvoer_id_d63ad9d4_fk_bag_reden FOREIGN KEY (reden_afvoer_id) REFERENCES bag_redenafvoer(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4015 (class 2606 OID 647035)
-- Name: bag_verblijfsobject bag_verblijfsobject_reden_opvoer_id_91720c49_fk_bag_reden; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_reden_opvoer_id_91720c49_fk_bag_reden FOREIGN KEY (reden_opvoer_id) REFERENCES bag_redenopvoer(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4016 (class 2606 OID 647085)
-- Name: bag_verblijfsobject bag_verblijfsobject_status_id_8e52e07c_fk_bag_status_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_status_id_8e52e07c_fk_bag_status_code FOREIGN KEY (status_id) REFERENCES bag_status(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4017 (class 2606 OID 647090)
-- Name: bag_verblijfsobject bag_verblijfsobject_toegang_id_d5013226_fk_bag_toegang_code; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobject
    ADD CONSTRAINT bag_verblijfsobject_toegang_id_d5013226_fk_bag_toegang_code FOREIGN KEY (toegang_id) REFERENCES bag_toegang(code) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4019 (class 2606 OID 647185)
-- Name: bag_verblijfsobjectpandrelatie bag_verblijfsobjectp_verblijfsobject_id_95cc1b5b_fk_bag_verbl; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobjectpandrelatie
    ADD CONSTRAINT bag_verblijfsobjectp_verblijfsobject_id_95cc1b5b_fk_bag_verbl FOREIGN KEY (verblijfsobject_id) REFERENCES bag_verblijfsobject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4018 (class 2606 OID 647120)
-- Name: bag_verblijfsobjectpandrelatie bag_verblijfsobjectpandrelatie_pand_id_083a5748_fk_bag_pand_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_verblijfsobjectpandrelatie
    ADD CONSTRAINT bag_verblijfsobjectpandrelatie_pand_id_083a5748_fk_bag_pand_id FOREIGN KEY (pand_id) REFERENCES bag_pand(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 4020 (class 2606 OID 646970)
-- Name: bag_woonplaats bag_woonplaats_gemeente_id_672595f6_fk_bag_gemeente_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bag_woonplaats
    ADD CONSTRAINT bag_woonplaats_gemeente_id_672595f6_fk_bag_gemeente_id FOREIGN KEY (gemeente_id) REFERENCES bag_gemeente(id) DEFERRABLE INITIALLY DEFERRED;


-- Completed on 2017-10-09 16:42:44 CEST

--
-- PostgreSQL database dump complete
--

