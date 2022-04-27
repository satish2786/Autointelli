--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: admin_bmc; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.admin_bmc (
    itsm_id integer NOT NULL,
    communication_type text,
    ip text NOT NULL,
    port integer NOT NULL,
    username text,
    password text,
    first_name text,
    last_name text,
    assignment_group_automation text,
    assignment_group_manual text,
    itsm_status text,
    priority text,
    impact text,
    urgency text,
    source text,
    service_type text,
    customer_name text,
    status text,
    createdtime timestamp without time zone DEFAULT now(),
    createdby text,
    modifiedtime timestamp without time zone,
    modifiedby text
);


ALTER TABLE public.admin_bmc OWNER TO autointelli;

--
-- Name: admin_bmc_itsm_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.admin_bmc_itsm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_bmc_itsm_id_seq OWNER TO autointelli;

--
-- Name: admin_bmc_itsm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.admin_bmc_itsm_id_seq OWNED BY public.admin_bmc.itsm_id;


--
-- Name: admin_integration_meta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.admin_integration_meta (
    id integer NOT NULL,
    integration_name text NOT NULL,
    integration_type text NOT NULL,
    status text NOT NULL
);


ALTER TABLE public.admin_integration_meta OWNER TO autointelli;

--
-- Name: admin_integration_meta_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.admin_integration_meta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_integration_meta_id_seq OWNER TO autointelli;

--
-- Name: admin_integration_meta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.admin_integration_meta_id_seq OWNED BY public.admin_integration_meta.id;


--
-- Name: admin_otrs; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.admin_otrs (
    itsm_id integer NOT NULL,
    communication_type text,
    ip text NOT NULL,
    port integer NOT NULL,
    username text,
    password text,
    assignment_group_automation text,
    assignment_group_manual text,
    itsm_status text,
    priority text,
    customer_name text,
    status text,
    createdtime timestamp without time zone DEFAULT now(),
    createdby text,
    modifiedtime timestamp without time zone,
    modifiedby text,
    itsm_wip_status text,
    itsm_res_status text
);


ALTER TABLE public.admin_otrs OWNER TO autointelli;

--
-- Name: admin_otrs_itsm_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.admin_otrs_itsm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_otrs_itsm_id_seq OWNER TO autointelli;

--
-- Name: admin_otrs_itsm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.admin_otrs_itsm_id_seq OWNED BY public.admin_otrs.itsm_id;


--
-- Name: admin_sdp; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.admin_sdp (
    itsm_id integer NOT NULL,
    communication_type text NOT NULL,
    ip text NOT NULL,
    port text NOT NULL,
    technician_key text NOT NULL,
    priority text NOT NULL,
    assignment_group_automation text NOT NULL,
    assignment_group_manual text NOT NULL,
    itsm_status text NOT NULL,
    service_category text NOT NULL,
    level text NOT NULL,
    status text NOT NULL,
    createdtime timestamp without time zone DEFAULT now(),
    createdby text,
    modifiedtime timestamp without time zone,
    modifiedby text,
    requester text NOT NULL,
    requesttemplate text NOT NULL,
    technician text NOT NULL,
    itsm_wip_status text NOT NULL,
    itsm_res_status text NOT NULL
);


ALTER TABLE public.admin_sdp OWNER TO autointelli;

--
-- Name: admin_sdp_itsm_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.admin_sdp_itsm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_sdp_itsm_id_seq OWNER TO autointelli;

--
-- Name: admin_sdp_itsm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.admin_sdp_itsm_id_seq OWNED BY public.admin_sdp.itsm_id;


--
-- Name: ai_application; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_application (
    application_id bigint NOT NULL,
    application_name character varying(200),
    fk_customer_id integer,
    application_class character varying(200),
    active_yn character varying(1),
    application_subclass character varying(200)
);


ALTER TABLE public.ai_application OWNER TO autointelli;

--
-- Name: ai_application_application_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_application_application_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_application_application_id_seq OWNER TO autointelli;

--
-- Name: ai_application_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_application_application_id_seq OWNED BY public.ai_application.application_id;


--
-- Name: ai_application_class; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_application_class (
    aclass_id bigint NOT NULL,
    aclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_application_class OWNER TO autointelli;

--
-- Name: ai_application_class_aclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_application_class_aclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_application_class_aclass_id_seq OWNER TO autointelli;

--
-- Name: ai_application_class_aclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_application_class_aclass_id_seq OWNED BY public.ai_application_class.aclass_id;


--
-- Name: ai_application_subclass; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_application_subclass (
    asclass_id bigint NOT NULL,
    asclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_application_subclass OWNER TO autointelli;

--
-- Name: ai_application_subclass_asclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_application_subclass_asclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_application_subclass_asclass_id_seq OWNER TO autointelli;

--
-- Name: ai_application_subclass_asclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_application_subclass_asclass_id_seq OWNED BY public.ai_application_subclass.asclass_id;


--
-- Name: ai_auto_classify_new; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_auto_classify_new (
    pk_id bigint NOT NULL,
    interaction character varying(20),
    open_time timestamp without time zone,
    category character varying(30),
    sub_category character varying(200),
    area character varying(200),
    sub_area character varying(200),
    assignment_group character varying(300),
    status character varying(30),
    description character varying,
    learning json
);


ALTER TABLE public.ai_auto_classify_new OWNER TO autointelli;

--
-- Name: ai_auto_classify_new_pk_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_auto_classify_new_pk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_auto_classify_new_pk_id_seq OWNER TO autointelli;

--
-- Name: ai_auto_classify_new_pk_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_auto_classify_new_pk_id_seq OWNED BY public.ai_auto_classify_new.pk_id;


--
-- Name: ai_automation_execution_history; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_automation_execution_history (
    pk_history_id integer NOT NULL,
    fk_execution_id integer NOT NULL,
    fk_stage_id integer NOT NULL,
    output text NOT NULL,
    status text NOT NULL,
    starttime numeric(20,5),
    endtime numeric(20,5)
);


ALTER TABLE public.ai_automation_execution_history OWNER TO autointelli;

--
-- Name: ai_automation_execution_history_pk_history_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_automation_execution_history_pk_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_automation_execution_history_pk_history_id_seq OWNER TO autointelli;

--
-- Name: ai_automation_execution_history_pk_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_automation_execution_history_pk_history_id_seq OWNED BY public.ai_automation_execution_history.pk_history_id;


--
-- Name: ai_automation_executions; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_automation_executions (
    pk_execution_id integer NOT NULL,
    fk_bot_id integer,
    fk_alert_id integer,
    execution_status text,
    starttime numeric(20,5),
    endtime numeric(20,5)
);


ALTER TABLE public.ai_automation_executions OWNER TO autointelli;

--
-- Name: ai_automation_executions_pk_execution_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_automation_executions_pk_execution_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_automation_executions_pk_execution_id_seq OWNER TO autointelli;

--
-- Name: ai_automation_executions_pk_execution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_automation_executions_pk_execution_id_seq OWNED BY public.ai_automation_executions.pk_execution_id;


--
-- Name: ai_automation_stages; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_automation_stages (
    stageid integer NOT NULL,
    stages text NOT NULL
);


ALTER TABLE public.ai_automation_stages OWNER TO autointelli;

--
-- Name: ai_automation_type; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_automation_type (
    methodid integer NOT NULL,
    automated text NOT NULL
);


ALTER TABLE public.ai_automation_type OWNER TO autointelli;

--
-- Name: ai_automation_type_methodid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_automation_type_methodid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_automation_type_methodid_seq OWNER TO autointelli;

--
-- Name: ai_automation_type_methodid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_automation_type_methodid_seq OWNED BY public.ai_automation_type.methodid;


--
-- Name: ai_bot_repo; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_bot_repo (
    pk_bot_id integer NOT NULL,
    bot_type text NOT NULL,
    bot_name text NOT NULL,
    bot_description text NOT NULL,
    bot_language text NOT NULL,
    script text NOT NULL,
    platform_type text NOT NULL,
    os_type text NOT NULL,
    component text NOT NULL,
    created_date numeric(20,5),
    modified_date numeric(20,5),
    botargs text,
    created_by text,
    bot_system integer,
    fk_branch_id integer,
    active_yn character varying(1)
);


ALTER TABLE public.ai_bot_repo OWNER TO autointelli;

--
-- Name: ai_bot_repo_pk_bot_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_bot_repo_pk_bot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_bot_repo_pk_bot_id_seq OWNER TO autointelli;

--
-- Name: ai_bot_repo_pk_bot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_bot_repo_pk_bot_id_seq OWNED BY public.ai_bot_repo.pk_bot_id;


--
-- Name: ai_bot_tree; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_bot_tree (
    pk_tree_id bigint NOT NULL,
    name character varying(100),
    type character varying(1),
    fk_parent_id integer,
    active_yn character varying(1)
);


ALTER TABLE public.ai_bot_tree OWNER TO autointelli;

--
-- Name: ai_bot_tree_pk_tree_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_bot_tree_pk_tree_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_bot_tree_pk_tree_id_seq OWNER TO autointelli;

--
-- Name: ai_bot_tree_pk_tree_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_bot_tree_pk_tree_id_seq OWNED BY public.ai_bot_tree.pk_tree_id;


--
-- Name: ai_cmdb; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_cmdb (
    cmdbid integer NOT NULL,
    hostname text NOT NULL,
    ipaddress text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    reachability text,
    remarks text,
    status text,
    lastaccessstime numeric(20,5)
);


ALTER TABLE public.ai_cmdb OWNER TO autointelli;

--
-- Name: ai_cmdb_cmdbid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_cmdb_cmdbid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_cmdb_cmdbid_seq OWNER TO autointelli;

--
-- Name: ai_cmdb_cmdbid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_cmdb_cmdbid_seq OWNED BY public.ai_cmdb.cmdbid;


--
-- Name: ai_device_credentials; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_device_credentials (
    cred_id bigint NOT NULL,
    cred_name character varying(50),
    cred_type character varying(10),
    username character varying(100),
    password character varying(200),
    sudo_yn character varying(1),
    field_2 character varying(1),
    field_3 character varying(1),
    field_4 character varying(1),
    active_yn character varying(1),
    port integer
);


ALTER TABLE public.ai_device_credentials OWNER TO autointelli;

--
-- Name: ai_device_discovery; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_device_discovery (
    pk_discovery_id bigint NOT NULL,
    ip_address character varying(50),
    operating_system character varying(50),
    fk_cred_id integer,
    gf_yn character varying(1),
    gf_error character varying(4000)
);


ALTER TABLE public.ai_device_discovery OWNER TO autointelli;

--
-- Name: ai_itsm_rest_master; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_itsm_rest_master (
    pk_itsm_rest_id bigint NOT NULL,
    itsm_name character varying(50),
    itsm_rest_name character varying(100),
    itsm_rest_url character varying(300),
    itsm_rest_method character varying(10),
    itsm_rest_params json,
    active_yn character(1),
    select_items character varying(100)
);


ALTER TABLE public.ai_itsm_rest_master OWNER TO autointelli;

--
-- Name: ai_itsm_rest_master_pk_itsm_rest_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_itsm_rest_master_pk_itsm_rest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_itsm_rest_master_pk_itsm_rest_id_seq OWNER TO autointelli;

--
-- Name: ai_itsm_rest_master_pk_itsm_rest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_itsm_rest_master_pk_itsm_rest_id_seq OWNED BY public.ai_itsm_rest_master.pk_itsm_rest_id;


--
-- Name: ai_license; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_license (
    pk_license_id bigint NOT NULL,
    license_str character varying(1000),
    active_yn character(1),
    created_date timestamp without time zone
);


ALTER TABLE public.ai_license OWNER TO autointelli;

--
-- Name: ai_license_pk_license_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_license_pk_license_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_license_pk_license_id_seq OWNER TO autointelli;

--
-- Name: ai_license_pk_license_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_license_pk_license_id_seq OWNED BY public.ai_license.pk_license_id;


--
-- Name: ai_machine; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_machine (
    machine_id bigint NOT NULL,
    machine_fqdn character varying(200),
    platform character varying(200),
    osname character varying(100),
    osversion character varying(20),
    remediate character varying(1),
    attribute json,
    fk_customer_id integer,
    ip_address character varying(20),
    fk_cred_id integer,
    active_yn character varying(1),
    inventory jsonb
);


ALTER TABLE public.ai_machine OWNER TO autointelli;

--
-- Name: ai_machine_class; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_machine_class (
    mclass_id bigint NOT NULL,
    mclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_machine_class OWNER TO autointelli;

--
-- Name: ai_machine_class_mclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_machine_class_mclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_machine_class_mclass_id_seq OWNER TO autointelli;

--
-- Name: ai_machine_class_mclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_machine_class_mclass_id_seq OWNED BY public.ai_machine_class.mclass_id;


--
-- Name: ai_machine_group_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_machine_group_mapping (
    pk_machine_group_map_id bigint NOT NULL,
    fk_group_id integer,
    fk_machine_id integer
);


ALTER TABLE public.ai_machine_group_mapping OWNER TO autointelli;

--
-- Name: ai_machine_group_mapping_pk_machine_group_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_machine_group_mapping_pk_machine_group_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_machine_group_mapping_pk_machine_group_map_id_seq OWNER TO autointelli;

--
-- Name: ai_machine_group_mapping_pk_machine_group_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_machine_group_mapping_pk_machine_group_map_id_seq OWNED BY public.ai_machine_group_mapping.pk_machine_group_map_id;


--
-- Name: ai_machine_grouping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_machine_grouping (
    pk_ai_machine_group_id bigint NOT NULL,
    group_name character varying(200),
    group_description character varying(1000),
    active_yn character(1)
);


ALTER TABLE public.ai_machine_grouping OWNER TO autointelli;

--
-- Name: ai_machine_grouping_pk_ai_machine_group_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_machine_grouping_pk_ai_machine_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_machine_grouping_pk_ai_machine_group_id_seq OWNER TO autointelli;

--
-- Name: ai_machine_grouping_pk_ai_machine_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_machine_grouping_pk_ai_machine_group_id_seq OWNED BY public.ai_machine_grouping.pk_ai_machine_group_id;


--
-- Name: ai_machine_machine_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_machine_machine_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_machine_machine_id_seq OWNER TO autointelli;

--
-- Name: ai_machine_machine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_machine_machine_id_seq OWNED BY public.ai_machine.machine_id;


--
-- Name: ai_machine_software_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_machine_software_mapping (
    ams_id bigint NOT NULL,
    fk_machine_id integer,
    fk_software_id integer
);


ALTER TABLE public.ai_machine_software_mapping OWNER TO autointelli;

--
-- Name: ai_machine_software_mapping_ams_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_machine_software_mapping_ams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_machine_software_mapping_ams_id_seq OWNER TO autointelli;

--
-- Name: ai_machine_software_mapping_ams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_machine_software_mapping_ams_id_seq OWNED BY public.ai_machine_software_mapping.ams_id;


--
-- Name: ai_network; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_network (
    device_id bigint NOT NULL,
    device_ip character varying(100),
    platform character varying(200),
    osname character varying(100),
    osversion character varying(20),
    attribute json,
    fk_customer_id integer
);


ALTER TABLE public.ai_network OWNER TO autointelli;

--
-- Name: ai_network_device_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_network_device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_network_device_id_seq OWNER TO autointelli;

--
-- Name: ai_network_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_network_device_id_seq OWNED BY public.ai_network.device_id;


--
-- Name: ai_network_machine_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_network_machine_mapping (
    anm_id bigint NOT NULL,
    fk_device_id integer,
    fk_machine_id integer
);


ALTER TABLE public.ai_network_machine_mapping OWNER TO autointelli;

--
-- Name: ai_network_machine_mapping_anm_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_network_machine_mapping_anm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_network_machine_mapping_anm_id_seq OWNER TO autointelli;

--
-- Name: ai_network_machine_mapping_anm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_network_machine_mapping_anm_id_seq OWNED BY public.ai_network_machine_mapping.anm_id;


--
-- Name: ai_patch_automation; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_patch_automation (
    id integer NOT NULL,
    name text NOT NULL,
    servergroup text NOT NULL,
    lastruntime timestamp without time zone,
    result text,
    outputpath text,
    active_y_n text
);


ALTER TABLE public.ai_patch_automation OWNER TO autointelli;

--
-- Name: ai_patch_automation_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_patch_automation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_patch_automation_id_seq OWNER TO autointelli;

--
-- Name: ai_patch_automation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_patch_automation_id_seq OWNED BY public.ai_patch_automation.id;


--
-- Name: ai_policyaction_meta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_policyaction_meta (
    actionid integer NOT NULL,
    actionname text NOT NULL
);


ALTER TABLE public.ai_policyaction_meta OWNER TO autointelli;

--
-- Name: ai_policyaction_meta_actionid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_policyaction_meta_actionid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_policyaction_meta_actionid_seq OWNER TO autointelli;

--
-- Name: ai_policyaction_meta_actionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_policyaction_meta_actionid_seq OWNED BY public.ai_policyaction_meta.actionid;


--
-- Name: ai_policyoperator_meta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_policyoperator_meta (
    operatorid integer NOT NULL,
    operator text NOT NULL
);


ALTER TABLE public.ai_policyoperator_meta OWNER TO autointelli;

--
-- Name: ai_policyoperator_meta_operatorid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_policyoperator_meta_operatorid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_policyoperator_meta_operatorid_seq OWNER TO autointelli;

--
-- Name: ai_policyoperator_meta_operatorid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_policyoperator_meta_operatorid_seq OWNED BY public.ai_policyoperator_meta.operatorid;


--
-- Name: ai_resource; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_resource (
    resource_id bigint NOT NULL,
    resource_name character varying(200),
    fk_customer_id integer,
    resource_class character varying(200),
    active_yn character varying(1)
);


ALTER TABLE public.ai_resource OWNER TO autointelli;

--
-- Name: ai_resource_application_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_resource_application_mapping (
    ara_id bigint NOT NULL,
    fk_resource_id integer,
    fk_application_id integer
);


ALTER TABLE public.ai_resource_application_mapping OWNER TO autointelli;

--
-- Name: ai_resource_application_mapping_ara_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_resource_application_mapping_ara_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_resource_application_mapping_ara_id_seq OWNER TO autointelli;

--
-- Name: ai_resource_application_mapping_ara_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_resource_application_mapping_ara_id_seq OWNED BY public.ai_resource_application_mapping.ara_id;


--
-- Name: ai_resource_class; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_resource_class (
    rclass_id bigint NOT NULL,
    rclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_resource_class OWNER TO autointelli;

--
-- Name: ai_resource_class_rclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_resource_class_rclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_resource_class_rclass_id_seq OWNER TO autointelli;

--
-- Name: ai_resource_class_rclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_resource_class_rclass_id_seq OWNED BY public.ai_resource_class.rclass_id;


--
-- Name: ai_resource_resource_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_resource_resource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_resource_resource_id_seq OWNER TO autointelli;

--
-- Name: ai_resource_resource_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_resource_resource_id_seq OWNED BY public.ai_resource.resource_id;


--
-- Name: ai_software; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_software (
    software_id bigint NOT NULL,
    software_class character varying(200),
    software_subclass character varying(200),
    remediate character varying(1),
    attribute json,
    fk_customer_id integer,
    software_name character varying(200),
    active_yn character varying(1)
);


ALTER TABLE public.ai_software OWNER TO autointelli;

--
-- Name: ai_software_class; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_software_class (
    sclass_id bigint NOT NULL,
    sclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_software_class OWNER TO autointelli;

--
-- Name: ai_software_class_sclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_software_class_sclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_software_class_sclass_id_seq OWNER TO autointelli;

--
-- Name: ai_software_class_sclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_software_class_sclass_id_seq OWNED BY public.ai_software_class.sclass_id;


--
-- Name: ai_software_resource_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_software_resource_mapping (
    asr_id bigint NOT NULL,
    fk_software_id integer,
    fk_resource_id integer
);


ALTER TABLE public.ai_software_resource_mapping OWNER TO autointelli;

--
-- Name: ai_software_resource_mapping_asr_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_software_resource_mapping_asr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_software_resource_mapping_asr_id_seq OWNER TO autointelli;

--
-- Name: ai_software_resource_mapping_asr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_software_resource_mapping_asr_id_seq OWNED BY public.ai_software_resource_mapping.asr_id;


--
-- Name: ai_software_software_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_software_software_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_software_software_id_seq OWNER TO autointelli;

--
-- Name: ai_software_software_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_software_software_id_seq OWNED BY public.ai_software.software_id;


--
-- Name: ai_software_subclass; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_software_subclass (
    ssclass_id bigint NOT NULL,
    ssclass_name character varying(100),
    active_yn character varying(1)
);


ALTER TABLE public.ai_software_subclass OWNER TO autointelli;

--
-- Name: ai_software_subclass_ssclass_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_software_subclass_ssclass_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_software_subclass_ssclass_id_seq OWNER TO autointelli;

--
-- Name: ai_software_subclass_ssclass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_software_subclass_ssclass_id_seq OWNED BY public.ai_software_subclass.ssclass_id;


--
-- Name: ai_ticket_details; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_ticket_details (
    pk_id integer NOT NULL,
    fk_alert_id integer,
    ticket_no text,
    ticket_status text,
    created_date numeric(20,5),
    modified_date numeric(20,5)
);


ALTER TABLE public.ai_ticket_details OWNER TO autointelli;

--
-- Name: ai_ticket_details_pk_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_ticket_details_pk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_ticket_details_pk_id_seq OWNER TO autointelli;

--
-- Name: ai_ticket_details_pk_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_ticket_details_pk_id_seq OWNED BY public.ai_ticket_details.pk_id;


--
-- Name: ai_triage_dynamic_form; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_triage_dynamic_form (
    pk_triage_df bigint NOT NULL,
    fk_triage_id integer,
    form_control_label character varying(100),
    form_control_type character varying(100),
    form_control_order integer,
    active_yn character(1)
);


ALTER TABLE public.ai_triage_dynamic_form OWNER TO autointelli;

--
-- Name: ai_triage_dynamic_form_pk_triage_df_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_triage_dynamic_form_pk_triage_df_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_triage_dynamic_form_pk_triage_df_seq OWNER TO autointelli;

--
-- Name: ai_triage_dynamic_form_pk_triage_df_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_triage_dynamic_form_pk_triage_df_seq OWNED BY public.ai_triage_dynamic_form.pk_triage_df;


--
-- Name: ai_triage_history; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_triage_history (
    pk_triage_history_id bigint NOT NULL,
    fk_triage_id integer,
    fk_alert_id integer,
    output character varying(10000),
    created_dt timestamp without time zone
);


ALTER TABLE public.ai_triage_history OWNER TO autointelli;

--
-- Name: ai_triage_history_pk_triage_history_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_triage_history_pk_triage_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_triage_history_pk_triage_history_id_seq OWNER TO autointelli;

--
-- Name: ai_triage_history_pk_triage_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_triage_history_pk_triage_history_id_seq OWNED BY public.ai_triage_history.pk_triage_history_id;


--
-- Name: ai_triage_master; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ai_triage_master (
    pk_triage_id bigint NOT NULL,
    triage_name character varying(100),
    triage_desc character varying(300),
    triage_rest_call character varying(300),
    active_yn character(1)
);


ALTER TABLE public.ai_triage_master OWNER TO autointelli;

--
-- Name: ai_triage_master_pk_triage_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ai_triage_master_pk_triage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_triage_master_pk_triage_id_seq OWNER TO autointelli;

--
-- Name: ai_triage_master_pk_triage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ai_triage_master_pk_triage_id_seq OWNED BY public.ai_triage_master.pk_triage_id;


--
-- Name: alert_data; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.alert_data (
    pk_alert_id bigint NOT NULL,
    ci_name character varying(100),
    component character varying(50),
    description character varying(200),
    notes character varying(2000),
    severity character varying(10),
    event_created_time numeric(20,5),
    source character varying(20),
    fk_status_id integer
);


ALTER TABLE public.alert_data OWNER TO autointelli;

--
-- Name: alert_data_pk_alert_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.alert_data_pk_alert_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.alert_data_pk_alert_id_seq OWNER TO autointelli;

--
-- Name: alert_data_pk_alert_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.alert_data_pk_alert_id_seq OWNED BY public.alert_data.pk_alert_id;


--
-- Name: attributes; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.attributes (
    attr_id bigint NOT NULL,
    mars_type character varying(15),
    item_class character varying(100),
    item_sub_class character varying(100),
    attribute character varying(500)
);


ALTER TABLE public.attributes OWNER TO autointelli;

--
-- Name: attributes_attr_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.attributes_attr_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.attributes_attr_id_seq OWNER TO autointelli;

--
-- Name: attributes_attr_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.attributes_attr_id_seq OWNED BY public.attributes.attr_id;


--
-- Name: celery_taskmeta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.celery_taskmeta (
    id integer NOT NULL,
    task_id character varying(155),
    status character varying(50),
    result bytea,
    date_done timestamp without time zone,
    traceback text
);


ALTER TABLE public.celery_taskmeta OWNER TO autointelli;

--
-- Name: celery_tasksetmeta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.celery_tasksetmeta (
    id integer NOT NULL,
    taskset_id character varying(155),
    result bytea,
    date_done timestamp without time zone
);


ALTER TABLE public.celery_tasksetmeta OWNER TO autointelli;

--
-- Name: chartdetails; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.chartdetails (
    pk_chart_id bigint NOT NULL,
    chart_name character varying(200),
    attributes json,
    active_yn character varying(1)
);


ALTER TABLE public.chartdetails OWNER TO autointelli;

--
-- Name: chartdetails_pk_chart_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.chartdetails_pk_chart_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chartdetails_pk_chart_id_seq OWNER TO autointelli;

--
-- Name: chartdetails_pk_chart_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.chartdetails_pk_chart_id_seq OWNED BY public.chartdetails.pk_chart_id;


--
-- Name: ci_name_details; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ci_name_details (
    ciname_id bigint NOT NULL,
    ci_name character varying(300),
    active_yn character(1)
);


ALTER TABLE public.ci_name_details OWNER TO autointelli;

--
-- Name: ci_name_details_ciname_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ci_name_details_ciname_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ci_name_details_ciname_id_seq OWNER TO autointelli;

--
-- Name: ci_name_details_ciname_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ci_name_details_ciname_id_seq OWNED BY public.ci_name_details.ciname_id;


--
-- Name: ci_name_user_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ci_name_user_mapping (
    ci_name_user_map_id bigint NOT NULL,
    user_id integer,
    ciname_id integer
);


ALTER TABLE public.ci_name_user_mapping OWNER TO autointelli;

--
-- Name: ci_name_user_mapping_ci_name_user_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ci_name_user_mapping_ci_name_user_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ci_name_user_mapping_ci_name_user_map_id_seq OWNER TO autointelli;

--
-- Name: ci_name_user_mapping_ci_name_user_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ci_name_user_mapping_ci_name_user_map_id_seq OWNED BY public.ci_name_user_mapping.ci_name_user_map_id;


--
-- Name: configuration; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.configuration (
    configid integer NOT NULL,
    configname text NOT NULL,
    configip text NOT NULL,
    configport integer NOT NULL,
    dbname text,
    username text,
    password text,
    communicationtype text,
    extra2 text
);


ALTER TABLE public.configuration OWNER TO autointelli;

--
-- Name: configuration_configid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.configuration_configid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.configuration_configid_seq OWNER TO autointelli;

--
-- Name: configuration_configid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.configuration_configid_seq OWNED BY public.configuration.configid;


--
-- Name: dashboard; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.dashboard (
    pk_dashboard_id bigint NOT NULL,
    dashboard_name character varying(200),
    active_yn character varying(1)
);


ALTER TABLE public.dashboard OWNER TO autointelli;

--
-- Name: dashboard_pk_dashboard_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.dashboard_pk_dashboard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dashboard_pk_dashboard_id_seq OWNER TO autointelli;

--
-- Name: dashboard_pk_dashboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.dashboard_pk_dashboard_id_seq OWNED BY public.dashboard.pk_dashboard_id;


--
-- Name: dashboard_role_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.dashboard_role_mapping (
    pk_map_id bigint NOT NULL,
    fk_dashboard_id integer,
    fk_role_id integer
);


ALTER TABLE public.dashboard_role_mapping OWNER TO autointelli;

--
-- Name: dashboard_role_mapping_pk_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.dashboard_role_mapping_pk_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dashboard_role_mapping_pk_map_id_seq OWNER TO autointelli;

--
-- Name: dashboard_role_mapping_pk_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.dashboard_role_mapping_pk_map_id_seq OWNED BY public.dashboard_role_mapping.pk_map_id;


--
-- Name: dashboard_widget_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.dashboard_widget_mapping (
    pk_map_id bigint NOT NULL,
    fk_dashboard_id integer,
    widget_custom_name character varying(200),
    fk_widget_id integer,
    widget_attributes json
);


ALTER TABLE public.dashboard_widget_mapping OWNER TO autointelli;

--
-- Name: dashboard_widget_mapping_pk_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.dashboard_widget_mapping_pk_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dashboard_widget_mapping_pk_map_id_seq OWNER TO autointelli;

--
-- Name: dashboard_widget_mapping_pk_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.dashboard_widget_mapping_pk_map_id_seq OWNED BY public.dashboard_widget_mapping.pk_map_id;


--
-- Name: device_credentials_cred_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.device_credentials_cred_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_credentials_cred_id_seq OWNER TO autointelli;

--
-- Name: device_credentials_cred_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.device_credentials_cred_id_seq OWNED BY public.ai_device_credentials.cred_id;


--
-- Name: device_discovery_pk_discovery_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.device_discovery_pk_discovery_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_discovery_pk_discovery_id_seq OWNER TO autointelli;

--
-- Name: device_discovery_pk_discovery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.device_discovery_pk_discovery_id_seq OWNED BY public.ai_device_discovery.pk_discovery_id;


--
-- Name: dropped_event; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.dropped_event (
    pk_dropped_event_id bigint NOT NULL,
    ci_name character varying(100),
    component character varying(50),
    description character varying(200),
    notes character varying(1000),
    severity character varying(10),
    event_created_time numeric(20,5),
    source character varying(20),
    fk_status_id integer,
    promote_yn character(1) NOT NULL,
    fk_event_id bigint
);


ALTER TABLE public.dropped_event OWNER TO autointelli;

--
-- Name: dropped_event_pk_dropped_event_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.dropped_event_pk_dropped_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dropped_event_pk_dropped_event_id_seq OWNER TO autointelli;

--
-- Name: dropped_event_pk_dropped_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.dropped_event_pk_dropped_event_id_seq OWNED BY public.dropped_event.pk_dropped_event_id;


--
-- Name: ea_status; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.ea_status (
    pk_ea_status_id bigint NOT NULL,
    stat_description character varying(15),
    active_yn character(1) NOT NULL
);


ALTER TABLE public.ea_status OWNER TO autointelli;

--
-- Name: ea_status_pk_ea_status_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.ea_status_pk_ea_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ea_status_pk_ea_status_id_seq OWNER TO autointelli;

--
-- Name: ea_status_pk_ea_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.ea_status_pk_ea_status_id_seq OWNED BY public.ea_status.pk_ea_status_id;


--
-- Name: event_alert_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.event_alert_mapping (
    pk_ea_id bigint NOT NULL,
    fk_event_id integer,
    fk_alert_id integer
);


ALTER TABLE public.event_alert_mapping OWNER TO autointelli;

--
-- Name: event_alert_mapping_pk_ea_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.event_alert_mapping_pk_ea_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_alert_mapping_pk_ea_id_seq OWNER TO autointelli;

--
-- Name: event_alert_mapping_pk_ea_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.event_alert_mapping_pk_ea_id_seq OWNED BY public.event_alert_mapping.pk_ea_id;


--
-- Name: event_data; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.event_data (
    pk_event_id bigint NOT NULL,
    ci_name character varying(100),
    component character varying(50),
    description character varying(2000),
    notes character varying(2000),
    severity character varying(10),
    event_created_time numeric(20,5),
    source character varying(20),
    fk_status_id integer
);


ALTER TABLE public.event_data OWNER TO autointelli;

--
-- Name: event_data_pk_event_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.event_data_pk_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_data_pk_event_id_seq OWNER TO autointelli;

--
-- Name: event_data_pk_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.event_data_pk_event_id_seq OWNED BY public.event_data.pk_event_id;


--
-- Name: hostautomationtype; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.hostautomationtype (
    id integer NOT NULL,
    hostname text,
    status text,
    automationtype text
);


ALTER TABLE public.hostautomationtype OWNER TO autointelli;

--
-- Name: hostautomationtype_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.hostautomationtype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.hostautomationtype_id_seq OWNER TO autointelli;

--
-- Name: hostautomationtype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.hostautomationtype_id_seq OWNED BY public.hostautomationtype.id;


--
-- Name: iojobs; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.iojobs (
    jobid integer NOT NULL,
    jobkey text NOT NULL,
    jobname text NOT NULL,
    status text NOT NULL,
    createdtime timestamp without time zone DEFAULT now(),
    modifiedtime timestamp without time zone
);


ALTER TABLE public.iojobs OWNER TO autointelli;

--
-- Name: iojobs_jobid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.iojobs_jobid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.iojobs_jobid_seq OWNER TO autointelli;

--
-- Name: iojobs_jobid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.iojobs_jobid_seq OWNED BY public.iojobs.jobid;


--
-- Name: itsm_dynamic_form; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.itsm_dynamic_form (
    fk_form_id bigint NOT NULL,
    itsm_name character varying(30),
    ticket_action character varying(20),
    form_control_label character varying(200),
    form_control_type character varying(100),
    form_control_order integer,
    active_yn character varying(1)
);


ALTER TABLE public.itsm_dynamic_form OWNER TO autointelli;

--
-- Name: itsm_dynamic_form_fk_form_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.itsm_dynamic_form_fk_form_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.itsm_dynamic_form_fk_form_id_seq OWNER TO autointelli;

--
-- Name: itsm_dynamic_form_fk_form_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.itsm_dynamic_form_fk_form_id_seq OWNED BY public.itsm_dynamic_form.fk_form_id;


--
-- Name: plottingapidetails; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.plottingapidetails (
    pk_api_id bigint NOT NULL,
    api_description character varying(200),
    api_address_or_link character varying(1000),
    api_method character varying(15),
    api_body character varying(2500),
    active_yn character varying(1)
);


ALTER TABLE public.plottingapidetails OWNER TO autointelli;

--
-- Name: plottingapidetails_pk_api_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.plottingapidetails_pk_api_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.plottingapidetails_pk_api_id_seq OWNER TO autointelli;

--
-- Name: plottingapidetails_pk_api_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.plottingapidetails_pk_api_id_seq OWNED BY public.plottingapidetails.pk_api_id;


--
-- Name: rulemeta; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.rulemeta (
    metadataid integer NOT NULL,
    componentname text NOT NULL,
    mappingname text NOT NULL
);


ALTER TABLE public.rulemeta OWNER TO autointelli;

--
-- Name: rulemeta_metadataid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.rulemeta_metadataid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rulemeta_metadataid_seq OWNER TO autointelli;

--
-- Name: rulemeta_metadataid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.rulemeta_metadataid_seq OWNED BY public.rulemeta.metadataid;


--
-- Name: rules; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.rules (
    ruleid integer NOT NULL,
    rulename text NOT NULL,
    status text NOT NULL,
    condition json NOT NULL,
    action text NOT NULL,
    actioncommand text NOT NULL,
    actionargs text NOT NULL,
    createdby text NOT NULL,
    modifiedby text,
    hostname text,
    createdtime numeric(20,5),
    modifiedtime numeric(20,5)
);


ALTER TABLE public.rules OWNER TO autointelli;

--
-- Name: rules_ruleid_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.rules_ruleid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rules_ruleid_seq OWNER TO autointelli;

--
-- Name: rules_ruleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.rules_ruleid_seq OWNED BY public.rules.ruleid;


--
-- Name: severity_mapping; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.severity_mapping (
    pk_map_id bigint NOT NULL,
    mtool_name character varying(50),
    mseverity character varying(20),
    aiseverity character varying(20),
    active_yn character varying(1)
);


ALTER TABLE public.severity_mapping OWNER TO autointelli;

--
-- Name: severity_mapping_pk_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.severity_mapping_pk_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.severity_mapping_pk_map_id_seq OWNER TO autointelli;

--
-- Name: severity_mapping_pk_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.severity_mapping_pk_map_id_seq OWNED BY public.severity_mapping.pk_map_id;


--
-- Name: synthetic_monitoring; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.synthetic_monitoring (
    id bigint NOT NULL,
    payload json
);


ALTER TABLE public.synthetic_monitoring OWNER TO autointelli;

--
-- Name: synthetic_monitoring_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.synthetic_monitoring_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.synthetic_monitoring_id_seq OWNER TO autointelli;

--
-- Name: synthetic_monitoring_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.synthetic_monitoring_id_seq OWNED BY public.synthetic_monitoring.id;


--
-- Name: task_id_sequence; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.task_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_id_sequence OWNER TO autointelli;

--
-- Name: taskset_id_sequence; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.taskset_id_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taskset_id_sequence OWNER TO autointelli;

--
-- Name: tbl_permission; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_permission (
    pk_permission_id bigint NOT NULL,
    permission_name character varying(30) NOT NULL,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_permission OWNER TO autointelli;

--
-- Name: tbl_permission_pk_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_permission_pk_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_permission_pk_permission_id_seq OWNER TO autointelli;

--
-- Name: tbl_permission_pk_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_permission_pk_permission_id_seq OWNED BY public.tbl_permission.pk_permission_id;


--
-- Name: tbl_role; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_role (
    pk_role_id bigint NOT NULL,
    role_name character varying(30) NOT NULL,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_role OWNER TO autointelli;

--
-- Name: tbl_role_pk_role_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_role_pk_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_role_pk_role_id_seq OWNER TO autointelli;

--
-- Name: tbl_role_pk_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_role_pk_role_id_seq OWNED BY public.tbl_role.pk_role_id;


--
-- Name: tbl_role_tab_permission; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_role_tab_permission (
    pk_role_tab_perm_map_id bigint NOT NULL,
    fk_role_id integer,
    fk_tab_id integer,
    fk_permission_id integer,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_role_tab_permission OWNER TO autointelli;

--
-- Name: tbl_role_tab_permission_pk_role_tab_perm_map_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_role_tab_permission_pk_role_tab_perm_map_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_role_tab_permission_pk_role_tab_perm_map_id_seq OWNER TO autointelli;

--
-- Name: tbl_role_tab_permission_pk_role_tab_perm_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_role_tab_permission_pk_role_tab_perm_map_id_seq OWNED BY public.tbl_role_tab_permission.pk_role_tab_perm_map_id;


--
-- Name: tbl_session_keys; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_session_keys (
    pk_session_key_id bigint NOT NULL,
    session_key character varying(128) NOT NULL,
    active_yn character(1) NOT NULL,
    fk_user_id bigint
);


ALTER TABLE public.tbl_session_keys OWNER TO autointelli;

--
-- Name: tbl_session_keys_pk_session_key_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_session_keys_pk_session_key_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_session_keys_pk_session_key_id_seq OWNER TO autointelli;

--
-- Name: tbl_session_keys_pk_session_key_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_session_keys_pk_session_key_id_seq OWNED BY public.tbl_session_keys.pk_session_key_id;


--
-- Name: tbl_tab; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_tab (
    pk_tab_id bigint NOT NULL,
    tab_name character varying(30) NOT NULL,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_tab OWNER TO autointelli;

--
-- Name: tbl_tab_pk_tab_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_tab_pk_tab_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_tab_pk_tab_id_seq OWNER TO autointelli;

--
-- Name: tbl_tab_pk_tab_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_tab_pk_tab_id_seq OWNED BY public.tbl_tab.pk_tab_id;


--
-- Name: tbl_user_details; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_user_details (
    pk_user_details_id bigint NOT NULL,
    user_id character varying(50) NOT NULL,
    user_password character varying(200),
    first_name character varying(40) NOT NULL,
    middle_name character varying(30),
    last_name character varying(40) NOT NULL,
    email_id character varying(50) NOT NULL,
    created_by integer,
    created_on date,
    modified_by integer,
    modified_on date,
    last_login date,
    phone_number character varying(15) NOT NULL,
    active_yn character(1) NOT NULL,
    fk_time_zone_id integer,
    fk_role_id integer,
    fk_user_type integer,
    attempts integer,
    orch_pass character varying(500)
);


ALTER TABLE public.tbl_user_details OWNER TO autointelli;

--
-- Name: tbl_user_details_pk_user_details_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_user_details_pk_user_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_user_details_pk_user_details_id_seq OWNER TO autointelli;

--
-- Name: tbl_user_details_pk_user_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_user_details_pk_user_details_id_seq OWNED BY public.tbl_user_details.pk_user_details_id;


--
-- Name: tbl_user_type; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_user_type (
    pk_user_type_id bigint NOT NULL,
    user_type_desc character varying(30) NOT NULL,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_user_type OWNER TO autointelli;

--
-- Name: tbl_user_type_pk_user_type_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_user_type_pk_user_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_user_type_pk_user_type_id_seq OWNER TO autointelli;

--
-- Name: tbl_user_type_pk_user_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_user_type_pk_user_type_id_seq OWNED BY public.tbl_user_type.pk_user_type_id;


--
-- Name: tbl_zone; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.tbl_zone (
    pk_zone_id bigint NOT NULL,
    country_code character varying(5) NOT NULL,
    country_name character varying(50) NOT NULL,
    time_zone character varying(100) NOT NULL,
    gmt_offset character varying(20) NOT NULL,
    active_yn character(1) NOT NULL
);


ALTER TABLE public.tbl_zone OWNER TO autointelli;

--
-- Name: tbl_zone_pk_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.tbl_zone_pk_zone_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tbl_zone_pk_zone_id_seq OWNER TO autointelli;

--
-- Name: tbl_zone_pk_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.tbl_zone_pk_zone_id_seq OWNED BY public.tbl_zone.pk_zone_id;


--
-- Name: view_7days_severity; Type: VIEW; Schema: public; Owner: autointelli
--

CREATE VIEW public.view_7days_severity AS
 SELECT main.alertdate,
    main.severity,
    COALESCE(child.total, (0)::bigint) AS total
   FROM (( SELECT x.alertdate,
            x.severity
           FROM ( VALUES (to_char((('now'::text)::date)::timestamp with time zone, 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date)::timestamp with time zone, 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '1 day'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '1 day'::interval), 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '2 days'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '2 days'::interval), 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '3 days'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '3 days'::interval), 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '4 days'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '4 days'::interval), 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '5 days'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '5 days'::interval), 'DD-MON-YYYY'::text),'WARNING'::text), (to_char((('now'::text)::date - '6 days'::interval), 'DD-MON-YYYY'::text),'CRITICAL'::text), (to_char((('now'::text)::date - '6 days'::interval), 'DD-MON-YYYY'::text),'WARNING'::text)) x(alertdate, severity)) main
     LEFT JOIN ( SELECT to_char(to_timestamp((alert_data.event_created_time)::double precision), 'DD-MON-YYYY'::text) AS alertdate,
            alert_data.severity,
            count(alert_data.severity) AS total
           FROM public.alert_data
          WHERE (to_timestamp((alert_data.event_created_time)::double precision) > (('now'::text)::date - '7 days'::interval))
          GROUP BY (to_char(to_timestamp((alert_data.event_created_time)::double precision), 'DD-MON-YYYY'::text)), alert_data.severity) child ON (((main.alertdate = child.alertdate) AND (main.severity = (child.severity)::text))))
  ORDER BY (to_date(main.alertdate, 'DD-MON-YYYY'::text)) DESC;


ALTER TABLE public.view_7days_severity OWNER TO autointelli;

--
-- Name: widget; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.widget (
    pk_widget_id bigint NOT NULL,
    widget_name character varying(50),
    fk_api_id integer,
    fk_category_id integer,
    fk_chart_id integer,
    active_yn character varying(1),
    wheight integer,
    wwidth integer
);


ALTER TABLE public.widget OWNER TO autointelli;

--
-- Name: widget_pk_widget_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.widget_pk_widget_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.widget_pk_widget_id_seq OWNER TO autointelli;

--
-- Name: widget_pk_widget_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.widget_pk_widget_id_seq OWNED BY public.widget.pk_widget_id;


--
-- Name: widgetcategory; Type: TABLE; Schema: public; Owner: autointelli
--

CREATE TABLE public.widgetcategory (
    pk_category_id bigint NOT NULL,
    category_name character varying(50),
    active_yn character varying(1)
);


ALTER TABLE public.widgetcategory OWNER TO autointelli;

--
-- Name: widgetcategory_pk_category_id_seq; Type: SEQUENCE; Schema: public; Owner: autointelli
--

CREATE SEQUENCE public.widgetcategory_pk_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.widgetcategory_pk_category_id_seq OWNER TO autointelli;

--
-- Name: widgetcategory_pk_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: autointelli
--

ALTER SEQUENCE public.widgetcategory_pk_category_id_seq OWNED BY public.widgetcategory.pk_category_id;


--
-- Name: admin_bmc itsm_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_bmc ALTER COLUMN itsm_id SET DEFAULT nextval('public.admin_bmc_itsm_id_seq'::regclass);


--
-- Name: admin_integration_meta id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_integration_meta ALTER COLUMN id SET DEFAULT nextval('public.admin_integration_meta_id_seq'::regclass);


--
-- Name: admin_otrs itsm_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_otrs ALTER COLUMN itsm_id SET DEFAULT nextval('public.admin_otrs_itsm_id_seq'::regclass);


--
-- Name: admin_sdp itsm_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_sdp ALTER COLUMN itsm_id SET DEFAULT nextval('public.admin_sdp_itsm_id_seq'::regclass);


--
-- Name: ai_application application_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application ALTER COLUMN application_id SET DEFAULT nextval('public.ai_application_application_id_seq'::regclass);


--
-- Name: ai_application_class aclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application_class ALTER COLUMN aclass_id SET DEFAULT nextval('public.ai_application_class_aclass_id_seq'::regclass);


--
-- Name: ai_application_subclass asclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application_subclass ALTER COLUMN asclass_id SET DEFAULT nextval('public.ai_application_subclass_asclass_id_seq'::regclass);


--
-- Name: ai_auto_classify_new pk_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_auto_classify_new ALTER COLUMN pk_id SET DEFAULT nextval('public.ai_auto_classify_new_pk_id_seq'::regclass);


--
-- Name: ai_automation_execution_history pk_history_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_execution_history ALTER COLUMN pk_history_id SET DEFAULT nextval('public.ai_automation_execution_history_pk_history_id_seq'::regclass);


--
-- Name: ai_automation_executions pk_execution_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_executions ALTER COLUMN pk_execution_id SET DEFAULT nextval('public.ai_automation_executions_pk_execution_id_seq'::regclass);


--
-- Name: ai_automation_type methodid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_type ALTER COLUMN methodid SET DEFAULT nextval('public.ai_automation_type_methodid_seq'::regclass);


--
-- Name: ai_bot_repo pk_bot_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_bot_repo ALTER COLUMN pk_bot_id SET DEFAULT nextval('public.ai_bot_repo_pk_bot_id_seq'::regclass);


--
-- Name: ai_bot_tree pk_tree_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_bot_tree ALTER COLUMN pk_tree_id SET DEFAULT nextval('public.ai_bot_tree_pk_tree_id_seq'::regclass);


--
-- Name: ai_cmdb cmdbid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_cmdb ALTER COLUMN cmdbid SET DEFAULT nextval('public.ai_cmdb_cmdbid_seq'::regclass);


--
-- Name: ai_device_credentials cred_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_device_credentials ALTER COLUMN cred_id SET DEFAULT nextval('public.device_credentials_cred_id_seq'::regclass);


--
-- Name: ai_device_discovery pk_discovery_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_device_discovery ALTER COLUMN pk_discovery_id SET DEFAULT nextval('public.device_discovery_pk_discovery_id_seq'::regclass);


--
-- Name: ai_itsm_rest_master pk_itsm_rest_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_itsm_rest_master ALTER COLUMN pk_itsm_rest_id SET DEFAULT nextval('public.ai_itsm_rest_master_pk_itsm_rest_id_seq'::regclass);


--
-- Name: ai_license pk_license_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_license ALTER COLUMN pk_license_id SET DEFAULT nextval('public.ai_license_pk_license_id_seq'::regclass);


--
-- Name: ai_machine machine_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine ALTER COLUMN machine_id SET DEFAULT nextval('public.ai_machine_machine_id_seq'::regclass);


--
-- Name: ai_machine_class mclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_class ALTER COLUMN mclass_id SET DEFAULT nextval('public.ai_machine_class_mclass_id_seq'::regclass);


--
-- Name: ai_machine_group_mapping pk_machine_group_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_group_mapping ALTER COLUMN pk_machine_group_map_id SET DEFAULT nextval('public.ai_machine_group_mapping_pk_machine_group_map_id_seq'::regclass);


--
-- Name: ai_machine_grouping pk_ai_machine_group_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_grouping ALTER COLUMN pk_ai_machine_group_id SET DEFAULT nextval('public.ai_machine_grouping_pk_ai_machine_group_id_seq'::regclass);


--
-- Name: ai_machine_software_mapping ams_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_software_mapping ALTER COLUMN ams_id SET DEFAULT nextval('public.ai_machine_software_mapping_ams_id_seq'::regclass);


--
-- Name: ai_network device_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network ALTER COLUMN device_id SET DEFAULT nextval('public.ai_network_device_id_seq'::regclass);


--
-- Name: ai_network_machine_mapping anm_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network_machine_mapping ALTER COLUMN anm_id SET DEFAULT nextval('public.ai_network_machine_mapping_anm_id_seq'::regclass);


--
-- Name: ai_patch_automation id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_patch_automation ALTER COLUMN id SET DEFAULT nextval('public.ai_patch_automation_id_seq'::regclass);


--
-- Name: ai_policyaction_meta actionid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_policyaction_meta ALTER COLUMN actionid SET DEFAULT nextval('public.ai_policyaction_meta_actionid_seq'::regclass);


--
-- Name: ai_policyoperator_meta operatorid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_policyoperator_meta ALTER COLUMN operatorid SET DEFAULT nextval('public.ai_policyoperator_meta_operatorid_seq'::regclass);


--
-- Name: ai_resource resource_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource ALTER COLUMN resource_id SET DEFAULT nextval('public.ai_resource_resource_id_seq'::regclass);


--
-- Name: ai_resource_application_mapping ara_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_application_mapping ALTER COLUMN ara_id SET DEFAULT nextval('public.ai_resource_application_mapping_ara_id_seq'::regclass);


--
-- Name: ai_resource_class rclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_class ALTER COLUMN rclass_id SET DEFAULT nextval('public.ai_resource_class_rclass_id_seq'::regclass);


--
-- Name: ai_software software_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software ALTER COLUMN software_id SET DEFAULT nextval('public.ai_software_software_id_seq'::regclass);


--
-- Name: ai_software_class sclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_class ALTER COLUMN sclass_id SET DEFAULT nextval('public.ai_software_class_sclass_id_seq'::regclass);


--
-- Name: ai_software_resource_mapping asr_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_resource_mapping ALTER COLUMN asr_id SET DEFAULT nextval('public.ai_software_resource_mapping_asr_id_seq'::regclass);


--
-- Name: ai_software_subclass ssclass_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_subclass ALTER COLUMN ssclass_id SET DEFAULT nextval('public.ai_software_subclass_ssclass_id_seq'::regclass);


--
-- Name: ai_ticket_details pk_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_ticket_details ALTER COLUMN pk_id SET DEFAULT nextval('public.ai_ticket_details_pk_id_seq'::regclass);


--
-- Name: ai_triage_dynamic_form pk_triage_df; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_dynamic_form ALTER COLUMN pk_triage_df SET DEFAULT nextval('public.ai_triage_dynamic_form_pk_triage_df_seq'::regclass);


--
-- Name: ai_triage_history pk_triage_history_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_history ALTER COLUMN pk_triage_history_id SET DEFAULT nextval('public.ai_triage_history_pk_triage_history_id_seq'::regclass);


--
-- Name: ai_triage_master pk_triage_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_master ALTER COLUMN pk_triage_id SET DEFAULT nextval('public.ai_triage_master_pk_triage_id_seq'::regclass);


--
-- Name: alert_data pk_alert_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.alert_data ALTER COLUMN pk_alert_id SET DEFAULT nextval('public.alert_data_pk_alert_id_seq'::regclass);


--
-- Name: attributes attr_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.attributes ALTER COLUMN attr_id SET DEFAULT nextval('public.attributes_attr_id_seq'::regclass);


--
-- Name: chartdetails pk_chart_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.chartdetails ALTER COLUMN pk_chart_id SET DEFAULT nextval('public.chartdetails_pk_chart_id_seq'::regclass);


--
-- Name: ci_name_details ciname_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_details ALTER COLUMN ciname_id SET DEFAULT nextval('public.ci_name_details_ciname_id_seq'::regclass);


--
-- Name: ci_name_user_mapping ci_name_user_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_user_mapping ALTER COLUMN ci_name_user_map_id SET DEFAULT nextval('public.ci_name_user_mapping_ci_name_user_map_id_seq'::regclass);


--
-- Name: configuration configid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.configuration ALTER COLUMN configid SET DEFAULT nextval('public.configuration_configid_seq'::regclass);


--
-- Name: dashboard pk_dashboard_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard ALTER COLUMN pk_dashboard_id SET DEFAULT nextval('public.dashboard_pk_dashboard_id_seq'::regclass);


--
-- Name: dashboard_role_mapping pk_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_role_mapping ALTER COLUMN pk_map_id SET DEFAULT nextval('public.dashboard_role_mapping_pk_map_id_seq'::regclass);


--
-- Name: dashboard_widget_mapping pk_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_widget_mapping ALTER COLUMN pk_map_id SET DEFAULT nextval('public.dashboard_widget_mapping_pk_map_id_seq'::regclass);


--
-- Name: dropped_event pk_dropped_event_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dropped_event ALTER COLUMN pk_dropped_event_id SET DEFAULT nextval('public.dropped_event_pk_dropped_event_id_seq'::regclass);


--
-- Name: ea_status pk_ea_status_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ea_status ALTER COLUMN pk_ea_status_id SET DEFAULT nextval('public.ea_status_pk_ea_status_id_seq'::regclass);


--
-- Name: event_alert_mapping pk_ea_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_alert_mapping ALTER COLUMN pk_ea_id SET DEFAULT nextval('public.event_alert_mapping_pk_ea_id_seq'::regclass);


--
-- Name: event_data pk_event_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_data ALTER COLUMN pk_event_id SET DEFAULT nextval('public.event_data_pk_event_id_seq'::regclass);


--
-- Name: hostautomationtype id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.hostautomationtype ALTER COLUMN id SET DEFAULT nextval('public.hostautomationtype_id_seq'::regclass);


--
-- Name: iojobs jobid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.iojobs ALTER COLUMN jobid SET DEFAULT nextval('public.iojobs_jobid_seq'::regclass);


--
-- Name: itsm_dynamic_form fk_form_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.itsm_dynamic_form ALTER COLUMN fk_form_id SET DEFAULT nextval('public.itsm_dynamic_form_fk_form_id_seq'::regclass);


--
-- Name: plottingapidetails pk_api_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.plottingapidetails ALTER COLUMN pk_api_id SET DEFAULT nextval('public.plottingapidetails_pk_api_id_seq'::regclass);


--
-- Name: rulemeta metadataid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.rulemeta ALTER COLUMN metadataid SET DEFAULT nextval('public.rulemeta_metadataid_seq'::regclass);


--
-- Name: rules ruleid; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.rules ALTER COLUMN ruleid SET DEFAULT nextval('public.rules_ruleid_seq'::regclass);


--
-- Name: severity_mapping pk_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.severity_mapping ALTER COLUMN pk_map_id SET DEFAULT nextval('public.severity_mapping_pk_map_id_seq'::regclass);


--
-- Name: synthetic_monitoring id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.synthetic_monitoring ALTER COLUMN id SET DEFAULT nextval('public.synthetic_monitoring_id_seq'::regclass);


--
-- Name: tbl_permission pk_permission_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_permission ALTER COLUMN pk_permission_id SET DEFAULT nextval('public.tbl_permission_pk_permission_id_seq'::regclass);


--
-- Name: tbl_role pk_role_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role ALTER COLUMN pk_role_id SET DEFAULT nextval('public.tbl_role_pk_role_id_seq'::regclass);


--
-- Name: tbl_role_tab_permission pk_role_tab_perm_map_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role_tab_permission ALTER COLUMN pk_role_tab_perm_map_id SET DEFAULT nextval('public.tbl_role_tab_permission_pk_role_tab_perm_map_id_seq'::regclass);


--
-- Name: tbl_session_keys pk_session_key_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_session_keys ALTER COLUMN pk_session_key_id SET DEFAULT nextval('public.tbl_session_keys_pk_session_key_id_seq'::regclass);


--
-- Name: tbl_tab pk_tab_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_tab ALTER COLUMN pk_tab_id SET DEFAULT nextval('public.tbl_tab_pk_tab_id_seq'::regclass);


--
-- Name: tbl_user_details pk_user_details_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_details ALTER COLUMN pk_user_details_id SET DEFAULT nextval('public.tbl_user_details_pk_user_details_id_seq'::regclass);


--
-- Name: tbl_user_type pk_user_type_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_type ALTER COLUMN pk_user_type_id SET DEFAULT nextval('public.tbl_user_type_pk_user_type_id_seq'::regclass);


--
-- Name: tbl_zone pk_zone_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_zone ALTER COLUMN pk_zone_id SET DEFAULT nextval('public.tbl_zone_pk_zone_id_seq'::regclass);


--
-- Name: widget pk_widget_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widget ALTER COLUMN pk_widget_id SET DEFAULT nextval('public.widget_pk_widget_id_seq'::regclass);


--
-- Name: widgetcategory pk_category_id; Type: DEFAULT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widgetcategory ALTER COLUMN pk_category_id SET DEFAULT nextval('public.widgetcategory_pk_category_id_seq'::regclass);


--
-- Name: admin_integration_meta admin_integration_meta_integration_type_integration_name_key; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_integration_meta
    ADD CONSTRAINT admin_integration_meta_integration_type_integration_name_key UNIQUE (integration_type, integration_name);


--
-- Name: admin_integration_meta admin_integration_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_integration_meta
    ADD CONSTRAINT admin_integration_meta_pkey PRIMARY KEY (id);


--
-- Name: admin_sdp admin_sdp_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.admin_sdp
    ADD CONSTRAINT admin_sdp_pkey PRIMARY KEY (itsm_id);


--
-- Name: ai_application_class ai_application_class_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application_class
    ADD CONSTRAINT ai_application_class_pkey PRIMARY KEY (aclass_id);


--
-- Name: ai_application ai_application_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application
    ADD CONSTRAINT ai_application_pkey PRIMARY KEY (application_id);


--
-- Name: ai_application_subclass ai_application_subclass_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_application_subclass
    ADD CONSTRAINT ai_application_subclass_pkey PRIMARY KEY (asclass_id);


--
-- Name: ai_auto_classify_new ai_auto_classify_new_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_auto_classify_new
    ADD CONSTRAINT ai_auto_classify_new_pkey PRIMARY KEY (pk_id);


--
-- Name: ai_automation_execution_history ai_automation_execution_history_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_execution_history
    ADD CONSTRAINT ai_automation_execution_history_pkey PRIMARY KEY (pk_history_id);


--
-- Name: ai_automation_executions ai_automation_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_executions
    ADD CONSTRAINT ai_automation_executions_pkey PRIMARY KEY (pk_execution_id);


--
-- Name: ai_automation_stages ai_automation_stages_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_stages
    ADD CONSTRAINT ai_automation_stages_pkey PRIMARY KEY (stageid);


--
-- Name: ai_automation_type ai_automation_type_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_type
    ADD CONSTRAINT ai_automation_type_pkey PRIMARY KEY (methodid);


--
-- Name: ai_bot_repo ai_bot_repo_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_bot_repo
    ADD CONSTRAINT ai_bot_repo_pkey PRIMARY KEY (pk_bot_id);


--
-- Name: ai_bot_tree ai_bot_tree_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_bot_tree
    ADD CONSTRAINT ai_bot_tree_pkey PRIMARY KEY (pk_tree_id);


--
-- Name: ai_cmdb ai_cmdb_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_cmdb
    ADD CONSTRAINT ai_cmdb_pkey PRIMARY KEY (cmdbid);


--
-- Name: ai_itsm_rest_master ai_itsm_rest_master_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_itsm_rest_master
    ADD CONSTRAINT ai_itsm_rest_master_pkey PRIMARY KEY (pk_itsm_rest_id);


--
-- Name: ai_license ai_license_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_license
    ADD CONSTRAINT ai_license_pkey PRIMARY KEY (pk_license_id);


--
-- Name: ai_machine_class ai_machine_class_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_class
    ADD CONSTRAINT ai_machine_class_pkey PRIMARY KEY (mclass_id);


--
-- Name: ai_machine_group_mapping ai_machine_group_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_group_mapping
    ADD CONSTRAINT ai_machine_group_mapping_pkey PRIMARY KEY (pk_machine_group_map_id);


--
-- Name: ai_machine_grouping ai_machine_grouping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_grouping
    ADD CONSTRAINT ai_machine_grouping_pkey PRIMARY KEY (pk_ai_machine_group_id);


--
-- Name: ai_machine ai_machine_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine
    ADD CONSTRAINT ai_machine_pkey PRIMARY KEY (machine_id);


--
-- Name: ai_machine_software_mapping ai_machine_software_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_software_mapping
    ADD CONSTRAINT ai_machine_software_mapping_pkey PRIMARY KEY (ams_id);


--
-- Name: ai_network_machine_mapping ai_network_machine_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network_machine_mapping
    ADD CONSTRAINT ai_network_machine_mapping_pkey PRIMARY KEY (anm_id);


--
-- Name: ai_network ai_network_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network
    ADD CONSTRAINT ai_network_pkey PRIMARY KEY (device_id);


--
-- Name: ai_patch_automation ai_patch_automation_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_patch_automation
    ADD CONSTRAINT ai_patch_automation_pkey PRIMARY KEY (id);


--
-- Name: ai_policyaction_meta ai_policyaction_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_policyaction_meta
    ADD CONSTRAINT ai_policyaction_meta_pkey PRIMARY KEY (actionid);


--
-- Name: ai_policyoperator_meta ai_policyoperator_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_policyoperator_meta
    ADD CONSTRAINT ai_policyoperator_meta_pkey PRIMARY KEY (operatorid);


--
-- Name: ai_resource_application_mapping ai_resource_application_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_application_mapping
    ADD CONSTRAINT ai_resource_application_mapping_pkey PRIMARY KEY (ara_id);


--
-- Name: ai_resource_class ai_resource_class_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_class
    ADD CONSTRAINT ai_resource_class_pkey PRIMARY KEY (rclass_id);


--
-- Name: ai_resource ai_resource_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource
    ADD CONSTRAINT ai_resource_pkey PRIMARY KEY (resource_id);


--
-- Name: ai_software_class ai_software_class_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_class
    ADD CONSTRAINT ai_software_class_pkey PRIMARY KEY (sclass_id);


--
-- Name: ai_software ai_software_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software
    ADD CONSTRAINT ai_software_pkey PRIMARY KEY (software_id);


--
-- Name: ai_software_resource_mapping ai_software_resource_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_resource_mapping
    ADD CONSTRAINT ai_software_resource_mapping_pkey PRIMARY KEY (asr_id);


--
-- Name: ai_software_subclass ai_software_subclass_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_subclass
    ADD CONSTRAINT ai_software_subclass_pkey PRIMARY KEY (ssclass_id);


--
-- Name: ai_ticket_details ai_ticket_details_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_ticket_details
    ADD CONSTRAINT ai_ticket_details_pkey PRIMARY KEY (pk_id);


--
-- Name: ai_triage_dynamic_form ai_triage_dynamic_form_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_dynamic_form
    ADD CONSTRAINT ai_triage_dynamic_form_pkey PRIMARY KEY (pk_triage_df);


--
-- Name: ai_triage_history ai_triage_history_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_history
    ADD CONSTRAINT ai_triage_history_pkey PRIMARY KEY (pk_triage_history_id);


--
-- Name: ai_triage_master ai_triage_master_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_master
    ADD CONSTRAINT ai_triage_master_pkey PRIMARY KEY (pk_triage_id);


--
-- Name: alert_data alert_data_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.alert_data
    ADD CONSTRAINT alert_data_pkey PRIMARY KEY (pk_alert_id);


--
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (attr_id);


--
-- Name: celery_taskmeta celery_taskmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_taskmeta celery_taskmeta_task_id_key; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.celery_taskmeta
    ADD CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id);


--
-- Name: celery_tasksetmeta celery_tasksetmeta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id);


--
-- Name: celery_tasksetmeta celery_tasksetmeta_taskset_id_key; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.celery_tasksetmeta
    ADD CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id);


--
-- Name: chartdetails chartdetails_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.chartdetails
    ADD CONSTRAINT chartdetails_pkey PRIMARY KEY (pk_chart_id);


--
-- Name: ci_name_details ci_name_details_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_details
    ADD CONSTRAINT ci_name_details_pkey PRIMARY KEY (ciname_id);


--
-- Name: ci_name_user_mapping ci_name_user_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_user_mapping
    ADD CONSTRAINT ci_name_user_mapping_pkey PRIMARY KEY (ci_name_user_map_id);


--
-- Name: configuration configuration_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.configuration
    ADD CONSTRAINT configuration_pkey PRIMARY KEY (configid);


--
-- Name: dashboard dashboard_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard
    ADD CONSTRAINT dashboard_pkey PRIMARY KEY (pk_dashboard_id);


--
-- Name: dashboard_role_mapping dashboard_role_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_role_mapping
    ADD CONSTRAINT dashboard_role_mapping_pkey PRIMARY KEY (pk_map_id);


--
-- Name: dashboard_widget_mapping dashboard_widget_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_widget_mapping
    ADD CONSTRAINT dashboard_widget_mapping_pkey PRIMARY KEY (pk_map_id);


--
-- Name: ai_device_credentials device_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_device_credentials
    ADD CONSTRAINT device_credentials_pkey PRIMARY KEY (cred_id);


--
-- Name: ai_device_discovery device_discovery_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_device_discovery
    ADD CONSTRAINT device_discovery_pkey PRIMARY KEY (pk_discovery_id);


--
-- Name: dropped_event dropped_event_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dropped_event
    ADD CONSTRAINT dropped_event_pkey PRIMARY KEY (pk_dropped_event_id);


--
-- Name: ea_status ea_status_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ea_status
    ADD CONSTRAINT ea_status_pkey PRIMARY KEY (pk_ea_status_id);


--
-- Name: event_alert_mapping event_alert_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_alert_mapping
    ADD CONSTRAINT event_alert_mapping_pkey PRIMARY KEY (pk_ea_id);


--
-- Name: event_data event_data_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_data
    ADD CONSTRAINT event_data_pkey PRIMARY KEY (pk_event_id);


--
-- Name: hostautomationtype hostautomationtype_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.hostautomationtype
    ADD CONSTRAINT hostautomationtype_pkey PRIMARY KEY (id);


--
-- Name: iojobs iojobs_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.iojobs
    ADD CONSTRAINT iojobs_pkey PRIMARY KEY (jobid);


--
-- Name: itsm_dynamic_form itsm_dynamic_form_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.itsm_dynamic_form
    ADD CONSTRAINT itsm_dynamic_form_pkey PRIMARY KEY (fk_form_id);


--
-- Name: plottingapidetails plottingapidetails_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.plottingapidetails
    ADD CONSTRAINT plottingapidetails_pkey PRIMARY KEY (pk_api_id);


--
-- Name: rulemeta rulemeta_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.rulemeta
    ADD CONSTRAINT rulemeta_pkey PRIMARY KEY (metadataid);


--
-- Name: rules rules_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (ruleid);


--
-- Name: severity_mapping severity_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.severity_mapping
    ADD CONSTRAINT severity_mapping_pkey PRIMARY KEY (pk_map_id);


--
-- Name: synthetic_monitoring synthetic_monitoring_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.synthetic_monitoring
    ADD CONSTRAINT synthetic_monitoring_pkey PRIMARY KEY (id);


--
-- Name: tbl_permission tbl_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_permission
    ADD CONSTRAINT tbl_permission_pkey PRIMARY KEY (pk_permission_id);


--
-- Name: tbl_role tbl_role_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role
    ADD CONSTRAINT tbl_role_pkey PRIMARY KEY (pk_role_id);


--
-- Name: tbl_role_tab_permission tbl_role_tab_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role_tab_permission
    ADD CONSTRAINT tbl_role_tab_permission_pkey PRIMARY KEY (pk_role_tab_perm_map_id);


--
-- Name: tbl_session_keys tbl_session_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_session_keys
    ADD CONSTRAINT tbl_session_keys_pkey PRIMARY KEY (pk_session_key_id);


--
-- Name: tbl_tab tbl_tab_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_tab
    ADD CONSTRAINT tbl_tab_pkey PRIMARY KEY (pk_tab_id);


--
-- Name: tbl_user_details tbl_user_details_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_details
    ADD CONSTRAINT tbl_user_details_pkey PRIMARY KEY (pk_user_details_id);


--
-- Name: tbl_user_type tbl_user_type_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_type
    ADD CONSTRAINT tbl_user_type_pkey PRIMARY KEY (pk_user_type_id);


--
-- Name: tbl_zone tbl_zone_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_zone
    ADD CONSTRAINT tbl_zone_pkey PRIMARY KEY (pk_zone_id);


--
-- Name: widget widget_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widget
    ADD CONSTRAINT widget_pkey PRIMARY KEY (pk_widget_id);


--
-- Name: widgetcategory widgetcategory_pkey; Type: CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widgetcategory
    ADD CONSTRAINT widgetcategory_pkey PRIMARY KEY (pk_category_id);


--
-- Name: ai_automation_execution_history ai_automation_execution_history_fk_execution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_execution_history
    ADD CONSTRAINT ai_automation_execution_history_fk_execution_id_fkey FOREIGN KEY (fk_execution_id) REFERENCES public.ai_automation_executions(pk_execution_id);


--
-- Name: ai_automation_execution_history ai_automation_execution_history_fk_stage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_execution_history
    ADD CONSTRAINT ai_automation_execution_history_fk_stage_id_fkey FOREIGN KEY (fk_stage_id) REFERENCES public.ai_automation_stages(stageid);


--
-- Name: ai_automation_executions ai_automation_executions_fk_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_executions
    ADD CONSTRAINT ai_automation_executions_fk_alert_id_fkey FOREIGN KEY (fk_alert_id) REFERENCES public.alert_data(pk_alert_id);


--
-- Name: ai_automation_executions ai_automation_executions_fk_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_automation_executions
    ADD CONSTRAINT ai_automation_executions_fk_bot_id_fkey FOREIGN KEY (fk_bot_id) REFERENCES public.ai_bot_repo(pk_bot_id);


--
-- Name: ai_machine ai_machine_fk_cred_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine
    ADD CONSTRAINT ai_machine_fk_cred_id_fkey FOREIGN KEY (fk_cred_id) REFERENCES public.ai_device_credentials(cred_id);


--
-- Name: ai_machine_software_mapping ai_machine_software_mapping_fk_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_software_mapping
    ADD CONSTRAINT ai_machine_software_mapping_fk_machine_id_fkey FOREIGN KEY (fk_machine_id) REFERENCES public.ai_machine(machine_id);


--
-- Name: ai_machine_software_mapping ai_machine_software_mapping_fk_software_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_software_mapping
    ADD CONSTRAINT ai_machine_software_mapping_fk_software_id_fkey FOREIGN KEY (fk_software_id) REFERENCES public.ai_software(software_id);


--
-- Name: ai_network_machine_mapping ai_network_machine_mapping_fk_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network_machine_mapping
    ADD CONSTRAINT ai_network_machine_mapping_fk_device_id_fkey FOREIGN KEY (fk_device_id) REFERENCES public.ai_network(device_id);


--
-- Name: ai_network_machine_mapping ai_network_machine_mapping_fk_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_network_machine_mapping
    ADD CONSTRAINT ai_network_machine_mapping_fk_machine_id_fkey FOREIGN KEY (fk_machine_id) REFERENCES public.ai_machine(machine_id);


--
-- Name: ai_resource_application_mapping ai_resource_application_mapping_fk_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_application_mapping
    ADD CONSTRAINT ai_resource_application_mapping_fk_application_id_fkey FOREIGN KEY (fk_application_id) REFERENCES public.ai_application(application_id);


--
-- Name: ai_resource_application_mapping ai_resource_application_mapping_fk_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_resource_application_mapping
    ADD CONSTRAINT ai_resource_application_mapping_fk_resource_id_fkey FOREIGN KEY (fk_resource_id) REFERENCES public.ai_resource(resource_id);


--
-- Name: ai_software_resource_mapping ai_software_resource_mapping_fk_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_resource_mapping
    ADD CONSTRAINT ai_software_resource_mapping_fk_resource_id_fkey FOREIGN KEY (fk_resource_id) REFERENCES public.ai_resource(resource_id);


--
-- Name: ai_software_resource_mapping ai_software_resource_mapping_fk_software_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_software_resource_mapping
    ADD CONSTRAINT ai_software_resource_mapping_fk_software_id_fkey FOREIGN KEY (fk_software_id) REFERENCES public.ai_software(software_id);


--
-- Name: ai_ticket_details ai_ticket_details_fk_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_ticket_details
    ADD CONSTRAINT ai_ticket_details_fk_alert_id_fkey FOREIGN KEY (fk_alert_id) REFERENCES public.alert_data(pk_alert_id);


--
-- Name: ai_triage_dynamic_form ai_triage_dynamic_form_fk_triage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_dynamic_form
    ADD CONSTRAINT ai_triage_dynamic_form_fk_triage_id_fkey FOREIGN KEY (fk_triage_id) REFERENCES public.ai_triage_master(pk_triage_id);


--
-- Name: ai_triage_history ai_triage_history_fk_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_history
    ADD CONSTRAINT ai_triage_history_fk_alert_id_fkey FOREIGN KEY (fk_alert_id) REFERENCES public.alert_data(pk_alert_id);


--
-- Name: ai_triage_history ai_triage_history_fk_triage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_triage_history
    ADD CONSTRAINT ai_triage_history_fk_triage_id_fkey FOREIGN KEY (fk_triage_id) REFERENCES public.ai_triage_master(pk_triage_id);


--
-- Name: alert_data alert_data_fk_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.alert_data
    ADD CONSTRAINT alert_data_fk_status_id_fkey FOREIGN KEY (fk_status_id) REFERENCES public.ea_status(pk_ea_status_id);


--
-- Name: dropped_event dropped_event_fk_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dropped_event
    ADD CONSTRAINT dropped_event_fk_status_id_fkey FOREIGN KEY (fk_status_id) REFERENCES public.ea_status(pk_ea_status_id);


--
-- Name: event_alert_mapping event_alert_mapping_fk_alert_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_alert_mapping
    ADD CONSTRAINT event_alert_mapping_fk_alert_id_fkey FOREIGN KEY (fk_alert_id) REFERENCES public.alert_data(pk_alert_id);


--
-- Name: event_alert_mapping event_alert_mapping_fk_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_alert_mapping
    ADD CONSTRAINT event_alert_mapping_fk_event_id_fkey FOREIGN KEY (fk_event_id) REFERENCES public.event_data(pk_event_id);


--
-- Name: event_data event_data_fk_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.event_data
    ADD CONSTRAINT event_data_fk_status_id_fkey FOREIGN KEY (fk_status_id) REFERENCES public.ea_status(pk_ea_status_id);


--
-- Name: widget fk_api_id_k; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widget
    ADD CONSTRAINT fk_api_id_k FOREIGN KEY (fk_api_id) REFERENCES public.plottingapidetails(pk_api_id);


--
-- Name: ai_bot_repo fk_branch_key; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_bot_repo
    ADD CONSTRAINT fk_branch_key FOREIGN KEY (fk_branch_id) REFERENCES public.ai_bot_tree(pk_tree_id);


--
-- Name: widget fk_category_id_k; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widget
    ADD CONSTRAINT fk_category_id_k FOREIGN KEY (fk_category_id) REFERENCES public.widgetcategory(pk_category_id);


--
-- Name: widget fk_chart_id_k; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.widget
    ADD CONSTRAINT fk_chart_id_k FOREIGN KEY (fk_chart_id) REFERENCES public.chartdetails(pk_chart_id);


--
-- Name: ci_name_user_mapping fk_ci_name_user_mapping_ciname_id; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_user_mapping
    ADD CONSTRAINT fk_ci_name_user_mapping_ciname_id FOREIGN KEY (ciname_id) REFERENCES public.ci_name_details(ciname_id);


--
-- Name: ci_name_user_mapping fk_ci_name_user_mapping_user_id; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ci_name_user_mapping
    ADD CONSTRAINT fk_ci_name_user_mapping_user_id FOREIGN KEY (user_id) REFERENCES public.tbl_user_details(pk_user_details_id);


--
-- Name: ai_machine_group_mapping fk_con_grp_id; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_group_mapping
    ADD CONSTRAINT fk_con_grp_id FOREIGN KEY (fk_group_id) REFERENCES public.ai_machine_grouping(pk_ai_machine_group_id);


--
-- Name: ai_machine_group_mapping fk_con_mach_id; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_machine_group_mapping
    ADD CONSTRAINT fk_con_mach_id FOREIGN KEY (fk_machine_id) REFERENCES public.ai_machine(machine_id);


--
-- Name: tbl_session_keys fk_const_user_id; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_session_keys
    ADD CONSTRAINT fk_const_user_id FOREIGN KEY (fk_user_id) REFERENCES public.tbl_user_details(pk_user_details_id);


--
-- Name: ai_device_discovery fk_cred; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.ai_device_discovery
    ADD CONSTRAINT fk_cred FOREIGN KEY (fk_cred_id) REFERENCES public.ai_device_credentials(cred_id);


--
-- Name: dashboard_role_mapping fk_dashboard_id_k; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_role_mapping
    ADD CONSTRAINT fk_dashboard_id_k FOREIGN KEY (fk_dashboard_id) REFERENCES public.dashboard(pk_dashboard_id);


--
-- Name: dashboard_widget_mapping fk_dashboard_id_kk; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_widget_mapping
    ADD CONSTRAINT fk_dashboard_id_kk FOREIGN KEY (fk_dashboard_id) REFERENCES public.dashboard(pk_dashboard_id);


--
-- Name: dropped_event fk_event_cons; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dropped_event
    ADD CONSTRAINT fk_event_cons FOREIGN KEY (fk_event_id) REFERENCES public.event_data(pk_event_id);


--
-- Name: dashboard_role_mapping fk_role_id_k; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_role_mapping
    ADD CONSTRAINT fk_role_id_k FOREIGN KEY (fk_role_id) REFERENCES public.tbl_role(pk_role_id);


--
-- Name: dashboard_widget_mapping fk_widget_id_kk; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.dashboard_widget_mapping
    ADD CONSTRAINT fk_widget_id_kk FOREIGN KEY (fk_widget_id) REFERENCES public.widget(pk_widget_id);


--
-- Name: tbl_role_tab_permission tbl_role_tab_permission_fk_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role_tab_permission
    ADD CONSTRAINT tbl_role_tab_permission_fk_permission_id_fkey FOREIGN KEY (fk_permission_id) REFERENCES public.tbl_permission(pk_permission_id);


--
-- Name: tbl_role_tab_permission tbl_role_tab_permission_fk_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role_tab_permission
    ADD CONSTRAINT tbl_role_tab_permission_fk_role_id_fkey FOREIGN KEY (fk_role_id) REFERENCES public.tbl_role(pk_role_id);


--
-- Name: tbl_role_tab_permission tbl_role_tab_permission_fk_tab_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_role_tab_permission
    ADD CONSTRAINT tbl_role_tab_permission_fk_tab_id_fkey FOREIGN KEY (fk_tab_id) REFERENCES public.tbl_tab(pk_tab_id);


--
-- Name: tbl_user_details tbl_user_details_fk_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_details
    ADD CONSTRAINT tbl_user_details_fk_role_id_fkey FOREIGN KEY (fk_role_id) REFERENCES public.tbl_role(pk_role_id);


--
-- Name: tbl_user_details tbl_user_details_fk_user_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: autointelli
--

ALTER TABLE ONLY public.tbl_user_details
    ADD CONSTRAINT tbl_user_details_fk_user_type_fkey FOREIGN KEY (fk_user_type) REFERENCES public.tbl_user_type(pk_user_type_id);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: admin_integration_meta; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.admin_integration_meta (id, integration_name, integration_type, status) VALUES (1, 'sdp', 'itsm', 'Enabled');


--
-- Name: admin_integration_meta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.admin_integration_meta_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: admin_otrs; Type: TABLE DATA; Schema: public; Owner: autointelli
--



--
-- Name: admin_otrs_itsm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.admin_otrs_itsm_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: admin_sdp; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.admin_sdp (itsm_id, communication_type, ip, port, technician_key, priority, assignment_group_automation, assignment_group_manual, itsm_status, service_category, level, status, createdtime, createdby, modifiedtime, modifiedby, requester, requesttemplate, technician, itsm_wip_status, itsm_res_status) VALUES (1, 'http', '192.168.1.105', '8080', '0DDC1E19-ADA4-42C2-989D-0CE5D18463F6', 'High', 'Autointelli', 'Service Desk', 'Open', 'Software', 'Tier 2', 'Enabled', '2018-11-17 14:10:56.318091', 'admin', NULL, NULL, 'Anand', 'Unable to Browse', 'administrator', 'In Progress', 'Resolved');


--
-- Name: admin_sdp_itsm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.admin_sdp_itsm_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_application_class; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (1, 'Data ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (2, 'Development ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (3, 'Education ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (4, 'Enterprise ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (5, 'Financial ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (6, 'Media ', 'Y');
INSERT INTO public.ai_application_class (aclass_id, aclass_name, active_yn) VALUES (7, 'Others ', 'Y');


--
-- Name: ai_application_class_aclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_application_class_aclass_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_application_subclass; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (1, 'DataManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (2, 'Datawarehouse ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (3, 'DigitalAssetManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (4, 'DocumentManagementSystem ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (5, 'GeographicInformationSystem ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (6, 'ComputerAidedEngineering ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (7, 'Diagramming ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (8, 'HardwareEngineering ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (9, 'IntegratedDevelopmentEnvironment ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (10, 'ProductEngineering ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (11, 'Simulation ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (12, 'SoftwareEngineering ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (13, 'Testing ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (14, 'WebDevelopment ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (15, 'ClassroomManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (16, 'Teaching ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (17, 'ApplicationSuite ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (18, 'AssetManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (19, 'BusinessWorkflow ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (20, 'CustomerRelationshipManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (21, 'Email ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (22, 'EnterpriseInfrastructure ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (23, 'EnterprisePortal ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (24, 'EnterpriseResourcePlanning ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (25, 'KnowledgeManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (26, 'ProcessManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (27, 'Accounting ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (28, 'Banking ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (29, 'ClearingSystems ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (30, 'Compliance ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (31, 'Controlling ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (32, 'FinancialModelling ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (33, 'RiskManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (34, 'Trading ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (35, 'Animation ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (36, 'Blog ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (37, 'ComputerGraphics ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (38, 'ComputerAidedDesign ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (39, 'DesktopPublishing ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (40, 'DocumentAssembly ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (41, 'DocumentAutomation ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (42, 'InformationManagementPortal ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (43, 'MediaDevelopment ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (44, 'Presentation ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (45, 'SoundEditing ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (46, 'VideoEditing ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (47, 'FieldServiceManagement ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (48, 'ReferenceSystems ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (49, 'ReservationSystems ', 'Y');
INSERT INTO public.ai_application_subclass (asclass_id, asclass_name, active_yn) VALUES (50, 'TransactionSystem ', 'Y');


--
-- Name: ai_application_subclass_asclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_application_subclass_asclass_id_seq', 50, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_automation_stages; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (1, 'CREATE TICKET');
INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (4, 'TICKET UPDATE');
INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (6, 'RESOLVE OR MOVE TICKET');
INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (2, 'CHECK HOST EXIST');
INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (3, 'CHECK RULES / BOTS');
INSERT INTO public.ai_automation_stages (stageid, stages) VALUES (5, 'EXECUTE BOTS / RULES');


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_automation_type; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_automation_type (methodid, automated) VALUES (1, 'Y');


--
-- Name: ai_automation_type_methodid_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_automation_type_methodid_seq', 1, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_bot_tree; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (1, 'System', 'd', NULL, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (2, 'Custom', 'd', NULL, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (3, 'Windows', 'd', 1, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (4, 'Linux', 'd', 1, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (10, 'test', 'd', 9, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (9, 'test', 'd', 8, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (11, 'testing 4', 'd', 8, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (12, 'testing 4', 'd', 8, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (13, 'testing 5', 'd', 8, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (8, 'testing three', 'd', 7, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (15, 'adsad', 'd', 5, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (14, 'Testing Three', 'd', 7, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (7, 'Test', 'd', 2, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (16, 'Network', 'd', 1, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (17, 'Storage', 'd', 1, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (18, 'CISCO', 'd', 16, 'Y');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (6, 'Windows Script', 'd', 3, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (5, 'Python Script', 'd', 4, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (21, 'New Folder', 'd', 19, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (24, 'New 1', 'd', 23, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (23, 'New 1', 'd', 20, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (22, 'New Folder2', 'd', 20, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (20, 'New Folder', 'd', 19, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (19, 'New Folder', 'd', 2, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (26, 'Folder2', 'd', 25, 'N');
INSERT INTO public.ai_bot_tree (pk_tree_id, name, type, fk_parent_id, active_yn) VALUES (25, 'Folder2', 'd', 2, 'N');


--
-- Name: ai_bot_tree_pk_tree_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_bot_tree_pk_tree_id_seq', 26, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_bot_repo; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (19, 'R', 'Kill Highly CPU Used Session', 'Kill Highly CPU Utilized Session', 'yaml', 'a8KiwqHCnCvCm8KUw43Dm8OfwpXDlMKvwpTCoFPCpcKiwpXCmsKcT8KSf8KUwo_ChMOdw6LDk8ORw4_ClcOKw6TDosKpQcOaw6PDiMONw5grwoHClcObw5DClcOWw5nDl8OLw5LCgsOEw6nDp8KpQcOUw5XDkcOfw5ErwoHClcOow5DClMOZw6fCn3bCjEHCjsKVw6LDkMKOw5PCrsKFwrHDpMKGw4TDqsOow5RBw4_ClMORw5vDj8KCw43ClcOXw57CjsObw5XDk8OQdkHCgcKVwpTDksKQw5vDocOGw5rDkFvCgcKkw6PDn8KVwp3DnsOHw5zDmVDCtMK4w4bCuHHDgsOHwpTCv8K9bcK0wrrDhsOFZsOAwqPCqMK8w4FjwrbDiMONwp5kwr7DicKnw4HCv3rCssOKwrnDgXrCr8OCwqnCt8K1bcKtwqPDpMOoQcOpw6_ChcONw5jChsOTw6nDk8OYwoXCjsOxw6J2woxBwoHClcOYw5TCjcOTw5vDhsOgw5HCgMOVw6TCrsKPwo3DncOXw4bDmMOUwpDDlMOpfsKPQcKOwpTDl8ORw5PCisOUw6nDmcOhW8KOw6bDisOfw6HCjcOVf37Cj0HCm8KUw5PDjcOZwobCm8KVw4fDl8KQw6XClMOXw5HDn8KWw43DqcOneUHCjsKUwoXDkMORwoPDlsOcwq55QcKOwpTChcKMwozCl8OCw6fCrsKPwpPDk8Onw5rDmMOgT8OUw6nDmMOewpbDon7ChcKMwoxBw4XDmsOgw5TCiMOPw6jDisOLw6DCkMKbwpXDoMOewoTDj8Ogw43Dm8OfwpVr', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'SQLCPU', NULL, NULL, 'KPI', 'Anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (7, 'D', 'Memory Diagnose', 'TOP 5 Process Consuming Memory', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCm8KUw5PDjcOZwobCm8KVw4bDlMKVw6DDncOKw6LDkUHDlcOkw6TCj1bCjsOEw5fDm8OPwobDlMOowpTCssKQw5zDp8Oaw5nDlcKPw4jClcOhw57Ck8OTwpTCssORw5nCkMOTw65-wo9Bwo7ClMOYw5TDkcKNw43Cr8KUw5_ClMKOwqHDisObwozChMOOw5nCoMKUwo7Dk8OhwoXCmcKZwpTDkMOnw6jCrE7Ck8Ohw4rDmcKMwp3CgcOdw5nDkMKFwo7CocKWwp3CjMKdwoHDqcOVw5jCjcKOwqHClsKcdkHCgcKVwpTDocKGw5XDncOYw6DDkcKTwpvClcOmw5TClMOjw6DDmXbCjEHCjsKVw6LDkMKOw5PCrsKFwrDDlcKUw5HDocOVw6hBw6LDnMOKwozCtnTCsMODwpTDlcKQw6DDocOGw6DDoMKGw4XClcOmw5TClMOjw6DDmcOfdkHCgcKVwpTDk8KGw5DDqcOMwqbCjMKXw4LDp8Kxw6HChsOhw6nDkcOgdg==', 'Linux', 'CentOS', 'Memory', 1545825900.82985, NULL, 'KPI', 'anand', 1, 4, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (9, 'R', 'Windows Service Remediate', 'To Remediate Windows Service Issue', 'yaml', 'a8KiwqHCnCvCm8KUw43Dm8OfwpXDlMKvwpTDkMKNw5p-woXCjMOTwoLDlcOdw5nDocKAw5TDlcOIw6DDn1vCgcK7w5XDm8KUw5N-woXCjMOiwoLDk8Oow5PDlcKKw5rDmcOYwqZ2QcKBwpXClMKcQcKdw6nDmMOewpvCjcOQw5jDlcObUMOPw6nDmcObw5XCj8OVw5rDoMObworCncOdw5TDkcOawojDisOjw5nCnsKUw5PDpsObw5XDj8KGw5TCpMOXw5zChcOQwqPCk8Ofw5HChMOTw5rDqMOiUMOpw6_ChcKtwrVpwrDDiMOIwo_CnsOrwqLDnsOZw5grwoHClcOow5DClMOZw6fCn3bCjEHCgcKVwqHCj8KPw4_DocOKwqbCjHTDlcOWw6bDo0HDj8KUw5jDkcOewpfDisOYw5l5QcKOwpTChcKMwozCmMOKw6PDk8OiwobDoMOqw47Dj8ORW2vClcKUwo9Bwo7ClMKFwozDmsKCw47DmsKuwo9Dw6nDr8KFwrfCvGrCgcOyw7HCkSvCjsKUwoXCjMKMQcKBwpXDp8OjwoLDosOZwp_CjMOfwpXDgsOnw6jDlMKFeMKUwoXCjMKMTsKBw5nDmcORwpbDlcKuwoXDmcOfwojCnsKXw4fDlMKTw6TDncOIw5HCjHTDlcOWw6bDo8KGw5LClMK4w6HDj8KEw4bDqMOnw5XClsOaw6DDnsKOdg==', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'Service', 1545825900.82985, NULL, 'KPI', 'Anand', 1, 3, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (18, 'D', 'List Highly CPU Used Session', 'List Highly CPU Utilized Session', 'yaml', 'a8KiwqHCnCvCm8KUw43Dm8OfwpXDlMKvwpTCoFPCpcKiwpXCmsKcT8KSf8KUwo_ChMOdw6LDk8ORw4_ClcOKw6TDosKpQcOaw6PDiMONw5grwoHClcObw5DClcOWw5nDl8OLw5LCgsOEw6nDp8KpQcOUw5XDkcOfw5ErwoHClcOow5DClMOZw6fCn3bCjEHCjsKVw6LDkMKOw5PCrsKFwrHDpMKGw4TDqsOow5RBw4_ClMORw5vDj8KCw43ClcOXw57CjsObw5XDk8OQdkHCgcKVwpTDksKQw5vDocOGw5rDkFvCgcKkw6PDn8KVwp3DnsOHw5zDmVDCtMK4w4bCuHHDgsOHwpTCv8K9bcK0wrrDhsOFZsOAwqPCqMK8w4FjwrbDiMONwp5kwr7DicKnw4HCv3rCssOKwrnDgXrCnMOkw552woxBwoHClcOYw5TCjcOTw5vDhsOgw5HCgMOVw6TCrsKPwo3DncOXw4bDmMOUwpDDlMOpfsKPQcKOwpTDl8ORw5PCisOUw6nDmcOhW8KOw6bDisOfw6HCjcOVf37Cj0HCm8KUw5PDjcOZwobCm8KVw4fDl8KQw6XClMOXw5HDn8KWw43DqcOneUHCjsKUwoXDkMORwoPDlsOcwq55QcKOwpTChcKMwozCl8OCw6fCrsKPwpPDk8Onw5rDmMOgT8OUw6nDmMOewpbDon7ChcKMwoxBw4XDmsOgw5TCiMOPw6jDisOLw6DCkMKbwpXDoMOewoTDj8Ogw43Dm8OfwpVr', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'SQLCPU', NULL, NULL, 'KPI', 'Anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (4, 'D', 'Disk Diagnose', 'Get Disk Information', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCm8KUw5PDjcOZwobCm8KVw4bDlMKVw6DDncOKw6LDkUHCpcOew6fDmkHDg8Onw4bDk8ORK8KBwpXClMKPwpTDlsOZw5HDmMKmQcKBw5nDmsKPTsOWwpTCh8Onw6dBwqzDhcK9wo_CnsOrwpbChcOowozClMOGw5nClMKcwobCjsKWw5jCm8K5wpDDlsOjw6jDlMKFwo7Do8OTwpvCucKQw5bDo8Oow5TChcONw6PDk8Kbw5NDwoHDscKUw5DCmMOZwpTCjMOnwpBSwp7CmcKlw6xSwpXClMK0wrLCv17Cg8KhwpZ5QcKOwpTChcOew5HCiMOKw6jDqMOUwpPCqMKUw5fDkcOfwpbDjcOpfsKPQcKbwpTDk8ONw5nChsKbwpXCuMOYwpTDnsOgw4bDpcKMwpXDicOawpTCuXTCvcOCwoXDksObwpPDjsOWw6jDo8KGw5LClMOXw5HDn8KWw43DqcOneUHCjsKUwoXDkMORwoPDlsOcwq7Cj8KXw4_DpsKiw57DkcKUw5bDocOoeQ==', 'Linux', 'CentOS', 'Disk', 1545825900.82985, NULL, 'KPI', 'anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (1, 'R', 'Linux Service Remediate', 'Remediate Service Related issues', 'yaml', 'a8KiwqHCnCvCm8KUw43Dm8OfwpXDlMKvwpTDkMKNw5p-woXCjMOTwoLDlcOdw5nDocKAw5TDlcOIw6DDn1vCgcK7w5XDm8KUw5N-woXCjMOOwobDhMOkw6HDlFvCjsOtw4rDn3ZBwoHDq8OVw6HClMONw5rDjsOYw5HClMKbf8KUwo9Bwo7CocKFwpvDocKUw5PCpMOgw57ChMOPw6DClMONw6HClcOQw57DosOjwobDmsOgw47Cm8OVwpDDhsOjw5vDmMKPw5PCo8OYw5HDnsKXw4rDmMOZw6JQw5HDocOJw47Cm0_DlMOaw5fDocKGw6LDp8KUw6fDp0HCosK-wrzCvnTDgsKUw6LDqcKawprDjsOhfsKPQcOiw5XDmMOXw59ba8KVwpTCj0HCm8KUw5PDjcOZwobCm8KVwrfDl8KGw5HDn8KFwr_DkcKTw5fDnsOXw5RBw4HDqMOGw6DDocKUa8KVwpTCj0HCjsKUw5jDkcOewpfDisOYw5nCqSvCjsKUwoXCjMKMQcKBwpXDosOQwo7Dk8KuwoXCjsOnwpzCgcOAw4TCuEHDq8Oxwod2woxBwoHClcKUwo9Bwo7Dp8OZw43DoMKGwpvClcOnw6PCgsOgw6jDisOQdkHCgcKVwpTCj0HCjsKUw4rDmsONwoPDjcOaw5jCqUHDp8OZw5h2woxBwoHClcKhwo_ChcOTw5bDmsOTwqZBw47DqMObwqxDw4HDmcOXw6LDlcKEw4bClcOHw6PCgsOgw6jDisOQwox0w5bDmMOXw5TClMOhw5rDmsOYw5jCmsKDfw==', 'Linux', 'CentOS', 'Service', 1545825900.82985, NULL, 'KPI', 'anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (2, 'R', 'Execute Remote Script', 'Execute a Remote Script', 'System', 'wo7CosKheU7CjsOiw4bDmcORW8KBwrrDrMOUwoTDo8Oow4rCjMK_woTDk8Oew6TDo0HDl8OiwoXCvsORwo7DkMOpw5nCj27Dj8OXw43DlcOawobCj3_ClMKPwonDncOnw5nDn8KmQcOCw6HDoHlBwo7Dm8OGw6DDlMKGw5PDlMOaw5DChMOiw6fCn8KMwrLCgsONw6jDmXlBwo7DqsOGw57Dn8KAw4fDnsOgw5TClMKofsKFwozCjEHCjsKVwqPDpMKUw6DCo8ORw5vDj8KCw43CpMOVw6TClcOdw53Dk8Ogw5HCjcONw57Co8OYwpDDk8Oiw4zDlcOawobCkMOow5nDocKXw5fDl8OKw5_Cm8KEw47DmcOWwp5Pw6TDlcOaw5jDoCvCgcKVw6jDkMKUw5nDp8KfdsKMQcKBwpXClMKcQcOcw5XDksORwqZBwqbDrcOZw5LClsOiw5nChcOgw5TChsKBw6jDl8OhworDnsOob8KMwoxBwoHClcKUwo_ChMOdw6HDksONw5rChcKbwpXClsOqwpzCjsOnw4jDnsOVwpHDlcOUw6LDkMKOw5PClMOiw6nCjivCgcKVwpTCj0HCjsKUw5fDkcOTworDlMOpw5nDoVvCjsOnw43DkcOYwo3DgMOkw6nDoyt4wpTChcKMwoxBwo7ClcOYw5TCg8Ojw5vCn8KMw5nClMOIwrLClsOqwpzCjsOnw43DkcOYwo3DgMOkw6nDo0_DocOow4nDm8OhwpXCgcOyw7HCkSs=', 'Linux', 'CentOS', 'REMOTE SCRIPT', 1545825900.82985, NULL, 'KPI', 'anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (12, 'R', 'Script 3', 'bbb', 'yaml', 'w5XDmsOnw5jCj8OVwpRvw5rDkcKYwoHDm8Odw5vChnjDosOKw6PCjMKHw4rDocOZwo9T', 'Storage', 'emc', 'LOCAL SCRIPT', NULL, 1545909365.37015, 'KPI', NULL, NULL, 14, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (8, 'R', 'Memory Diagnose', 'TOP 5 Process Consuming Memory', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCm8KUw5PDjcOZwobCm8KVw4bDlMKVw6DDncOKw6LDkUHDlcOkw6TCj1bCjsOEw5fDm8OPwobDlMOowpTCssKQw5zDp8Oaw5nDlcKPw4jClcOhw57Ck8OTwpTCssORw5nCkMOTw65-wo9Bwo7ClMOYw5TDkcKNw43Cr8KUw5_ClMKOwqHDisObwozChMOOw5nCoMKUwo7Dk8OhwoXCmcKZwpTDkMOnw6jCrE7Ck8Ohw4rDmcKMwp3CgcOdw5nDkMKFwo7CocKWwp3CjMKdwoHDqcOVw5jCjcKOwqHClsKcdkHCgcKVwpTDocKGw5XDncOYw6DDkcKTwpvClcOmw5TClMOjw6DDmXbCjEHCjsKVw6LDkMKOw5PCrsKFwrDDlcKUw5HDocOVw6hBw6LDnMOKwozCtnTCsMODwpTDlcKQw6DDocOGw6DDoMKGw4XClcOmw5TClMOjw6DDmcOfdkHCgcKVwpTDk8KGw5DDqcOMwqbCjMKXw4LDp8Kxw6HChsOhw6nDkcOgdg==', 'Linux', 'CentOS', 'Memory', 1545825900.82985, NULL, 'KPI', 'anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (10, 'R', 'Script 1', 'Test', 'powershell', 'w5XDmsOnw6PCisOcw5tvw5rDkcKYw43DnsOiw5Qrw6LDmcOYw6DDlcKPw4jClcOiw5TCmMKOw6DDjsOaw5Erw5XDmsOnw6PCisOcw5vChcOaw5HCmMKBw6HDncOdwobCjsKmb8OSw5DCicOIw5vDm8OX', 'Linux', 'emc', 'Memory', NULL, 1545907935.03136, 'KPI', NULL, NULL, 14, 'N');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (3, 'R', 'Service Remediate', 'Remediate Service Issues', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCjsKUwpLCjMOawoLDjsOawq7Cj2TDlsOZw4jDl8KMdMOGw6fDqsOYwoTDk8KUwrjDoMONwpXDlsOofsKPQcKOwpTChcKMw5_ChsOTw6vDncOSwobCqMKUb8KMwoxBwoHClcKUwo9Bw5zDlcOSw5HCpkHCg8Oww6_Cj2zCvsK9woXDqcOpQ2vClcKUwo9Bwo7ClMKFwozDn8KVw4LDqcOZwqlBw6HDqMOGw57DoMKGw4V_wpTCj0HCjsKUwoXCjMKMwobDj8OWw5bDm8KGw5LCrsKFw6XDkcKUa8KVwpTCj0HCm8KUw4nDkcOOwpbDiMKvwpTDnMKUw5XCscKHwr_DkcKTw5fDnsOXw5RBw4HDqMOGw57DoMKGw4XClcOHw6TChMORw5nDmMOfw5LClsONw6HDrcKRKw==', 'Linux', 'CentOS', 'Process', 1545825900.82985, NULL, 'KPI', 'anand', 1, 4, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (13, 'R', 'new bot 1', 'new1', 'yaml', 'w4_DmsOrwo_Ch8OXw6DDinbDmsKGw5jClcOaw5jCjcOTwqZvw5rDkcKYwoHDm8Odw5vChsKhfg==', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'new1', NULL, 1545915327.89454, 'KPI', NULL, NULL, 14, NULL);
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (14, 'R', 'new bot5', 'sdfsdf', 'yaml', 'w5TDmcOaw6LChcOUfsOYw5DDksKUw4XDm37DosKFw5R-w5jDkMOSwpTDhcOb', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'sdfsdf', NULL, 1546005275.36365, 'KPI', NULL, NULL, 14, NULL);
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (17, 'R', 'List SQL Sessions', 'List all SQL Session', 'yaml', 'a8KiwqHCnCvCm8KUw43Dm8OfwpXDlMKvwpTCoFPCpcKiwpXCmsKcT8KSf8KUwo_ChMOdw6LDk8ORw4_ClcOKw6TDosKpQcOaw6PDiMONw5grwoHClcObw5DClcOWw5nDl8OLw5LCgsOEw6nDp8KpQcOUw5XDkcOfw5ErwoHClcOow5DClMOZw6fCn3bCjEHCjsKVw6LDkMKOw5PCrsKFwrHDpMKGw4TDqsOow5RBw4_ClMORw5vDj8KCw43ClcOXw57CjsObw5XDk8OQdkHCgcKVwpTDksKQw5vDocOGw5rDkFvCgcKkw6bDnsKQw6LCo8K5wrHCv3XCj8Olw615QcKOwpTChcOQw5HCjcOGw5zDlcOjwobDjcOow5TCpsKMwo3DkMOYw5XDm8KJw53Dp8OZdsKMQcKBwpXDpsOUwojDl8Onw5nDkcOeW8KBw6fDmcOiwpbDmsOob3bCjEHCjsKVw6LDkMKOw5PCrsKFwr_DlMKQw5jClcOmw5TClMOjw6DDmcOfdkHCgcKVwpTDk8KGw5DDqcOMwqZ2QcKBwpXClMKPQcOkw5XDl8KmwozCk8OGw6jDqcObwpXCnMOnw5nDkMObwpbDlX_ClMKPQcKOw5jDisOYw5HCiMOCw6nDmcOOwpXDncKuwoXDmMObwoTDgsOhw5zDnsKUw6J-', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'SQLConnection', NULL, NULL, 'KPI', 'Anand', 1, NULL, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (5, 'D', 'Load Diagnose', 'TOP 5 Process Consuming CPU', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCm8KUw5PDjcOZwobCm8KVw4bDlMKVw6DDncOKw6LDkUHDlcOkw6TCj1bCjsOEw5fDm8OPwobDlMOowpTCssKQw5zDp8Oaw5nDlcKPw4jClcOhw57Ck8OTwpTCqMK8w4ErwoHClcKUwo_ClMOWw5nDkcOYwqZBw5HDqMKUwpzChsOdwpTDiMOZw5BNwobDmMOkw6RBwpvCocOYw5vDnsKVwp7CosKZw5LCkcOjwpTDocKMw5TChsOCw5nClMKcUsKfwpTDocKMw6DCgsOKw6HClMKcUsKefsKFwozCjEHDk8Oaw5vDmMKUw6LDmcOXwqbCjMKTw4bDqMOpw5vClXjClMKFwpnCjMKPw4LDosOZwqlBwrLDncOYw5zDmMKCw5rClcOow5fChsKOwr7CuMK7wrpBw4fDpMOmw5zCgsOiw6jDisOQwozCk8OGw6jDqcObwpXDoX7ChcKMwoxBw4XDmsOWw6TCiMKowpTDm8ONw55ew5PDmsOnw6TCjcOifg==', 'Linux', 'CentOS', 'Load', 1545825900.82985, NULL, 'KPI', 'anand', 1, 4, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (6, 'R', 'Load Remediate', 'TOP 5 Process Consuming CPU', 'yaml', 'wo7CosKheU7CjsOcw5TDn8OgwpTCm8KVw5XDm8KNeMKUwoXDk8ONwpXDicOaw6bDjsKHw4_Dl8OZw5_CpkHCp8OWw6DDosKGeMKUwoXDjsORwoTDkMOiw5nCqUHDp8OZw5h2woxBw5fDlsOmw6LCgMOUw53DkcORw59ba8KVwpTCj0HCm8KUwpTDocOfwpPCkMOhw6PDksKCw5rCo8OGw6HDoMKQw4rDo8Oow5TCjcOaw53ClMOVw5vChsOPw5zDncOdwobCncOnw4rDnsOiworDhMOaw6fCnsKEw5vDmMOHwpvCmsKXw4LDqsOgw6Mrwo7ClMOZw43Dn8KMw5TCr37Cj0HCm8KUw5PDjcOZwobCm8KVw4bDlMKVw6DDncOKw6LDkUHDlcOkw6TCj1bCjsOEw5fDm8OPwobDlMOowpTCssKQw5zDp8Oaw5nDlcKPw4jClcOhw57Ck8OTwpTCqMK8w4ErwoHClcKUwo_ClMOWw5nDkcOYwqZBw5HDqMKUwpzChsOdwpTDiMOZw5BNwobDmMOkw6RBwpvCocOYw5vDnsKVwp7CosKZw5LCkcOjwpTDocKMw5TChsOCw5nClMKcUsKfwpTDocKMw6DCgsOKw6HClMKcUsKefsKFwozCjEHDk8Oaw5vDmMKUw6LDmcOXwqbCjMKTw4bDqMOpw5vClXjClMKFwpnCjMKPw4LDosOZwqlBwrLDncOYw5zDmMKCw5rClcOow5fChsKOwr7CuMK7wrpBw4fDpMOmw5zCgsOiw6jDisOQwozCk8OGw6jDqcObwpXDoX7ChcKMwoxBw4XDmsOWw6TCiMKowpTDm8ONw55ew5PDmsOnw6TCjcOifg==', 'Linux', 'CentOS', 'Load', 1545825900.82985, NULL, 'KPI', 'anand', 1, 4, 'Y');
INSERT INTO public.ai_bot_repo (pk_bot_id, bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, created_date, modified_date, botargs, created_by, bot_system, fk_branch_id, active_yn) VALUES (11, 'R', 'Script 2', 'neww', 'yaml', 'wo7CosKhfCvCm8KUw43Dm8OfwpXDlMKvwpTDkMKNw5rCgW_CjMKMwojDgsOpw5zDlMKTw43DmsOGw4_DoMKUwpvClcK6w5DCjcOhw5lydsKMQcOXw5bDpsOiwoDDlMOdw5HDkcOfW25_wpTCj0HCjsKhwoXCm8OhwpTDk8Kkw6DDnsKEw4_DoMKUw43DocKVw5DDnsOiw6PChsOaw6DDjsKbw5XCkMOGw6PDm8OYwo_Dk8Kjw5jDkcOewpfDisOYw5nDolDDkcOhw4nDjsKbT8OUw5rDl8OhwobDosOnwpTDp8OnQcOCw6PDp8OYwoPDmsOZw4TDlMObwpTDlcOjw5XDnMKGwo7DscOiwprDpcKOw43Cgn7Cj0HDosOVw5jDl8OfW25_wpTCj0HCjsKhwoXDmsONwo7DhsKvwpTDgsKVw4_DpsOZwozDjUHDlMOaw6bDpcKKw5HDmXJ2woxBwoHClcKUwo_CmMOXw6LDhMOfw5HCk8OXw57Dl8OUW3t-woXCjMKMQcKBwpXClMKPwo_Dj8Ohw4rCpsKMQ8Ocw7DClMK6ccK3wpTDosOpwo4ua8KVwpTCj0HCjsKUwoXCjMOfwpXDgsOpw5nCqUHDocOow4bDnsOgwobDhcKCfsKPQcKOwpTCksKMw5DChsODw6rDm8KpQcObw6fDjMKpwo50w4bDp8Oqw5jChMOTwpTCuMOgw43Ck8OVw5rDmMKPdMOjw5fDiMORw5_ClMOHw6rDoMObwprCkMKBbw==', 'Windows', 'Microsoft Windows Server 2012 R2 Standard', 'LOCAL SCRIPT', NULL, 1545908050.40012, 'KPI', NULL, NULL, 14, 'Y');


--
-- Name: ai_bot_repo_pk_bot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_bot_repo_pk_bot_id_seq', 19, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_machine_class; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (1, 'AIX ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (2, 'HPUX ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (3, 'Linux ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (4, 'Solaris ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (5, 'UNIX ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (6, 'Windows ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (7, 'Router ', 'Y');
INSERT INTO public.ai_machine_class (mclass_id, mclass_name, active_yn) VALUES (8, 'Switch ', 'Y');


--
-- Name: ai_machine_class_mclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_machine_class_mclass_id_seq', 8, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_policyaction_meta; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_policyaction_meta (actionid, actionname) VALUES (1, 'EMAIL');
INSERT INTO public.ai_policyaction_meta (actionid, actionname) VALUES (2, 'LOCAL SCRIPT');
INSERT INTO public.ai_policyaction_meta (actionid, actionname) VALUES (3, 'REMOTE SCRIPT');
INSERT INTO public.ai_policyaction_meta (actionid, actionname) VALUES (4, 'SMS');


--
-- Name: ai_policyaction_meta_actionid_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_policyaction_meta_actionid_seq', 4, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_policyoperator_meta; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_policyoperator_meta (operatorid, operator) VALUES (1, 'equal');
INSERT INTO public.ai_policyoperator_meta (operatorid, operator) VALUES (2, 'not equals');
INSERT INTO public.ai_policyoperator_meta (operatorid, operator) VALUES (3, 'contains');


--
-- Name: ai_policyoperator_meta_operatorid_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_policyoperator_meta_operatorid_seq', 3, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_resource_class; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (1, 'Backend ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (2, 'CoreApplication ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (3, 'Database ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (4, 'Frontend ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (5, 'Infrastructure ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (6, 'Interface ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (7, 'Middleware ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (8, 'Monitoring ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (9, 'PhysicalObject ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (10, 'Process ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (11, 'Service ', 'Y');
INSERT INTO public.ai_resource_class (rclass_id, rclass_name, active_yn) VALUES (12, 'Storage ', 'Y');


--
-- Name: ai_resource_class_rclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_resource_class_rclass_id_seq', 12, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_software_class; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (1, 'Administration ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (2, 'ApplicationServer ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (3, 'Automation ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (4, 'Backup ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (5, 'DBMS ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (6, 'FileServices ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (7, 'Firewall ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (8, 'IAM ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (9, 'ITSM ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (10, 'LDAP ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (11, 'Virtualization ', 'Y');
INSERT INTO public.ai_software_class (sclass_id, sclass_name, active_yn) VALUES (12, 'WebServer ', 'Y');


--
-- Name: ai_software_class_sclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_software_class_sclass_id_seq', 12, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_software_subclass; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (1, 'ApacheHTTPD ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (2, 'Biztalk ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (3, 'DB2 ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (4, 'Elasticsearch ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (5, 'Glassfish ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (6, 'HyperV ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (7, 'IIS ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (8, 'JIRA ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (9, 'Kafka ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (10, 'lighttpd ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (11, 'MongoDB ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (12, 'MySQL ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (13, 'Nagios ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (14, 'nginx ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (15, 'OpenLDAP ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (16, 'OpenSSH ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (17, 'Oracle ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (18, 'PostgreSQL ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (19, 'Python ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (20, 'QlikView ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (21, 'SCOM ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (22, 'Sendmail ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (23, 'SFTP ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (24, 'Tomcat ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (25, 'Zabbix ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (26, 'Zookeeper ', 'Y');
INSERT INTO public.ai_software_subclass (ssclass_id, ssclass_name, active_yn) VALUES (27, 'VMWare ', 'Y');


--
-- Name: ai_software_subclass_ssclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_software_subclass_ssclass_id_seq', 27, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_triage_master; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (7, 'Check Folder Size', 'Check Folder Size', NULL, 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (8, 'Check File Exists', 'Check File Exists', NULL, 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (11, 'Check Process', 'Check Process', NULL, 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (3, 'Service Status', 'Service Status', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/service_status', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (2, 'Telnet', 'Telnet', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/telnet', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (4, 'CPU Usage', 'CPU Usage', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/cpu_usage', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (6, 'Memory Usage', 'Memory Usage', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/memory_usage', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (5, 'Disk Usage', 'Disk Usage', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/disk_usage', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (9, 'Execute Command', 'Execute Command', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/exec_cmd', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (10, 'Service Restart', 'Service Restart', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/service_restart', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (12, 'Kill Process', 'Kill Process', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/kill_process', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (13, 'Kill SQL Session', 'Kill SQL Session', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/kill_sql_session', 'Y');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (14, 'Exec SQL CMD', 'Exec SQL CMD', 'http://127.0.0.1:8000/ui/api1.0/triage/bots/exec_sql_cmd', 'N');
INSERT INTO public.ai_triage_master (pk_triage_id, triage_name, triage_desc, triage_rest_call, active_yn) VALUES (1, 'Ping', 'Ping', 'http://127.0.0.1:5001/ui/api1.0/triage/bots/ping', 'Y');


--
-- Name: ai_triage_master_pk_triage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_triage_master_pk_triage_id_seq', 14, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_triage_dynamic_form; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (1, 3, 'Service Name', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (2, 2, 'Port', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (3, 9, 'Command', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (4, 10, 'Service Name', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (5, 12, 'Process ID', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (6, 13, 'Session ID', 'TextBox', 1, 'Y');
INSERT INTO public.ai_triage_dynamic_form (pk_triage_df, fk_triage_id, form_control_label, form_control_type, form_control_order, active_yn) VALUES (7, 14, 'Command', 'TextBox', 1, 'Y');


--
-- Name: ai_triage_dynamic_form_pk_triage_df_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ai_triage_dynamic_form_pk_triage_df_seq', 7, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: attributes; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.attributes (attr_id, mars_type, item_class, item_sub_class, attribute) VALUES (1, 'software', 'dbms', 'postgresql', 'ipaddress,port,username,password,dbname');


--
-- Name: attributes_attr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.attributes_attr_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: configuration; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.configuration (configid, configname, configip, configport, dbname, username, password, communicationtype, extra2) VALUES (2, 'CMDB', '127.0.0.1', 27017, 'admin', 'root', 'w5PDpMOjw6NSwqDCpw==', NULL, NULL);
INSERT INTO public.configuration (configid, configname, configip, configport, dbname, username, password, communicationtype, extra2) VALUES (1, 'MQ', '127.0.0.1', 5672, 'autointelli', 'autointelli', 'w4LDqsOow57CisOcw6jDisOYw5jCig==', NULL, NULL);
INSERT INTO public.configuration (configid, configname, configip, configport, dbname, username, password, communicationtype, extra2) VALUES (3, 'RECEIVER', '127.0.0.1', 5006, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.configuration (configid, configname, configip, configport, dbname, username, password, communicationtype, extra2) VALUES (6, 'SMTP', 'webmail.autointelli.com', 25, NULL, 'vignesh.m@autointelli.com', 'wqjDpMOjw5bCjcOTwrTClsKewp8=', 'smtp', NULL);
INSERT INTO public.configuration (configid, configname, configip, configport, dbname, username, password, communicationtype, extra2) VALUES (5, 'LDAP', '192.168.1.104', 389, NULL, NULL, NULL, 'ldaps', NULL);


--
-- Name: configuration_configid_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.configuration_configid_seq', 6, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ea_status; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.ea_status (pk_ea_status_id, stat_description, active_yn) VALUES (5, 'closed', 'Y');
INSERT INTO public.ea_status (pk_ea_status_id, stat_description, active_yn) VALUES (1, 'open', 'Y');
INSERT INTO public.ea_status (pk_ea_status_id, stat_description, active_yn) VALUES (2, 'wip', 'Y');
INSERT INTO public.ea_status (pk_ea_status_id, stat_description, active_yn) VALUES (3, 'pending', 'Y');
INSERT INTO public.ea_status (pk_ea_status_id, stat_description, active_yn) VALUES (4, 'resolved', 'Y');


--
-- Name: ea_status_pk_ea_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.ea_status_pk_ea_status_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: itsm_dynamic_form; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (2, 'SDP', 'CREATE', 'Subject', 'TextBox', 2, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (3, 'SDP', 'CREATE', 'Description', 'TextArea', 3, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (5, 'SDP', 'CREATE', 'Priority', 'Dropdown', 5, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (7, 'SDP', 'CREATE', 'Group', 'Dropdown', 7, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (10, 'SDP', 'CREATE', 'Status', 'Dropdown', 10, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (12, 'SDP', 'CREATE', 'Category', 'Dropdown', 12, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (13, 'SDP', 'CREATE', 'Sub-Category', 'Dropdown', 13, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (14, 'SDP', 'UPDATE', 'Ticket ID', 'Label', 1, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (15, 'SDP', 'UPDATE', 'Group', 'Dropdown', 2, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (16, 'SDP', 'STATUS_CHANGE', 'Ticket ID', 'Label', 1, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (17, 'SDP', 'STATUS_CHANGE', 'Status', 'Dropdown', 2, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (18, 'SDP', 'WORKLOG_UPDATE', 'Ticket ID', 'Label', 1, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (19, 'SDP', 'WORKLOG_UPDATE', 'Worklog', 'TextArea', 2, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (20, 'SDP', 'RESOLVE', 'Ticket ID', 'Label', 1, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (22, 'SDP', 'RESOLVE', 'Resolution Comment', 'TextArea', 3, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (1, 'SDP', 'CREATE', 'Requester', 'TextBox', 1, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (4, 'SDP', 'CREATE', 'Request Template', 'Label', 4, 'N');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (6, 'SDP', 'CREATE', 'Site', 'Dropdown', 6, 'N');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (9, 'SDP', 'CREATE', 'Level', 'Dropdown', 9, 'N');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (11, 'SDP', 'CREATE', 'Service Category', 'Dropdown', 11, 'N');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (21, 'SDP', 'RESOLVE', 'Status', 'Label', 2, 'N');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (8, 'SDP', 'CREATE', 'Technician', 'TextBox', 8, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (23, 'SDP', 'WORKLOG_UPDATE', 'Technician', 'TextBox', 3, 'Y');
INSERT INTO public.itsm_dynamic_form (fk_form_id, itsm_name, ticket_action, form_control_label, form_control_type, form_control_order, active_yn) VALUES (24, 'SDP', 'UPDATE', 'Technician', 'TextBox', 3, 'Y');


--
-- Name: itsm_dynamic_form_fk_form_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.itsm_dynamic_form_fk_form_id_seq', 24, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: rulemeta; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (3, 'Hostname', 'alert_data.ci_name');
INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (4, 'Event Description', 'alert_data.description');
INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (5, 'Event Component', 'alert_data.component');
INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (6, 'Event Severity', 'alert_data.severity');
INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (2, 'OS', 'ai_machine.osname');
INSERT INTO public.rulemeta (metadataid, componentname, mappingname) VALUES (1, 'Platform', 'ai_machine.platform');


--
-- Name: rulemeta_metadataid_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.rulemeta_metadataid_seq', 6, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: severity_mapping; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (1, 'nagios', 'ok', 'ok', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (2, 'nagios', 'warning', 'warning', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (3, 'nagios', 'critical', 'critical', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (4, 'nagios', 'unknown', 'unknown', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (5, 'zabbix', 'average', 'warning', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (7, 'zabbix', 'major', 'critical', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (8, 'zabbix', 'unknown', 'unknown', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (6, 'zabbix', 'minor', 'warning', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (9, 'autointelli', 'ok', 'ok', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (10, 'autointelli', 'warning', 'warning', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (11, 'autointelli', 'critical', 'critical', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (12, 'autointelli', 'unknown', 'unknown', 'Y');
INSERT INTO public.severity_mapping (pk_map_id, mtool_name, mseverity, aiseverity, active_yn) VALUES (13, 'HP OMI', 'critical', 'critical', 'Y');


--
-- Name: severity_mapping_pk_map_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.severity_mapping_pk_map_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_permission; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (1, 'R', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (2, 'RW', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (3, 'RWX', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (4, 'WX', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (5, 'RX', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (6, 'W', 'Y');
INSERT INTO public.tbl_permission (pk_permission_id, permission_name, active_yn) VALUES (7, 'X', 'Y');


--
-- Name: tbl_permission_pk_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_permission_pk_permission_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_role; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (1, 'admin', 'Y');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (2, 'superadmin', 'Y');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (3, 'readonly', 'Y');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (5, 'Admin-1', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (7, 'Admin2', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (10, 'admin3', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (11, 'admin3', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (8, 'admin2', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (9, 'admin2', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (4, 'test', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (13, 'misell', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (16, 'user', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (12, 'admin4', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (15, 'admin4', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (6, 'admin1', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (14, 'admin1', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (17, 'test user', 'N');
INSERT INTO public.tbl_role (pk_role_id, role_name, active_yn) VALUES (18, 'monitor', 'N');


--
-- Name: tbl_role_pk_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_role_pk_role_id_seq', 18, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_tab; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (1, 'user_management', 'Y');
INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (2, 'dashboard', 'Y');
INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (3, 'evm', 'Y');
INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (4, 'automation', 'Y');
INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (5, 'review', 'Y');
INSERT INTO public.tbl_tab (pk_tab_id, tab_name, active_yn) VALUES (6, 'cmdb', 'Y');


--
-- Name: tbl_tab_pk_tab_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_tab_pk_tab_id_seq', 6, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_role_tab_permission; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (25, 5, 1, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (26, 5, 2, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (27, 5, 3, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (28, 5, 4, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (35, 7, 1, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (36, 7, 2, NULL, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (37, 7, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (38, 7, 4, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (39, 7, 6, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (40, 8, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (41, 8, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (42, 8, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (43, 8, 4, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (44, 8, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (45, 8, 6, NULL, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (47, 10, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (48, 10, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (49, 10, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (50, 10, 4, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (51, 10, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (52, 10, 6, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (61, 16, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (62, 16, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (63, 16, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (64, 16, 4, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (65, 16, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (66, 16, 6, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (67, 17, 1, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (68, 17, 2, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (69, 17, 3, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (70, 17, 4, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (32, 6, 4, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (34, 6, 6, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (30, 6, 2, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (31, 6, 3, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (33, 6, 5, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (29, 6, 1, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (19, 4, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (20, 4, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (21, 4, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (22, 4, 4, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (23, 4, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (24, 4, 6, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (71, 17, 5, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (72, 17, 6, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (73, 18, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (1, 1, 1, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (4, 1, 2, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (2, 1, 3, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (3, 1, 4, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (5, 1, 5, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (15, 1, 6, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (12, 3, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (13, 3, 1, 6, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (14, 3, 5, 2, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (11, 3, 2, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (53, 12, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (54, 12, 2, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (55, 12, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (56, 12, 4, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (57, 12, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (58, 12, 6, 1, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (17, 3, 4, 2, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (18, 3, 6, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (7, 2, 3, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (8, 2, 1, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (10, 2, 5, 3, 'N');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (6, 2, 2, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (9, 2, 4, 3, 'Y');
INSERT INTO public.tbl_role_tab_permission (pk_role_tab_perm_map_id, fk_role_id, fk_tab_id, fk_permission_id, active_yn) VALUES (16, 2, 6, 3, 'Y');


--
-- Name: tbl_role_tab_permission_pk_role_tab_perm_map_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_role_tab_permission_pk_role_tab_perm_map_id_seq', 73, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_user_type; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_user_type (pk_user_type_id, user_type_desc, active_yn) VALUES (1, 'Non LDAP', 'Y');
INSERT INTO public.tbl_user_type (pk_user_type_id, user_type_desc, active_yn) VALUES (2, 'LDAP', 'Y');


--
-- Name: tbl_user_type_pk_user_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_user_type_pk_user_type_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_user_details; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (3, 'dinesh@autointellidev.com', 'U2FsdGVkX1+OogHs9dlFCnyMQe++QM18oVtw8vWRE2k=', 'Dinesh', 'B', 'Balaraman', 'dinesh@gmail.com', 1, '2018-09-19', 1, '2019-07-24', NULL, '8553184171', 'Y', 186, 2, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (48, 'anand@autointellidev.com', 'U2FsdGVkX1/QQ2+O1brPDy9DohZRHCcfOEcc3djdJyQ=', 'Anand', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-10-04', 1, '2019-11-08', NULL, '9988776655', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (45, 'Enduser', 'U2FsdGVkX19+evl5Plb67hXKKCsC6su3DsjWDt4//Ww=', 'Enduser', 'Enduser', 'end', 'mukesh.k@gmail.com', 1, '2019-09-27', NULL, NULL, NULL, '9999933333', 'Y', 186, 2, 1, 0, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (40, 'malvino.bkp', 'U2FsdGVkX19lYPrTAr26LGdKuy9FtJ1Ipqm0hhucFhc=', 'malvino', '', 't', 'malvino@autointelli.com', 1, '2019-09-18', NULL, NULL, NULL, '97855456734', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (42, 'kavitha.bkp', 'U2FsdGVkX1/kJyNsWrzgwhHekCgeh/k/xGNgqjvOeq8=', 'Kavitha', '', 'M', 'kavitha.m@autointelli.com', 1, '2019-09-26', NULL, NULL, NULL, '34534534545', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (51, 'kietestone.bkp', 'U2FsdGVkX1/9Ni7InS6joOh8pRDq9I5ggrmQEIOetoM=', 'kietest', '', 'one', 'kietestone@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '4545345435', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (54, 'kietestfour.bkp', 'U2FsdGVkX1+mSKM2urT/IohUfar/zw9MUSgeQSC71SE=', 'kietest', '', 'four', 'kietestfour@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '9123123213', 'N', 154, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (57, 'kietestseven.bkp', 'U2FsdGVkX1+4ixcg0IhxGvueMnd4F5KzWDfI1Fvz+pM=', 'kietest', '', 'seven', 'kietestseven@abc.com', 1, '2019-10-08', 1, '2019-10-08', NULL, '98234234234', 'N', 221, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (60, 'kietestten.bkp', 'U2FsdGVkX1/+BuCA2/pNjeRu8vSt1AOVphk+ce+1H6w=', 'kietest', '', 'ten', 'kietestten@abc.com', 1, '2019-10-09', NULL, NULL, NULL, '63453453452', 'N', 218, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (25, 'guest.bkp', 'U2FsdGVkX19MGh53XxA9RQqAnkEmk4F/WElOykh3wEE=', 'guest', 'w', 'w', 'guest@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '8745345678', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (19, 'guest.bkp', 'U2FsdGVkX18GcR1zzmXYVSVyh+KkM9wuzMRMfpK36HI=', 'guest', '', 'd', 'guest@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9867654342', 'N', 186, 6, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (5, 'Test.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'Test 1', 'Test 2', ' Main', 'test@autointelli.com', 1, '2019-01-08', 1, '2019-07-03', NULL, '98123123123', 'N', 186, 3, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (10, 'mukesh.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'mukesh', 'k', 'kumar', 'mukesh@autointelli.com', 1, '2019-07-03', 1, '2019-07-03', NULL, '8756425345', 'N', 186, 2, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (24, 'malvino.bkp', 'U2FsdGVkX19vNtDkAdXGwKPRBCtNb37dK3WnDqe+rt4=', 'malvino', '', 't', 'malvino@autointelli.com', 1, '2019-07-17', 1, '2019-07-24', NULL, '9856434567', 'N', 186, 2, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (6, 'anand@autointellidev.com.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'Anandaraaj', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-04-10', 1, '2019-07-03', NULL, '8861631703', 'N', 186, 3, 2, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (27, 'malvino.bkp', 'U2FsdGVkX19vNtDkAdXGwKPRBCtNb37dK3WnDqe+rt4=', 'malvino', '', 't', 'malvino@autointelli.com', 1, '2019-07-24', 1, '2019-07-24', NULL, '9856434567', 'N', 186, 2, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (28, 'malvino.bkp', 'U2FsdGVkX1/a+oLBuKVSYLpVE5ntP5iz/g7tY5tr3QA=', 'malvino', 'w', 't', 'malvino@autointelli.com', 1, '2019-07-24', NULL, NULL, NULL, '345643455', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (30, 'malvino.bkp', 'U2FsdGVkX1/7O6OAL7837IuWkCZTmf8DBB0hkhfOG3o=', 'malvino', '', 't', 'malvino@autointelli.com', 1, '2019-07-24', NULL, NULL, NULL, '234556667777', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (35, 'satz.bkp', 'U2FsdGVkX19RFzIzBalwjtZ3Ov+4RecioxYkvHealCQ=', 'satz', '', 'satz', 'satz@autointelli.com', 1, '2019-09-03', NULL, NULL, NULL, '789654321', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (33, 'admin.bkp', 'U2FsdGVkX1/ui4d61my4/pOBA1wqHZEGPQ24jhvWpDI=', 'vino', '', 'u', 'vino@autointelli.com', 1, '2019-08-29', NULL, NULL, NULL, '1234567890', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (26, 'satz.bkp', 'U2FsdGVkX1/XS4Ws1sHkDwqM7oUbPZMfXceGqUWCFOE=', 'satz', '', 'SK', 'sk@gmail.com', 1, '2019-07-22', 1, '2019-09-02', NULL, '2112122121', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (38, 'mal.bkp', 'U2FsdGVkX1+CfWiRJ2PqZuakiFNi2eGyminSm/Krv4E=', 'mal', 'a', 'vino', 'malvino@autointelli.com', 1, '2019-09-10', NULL, NULL, NULL, '1254678987', 'N', 186, 12, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (32, 'malvino.bkp', 'U2FsdGVkX18yKza5jF1Dc/7p8H0K7tRWap59EI8N2v0=', 'malvino', '', 'T', 'malvino.t@autointelli.com', 1, '2019-07-25', NULL, NULL, NULL, '9878787878', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (37, 'malvino.bkp', 'U2FsdGVkX19O9bWpeYpg2rpZLfGfCldXL/tbeWU7wjw=', 'mal', 'a', 'vino', 'mal@autointelli.com', 1, '2019-09-10', NULL, NULL, NULL, '567456779', 'N', 186, 6, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (46, 'sk_admin', 'U2FsdGVkX18S2AREs8W9p9AHKKxYeF97UWkogp3YJ40=', 'sathish', '', 'sk', 'sathish@autointelli.com', 1, '2019-10-04', NULL, NULL, NULL, '9090900909', 'Y', 186, 1, 1, 3, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (2, 'Anand', 'U2FsdGVkX1/vxJ+xC7obdkzeolaIEix57mCHKIBXU60=', 'Anand', '', 'Parthiban', 'anand_p@live.in', 1, '2018-09-15', 1, '2019-09-23', NULL, '8861631703', 'Y', 186, 1, 1, 0, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (43, 'kavitha', 'U2FsdGVkX1/H0KvKs3GWZV1uWWbzfxkmdUe1Tjbghoo=', 'Kavitha', '', 'Mohan', 'kavitha.m@autointelli.com', 1, '2019-09-26', NULL, NULL, NULL, '978977098', 'Y', 186, 3, 1, 0, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (13, 'vicky', 'U2FsdGVkX18n+ZJafu2hadIwRMmyhKFNoBgFn0+RHWI=', 'vicky', 'g', 'g', 'vicky@autointelli.com', 1, '2019-07-09', 1, '2019-09-23', NULL, '9799357595', 'Y', 186, 3, 1, 4, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (49, 'anand@autointellidev.com', 'U2FsdGVkX1/QQ2+O1brPDy9DohZRHCcfOEcc3djdJyQ=', 'Anand', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-10-08', 1, '2019-11-08', NULL, '9988776655', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (39, 'anand@autointellidev.com', 'U2FsdGVkX1/QQ2+O1brPDy9DohZRHCcfOEcc3djdJyQ=', 'Anand', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-09-14', 1, '2019-11-08', NULL, '9988776655', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (41, 'malvino.bkp', 'U2FsdGVkX19wlZ0NcDX/gKbruIhUtPS8eS8UYCiyglw=', 'malvino', 't', 'vino', 'malvino@autointelli.com', 1, '2019-09-19', NULL, NULL, NULL, '98463746347', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (44, 'manager', 'U2FsdGVkX1/vS9jSPayUp3CE18RGP2LqVwgGByDgk0M=', 'manager', 'manager', 'manager', 'mukesh.k@autointelli.com', 1, '2019-09-27', NULL, NULL, NULL, '9999944444', 'Y', 186, 2, 1, 0, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (47, 'anand@autointellidev.com', 'U2FsdGVkX1/QQ2+O1brPDy9DohZRHCcfOEcc3djdJyQ=', 'Anand', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-10-04', 1, '2019-11-08', NULL, '9988776655', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (52, 'kietesttwo.bkp', 'U2FsdGVkX18SQGmIu8SaSc/Vf3hfvVYLPP9jOjSVul8=', 'kietest', '', 'two', 'kietesttwo@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '8623412345', 'N', 261, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (55, 'kietestfive.bkp', 'U2FsdGVkX1+b/NsEWIXfl+CP2pGM+ec3AoURvoJeXHk=', 'kietest', '', 'five', 'kietestfive@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '9123123211', 'N', 198, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (58, 'kietesteight.bkp', 'U2FsdGVkX19pmya7BSfEIz+SHf3PvYCGhdlVp6QUUSU=', 'kietest', '', 'eight', 'kietesteight@abc.com', 1, '2019-10-09', NULL, NULL, NULL, '545242342342', 'N', 8, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (61, 'kietesteleven.bkp', 'U2FsdGVkX1+cwZLzNeBNfqmZkbfMa6PjZJHclbeN3Dk=', 'kietest', '', 'eleven', 'kietesteleven@abc.com', 1, '2019-10-09', NULL, NULL, NULL, '9234234324', 'N', 167, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (4, 'guest.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'guest', 'guest', 'guest', 'guest@autointelli.com', 1, '2018-09-19', 1, '2019-07-02', NULL, '08553184171', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (14, 'admin1.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'satz', '', 'Sk', 'satz@gmail.com', 1, '2019-07-13', NULL, NULL, NULL, '4545454545', 'N', 186, 6, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (11, 'test2.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'test2', 's', 'time', 'test2@autointelli.com', 1, '2019-07-06', NULL, NULL, NULL, '9543276789', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (15, 'test1.bkp', 'U2FsdGVkX18DoFrpGoqzIrUOJKpU/XcB40v377YuK58=', 'test ', 'u', 't', 'test@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9867356217', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (21, 'guest.bkp', 'U2FsdGVkX188JVB8eUyyA7Q9ZzduMSqylfVuSss0AMc=', 'guest', 'd', 'm', 'guest@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '96745678934', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (22, 'user1.bkp', 'U2FsdGVkX185zSNWAnu3ry5Mi1MtvlIfA0WJQHZPGyw=', 'user1', '', 'e', 'user1@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9865478765', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (36, 'saz.bkp', 'U2FsdGVkX18TqM/b+q1GzqI6nl8S6JLc05VGToofRJ8=', 'saz', 'v', 's', 'saz@autointelli.com', 1, '2019-09-10', NULL, NULL, NULL, '9456743216', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (56, 'kietestsix.bkp', 'U2FsdGVkX1/SVu/GGM8rg54aaQr/SV9Og5ZmlwhsKrQ=', 'kietest', '', 'six', 'kietestsix@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '9723342342', 'N', 7, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (59, 'kietestnine.bkp', 'U2FsdGVkX19hI03iEmnfAQ2hoH8qS1CL7mHImRiIlBg=', 'kietest', '', 'nine', 'kietestnine@abc.com', 1, '2019-10-09', NULL, NULL, NULL, '45645654645', 'N', 197, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (29, 'muk.bkp', 'U2FsdGVkX18+lJ5zq7VF41QeQZxSvVy2M2XNzt4Xfx0=', 'mukesh', 'w', 'q', 'mukesh@autointelli.com', 1, '2019-07-24', NULL, NULL, NULL, '345634645636', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (23, 'user1.bkp', 'U2FsdGVkX1/prQi19bDdUdWuGrUO3ug9yXkGSxjMEtQ=', 'user1', '2', 'w', 'user1@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9856434567', 'N', 186, 2, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (17, 'malvino.bkp', 'U2FsdGVkX1/2//jEmqmsz+QgqvjtdbE4oOa500Dovtg=', 'malvino', '', 't', 'malvino@autointelli.com', 1, '2019-07-17', 1, '2019-07-17', NULL, '9864378364', 'N', 186, 3, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (20, 'guest.bkp', 'U2FsdGVkX18/knw2tcUnlCeO0h2P6QhGyn0cjo1eeKo=', 'guest', '', 'd', 'guest@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9867654342', 'N', 186, 6, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (7, 'admin.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'admin', 'admin', 'role', 'admin@autointelli.com', 1, '2019-07-02', NULL, NULL, NULL, '8976543210', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (8, 'sam.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'sathis', 'k', 'kumar', 'sam@gmail.com', 1, '2019-07-02', NULL, NULL, NULL, '89876546534', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (9, 'sam.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'sathis', 'k', 'kumar', 'sam@gmail.com', 1, '2019-07-02', NULL, NULL, NULL, '89876546534', 'N', 186, 1, 2, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (12, 'kumar.bkp', 'U2FsdGVkX1+SrA59cPuVcwYm3ijLwjlxpVxRXLKfoYI=', 'dell', 'hp', 'hp', 'mukeshmech10@gmail.com', 1, '2019-07-08', NULL, NULL, NULL, '89876546534', 'N', 1, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (18, 'test2.bkp', 'U2FsdGVkX19bhRDmuotRhQuh5PORSawK+F64NpgToN8=', 'test2', '', 'e', 'test2@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '9867564372', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (16, 'testme.bkp', 'U2FsdGVkX1+RFf39GV2mImh+c1aZbymRNXEpsdA5hXQ=', 'test', '1', 'e', 'test1@autointelli.com', 1, '2019-07-17', NULL, NULL, NULL, '83456765', 'N', 186, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (53, 'kietestthree.bkp', 'U2FsdGVkX1+6un4WXLtvySgRddntRZ5goLy13OV9j1o=', 'kietest', '', 'three', 'kietestthree@abc.com', 1, '2019-10-08', NULL, NULL, NULL, '576567657567', 'N', 196, 1, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (31, 'kavitha.m.bkp', 'U2FsdGVkX19FxdrW1KEJLFnceydBWGKaZncDllpwDA8=', 'Kavitha', '', 'M', 'kavitha.m@autointelli.com', 1, '2019-07-25', NULL, NULL, NULL, '9876543256', 'N', 186, 3, 1, 0, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (62, 'malvino.bkp', 'U2FsdGVkX1/oA+RMGG323nmfLlfvHUjUpEPpi5IyzXU=', 'malvino', 'a', 'vino', 'malvino@autointelli.com', 1, '2019-11-08', NULL, NULL, NULL, '54667890877', 'N', 186, 3, 1, NULL, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (63, 'malvino@autointellidev.com.bkp', 'U2FsdGVkX189QW9uAl0B6l2m42Db10VRn24wkjdxE4s=', 'Malvino', '', 'Malvino', 'malvino@autointelli.com', 1, '2019-11-08', NULL, NULL, NULL, '8532842555', 'N', 186, 2, 2, NULL, NULL);
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (1, 'admin', 'U2FsdGVkX19cYDKT6jt5zGTUnLEnU2oD8gwwYWNc7WY=', 'admin', '', 'admin', 'admin@autointelli.com', NULL, NULL, 1, '2019-09-03', NULL, '8553184171', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (64, 'malvino@autointellidev.com', 'U2FsdGVkX1/lvsbpBl0S3qTCh0eO41232uyDBrMPjtA=', 'malvino', '', 't', 'malvino@autointellidev.com', 1, '2019-11-08', NULL, NULL, NULL, '4567678987', 'Y', 186, 1, 2, NULL, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (34, 'nakkeeran', 'U2FsdGVkX18Cmcgw+WgvfmSG3PWhRY93UyfRlmKC/+M=', 'Nakkeeran', '', 'K', 'nakkeeran@autointelli.com', 1, '2019-09-03', 1, '2019-10-12', NULL, '8553184171', 'Y', 186, 3, 1, 3, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (50, 'anand@autointellidev.com', 'U2FsdGVkX1/QQ2+O1brPDy9DohZRHCcfOEcc3djdJyQ=', 'Anand', '', 'Parthiban', 'anand@autointellidev.com', 1, '2019-10-08', 1, '2019-11-08', NULL, '9988776655', 'Y', 186, 1, 1, 2, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');
INSERT INTO public.tbl_user_details (pk_user_details_id, user_id, user_password, first_name, middle_name, last_name, email_id, created_by, created_on, modified_by, modified_on, last_login, phone_number, active_yn, fk_time_zone_id, fk_role_id, fk_user_type, attempts, orch_pass) VALUES (65, 'sk_admin', 'U2FsdGVkX19owMw3P/yxlqQWkImG9O1MFp1DhJdlNc0=', 'sathish', '', 'sk', 'sathish@autointelli.com', 1, '2019-11-08', NULL, NULL, NULL, '12121212', 'Y', 186, 1, 1, NULL, 'jGl25bVBBBW96Qi9Te4V37Fnqchz/Eu4qB9vKrRIqRg=');


--
-- Name: tbl_user_details_pk_user_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_user_details_pk_user_details_id_seq', 65, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tbl_zone; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (1, 'AF', 'Afghanistan', 'Asia/Kabul', 'UTC +04:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (2, 'AX', 'Aland Islands', 'Europe/Mariehamn', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (3, 'AL', 'Albania', 'Europe/Tirane', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (4, 'DZ', 'Algeria', 'Africa/Algiers', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (5, 'AS', 'American Samoa', 'Pacific/Pago_Pago', 'UTC -11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (6, 'AD', 'Andorra', 'Europe/Andorra', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (7, 'AO', 'Angola', 'Africa/Luanda', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (8, 'AI', 'Anguilla', 'America/Anguilla', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (9, 'AQ', 'Antarctica', 'Antarctica/Casey', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (10, 'AQ', 'Antarctica', 'Antarctica/Davis', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (11, 'AQ', 'Antarctica', 'Antarctica/DumontDUrville', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (12, 'AQ', 'Antarctica', 'Antarctica/Mawson', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (13, 'AQ', 'Antarctica', 'Antarctica/McMurdo', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (14, 'AQ', 'Antarctica', 'Antarctica/Palmer', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (15, 'AQ', 'Antarctica', 'Antarctica/Rothera', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (16, 'AQ', 'Antarctica', 'Antarctica/Syowa', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (17, 'AQ', 'Antarctica', 'Antarctica/Troll', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (18, 'AQ', 'Antarctica', 'Antarctica/Vostok', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (19, 'AG', 'Antigua and Barbuda', 'America/Antigua', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (20, 'AR', 'Argentina', 'America/Argentina/Buenos_Aires', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (21, 'AR', 'Argentina', 'America/Argentina/Catamarca', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (22, 'AR', 'Argentina', 'America/Argentina/Cordoba', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (23, 'AR', 'Argentina', 'America/Argentina/Jujuy', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (24, 'AR', 'Argentina', 'America/Argentina/La_Rioja', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (25, 'AR', 'Argentina', 'America/Argentina/Mendoza', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (26, 'AR', 'Argentina', 'America/Argentina/Rio_Gallegos', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (27, 'AR', 'Argentina', 'America/Argentina/Salta', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (28, 'AR', 'Argentina', 'America/Argentina/San_Juan', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (29, 'AR', 'Argentina', 'America/Argentina/San_Luis', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (30, 'AR', 'Argentina', 'America/Argentina/Tucuman', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (31, 'AR', 'Argentina', 'America/Argentina/Ushuaia', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (32, 'AM', 'Armenia', 'Asia/Yerevan', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (33, 'AW', 'Aruba', 'America/Aruba', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (34, 'AU', 'Australia', 'Antarctica/Macquarie', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (35, 'AU', 'Australia', 'Australia/Adelaide', 'UTC +09:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (36, 'AU', 'Australia', 'Australia/Brisbane', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (37, 'AU', 'Australia', 'Australia/Broken_Hill', 'UTC +09:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (38, 'AU', 'Australia', 'Australia/Currie', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (39, 'AU', 'Australia', 'Australia/Darwin', 'UTC +09:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (40, 'AU', 'Australia', 'Australia/Eucla', 'UTC +08:45', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (41, 'AU', 'Australia', 'Australia/Hobart', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (42, 'AU', 'Australia', 'Australia/Lindeman', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (43, 'AU', 'Australia', 'Australia/Lord_Howe', 'UTC +10:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (44, 'AU', 'Australia', 'Australia/Melbourne', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (45, 'AU', 'Australia', 'Australia/Perth', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (46, 'AU', 'Australia', 'Australia/Sydney', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (47, 'AT', 'Austria', 'Europe/Vienna', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (48, 'AZ', 'Azerbaijan', 'Asia/Baku', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (49, 'BS', 'Bahamas', 'America/Nassau', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (50, 'BH', 'Bahrain', 'Asia/Bahrain', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (51, 'BD', 'Bangladesh', 'Asia/Dhaka', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (52, 'BB', 'Barbados', 'America/Barbados', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (53, 'BY', 'Belarus', 'Europe/Minsk', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (54, 'BE', 'Belgium', 'Europe/Brussels', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (55, 'BZ', 'Belize', 'America/Belize', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (56, 'BJ', 'Benin', 'Africa/Porto-Novo', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (57, 'BM', 'Bermuda', 'Atlantic/Bermuda', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (58, 'BT', 'Bhutan', 'Asia/Thimphu', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (59, 'BO', 'Bolivia', 'America/La_Paz', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (60, 'BQ', 'Bonaire, Saint Eustatius and Saba', 'America/Kralendijk', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (61, 'BA', 'Bosnia and Herzegovina', 'Europe/Sarajevo', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (62, 'BW', 'Botswana', 'Africa/Gaborone', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (63, 'BR', 'Brazil', 'America/Araguaina', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (64, 'BR', 'Brazil', 'America/Bahia', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (65, 'BR', 'Brazil', 'America/Belem', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (66, 'BR', 'Brazil', 'America/Boa_Vista', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (67, 'BR', 'Brazil', 'America/Campo_Grande', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (68, 'BR', 'Brazil', 'America/Cuiaba', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (69, 'BR', 'Brazil', 'America/Eirunepe', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (70, 'BR', 'Brazil', 'America/Fortaleza', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (71, 'BR', 'Brazil', 'America/Maceio', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (72, 'BR', 'Brazil', 'America/Manaus', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (73, 'BR', 'Brazil', 'America/Noronha', 'UTC -02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (74, 'BR', 'Brazil', 'America/Porto_Velho', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (75, 'BR', 'Brazil', 'America/Recife', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (76, 'BR', 'Brazil', 'America/Rio_Branco', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (77, 'BR', 'Brazil', 'America/Santarem', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (78, 'BR', 'Brazil', 'America/Sao_Paulo', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (79, 'IO', 'British Indian Ocean Territory', 'Indian/Chagos', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (80, 'VG', 'British Virgin Islands', 'America/Tortola', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (81, 'BN', 'Brunei', 'Asia/Brunei', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (82, 'BG', 'Bulgaria', 'Europe/Sofia', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (83, 'BF', 'Burkina Faso', 'Africa/Ouagadougou', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (84, 'BI', 'Burundi', 'Africa/Bujumbura', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (85, 'KH', 'Cambodia', 'Asia/Phnom_Penh', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (86, 'CM', 'Cameroon', 'Africa/Douala', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (87, 'CA', 'Canada', 'America/Atikokan', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (88, 'CA', 'Canada', 'America/Blanc-Sablon', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (89, 'CA', 'Canada', 'America/Cambridge_Bay', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (90, 'CA', 'Canada', 'America/Creston', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (91, 'CA', 'Canada', 'America/Dawson', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (92, 'CA', 'Canada', 'America/Dawson_Creek', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (93, 'CA', 'Canada', 'America/Edmonton', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (94, 'CA', 'Canada', 'America/Fort_Nelson', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (95, 'CA', 'Canada', 'America/Glace_Bay', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (96, 'CA', 'Canada', 'America/Goose_Bay', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (97, 'CA', 'Canada', 'America/Halifax', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (98, 'CA', 'Canada', 'America/Inuvik', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (99, 'CA', 'Canada', 'America/Iqaluit', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (100, 'CA', 'Canada', 'America/Moncton', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (101, 'CA', 'Canada', 'America/Nipigon', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (102, 'CA', 'Canada', 'America/Pangnirtung', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (103, 'CA', 'Canada', 'America/Rainy_River', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (104, 'CA', 'Canada', 'America/Rankin_Inlet', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (105, 'CA', 'Canada', 'America/Regina', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (106, 'CA', 'Canada', 'America/Resolute', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (107, 'CA', 'Canada', 'America/St_Johns', 'UTC -02:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (108, 'CA', 'Canada', 'America/Swift_Current', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (109, 'CA', 'Canada', 'America/Thunder_Bay', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (110, 'CA', 'Canada', 'America/Toronto', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (111, 'CA', 'Canada', 'America/Vancouver', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (112, 'CA', 'Canada', 'America/Whitehorse', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (113, 'CA', 'Canada', 'America/Winnipeg', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (114, 'CA', 'Canada', 'America/Yellowknife', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (115, 'CV', 'Cape Verde', 'Atlantic/Cape_Verde', 'UTC -01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (116, 'KY', 'Cayman Islands', 'America/Cayman', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (117, 'CF', 'Central African Republic', 'Africa/Bangui', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (118, 'TD', 'Chad', 'Africa/Ndjamena', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (119, 'CL', 'Chile', 'America/Punta_Arenas', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (120, 'CL', 'Chile', 'America/Santiago', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (121, 'CL', 'Chile', 'Pacific/Easter', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (122, 'CN', 'China', 'Asia/Shanghai', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (123, 'CN', 'China', 'Asia/Urumqi', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (124, 'CX', 'Christmas Island', 'Indian/Christmas', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (125, 'CC', 'Cocos Islands', 'Indian/Cocos', 'UTC +06:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (126, 'CO', 'Colombia', 'America/Bogota', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (127, 'KM', 'Comoros', 'Indian/Comoro', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (128, 'CK', 'Cook Islands', 'Pacific/Rarotonga', 'UTC -10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (129, 'CR', 'Costa Rica', 'America/Costa_Rica', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (130, 'HR', 'Croatia', 'Europe/Zagreb', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (131, 'CU', 'Cuba', 'America/Havana', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (132, 'CW', 'Curaçao', 'America/Curacao', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (133, 'CY', 'Cyprus', 'Asia/Famagusta', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (134, 'CY', 'Cyprus', 'Asia/Nicosia', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (135, 'CZ', 'Czech Republic', 'Europe/Prague', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (136, 'CD', 'Democratic Republic of the Congo', 'Africa/Kinshasa', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (137, 'CD', 'Democratic Republic of the Congo', 'Africa/Lubumbashi', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (138, 'DK', 'Denmark', 'Europe/Copenhagen', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (139, 'DJ', 'Djibouti', 'Africa/Djibouti', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (140, 'DM', 'Dominica', 'America/Dominica', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (141, 'DO', 'Dominican Republic', 'America/Santo_Domingo', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (142, 'TL', 'East Timor', 'Asia/Dili', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (143, 'EC', 'Ecuador', 'America/Guayaquil', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (144, 'EC', 'Ecuador', 'Pacific/Galapagos', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (145, 'EG', 'Egypt', 'Africa/Cairo', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (146, 'SV', 'El Salvador', 'America/El_Salvador', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (147, 'GQ', 'Equatorial Guinea', 'Africa/Malabo', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (148, 'ER', 'Eritrea', 'Africa/Asmara', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (149, 'EE', 'Estonia', 'Europe/Tallinn', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (150, 'ET', 'Ethiopia', 'Africa/Addis_Ababa', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (151, 'FK', 'Falkland Islands', 'Atlantic/Stanley', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (152, 'FO', 'Faroe Islands', 'Atlantic/Faroe', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (153, 'FJ', 'Fiji', 'Pacific/Fiji', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (154, 'FI', 'Finland', 'Europe/Helsinki', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (155, 'FR', 'France', 'Europe/Paris', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (156, 'GF', 'French Guiana', 'America/Cayenne', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (157, 'PF', 'French Polynesia', 'Pacific/Gambier', 'UTC -09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (158, 'PF', 'French Polynesia', 'Pacific/Marquesas', 'UTC -09:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (159, 'PF', 'French Polynesia', 'Pacific/Tahiti', 'UTC -10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (160, 'TF', 'French Southern Territories', 'Indian/Kerguelen', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (161, 'GA', 'Gabon', 'Africa/Libreville', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (162, 'GM', 'Gambia', 'Africa/Banjul', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (163, 'GE', 'Georgia', 'Asia/Tbilisi', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (164, 'DE', 'Germany', 'Europe/Berlin', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (165, 'DE', 'Germany', 'Europe/Busingen', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (166, 'GH', 'Ghana', 'Africa/Accra', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (167, 'GI', 'Gibraltar', 'Europe/Gibraltar', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (168, 'GR', 'Greece', 'Europe/Athens', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (169, 'GL', 'Greenland', 'America/Danmarkshavn', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (170, 'GL', 'Greenland', 'America/Godthab', 'UTC -02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (171, 'GL', 'Greenland', 'America/Scoresbysund', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (172, 'GL', 'Greenland', 'America/Thule', 'UTC -03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (173, 'GD', 'Grenada', 'America/Grenada', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (174, 'GP', 'Guadeloupe', 'America/Guadeloupe', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (175, 'GU', 'Guam', 'Pacific/Guam', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (176, 'GT', 'Guatemala', 'America/Guatemala', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (177, 'GG', 'Guernsey', 'Europe/Guernsey', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (178, 'GN', 'Guinea', 'Africa/Conakry', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (179, 'GW', 'Guinea-Bissau', 'Africa/Bissau', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (180, 'GY', 'Guyana', 'America/Guyana', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (181, 'HT', 'Haiti', 'America/Port-au-Prince', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (182, 'HN', 'Honduras', 'America/Tegucigalpa', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (183, 'HK', 'Hong Kong', 'Asia/Hong_Kong', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (184, 'HU', 'Hungary', 'Europe/Budapest', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (185, 'IS', 'Iceland', 'Atlantic/Reykjavik', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (186, 'IN', 'India', 'Asia/Kolkata', 'UTC +05:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (187, 'ID', 'Indonesia', 'Asia/Jakarta', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (188, 'ID', 'Indonesia', 'Asia/Jayapura', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (189, 'ID', 'Indonesia', 'Asia/Makassar', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (190, 'ID', 'Indonesia', 'Asia/Pontianak', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (191, 'IR', 'Iran', 'Asia/Tehran', 'UTC +04:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (192, 'IQ', 'Iraq', 'Asia/Baghdad', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (193, 'IE', 'Ireland', 'Europe/Dublin', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (194, 'IM', 'Isle of Man', 'Europe/Isle_of_Man', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (195, 'IL', 'Israel', 'Asia/Jerusalem', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (196, 'IT', 'Italy', 'Europe/Rome', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (197, 'CI', 'Ivory Coast', 'Africa/Abidjan', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (198, 'JM', 'Jamaica', 'America/Jamaica', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (199, 'JP', 'Japan', 'Asia/Tokyo', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (200, 'JE', 'Jersey', 'Europe/Jersey', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (201, 'JO', 'Jordan', 'Asia/Amman', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (202, 'KZ', 'Kazakhstan', 'Asia/Almaty', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (203, 'KZ', 'Kazakhstan', 'Asia/Aqtau', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (204, 'KZ', 'Kazakhstan', 'Asia/Aqtobe', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (205, 'KZ', 'Kazakhstan', 'Asia/Atyrau', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (206, 'KZ', 'Kazakhstan', 'Asia/Oral', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (207, 'KZ', 'Kazakhstan', 'Asia/Qyzylorda', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (208, 'KE', 'Kenya', 'Africa/Nairobi', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (209, 'KI', 'Kiribati', 'Pacific/Enderbury', 'UTC +13:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (210, 'KI', 'Kiribati', 'Pacific/Kiritimati', 'UTC +14:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (211, 'KI', 'Kiribati', 'Pacific/Tarawa', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (212, 'KW', 'Kuwait', 'Asia/Kuwait', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (213, 'KG', 'Kyrgyzstan', 'Asia/Bishkek', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (214, 'LA', 'Laos', 'Asia/Vientiane', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (215, 'LV', 'Latvia', 'Europe/Riga', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (216, 'LB', 'Lebanon', 'Asia/Beirut', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (217, 'LS', 'Lesotho', 'Africa/Maseru', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (218, 'LR', 'Liberia', 'Africa/Monrovia', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (219, 'LY', 'Libya', 'Africa/Tripoli', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (220, 'LI', 'Liechtenstein', 'Europe/Vaduz', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (221, 'LT', 'Lithuania', 'Europe/Vilnius', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (222, 'LU', 'Luxembourg', 'Europe/Luxembourg', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (223, 'MO', 'Macao', 'Asia/Macau', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (224, 'MK', 'Macedonia', 'Europe/Skopje', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (225, 'MG', 'Madagascar', 'Indian/Antananarivo', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (226, 'MW', 'Malawi', 'Africa/Blantyre', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (227, 'MY', 'Malaysia', 'Asia/Kuala_Lumpur', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (228, 'MY', 'Malaysia', 'Asia/Kuching', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (229, 'MV', 'Maldives', 'Indian/Maldives', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (230, 'ML', 'Mali', 'Africa/Bamako', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (231, 'MT', 'Malta', 'Europe/Malta', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (232, 'MH', 'Marshall Islands', 'Pacific/Kwajalein', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (233, 'MH', 'Marshall Islands', 'Pacific/Majuro', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (234, 'MQ', 'Martinique', 'America/Martinique', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (235, 'MR', 'Mauritania', 'Africa/Nouakchott', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (236, 'MU', 'Mauritius', 'Indian/Mauritius', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (237, 'YT', 'Mayotte', 'Indian/Mayotte', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (238, 'MX', 'Mexico', 'America/Bahia_Banderas', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (239, 'MX', 'Mexico', 'America/Cancun', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (240, 'MX', 'Mexico', 'America/Chihuahua', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (241, 'MX', 'Mexico', 'America/Hermosillo', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (242, 'MX', 'Mexico', 'America/Matamoros', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (243, 'MX', 'Mexico', 'America/Mazatlan', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (244, 'MX', 'Mexico', 'America/Merida', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (245, 'MX', 'Mexico', 'America/Mexico_City', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (246, 'MX', 'Mexico', 'America/Monterrey', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (247, 'MX', 'Mexico', 'America/Ojinaga', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (248, 'MX', 'Mexico', 'America/Tijuana', 'UTC -07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (249, 'FM', 'Micronesia', 'Pacific/Chuuk', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (250, 'FM', 'Micronesia', 'Pacific/Kosrae', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (251, 'FM', 'Micronesia', 'Pacific/Pohnpei', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (252, 'MD', 'Moldova', 'Europe/Chisinau', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (253, 'MC', 'Monaco', 'Europe/Monaco', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (254, 'MN', 'Mongolia', 'Asia/Choibalsan', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (255, 'MN', 'Mongolia', 'Asia/Hovd', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (256, 'MN', 'Mongolia', 'Asia/Ulaanbaatar', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (257, 'ME', 'Montenegro', 'Europe/Podgorica', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (258, 'MS', 'Montserrat', 'America/Montserrat', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (259, 'MA', 'Morocco', 'Africa/Casablanca', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (260, 'MZ', 'Mozambique', 'Africa/Maputo', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (261, 'MM', 'Myanmar', 'Asia/Yangon', 'UTC +06:30', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (262, 'NA', 'Namibia', 'Africa/Windhoek', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (263, 'NR', 'Nauru', 'Pacific/Nauru', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (264, 'NP', 'Nepal', 'Asia/Kathmandu', 'UTC +05:45', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (265, 'NL', 'Netherlands', 'Europe/Amsterdam', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (266, 'NC', 'New Caledonia', 'Pacific/Noumea', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (267, 'NZ', 'New Zealand', 'Pacific/Auckland', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (268, 'NZ', 'New Zealand', 'Pacific/Chatham', 'UTC +12:45', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (269, 'NI', 'Nicaragua', 'America/Managua', 'UTC -06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (270, 'NE', 'Niger', 'Africa/Niamey', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (271, 'NG', 'Nigeria', 'Africa/Lagos', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (272, 'NU', 'Niue', 'Pacific/Niue', 'UTC -11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (273, 'NF', 'Norfolk Island', 'Pacific/Norfolk', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (274, 'KP', 'North Korea', 'Asia/Pyongyang', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (275, 'MP', 'Northern Mariana Islands', 'Pacific/Saipan', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (276, 'NO', 'Norway', 'Europe/Oslo', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (277, 'OM', 'Oman', 'Asia/Muscat', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (278, 'PK', 'Pakistan', 'Asia/Karachi', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (279, 'PW', 'Palau', 'Pacific/Palau', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (280, 'PS', 'Palestinian Territory', 'Asia/Gaza', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (281, 'PS', 'Palestinian Territory', 'Asia/Hebron', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (282, 'PA', 'Panama', 'America/Panama', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (283, 'PG', 'Papua New Guinea', 'Pacific/Bougainville', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (284, 'PG', 'Papua New Guinea', 'Pacific/Port_Moresby', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (285, 'PY', 'Paraguay', 'America/Asuncion', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (286, 'PE', 'Peru', 'America/Lima', 'UTC -05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (287, 'PH', 'Philippines', 'Asia/Manila', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (288, 'PN', 'Pitcairn', 'Pacific/Pitcairn', 'UTC -08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (289, 'PL', 'Poland', 'Europe/Warsaw', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (290, 'PT', 'Portugal', 'Atlantic/Azores', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (291, 'PT', 'Portugal', 'Atlantic/Madeira', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (292, 'PT', 'Portugal', 'Europe/Lisbon', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (293, 'PR', 'Puerto Rico', 'America/Puerto_Rico', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (294, 'QA', 'Qatar', 'Asia/Qatar', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (295, 'CG', 'Republic of the Congo', 'Africa/Brazzaville', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (296, 'RE', 'Reunion', 'Indian/Reunion', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (297, 'RO', 'Romania', 'Europe/Bucharest', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (298, 'RU', 'Russia', 'Asia/Anadyr', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (299, 'RU', 'Russia', 'Asia/Barnaul', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (300, 'RU', 'Russia', 'Asia/Chita', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (301, 'RU', 'Russia', 'Asia/Irkutsk', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (302, 'RU', 'Russia', 'Asia/Kamchatka', 'UTC +12:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (303, 'RU', 'Russia', 'Asia/Khandyga', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (304, 'RU', 'Russia', 'Asia/Krasnoyarsk', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (305, 'RU', 'Russia', 'Asia/Magadan', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (306, 'RU', 'Russia', 'Asia/Novokuznetsk', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (307, 'RU', 'Russia', 'Asia/Novosibirsk', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (308, 'RU', 'Russia', 'Asia/Omsk', 'UTC +06:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (309, 'RU', 'Russia', 'Asia/Sakhalin', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (310, 'RU', 'Russia', 'Asia/Srednekolymsk', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (311, 'RU', 'Russia', 'Asia/Tomsk', 'UTC +07:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (312, 'RU', 'Russia', 'Asia/Ust-Nera', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (313, 'RU', 'Russia', 'Asia/Vladivostok', 'UTC +10:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (314, 'RU', 'Russia', 'Asia/Yakutsk', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (315, 'RU', 'Russia', 'Asia/Yekaterinburg', 'UTC +05:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (316, 'RU', 'Russia', 'Europe/Astrakhan', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (317, 'RU', 'Russia', 'Europe/Kaliningrad', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (318, 'RU', 'Russia', 'Europe/Kirov', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (319, 'RU', 'Russia', 'Europe/Moscow', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (320, 'RU', 'Russia', 'Europe/Samara', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (321, 'RU', 'Russia', 'Europe/Saratov', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (322, 'RU', 'Russia', 'Europe/Simferopol', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (323, 'RU', 'Russia', 'Europe/Ulyanovsk', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (324, 'RU', 'Russia', 'Europe/Volgograd', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (325, 'RW', 'Rwanda', 'Africa/Kigali', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (326, 'BL', 'Saint Barthélemy', 'America/St_Barthelemy', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (327, 'SH', 'Saint Helena', 'Atlantic/St_Helena', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (328, 'KN', 'Saint Kitts and Nevis', 'America/St_Kitts', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (329, 'LC', 'Saint Lucia', 'America/St_Lucia', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (330, 'MF', 'Saint Martin', 'America/Marigot', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (331, 'PM', 'Saint Pierre and Miquelon', 'America/Miquelon', 'UTC -02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (332, 'VC', 'Saint Vincent and the Grenadines', 'America/St_Vincent', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (333, 'WS', 'Samoa', 'Pacific/Apia', 'UTC +13:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (334, 'SM', 'San Marino', 'Europe/San_Marino', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (335, 'ST', 'Sao Tome and Principe', 'Africa/Sao_Tome', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (336, 'SA', 'Saudi Arabia', 'Asia/Riyadh', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (337, 'SN', 'Senegal', 'Africa/Dakar', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (338, 'RS', 'Serbia', 'Europe/Belgrade', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (339, 'SC', 'Seychelles', 'Indian/Mahe', 'UTC +04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (340, 'SL', 'Sierra Leone', 'Africa/Freetown', 'UTC', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (341, 'SG', 'Singapore', 'Asia/Singapore', 'UTC +08:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (342, 'SX', 'Sint Maarten', 'America/Lower_Princes', 'UTC -04:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (343, 'SK', 'Slovakia', 'Europe/Bratislava', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (344, 'SI', 'Slovenia', 'Europe/Ljubljana', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (345, 'SB', 'Solomon Islands', 'Pacific/Guadalcanal', 'UTC +11:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (346, 'SO', 'Somalia', 'Africa/Mogadishu', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (347, 'ZA', 'South Africa', 'Africa/Johannesburg', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (348, 'GS', 'South Georgia and the South Sandwich Islands', 'Atlantic/South_Georgia', 'UTC -02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (349, 'KR', 'South Korea', 'Asia/Seoul', 'UTC +09:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (350, 'SS', 'South Sudan', 'Africa/Juba', 'UTC +03:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (351, 'ES', 'Spain', 'Africa/Ceuta', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (352, 'ES', 'Spain', 'Atlantic/Canary', 'UTC +01:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (353, 'ES', 'Spain', 'Europe/Madrid', 'UTC +02:00', 'Y');
INSERT INTO public.tbl_zone (pk_zone_id, country_code, country_name, time_zone, gmt_offset, active_yn) VALUES (354, 'LK', 'Sri Lanka', 'Asia/Colombo', 'UTC +05:30', 'Y');


--
-- Name: tbl_zone_pk_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.tbl_zone_pk_zone_id_seq', 354, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: chartdetails; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (1, 'Bar Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (2, 'Donut Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (3, 'Line Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (4, 'Area Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (5, 'Heat Map Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (6, 'Matrix Chart', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (7, 'Count Labels', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y", "select_items": ["Total_Events", "Total_Alerts", "Total_Tickets", "Total_BOTs_Executed", "Total_Workflows_Executed"]}', 'Y');
INSERT INTO public.chartdetails (pk_chart_id, chart_name, attributes, active_yn) VALUES (8, 'IFrame', '{"width": 0, "height": 0, "top": 0, "left": 0, "hyper_link": "", "realtime_yn": "Y"}', 'Y');


--
-- Name: chartdetails_pk_chart_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.chartdetails_pk_chart_id_seq', 8, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: plottingapidetails; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (1, 'Alert Severity', 'http://95.216.28.228:4006/dashboard/api1.0/alertseveritybc/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (2, 'Automation Type', 'http://95.216.28.228:4006/dashboard/api1.0/automationtypebc/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (3, 'Workflows Status', 'http://95.216.28.228:4006/dashboard/api1.0/workflowstatusbc/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (4, 'Alert Status', 'http://95.216.28.228:4006/dashboard/api1.0/alertstatus/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (5, 'Automation Status', 'http://95.216.28.228:4006/dashboard/api1.0/automationstatus/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (6, 'Ticket Status', 'http://95.216.28.228:4006/dashboard/api1.0/ticketstatus/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (7, 'Top 5 Component', 'http://95.216.28.228:4006/dashboard/api1.0/top5component/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (8, 'Top 5 Automation', 'http://95.216.28.228:4006/dashboard/api1.0/top5automation/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (9, 'Supression 30 Days', 'http://95.216.28.228:4006/dashboard/api1.0/suppression30days/all/0', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (10, 'Total Counts', 'http://95.216.28.228:4006/dashboard/api1.0/executiveheadersdd/all/0/', 'GET', '', 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (11, 'CPU Anomaly', 'http://95.216.115.48:7171/V1/anomaly/cpu', NULL, NULL, 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (12, 'Memory Anomaly', 'http://95.216.115.48:7171/V1/anomaly/memory', NULL, NULL, 'Y');
INSERT INTO public.plottingapidetails (pk_api_id, api_description, api_address_or_link, api_method, api_body, active_yn) VALUES (13, 'IP Anomaly', 'http://95.216.115.48:7171/V1/anomaly/ip', NULL, NULL, 'Y');


--
-- Name: plottingapidetails_pk_api_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.plottingapidetails_pk_api_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: widgetcategory; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.widgetcategory (pk_category_id, category_name, active_yn) VALUES (1, 'Event Management', 'Y');
INSERT INTO public.widgetcategory (pk_category_id, category_name, active_yn) VALUES (2, 'Orchestration', 'Y');
INSERT INTO public.widgetcategory (pk_category_id, category_name, active_yn) VALUES (3, 'Others', 'Y');
INSERT INTO public.widgetcategory (pk_category_id, category_name, active_yn) VALUES (4, 'Anomaly', 'Y');


--
-- Name: widgetcategory_pk_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.widgetcategory_pk_category_id_seq', 4, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: widget; Type: TABLE DATA; Schema: public; Owner: autointelli
--

INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (1, 'Alert Severity', 1, 1, 1, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (4, 'Alert Status', 4, 1, 2, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (6, 'Ticket Status', 6, 1, 2, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (7, 'Top 5 Component', 7, 1, 2, 'Y', 3, 4);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (8, 'Top 5 Automation', 8, 1, 2, 'Y', 3, 4);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (2, 'Automation Type', 2, 2, 1, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (3, 'Workflows Status', 3, 2, 1, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (5, 'Automation Status', 5, 2, 2, 'Y', 3, 3);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (9, 'Supression 30 Days', 9, 3, 3, 'Y', 3, 9);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (10, 'Total Counts', 10, 1, 7, 'Y', 1, 2);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (11, 'CPU Anomaly', 11, 4, 8, 'Y', 3, 12);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (12, 'Memory Anomaly', 12, 4, 8, 'Y', 3, 12);
INSERT INTO public.widget (pk_widget_id, widget_name, fk_api_id, fk_category_id, fk_chart_id, active_yn, wheight, wwidth) VALUES (13, 'IP Anomaly', 13, 4, 8, 'Y', 3, 12);


--
-- Name: widget_pk_widget_id_seq; Type: SEQUENCE SET; Schema: public; Owner: autointelli
--

SELECT pg_catalog.setval('public.widget_pk_widget_id_seq', 13, true);


--
-- PostgreSQL database dump complete
--

