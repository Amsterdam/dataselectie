-- Create bag indexes

--
-- TOC entry 3760 (class 1259 OID 645526)
-- Name: bag_bouwblok_buurt_id_ff870647; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bouwblok_buurt_id_ff870647 ON bag_bouwblok USING btree (buurt_id);


--
-- TOC entry 3761 (class 1259 OID 645527)
-- Name: bag_bouwblok_buurt_id_ff870647_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bouwblok_buurt_id_ff870647_like ON bag_bouwblok USING btree (buurt_id varchar_pattern_ops);


--
-- TOC entry 3762 (class 1259 OID 645528)
-- Name: bag_bouwblok_code_ae4b5c1e_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bouwblok_code_ae4b5c1e_like ON bag_bouwblok USING btree (code varchar_pattern_ops);


--
-- TOC entry 3765 (class 1259 OID 645529)
-- Name: bag_bouwblok_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bouwblok_geometrie_id ON bag_bouwblok USING gist (geometrie);


--
-- TOC entry 3766 (class 1259 OID 645530)
-- Name: bag_bouwblok_id_0d16292c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bouwblok_id_0d16292c_like ON bag_bouwblok USING btree (id varchar_pattern_ops);


--
-- TOC entry 3769 (class 1259 OID 645385)
-- Name: bag_bron_code_5fa17b9b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_bron_code_5fa17b9b_like ON bag_bron USING btree (code varchar_pattern_ops);


--
-- TOC entry 3772 (class 1259 OID 645458)
-- Name: bag_buurt_buurtcombinatie_id_e4f5ff64; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_buurtcombinatie_id_e4f5ff64 ON bag_buurt USING btree (buurtcombinatie_id);


--
-- TOC entry 3773 (class 1259 OID 645459)
-- Name: bag_buurt_buurtcombinatie_id_e4f5ff64_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_buurtcombinatie_id_e4f5ff64_like ON bag_buurt USING btree (buurtcombinatie_id varchar_pattern_ops);


--
-- TOC entry 3774 (class 1259 OID 645460)
-- Name: bag_buurt_code_4d4957a1_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_code_4d4957a1_like ON bag_buurt USING btree (code varchar_pattern_ops);


--
-- TOC entry 3777 (class 1259 OID 645461)
-- Name: bag_buurt_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_geometrie_id ON bag_buurt USING gist (geometrie);


--
-- TOC entry 3778 (class 1259 OID 645462)
-- Name: bag_buurt_id_474bfe01_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_id_474bfe01_like ON bag_buurt USING btree (id varchar_pattern_ops);


--
-- TOC entry 3781 (class 1259 OID 645463)
-- Name: bag_buurt_stadsdeel_id_0e62f99f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_stadsdeel_id_0e62f99f ON bag_buurt USING btree (stadsdeel_id);


--
-- TOC entry 3782 (class 1259 OID 645464)
-- Name: bag_buurt_stadsdeel_id_0e62f99f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurt_stadsdeel_id_0e62f99f_like ON bag_buurt USING btree (stadsdeel_id varchar_pattern_ops);


--
-- TOC entry 3783 (class 1259 OID 645394)
-- Name: bag_buurtcombinatie_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurtcombinatie_geometrie_id ON bag_buurtcombinatie USING gist (geometrie);


--
-- TOC entry 3784 (class 1259 OID 645395)
-- Name: bag_buurtcombinatie_id_f0fb65c1_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurtcombinatie_id_f0fb65c1_like ON bag_buurtcombinatie USING btree (id varchar_pattern_ops);


--
-- TOC entry 3787 (class 1259 OID 645396)
-- Name: bag_buurtcombinatie_stadsdeel_id_06f6a98f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurtcombinatie_stadsdeel_id_06f6a98f ON bag_buurtcombinatie USING btree (stadsdeel_id);


--
-- TOC entry 3788 (class 1259 OID 645397)
-- Name: bag_buurtcombinatie_stadsdeel_id_06f6a98f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_buurtcombinatie_stadsdeel_id_06f6a98f_like ON bag_buurtcombinatie USING btree (stadsdeel_id varchar_pattern_ops);


--
-- TOC entry 3795 (class 1259 OID 645403)
-- Name: bag_gebiedsgerichtwerken_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_gebiedsgerichtwerken_geometrie_id ON bag_gebiedsgerichtwerken USING gist (geometrie);


--
-- TOC entry 3798 (class 1259 OID 645404)
-- Name: bag_gebiedsgerichtwerken_stadsdeel_id_9ad56674; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_gebiedsgerichtwerken_stadsdeel_id_9ad56674 ON bag_gebiedsgerichtwerken USING btree (stadsdeel_id);


--
-- TOC entry 3799 (class 1259 OID 645405)
-- Name: bag_gebiedsgerichtwerken_stadsdeel_id_9ad56674_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_gebiedsgerichtwerken_stadsdeel_id_9ad56674_like ON bag_gebiedsgerichtwerken USING btree (stadsdeel_id varchar_pattern_ops);


--
-- TOC entry 3807 (class 1259 OID 645410)
-- Name: bag_gemeente_code_d4536853_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_gemeente_code_d4536853_like ON bag_gemeente USING btree (code varchar_pattern_ops);


--
-- TOC entry 3810 (class 1259 OID 645411)
-- Name: bag_gemeente_id_801cf9c7_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_gemeente_id_801cf9c7_like ON bag_gemeente USING btree (id varchar_pattern_ops);


--
-- TOC entry 3813 (class 1259 OID 645414)
-- Name: bag_grootstedelijkgebied_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_grootstedelijkgebied_geometrie_id ON bag_grootstedelijkgebied USING gist (geometrie);


--
-- TOC entry 3819 (class 1259 OID 645428)
-- Name: bag_ligplaats__gebiedsgerichtwerken_id_7921ca73; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats__gebiedsgerichtwerken_id_7921ca73 ON bag_ligplaats USING btree (_gebiedsgerichtwerken_id);


--
-- TOC entry 3820 (class 1259 OID 645429)
-- Name: bag_ligplaats__gebiedsgerichtwerken_id_7921ca73_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats__gebiedsgerichtwerken_id_7921ca73_like ON bag_ligplaats USING btree (_gebiedsgerichtwerken_id varchar_pattern_ops);


--
-- TOC entry 3821 (class 1259 OID 645430)
-- Name: bag_ligplaats__grootstedelijkgebied_id_b1924b41; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats__grootstedelijkgebied_id_b1924b41 ON bag_ligplaats USING btree (_grootstedelijkgebied_id);


--
-- TOC entry 3822 (class 1259 OID 645431)
-- Name: bag_ligplaats__grootstedelijkgebied_id_b1924b41_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats__grootstedelijkgebied_id_b1924b41_like ON bag_ligplaats USING btree (_grootstedelijkgebied_id varchar_pattern_ops);


--
-- TOC entry 3823 (class 1259 OID 645432)
-- Name: bag_ligplaats__openbare_ruimte_naam__h_f2abf2c6_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats__openbare_ruimte_naam__h_f2abf2c6_idx ON bag_ligplaats USING btree (_openbare_ruimte_naam, _huisnummer, _huisletter, _huisnummer_toevoeging);


--
-- TOC entry 3824 (class 1259 OID 645433)
-- Name: bag_ligplaats_bron_id_9916456f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_bron_id_9916456f ON bag_ligplaats USING btree (bron_id);


--
-- TOC entry 3825 (class 1259 OID 645434)
-- Name: bag_ligplaats_bron_id_9916456f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_bron_id_9916456f_like ON bag_ligplaats USING btree (bron_id varchar_pattern_ops);


--
-- TOC entry 3826 (class 1259 OID 645435)
-- Name: bag_ligplaats_buurt_id_596acb57; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_buurt_id_596acb57 ON bag_ligplaats USING btree (buurt_id);


--
-- TOC entry 3827 (class 1259 OID 645436)
-- Name: bag_ligplaats_buurt_id_596acb57_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_buurt_id_596acb57_like ON bag_ligplaats USING btree (buurt_id varchar_pattern_ops);


--
-- TOC entry 3828 (class 1259 OID 645437)
-- Name: bag_ligplaats_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_geometrie_id ON bag_ligplaats USING gist (geometrie);


--
-- TOC entry 3829 (class 1259 OID 645438)
-- Name: bag_ligplaats_id_a6e0cc61_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_id_a6e0cc61_like ON bag_ligplaats USING btree (id varchar_pattern_ops);


--
-- TOC entry 3830 (class 1259 OID 645439)
-- Name: bag_ligplaats_landelijk_id_8c52853f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_landelijk_id_8c52853f_like ON bag_ligplaats USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3835 (class 1259 OID 645443)
-- Name: bag_ligplaats_status_2c8abc61; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_status_2c8abc61 ON bag_ligplaats USING btree (status);


--
-- TOC entry 3836 (class 1259 OID 645447)
-- Name: bag_ligplaats_status_2c8abc61_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_ligplaats_status_2c8abc61_like ON bag_ligplaats USING btree (status varchar_pattern_ops);


--
-- TOC entry 3840 (class 1259 OID 646664)
-- Name: bag_nummeraanduiding__openbare_ruimte_naam_hu_0a789e26_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding__openbare_ruimte_naam_hu_0a789e26_idx ON bag_nummeraanduiding USING btree (_openbare_ruimte_naam, huisnummer, huisletter, huisnummer_toevoeging);


--
-- TOC entry 3841 (class 1259 OID 646670)
-- Name: bag_nummeraanduiding_bron_id_69a6a637; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_bron_id_69a6a637 ON bag_nummeraanduiding USING btree (bron_id);


--
-- TOC entry 3842 (class 1259 OID 646671)
-- Name: bag_nummeraanduiding_bron_id_69a6a637_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_bron_id_69a6a637_like ON bag_nummeraanduiding USING btree (bron_id varchar_pattern_ops);


--
-- TOC entry 3843 (class 1259 OID 646672)
-- Name: bag_nummeraanduiding_id_af996b5f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_id_af996b5f_like ON bag_nummeraanduiding USING btree (id varchar_pattern_ops);


--
-- TOC entry 3844 (class 1259 OID 646673)
-- Name: bag_nummeraanduiding_landelijk_id_4305fe04_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_landelijk_id_4305fe04_like ON bag_nummeraanduiding USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3847 (class 1259 OID 646674)
-- Name: bag_nummeraanduiding_ligplaats_id_ccf19788; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_ligplaats_id_ccf19788 ON bag_nummeraanduiding USING btree (ligplaats_id);


--
-- TOC entry 3848 (class 1259 OID 646675)
-- Name: bag_nummeraanduiding_ligplaats_id_ccf19788_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_ligplaats_id_ccf19788_like ON bag_nummeraanduiding USING btree (ligplaats_id varchar_pattern_ops);


--
-- TOC entry 3849 (class 1259 OID 646676)
-- Name: bag_nummeraanduiding_openbare_ruimte_id_70ec9873; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_openbare_ruimte_id_70ec9873 ON bag_nummeraanduiding USING btree (openbare_ruimte_id);


--
-- TOC entry 3850 (class 1259 OID 646677)
-- Name: bag_nummeraanduiding_openbare_ruimte_id_70ec9873_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_openbare_ruimte_id_70ec9873_like ON bag_nummeraanduiding USING btree (openbare_ruimte_id varchar_pattern_ops);


--
-- TOC entry 3853 (class 1259 OID 646678)
-- Name: bag_nummeraanduiding_standplaats_id_e4275a89; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_standplaats_id_e4275a89 ON bag_nummeraanduiding USING btree (standplaats_id);


--
-- TOC entry 3854 (class 1259 OID 646679)
-- Name: bag_nummeraanduiding_standplaats_id_e4275a89_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_standplaats_id_e4275a89_like ON bag_nummeraanduiding USING btree (standplaats_id varchar_pattern_ops);


--
-- TOC entry 3855 (class 1259 OID 646680)
-- Name: bag_nummeraanduiding_status_cca87526; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_status_cca87526 ON bag_nummeraanduiding USING btree (status);


--
-- TOC entry 3856 (class 1259 OID 646681)
-- Name: bag_nummeraanduiding_status_cca87526_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_status_cca87526_like ON bag_nummeraanduiding USING btree (status varchar_pattern_ops);


--
-- TOC entry 3857 (class 1259 OID 646682)
-- Name: bag_nummeraanduiding_verblijfsobject_id_ffa54442; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_verblijfsobject_id_ffa54442 ON bag_nummeraanduiding USING btree (verblijfsobject_id);


--
-- TOC entry 3858 (class 1259 OID 646683)
-- Name: bag_nummeraanduiding_verblijfsobject_id_ffa54442_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_nummeraanduiding_verblijfsobject_id_ffa54442_like ON bag_nummeraanduiding USING btree (verblijfsobject_id varchar_pattern_ops);


--
-- TOC entry 3859 (class 1259 OID 646585)
-- Name: bag_openbareruimte_bron_id_cbea113b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_bron_id_cbea113b ON bag_openbareruimte USING btree (bron_id);


--
-- TOC entry 3860 (class 1259 OID 646586)
-- Name: bag_openbareruimte_bron_id_cbea113b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_bron_id_cbea113b_like ON bag_openbareruimte USING btree (bron_id varchar_pattern_ops);


--
-- TOC entry 3864 (class 1259 OID 646588)
-- Name: bag_openbareruimte_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_geometrie_id ON bag_openbareruimte USING gist (geometrie);


--
-- TOC entry 3865 (class 1259 OID 646589)
-- Name: bag_openbareruimte_id_baceaee3_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_id_baceaee3_like ON bag_openbareruimte USING btree (id varchar_pattern_ops);


--
-- TOC entry 3866 (class 1259 OID 646590)
-- Name: bag_openbareruimte_landelijk_id_2e2c50bb_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_landelijk_id_2e2c50bb_like ON bag_openbareruimte USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3871 (class 1259 OID 646591)
-- Name: bag_openbareruimte_status_2129d363; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_status_2129d363 ON bag_openbareruimte USING btree (status);


--
-- TOC entry 3872 (class 1259 OID 646592)
-- Name: bag_openbareruimte_status_2129d363_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_status_2129d363_like ON bag_openbareruimte USING btree (status varchar_pattern_ops);


--
-- TOC entry 3873 (class 1259 OID 646593)
-- Name: bag_openbareruimte_woonplaats_id_487c4f06; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_woonplaats_id_487c4f06 ON bag_openbareruimte USING btree (woonplaats_id);


--
-- TOC entry 3874 (class 1259 OID 646594)
-- Name: bag_openbareruimte_woonplaats_id_487c4f06_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_openbareruimte_woonplaats_id_487c4f06_like ON bag_openbareruimte USING btree (woonplaats_id varchar_pattern_ops);


--
-- TOC entry 3875 (class 1259 OID 646597)
-- Name: bag_pand_bouwblok_id_bd200ca2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_bouwblok_id_bd200ca2 ON bag_pand USING btree (bouwblok_id);


--
-- TOC entry 3876 (class 1259 OID 646598)
-- Name: bag_pand_bouwblok_id_bd200ca2_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_bouwblok_id_bd200ca2_like ON bag_pand USING btree (bouwblok_id varchar_pattern_ops);


--
-- TOC entry 3877 (class 1259 OID 646599)
-- Name: bag_pand_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_geometrie_id ON bag_pand USING gist (geometrie);


--
-- TOC entry 3878 (class 1259 OID 646600)
-- Name: bag_pand_id_7652a149_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_id_7652a149_like ON bag_pand USING btree (id varchar_pattern_ops);


--
-- TOC entry 3879 (class 1259 OID 646601)
-- Name: bag_pand_landelijk_id_a00fbb2c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_landelijk_id_a00fbb2c_like ON bag_pand USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3884 (class 1259 OID 646602)
-- Name: bag_pand_status_1855bcfd; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_status_1855bcfd ON bag_pand USING btree (status);


--
-- TOC entry 3885 (class 1259 OID 646603)
-- Name: bag_pand_status_1855bcfd_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_pand_status_1855bcfd_like ON bag_pand USING btree (status varchar_pattern_ops);


--
-- TOC entry 3892 (class 1259 OID 645541)
-- Name: bag_stadsdeel_code_12eafcba_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_stadsdeel_code_12eafcba_like ON bag_stadsdeel USING btree (code varchar_pattern_ops);


--
-- TOC entry 3895 (class 1259 OID 645542)
-- Name: bag_stadsdeel_gemeente_id_3f93513f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_stadsdeel_gemeente_id_3f93513f ON bag_stadsdeel USING btree (gemeente_id);


--
-- TOC entry 3896 (class 1259 OID 645543)
-- Name: bag_stadsdeel_gemeente_id_3f93513f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_stadsdeel_gemeente_id_3f93513f_like ON bag_stadsdeel USING btree (gemeente_id varchar_pattern_ops);


--
-- TOC entry 3897 (class 1259 OID 645544)
-- Name: bag_stadsdeel_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_stadsdeel_geometrie_id ON bag_stadsdeel USING gist (geometrie);


--
-- TOC entry 3898 (class 1259 OID 645545)
-- Name: bag_stadsdeel_id_7c99b001_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_stadsdeel_id_7c99b001_like ON bag_stadsdeel USING btree (id varchar_pattern_ops);


--
-- TOC entry 3901 (class 1259 OID 645550)
-- Name: bag_standplaats__gebiedsgerichtwerken_id_82c43a3b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats__gebiedsgerichtwerken_id_82c43a3b ON bag_standplaats USING btree (_gebiedsgerichtwerken_id);


--
-- TOC entry 3902 (class 1259 OID 645551)
-- Name: bag_standplaats__gebiedsgerichtwerken_id_82c43a3b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats__gebiedsgerichtwerken_id_82c43a3b_like ON bag_standplaats USING btree (_gebiedsgerichtwerken_id varchar_pattern_ops);


--
-- TOC entry 3903 (class 1259 OID 645552)
-- Name: bag_standplaats__grootstedelijkgebied_id_c782a144; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats__grootstedelijkgebied_id_c782a144 ON bag_standplaats USING btree (_grootstedelijkgebied_id);


--
-- TOC entry 3904 (class 1259 OID 645553)
-- Name: bag_standplaats__grootstedelijkgebied_id_c782a144_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats__grootstedelijkgebied_id_c782a144_like ON bag_standplaats USING btree (_grootstedelijkgebied_id varchar_pattern_ops);


--
-- TOC entry 3905 (class 1259 OID 645554)
-- Name: bag_standplaats__openbare_ruimte_naam__h_7afe0a70_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats__openbare_ruimte_naam__h_7afe0a70_idx ON bag_standplaats USING btree (_openbare_ruimte_naam, _huisnummer, _huisletter, _huisnummer_toevoeging);


--
-- TOC entry 3906 (class 1259 OID 645555)
-- Name: bag_standplaats_bron_id_0f958d87; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_bron_id_0f958d87 ON bag_standplaats USING btree (bron_id);


--
-- TOC entry 3907 (class 1259 OID 645556)
-- Name: bag_standplaats_bron_id_0f958d87_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_bron_id_0f958d87_like ON bag_standplaats USING btree (bron_id varchar_pattern_ops);


--
-- TOC entry 3908 (class 1259 OID 645557)
-- Name: bag_standplaats_buurt_id_efa5da1b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_buurt_id_efa5da1b ON bag_standplaats USING btree (buurt_id);


--
-- TOC entry 3909 (class 1259 OID 645558)
-- Name: bag_standplaats_buurt_id_efa5da1b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_buurt_id_efa5da1b_like ON bag_standplaats USING btree (buurt_id varchar_pattern_ops);


--
-- TOC entry 3910 (class 1259 OID 645559)
-- Name: bag_standplaats_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_geometrie_id ON bag_standplaats USING gist (geometrie);


--
-- TOC entry 3911 (class 1259 OID 645560)
-- Name: bag_standplaats_id_ba68ff9c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_id_ba68ff9c_like ON bag_standplaats USING btree (id varchar_pattern_ops);


--
-- TOC entry 3912 (class 1259 OID 645561)
-- Name: bag_standplaats_landelijk_id_7ff59407_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_landelijk_id_7ff59407_like ON bag_standplaats USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3917 (class 1259 OID 645562)
-- Name: bag_standplaats_status_7aa01805; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_status_7aa01805 ON bag_standplaats USING btree (status);


--
-- TOC entry 3918 (class 1259 OID 645563)
-- Name: bag_standplaats_status_7aa01805_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_standplaats_status_7aa01805_like ON bag_standplaats USING btree (status varchar_pattern_ops);


--
-- TOC entry 3925 (class 1259 OID 645572)
-- Name: bag_unesco_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_unesco_geometrie_id ON bag_unesco USING gist (geometrie);


--
-- TOC entry 3928 (class 1259 OID 646720)
-- Name: bag_verblijfsobject__gebiedsgerichtwerken_id_45ee3c7a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject__gebiedsgerichtwerken_id_45ee3c7a ON bag_verblijfsobject USING btree (_gebiedsgerichtwerken_id);


--
-- TOC entry 3929 (class 1259 OID 646721)
-- Name: bag_verblijfsobject__gebiedsgerichtwerken_id_45ee3c7a_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject__gebiedsgerichtwerken_id_45ee3c7a_like ON bag_verblijfsobject USING btree (_gebiedsgerichtwerken_id varchar_pattern_ops);


--
-- TOC entry 3930 (class 1259 OID 646722)
-- Name: bag_verblijfsobject__grootstedelijkgebied_id_197094b4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject__grootstedelijkgebied_id_197094b4 ON bag_verblijfsobject USING btree (_grootstedelijkgebied_id);


--
-- TOC entry 3931 (class 1259 OID 646723)
-- Name: bag_verblijfsobject__grootstedelijkgebied_id_197094b4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject__grootstedelijkgebied_id_197094b4_like ON bag_verblijfsobject USING btree (_grootstedelijkgebied_id varchar_pattern_ops);


--
-- TOC entry 3932 (class 1259 OID 646724)
-- Name: bag_verblijfsobject__openbare_ruimte_naam__h_fda887bb_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject__openbare_ruimte_naam__h_fda887bb_idx ON bag_verblijfsobject USING btree (_openbare_ruimte_naam, _huisnummer, _huisletter, _huisnummer_toevoeging);


--
-- TOC entry 3933 (class 1259 OID 646725)
-- Name: bag_verblijfsobject_bron_id_6983ff76; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_bron_id_6983ff76 ON bag_verblijfsobject USING btree (bron_id);


--
-- TOC entry 3934 (class 1259 OID 646726)
-- Name: bag_verblijfsobject_bron_id_6983ff76_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_bron_id_6983ff76_like ON bag_verblijfsobject USING btree (bron_id varchar_pattern_ops);


--
-- TOC entry 3935 (class 1259 OID 646727)
-- Name: bag_verblijfsobject_buurt_id_147c7220; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_buurt_id_147c7220 ON bag_verblijfsobject USING btree (buurt_id);


--
-- TOC entry 3936 (class 1259 OID 646728)
-- Name: bag_verblijfsobject_buurt_id_147c7220_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_buurt_id_147c7220_like ON bag_verblijfsobject USING btree (buurt_id varchar_pattern_ops);


--
-- TOC entry 3941 (class 1259 OID 646733)
-- Name: bag_verblijfsobject_gebruik_id_750be72a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_gebruik_750be72a ON bag_verblijfsobject USING btree (gebruik);


--
-- TOC entry 3942 (class 1259 OID 646735)
-- Name: bag_verblijfsobject_gebruik_750be72a_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_gebruik_750be72a_like ON bag_verblijfsobject USING btree (gebruik varchar_pattern_ops);


--
-- TOC entry 3943 (class 1259 OID 646736)
-- Name: bag_verblijfsobject_geometrie_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_geometrie_id ON bag_verblijfsobject USING gist (geometrie);


--
-- TOC entry 3944 (class 1259 OID 646737)
-- Name: bag_verblijfsobject_id_3390cd84_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_id_3390cd84_like ON bag_verblijfsobject USING btree (id varchar_pattern_ops);


--
-- TOC entry 3945 (class 1259 OID 646738)
-- Name: bag_verblijfsobject_landelijk_id_7b44ae0d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_landelijk_id_7b44ae0d_like ON bag_verblijfsobject USING btree (landelijk_id varchar_pattern_ops);


--
-- TOC entry 3954 (class 1259 OID 646750)
-- Name: bag_verblijfsobject_reden_afvoer_d63ad9d4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_reden_afvoer_d63ad9d4 ON bag_verblijfsobject USING btree (reden_afvoer);


--
-- TOC entry 3955 (class 1259 OID 646751)
-- Name: bag_verblijfsobject_reden_afvoer_d63ad9d4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_reden_afvoer_d63ad9d4_like ON bag_verblijfsobject USING btree (reden_afvoer varchar_pattern_ops);


--
-- TOC entry 3956 (class 1259 OID 646752)
-- Name: bag_verblijfsobject_reden_opvoer_91720c49; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_reden_opvoer_91720c49 ON bag_verblijfsobject USING btree (reden_opvoer);


--
-- TOC entry 3957 (class 1259 OID 646753)
-- Name: bag_verblijfsobject_reden_opvoer_91720c49_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_reden_opvoer_91720c49_like ON bag_verblijfsobject USING btree (reden_opvoer varchar_pattern_ops);


--
-- TOC entry 3958 (class 1259 OID 646755)
-- Name: bag_verblijfsobject_status_8e52e07c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_status_8e52e07c ON bag_verblijfsobject USING btree (status);


--
-- TOC entry 3959 (class 1259 OID 646756)
-- Name: bag_verblijfsobject_status_8e52e07c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_status_8e52e07c_like ON bag_verblijfsobject USING btree (status varchar_pattern_ops);


--
-- TOC entry 3960 (class 1259 OID 646757)
-- Name: bag_verblijfsobject_toegang_d5013226; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_toegang_d5013226 ON bag_verblijfsobject USING btree (toegang);


--
-- TOC entry 3961 (class 1259 OID 646758)
-- Name: bag_verblijfsobject_toegang_d5013226_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobject_toegang_d5013226_like ON bag_verblijfsobject USING btree (toegang varchar_pattern_ops);


--
-- TOC entry 3962 (class 1259 OID 646604)
-- Name: bag_verblijfsobjectpandrelatie_id_ca3665bd_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobjectpandrelatie_id_ca3665bd_like ON bag_verblijfsobjectpandrelatie USING btree (id varchar_pattern_ops);


--
-- TOC entry 3963 (class 1259 OID 646605)
-- Name: bag_verblijfsobjectpandrelatie_pand_id_083a5748; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobjectpandrelatie_pand_id_083a5748 ON bag_verblijfsobjectpandrelatie USING btree (pand_id);


--
-- TOC entry 3964 (class 1259 OID 646606)
-- Name: bag_verblijfsobjectpandrelatie_pand_id_083a5748_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobjectpandrelatie_pand_id_083a5748_like ON bag_verblijfsobjectpandrelatie USING btree (pand_id varchar_pattern_ops);


--
-- TOC entry 3967 (class 1259 OID 646607)
-- Name: bag_verblijfsobjectpandrelatie_verblijfsobject_id_95cc1b5b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobjectpandrelatie_verblijfsobject_id_95cc1b5b ON bag_verblijfsobjectpandrelatie USING btree (verblijfsobject_id);


--
-- TOC entry 3968 (class 1259 OID 646608)
-- Name: bag_verblijfsobjectpandrelatie_verblijfsobject_id_95cc1b5b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_verblijfsobjectpandrelatie_verblijfsobject_id_95cc1b5b_like ON bag_verblijfsobjectpandrelatie USING btree (verblijfsobject_id varchar_pattern_ops);


--
-- TOC entry 3969 (class 1259 OID 646556)
-- Name: bag_woonplaats_gemeente_id_672595f6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_woonplaats_gemeente_id_672595f6 ON bag_woonplaats USING btree (gemeente_id);


--
-- TOC entry 3970 (class 1259 OID 646557)
-- Name: bag_woonplaats_gemeente_id_672595f6_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_woonplaats_gemeente_id_672595f6_like ON bag_woonplaats USING btree (gemeente_id varchar_pattern_ops);


--
-- TOC entry 3971 (class 1259 OID 646558)
-- Name: bag_woonplaats_id_3b960ae1_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_woonplaats_id_3b960ae1_like ON bag_woonplaats USING btree (id varchar_pattern_ops);


--
-- TOC entry 3972 (class 1259 OID 646559)
-- Name: bag_woonplaats_landelijk_id_53bb97c0_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX bag_woonplaats_landelijk_id_53bb97c0_like ON bag_woonplaats USING btree (landelijk_id varchar_pattern_ops);


