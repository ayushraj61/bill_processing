--
-- PostgreSQL database dump
--

\restrict 4MkDChzykfYkhauYyZqTieWgu22vVX0eG7bje0uOrHmpAMBMbqZKxUPa9VfdQCl

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_email character varying NOT NULL,
    action_type character varying NOT NULL,
    bill_id character varying,
    company_name character varying,
    "timestamp" timestamp with time zone,
    ip_address character varying,
    details json
);


ALTER TABLE public.audit_log OWNER TO bill_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO bill_user;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: bills; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.bills (
    id character varying NOT NULL,
    drive_file_id character varying,
    invoice_reference character varying,
    filename character varying,
    supplier_name character varying,
    upload_date timestamp with time zone,
    invoice_date date,
    gross_amount numeric(10,2),
    status character varying,
    extracted_data json,
    email_text text,
    web_view_link character varying
);


ALTER TABLE public.bills OWNER TO bill_user;

--
-- Name: bpoil; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.bpoil (
    id integer NOT NULL,
    drive_file_id character varying,
    invoice_reference character varying,
    bill_reference_number character varying,
    filename character varying,
    supplier_name character varying,
    upload_date timestamp with time zone,
    invoice_date date,
    gross_amount numeric(10,2),
    status character varying,
    extracted_data jsonb,
    email_text text,
    type character varying,
    a_c character varying,
    date date,
    ref character varying,
    ex_ref character varying,
    n_c character varying,
    dept character varying,
    details character varying,
    net numeric(10,2),
    t_c character varying,
    vat numeric(10,2),
    web_view_link character varying
);


ALTER TABLE public.bpoil OWNER TO bill_user;

--
-- Name: bpoil_new_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.bpoil_new_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bpoil_new_id_seq OWNER TO bill_user;

--
-- Name: bpoil_new_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.bpoil_new_id_seq OWNED BY public.bpoil.id;


--
-- Name: company_email_mapping; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.company_email_mapping (
    id integer NOT NULL,
    company_name character varying NOT NULL,
    sender_email character varying NOT NULL,
    created_at timestamp with time zone
);


ALTER TABLE public.company_email_mapping OWNER TO bill_user;

--
-- Name: company_email_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.company_email_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.company_email_mapping_id_seq OWNER TO bill_user;

--
-- Name: company_email_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.company_email_mapping_id_seq OWNED BY public.company_email_mapping.id;


--
-- Name: nominal_code; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.nominal_code (
    id integer NOT NULL,
    code character varying NOT NULL,
    object_name character varying NOT NULL
);


ALTER TABLE public.nominal_code OWNER TO bill_user;

--
-- Name: nominal_code_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.nominal_code_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nominal_code_id_seq OWNER TO bill_user;

--
-- Name: nominal_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.nominal_code_id_seq OWNED BY public.nominal_code.id;


--
-- Name: site_mappings; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.site_mappings (
    id integer NOT NULL,
    site_name character varying NOT NULL,
    dept character varying,
    short_code character varying,
    company character varying,
    post_code character varying,
    ac_code character varying
);


ALTER TABLE public.site_mappings OWNER TO bill_user;

--
-- Name: site_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.site_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.site_mappings_id_seq OWNER TO bill_user;

--
-- Name: site_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.site_mappings_id_seq OWNED BY public.site_mappings.id;


--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_email character varying NOT NULL,
    session_token character varying NOT NULL,
    created_at timestamp with time zone,
    last_activity timestamp with time zone,
    ip_address character varying,
    is_active boolean
);


ALTER TABLE public.user_sessions OWNER TO bill_user;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_sessions_id_seq OWNER TO bill_user;

--
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: bill_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    role character varying NOT NULL,
    accessible_companies json,
    is_active boolean,
    created_at timestamp with time zone,
    created_by character varying
);


ALTER TABLE public.users OWNER TO bill_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: bill_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO bill_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: bill_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: bpoil id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.bpoil ALTER COLUMN id SET DEFAULT nextval('public.bpoil_new_id_seq'::regclass);


--
-- Name: company_email_mapping id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.company_email_mapping ALTER COLUMN id SET DEFAULT nextval('public.company_email_mapping_id_seq'::regclass);


--
-- Name: nominal_code id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.nominal_code ALTER COLUMN id SET DEFAULT nextval('public.nominal_code_id_seq'::regclass);


--
-- Name: site_mappings id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.site_mappings ALTER COLUMN id SET DEFAULT nextval('public.site_mappings_id_seq'::regclass);


--
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (id);


--
-- Name: bpoil bpoil_new_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.bpoil
    ADD CONSTRAINT bpoil_new_pkey PRIMARY KEY (id);


--
-- Name: company_email_mapping company_email_mapping_company_name_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.company_email_mapping
    ADD CONSTRAINT company_email_mapping_company_name_key UNIQUE (company_name);


--
-- Name: company_email_mapping company_email_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.company_email_mapping
    ADD CONSTRAINT company_email_mapping_pkey PRIMARY KEY (id);


--
-- Name: company_email_mapping company_email_mapping_sender_email_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.company_email_mapping
    ADD CONSTRAINT company_email_mapping_sender_email_key UNIQUE (sender_email);


--
-- Name: nominal_code nominal_code_code_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.nominal_code
    ADD CONSTRAINT nominal_code_code_key UNIQUE (code);


--
-- Name: nominal_code nominal_code_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.nominal_code
    ADD CONSTRAINT nominal_code_pkey PRIMARY KEY (id);


--
-- Name: site_mappings site_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.site_mappings
    ADD CONSTRAINT site_mappings_pkey PRIMARY KEY (id);


--
-- Name: site_mappings site_mappings_site_name_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.site_mappings
    ADD CONSTRAINT site_mappings_site_name_key UNIQUE (site_name);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_key UNIQUE (session_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: bill_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4MkDChzykfYkhauYyZqTieWgu22vVX0eG7bje0uOrHmpAMBMbqZKxUPa9VfdQCl

