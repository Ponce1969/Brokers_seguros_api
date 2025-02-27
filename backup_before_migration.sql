--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6 (Debian 16.6-1.pgdg120+1)
-- Dumped by pg_dump version 16.6 (Debian 16.6-1.pgdg120+1)

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
-- Name: tipo_duracion; Type: TYPE; Schema: public; Owner: admin_broker
--

CREATE TYPE public.tipo_duracion AS ENUM (
    'diaria',
    'semanal',
    'mensual',
    'trimestral',
    'semestral',
    'anual'
);


ALTER TYPE public.tipo_duracion OWNER TO admin_broker;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO admin_broker;

--
-- Name: aseguradoras; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.aseguradoras (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    telefono character varying(20),
    direccion character varying(200),
    email character varying(100),
    pagina_web character varying(100),
    identificador_fiscal character varying(12),
    esta_activa boolean DEFAULT true,
    observaciones text,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone
);


ALTER TABLE public.aseguradoras OWNER TO admin_broker;

--
-- Name: COLUMN aseguradoras.identificador_fiscal; Type: COMMENT; Schema: public; Owner: admin_broker
--

COMMENT ON COLUMN public.aseguradoras.identificador_fiscal IS 'Identificador fiscal de la aseguradora (RUT, CUIT, NIF, etc.)';


--
-- Name: aseguradoras_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.aseguradoras_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.aseguradoras_id_seq OWNER TO admin_broker;

--
-- Name: aseguradoras_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.aseguradoras_id_seq OWNED BY public.aseguradoras.id;


--
-- Name: cliente_numero_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.cliente_numero_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_numero_seq OWNER TO admin_broker;

--
-- Name: clientes; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.clientes (
    id uuid NOT NULL,
    numero_cliente integer DEFAULT nextval('public.cliente_numero_seq'::regclass) NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    tipo_documento_id integer NOT NULL,
    numero_documento character varying(50) NOT NULL,
    fecha_nacimiento date NOT NULL,
    direccion character varying(200) NOT NULL,
    localidad character varying(50),
    telefonos character varying(100) NOT NULL,
    movil character varying(100) NOT NULL,
    mail character varying(100) NOT NULL,
    observaciones text,
    creado_por_id integer NOT NULL,
    modificado_por_id integer NOT NULL,
    fecha_creacion timestamp with time zone,
    fecha_modificacion timestamp with time zone
);


ALTER TABLE public.clientes OWNER TO admin_broker;

--
-- Name: clientes_corredores; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.clientes_corredores (
    cliente_id uuid NOT NULL,
    corredor_numero integer NOT NULL,
    fecha_asignacion date,
    corredor_id integer
);


ALTER TABLE public.clientes_corredores OWNER TO admin_broker;

--
-- Name: corredores_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.corredores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.corredores_id_seq OWNER TO admin_broker;

--
-- Name: corredores; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.corredores (
    numero integer NOT NULL,
    nombres character varying(30),
    apellidos character varying(30) NOT NULL,
    documento character varying(20) NOT NULL,
    direccion character varying(70) NOT NULL,
    localidad character varying(15) NOT NULL,
    telefonos character varying(20),
    movil character varying(20),
    mail character varying(40) NOT NULL,
    observaciones text,
    fecha_alta date,
    fecha_baja date,
    matricula character varying(50),
    especializacion character varying(100),
    id integer DEFAULT nextval('public.corredores_id_seq'::regclass) NOT NULL
);


ALTER TABLE public.corredores OWNER TO admin_broker;

--
-- Name: corredores_numero_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.corredores_numero_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.corredores_numero_seq OWNER TO admin_broker;

--
-- Name: corredores_numero_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.corredores_numero_seq OWNED BY public.corredores.numero;


--
-- Name: monedas; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.monedas (
    id integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(50) NOT NULL,
    simbolo character varying(5) NOT NULL,
    descripcion character varying(200),
    es_default boolean DEFAULT false,
    esta_activa boolean DEFAULT true,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone
);


ALTER TABLE public.monedas OWNER TO admin_broker;

--
-- Name: monedas_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.monedas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monedas_id_seq OWNER TO admin_broker;

--
-- Name: monedas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.monedas_id_seq OWNED BY public.monedas.id;


--
-- Name: movimientos_vigencias; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.movimientos_vigencias (
    id integer NOT NULL,
    cliente_id uuid NOT NULL,
    corredor_id integer,
    tipo_seguro_id integer NOT NULL,
    carpeta character varying(100),
    numero_poliza character varying(100) NOT NULL,
    endoso character varying(100),
    fecha_inicio date NOT NULL,
    fecha_vencimiento date NOT NULL,
    fecha_emision date,
    estado_poliza character varying(20),
    forma_pago character varying(20),
    tipo_endoso character varying(50),
    moneda_id integer,
    suma_asegurada double precision NOT NULL,
    prima double precision NOT NULL,
    comision double precision,
    cuotas integer,
    observaciones character varying(500),
    tipo_duracion public.tipo_duracion DEFAULT 'anual'::public.tipo_duracion NOT NULL
);


ALTER TABLE public.movimientos_vigencias OWNER TO admin_broker;

--
-- Name: movimientos_vigencias_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.movimientos_vigencias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimientos_vigencias_id_seq OWNER TO admin_broker;

--
-- Name: movimientos_vigencias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.movimientos_vigencias_id_seq OWNED BY public.movimientos_vigencias.id;


--
-- Name: tipos_de_seguros; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.tipos_de_seguros (
    id integer NOT NULL,
    categoria character varying(30) NOT NULL,
    cobertura text NOT NULL,
    vigencia_default integer,
    aseguradora_id integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    es_default boolean DEFAULT false,
    esta_activo boolean DEFAULT true,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone
);


ALTER TABLE public.tipos_de_seguros OWNER TO admin_broker;

--
-- Name: tipos_de_seguros_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.tipos_de_seguros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipos_de_seguros_id_seq OWNER TO admin_broker;

--
-- Name: tipos_de_seguros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.tipos_de_seguros_id_seq OWNED BY public.tipos_de_seguros.id;


--
-- Name: tipos_documento; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.tipos_documento (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    codigo character varying(10) NOT NULL,
    descripcion character varying(200),
    es_default boolean DEFAULT false,
    esta_activo boolean DEFAULT true
);


ALTER TABLE public.tipos_documento OWNER TO admin_broker;

--
-- Name: tipos_documento_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.tipos_documento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tipos_documento_id_seq OWNER TO admin_broker;

--
-- Name: tipos_documento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.tipos_documento_id_seq OWNED BY public.tipos_documento.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: admin_broker
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nombre character varying(64) NOT NULL,
    apellido character varying(64) NOT NULL,
    email character varying(64) NOT NULL,
    username character varying(64) NOT NULL,
    hashed_password character varying(128) NOT NULL,
    is_active boolean,
    is_superuser boolean,
    role character varying(20),
    comision_porcentaje double precision,
    telefono character varying(20),
    corredor_numero integer,
    fecha_creacion timestamp with time zone,
    fecha_modificacion timestamp with time zone,
    corredor_id integer
);


ALTER TABLE public.usuarios OWNER TO admin_broker;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: admin_broker
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO admin_broker;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin_broker
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: aseguradoras id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.aseguradoras ALTER COLUMN id SET DEFAULT nextval('public.aseguradoras_id_seq'::regclass);


--
-- Name: corredores numero; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.corredores ALTER COLUMN numero SET DEFAULT nextval('public.corredores_numero_seq'::regclass);


--
-- Name: monedas id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.monedas ALTER COLUMN id SET DEFAULT nextval('public.monedas_id_seq'::regclass);


--
-- Name: movimientos_vigencias id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias ALTER COLUMN id SET DEFAULT nextval('public.movimientos_vigencias_id_seq'::regclass);


--
-- Name: tipos_de_seguros id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_de_seguros ALTER COLUMN id SET DEFAULT nextval('public.tipos_de_seguros_id_seq'::regclass);


--
-- Name: tipos_documento id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_documento ALTER COLUMN id SET DEFAULT nextval('public.tipos_documento_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.alembic_version (version_num) FROM stdin;
merge_heads_corredor_sequence
\.


--
-- Data for Name: aseguradoras; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.aseguradoras (id, nombre, telefono, direccion, email, pagina_web, identificador_fiscal, esta_activa, observaciones, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.clientes (id, numero_cliente, nombres, apellidos, tipo_documento_id, numero_documento, fecha_nacimiento, direccion, localidad, telefonos, movil, mail, observaciones, creado_por_id, modificado_por_id, fecha_creacion, fecha_modificacion) FROM stdin;
\.


--
-- Data for Name: clientes_corredores; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.clientes_corredores (cliente_id, corredor_numero, fecha_asignacion, corredor_id) FROM stdin;
\.


--
-- Data for Name: corredores; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.corredores (numero, nombres, apellidos, documento, direccion, localidad, telefonos, movil, mail, observaciones, fecha_alta, fecha_baja, matricula, especializacion, id) FROM stdin;
4554	Rodrigo	Ponce	12345678	Dirección de prueba	Montevideo	91136995733	91136995733	rpd.ramas@gmail.com	Corredor administrador	2025-02-19	\N	\N	\N	4554
4555	Juan	García	87654321	Av. Principal 123	Montevideo	91234567	91234567	jgarcia@corredor.com	Corredor regular	2025-02-19	\N	\N	\N	4555
\.


--
-- Data for Name: monedas; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.monedas (id, codigo, nombre, simbolo, descripcion, es_default, esta_activa, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: movimientos_vigencias; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.movimientos_vigencias (id, cliente_id, corredor_id, tipo_seguro_id, carpeta, numero_poliza, endoso, fecha_inicio, fecha_vencimiento, fecha_emision, estado_poliza, forma_pago, tipo_endoso, moneda_id, suma_asegurada, prima, comision, cuotas, observaciones, tipo_duracion) FROM stdin;
\.


--
-- Data for Name: tipos_de_seguros; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.tipos_de_seguros (id, categoria, cobertura, vigencia_default, aseguradora_id, codigo, nombre, descripcion, es_default, esta_activo, fecha_creacion, fecha_actualizacion) FROM stdin;
\.


--
-- Data for Name: tipos_documento; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.tipos_documento (id, nombre, codigo, descripcion, es_default, esta_activo) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: admin_broker
--

COPY public.usuarios (id, nombre, apellido, email, username, hashed_password, is_active, is_superuser, role, comision_porcentaje, telefono, corredor_numero, fecha_creacion, fecha_modificacion, corredor_id) FROM stdin;
3	Juan	García	jgarcia@corredor.com	jgarcia@corredor.com	$2b$12$cRml0T.gCptwEHjgj20MfuWmDCoge6sDSg1xMcV7Pmff./kL5aAzi	t	f	corredor	0	91234567	4555	2025-02-19 01:33:59.503627+00	2025-02-19 01:33:59.503642+00	4555
2	Rodrigo	Ponce	rpd.ramas@gmail.com	rponce	$2b$12$5QOyWMTvaEp6OxPOWArqC.cl0cEBJIJyK0Sj.cwbq.NKAkzkJ1CNG	t	t	admin	0	91136995733	4554	2025-02-19 01:22:22.875577+00	2025-02-19 01:40:59.932792+00	4554
\.


--
-- Name: aseguradoras_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.aseguradoras_id_seq', 1, false);


--
-- Name: cliente_numero_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.cliente_numero_seq', 1, false);


--
-- Name: corredores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.corredores_id_seq', 4556, false);


--
-- Name: corredores_numero_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.corredores_numero_seq', 1, false);


--
-- Name: monedas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.monedas_id_seq', 1, false);


--
-- Name: movimientos_vigencias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.movimientos_vigencias_id_seq', 1, false);


--
-- Name: tipos_de_seguros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.tipos_de_seguros_id_seq', 1, false);


--
-- Name: tipos_documento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.tipos_documento_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_broker
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: aseguradoras aseguradoras_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.aseguradoras
    ADD CONSTRAINT aseguradoras_nombre_key UNIQUE (nombre);


--
-- Name: aseguradoras aseguradoras_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.aseguradoras
    ADD CONSTRAINT aseguradoras_pkey PRIMARY KEY (id);


--
-- Name: clientes_corredores clientes_corredores_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes_corredores
    ADD CONSTRAINT clientes_corredores_pkey PRIMARY KEY (cliente_id, corredor_numero);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- Name: corredores corredores_documento_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.corredores
    ADD CONSTRAINT corredores_documento_key UNIQUE (documento);


--
-- Name: corredores corredores_mail_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.corredores
    ADD CONSTRAINT corredores_mail_key UNIQUE (mail);


--
-- Name: corredores corredores_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.corredores
    ADD CONSTRAINT corredores_pkey PRIMARY KEY (id);


--
-- Name: monedas monedas_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.monedas
    ADD CONSTRAINT monedas_codigo_key UNIQUE (codigo);


--
-- Name: monedas monedas_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.monedas
    ADD CONSTRAINT monedas_pkey PRIMARY KEY (id);


--
-- Name: movimientos_vigencias movimientos_vigencias_numero_poliza_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_numero_poliza_key UNIQUE (numero_poliza);


--
-- Name: movimientos_vigencias movimientos_vigencias_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_pkey PRIMARY KEY (id);


--
-- Name: tipos_de_seguros tipos_de_seguros_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_de_seguros
    ADD CONSTRAINT tipos_de_seguros_pkey PRIMARY KEY (id);


--
-- Name: tipos_documento tipos_documento_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_documento
    ADD CONSTRAINT tipos_documento_pkey PRIMARY KEY (id);


--
-- Name: aseguradoras uq_aseguradoras_rut; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.aseguradoras
    ADD CONSTRAINT uq_aseguradoras_rut UNIQUE (identificador_fiscal);


--
-- Name: corredores uq_corredores_numero; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.corredores
    ADD CONSTRAINT uq_corredores_numero UNIQUE (numero);


--
-- Name: tipos_de_seguros uq_tipos_de_seguros_codigo; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_de_seguros
    ADD CONSTRAINT uq_tipos_de_seguros_codigo UNIQUE (codigo);


--
-- Name: tipos_documento uq_tipos_documento_codigo; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_documento
    ADD CONSTRAINT uq_tipos_documento_codigo UNIQUE (codigo);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: ix_aseguradoras_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_aseguradoras_id ON public.aseguradoras USING btree (id);


--
-- Name: ix_clientes_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_clientes_id ON public.clientes USING btree (id);


--
-- Name: ix_clientes_mail; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE UNIQUE INDEX ix_clientes_mail ON public.clientes USING btree (mail);


--
-- Name: ix_clientes_numero_cliente; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE UNIQUE INDEX ix_clientes_numero_cliente ON public.clientes USING btree (numero_cliente);


--
-- Name: ix_clientes_numero_documento; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE UNIQUE INDEX ix_clientes_numero_documento ON public.clientes USING btree (numero_documento);


--
-- Name: ix_corredores_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE UNIQUE INDEX ix_corredores_id ON public.corredores USING btree (id);


--
-- Name: ix_monedas_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_monedas_id ON public.monedas USING btree (id);


--
-- Name: ix_movimientos_vigencias_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_movimientos_vigencias_id ON public.movimientos_vigencias USING btree (id);


--
-- Name: ix_tipos_documento_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_tipos_documento_id ON public.tipos_documento USING btree (id);


--
-- Name: ix_usuarios_id; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE INDEX ix_usuarios_id ON public.usuarios USING btree (id);


--
-- Name: ix_usuarios_username; Type: INDEX; Schema: public; Owner: admin_broker
--

CREATE UNIQUE INDEX ix_usuarios_username ON public.usuarios USING btree (username);


--
-- Name: clientes_corredores clientes_corredores_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes_corredores
    ADD CONSTRAINT clientes_corredores_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: clientes_corredores clientes_corredores_corredor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes_corredores
    ADD CONSTRAINT clientes_corredores_corredor_id_fkey FOREIGN KEY (corredor_id) REFERENCES public.corredores(id);


--
-- Name: clientes clientes_creado_por_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_creado_por_id_fkey FOREIGN KEY (creado_por_id) REFERENCES public.usuarios(id);


--
-- Name: clientes clientes_modificado_por_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_modificado_por_id_fkey FOREIGN KEY (modificado_por_id) REFERENCES public.usuarios(id);


--
-- Name: clientes clientes_tipo_documento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_tipo_documento_id_fkey FOREIGN KEY (tipo_documento_id) REFERENCES public.tipos_documento(id);


--
-- Name: movimientos_vigencias movimientos_vigencias_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: movimientos_vigencias movimientos_vigencias_corredor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_corredor_id_fkey FOREIGN KEY (corredor_id) REFERENCES public.corredores(id);


--
-- Name: movimientos_vigencias movimientos_vigencias_moneda_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_moneda_id_fkey FOREIGN KEY (moneda_id) REFERENCES public.monedas(id);


--
-- Name: movimientos_vigencias movimientos_vigencias_tipo_seguro_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.movimientos_vigencias
    ADD CONSTRAINT movimientos_vigencias_tipo_seguro_id_fkey FOREIGN KEY (tipo_seguro_id) REFERENCES public.tipos_de_seguros(id);


--
-- Name: tipos_de_seguros tipos_de_seguros_aseguradora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.tipos_de_seguros
    ADD CONSTRAINT tipos_de_seguros_aseguradora_id_fkey FOREIGN KEY (aseguradora_id) REFERENCES public.aseguradoras(id);


--
-- Name: usuarios usuarios_corredor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin_broker
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_corredor_id_fkey FOREIGN KEY (corredor_id) REFERENCES public.corredores(id);


--
-- PostgreSQL database dump complete
--

