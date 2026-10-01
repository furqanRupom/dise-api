--
-- PostgreSQL database dump
--

\restrict RMi34VPTgKLAH2eDbZdCvRlAv2D7hTgdiL0AhUUbwpTrGX6tgFE3GCYvpmd0Q1c

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

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
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- Name: bookingstatus; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.bookingstatus AS ENUM (
    'pending_payment',
    'pending_approval',
    'confirmed',
    'active',
    'completed',
    'cancelled',
    'rejected',
    'no_show',
    'expired'
);


ALTER TYPE public.bookingstatus OWNER TO diseuser;

--
-- Name: discounttype; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.discounttype AS ENUM (
    'percentage',
    'fixed_amount'
);


ALTER TYPE public.discounttype OWNER TO diseuser;

--
-- Name: fueltype; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.fueltype AS ENUM (
    'petrol',
    'diesel',
    'hybrid',
    'electric'
);


ALTER TYPE public.fueltype OWNER TO diseuser;

--
-- Name: licensestatus; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.licensestatus AS ENUM (
    'unsubmitted',
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.licensestatus OWNER TO diseuser;

--
-- Name: notificationchannel; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.notificationchannel AS ENUM (
    'email',
    'sms',
    'push'
);


ALTER TYPE public.notificationchannel OWNER TO diseuser;

--
-- Name: notificationstatus; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.notificationstatus AS ENUM (
    'queued',
    'sent',
    'failed'
);


ALTER TYPE public.notificationstatus OWNER TO diseuser;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.paymentstatus AS ENUM (
    'pending',
    'succeeded',
    'failed',
    'cancelled'
);


ALTER TYPE public.paymentstatus OWNER TO diseuser;

--
-- Name: paymenttype; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.paymenttype AS ENUM (
    'charge',
    'deposit_hold',
    'deposit_capture',
    'deposit_release',
    'refund'
);


ALTER TYPE public.paymenttype OWNER TO diseuser;

--
-- Name: reporttype; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.reporttype AS ENUM (
    'check_in',
    'check_out'
);


ALTER TYPE public.reporttype OWNER TO diseuser;

--
-- Name: transmissiontype; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.transmissiontype AS ENUM (
    'automatic',
    'manual'
);


ALTER TYPE public.transmissiontype OWNER TO diseuser;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.userrole AS ENUM (
    'customer',
    'fleet_staff',
    'support',
    'admin'
);


ALTER TYPE public.userrole OWNER TO diseuser;

--
-- Name: vehiclestatus; Type: TYPE; Schema: public; Owner: diseuser
--

CREATE TYPE public.vehiclestatus AS ENUM (
    'available',
    'booked',
    'in_maintenance',
    'retired'
);


ALTER TYPE public.vehiclestatus OWNER TO diseuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO diseuser;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.audit_logs (
    id uuid NOT NULL,
    actor_id uuid NOT NULL,
    action character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id uuid NOT NULL,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO diseuser;

--
-- Name: booking_status_history; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.booking_status_history (
    id uuid NOT NULL,
    booking_id uuid NOT NULL,
    from_status character varying(30),
    to_status character varying(30) NOT NULL,
    changed_by uuid,
    reason character varying(500),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.booking_status_history OWNER TO diseuser;

--
-- Name: bookings; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.bookings (
    id uuid NOT NULL,
    customer_id uuid NOT NULL,
    vehicle_id uuid NOT NULL,
    pickup_location_id uuid NOT NULL,
    dropoff_location_id uuid NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status public.bookingstatus NOT NULL,
    base_price numeric(10,2) NOT NULL,
    discount_amount numeric(10,2) NOT NULL,
    total_price numeric(10,2) NOT NULL,
    currency character varying(3) NOT NULL,
    coupon_id uuid,
    deposit_hold_amount numeric(10,2) NOT NULL,
    approval_deadline timestamp with time zone,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_bookings_base_price CHECK ((base_price >= (0)::numeric)),
    CONSTRAINT ck_bookings_dates CHECK ((end_date > start_date)),
    CONSTRAINT ck_bookings_deposit_hold_amount CHECK ((deposit_hold_amount >= (0)::numeric)),
    CONSTRAINT ck_bookings_discount_amount CHECK ((discount_amount >= (0)::numeric)),
    CONSTRAINT ck_bookings_total_price CHECK ((total_price >= (0)::numeric))
);


ALTER TABLE public.bookings OWNER TO diseuser;

--
-- Name: condition_report_images; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.condition_report_images (
    id uuid NOT NULL,
    condition_report_id uuid NOT NULL,
    image_url character varying(500) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.condition_report_images OWNER TO diseuser;

--
-- Name: condition_reports; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.condition_reports (
    id uuid NOT NULL,
    booking_id uuid NOT NULL,
    type public.reporttype NOT NULL,
    odometer_km integer NOT NULL,
    fuel_level_pct smallint NOT NULL,
    notes text,
    recorded_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_condition_reports_fuel CHECK (((fuel_level_pct >= 0) AND (fuel_level_pct <= 100))),
    CONSTRAINT ck_condition_reports_odometer CHECK ((odometer_km >= 0))
);


ALTER TABLE public.condition_reports OWNER TO diseuser;

--
-- Name: coupon_usages; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.coupon_usages (
    id uuid NOT NULL,
    coupon_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    booking_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.coupon_usages OWNER TO diseuser;

--
-- Name: coupons; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.coupons (
    id uuid NOT NULL,
    code character varying(30) NOT NULL,
    discount_type public.discounttype NOT NULL,
    discount_value numeric(10,2) NOT NULL,
    max_usage integer,
    usage_count integer NOT NULL,
    valid_from timestamp with time zone NOT NULL,
    valid_to timestamp with time zone NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_coupons_date_range CHECK ((valid_to > valid_from)),
    CONSTRAINT ck_coupons_discount_value CHECK ((discount_value > (0)::numeric)),
    CONSTRAINT ck_coupons_max_usage CHECK (((max_usage IS NULL) OR (max_usage > 0))),
    CONSTRAINT ck_coupons_usage_count CHECK ((usage_count >= 0))
);


ALTER TABLE public.coupons OWNER TO diseuser;

--
-- Name: locations; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.locations (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    city character varying(100) NOT NULL,
    address text NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE public.locations OWNER TO diseuser;

--
-- Name: maintenance_blocks; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.maintenance_blocks (
    id uuid NOT NULL,
    vehicle_id uuid NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    reason character varying(255),
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_maintenance_dates CHECK ((end_date > start_date))
);


ALTER TABLE public.maintenance_blocks OWNER TO diseuser;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.notifications (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    channel public.notificationchannel NOT NULL,
    type character varying(50) NOT NULL,
    payload jsonb NOT NULL,
    status public.notificationstatus NOT NULL,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO diseuser;

--
-- Name: payments; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.payments (
    id uuid NOT NULL,
    booking_id uuid NOT NULL,
    type public.paymenttype NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character varying(3) NOT NULL,
    status public.paymentstatus NOT NULL,
    stripe_payment_intent_id character varying(100),
    idempotency_key character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payments_amount CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.payments OWNER TO diseuser;

--
-- Name: refund_policy_tiers; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.refund_policy_tiers (
    id uuid NOT NULL,
    hours_before_pickup integer NOT NULL,
    refund_percentage numeric(5,2) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_hours_before_pickup_non_negative CHECK ((hours_before_pickup >= 0)),
    CONSTRAINT ck_refund_percentage_range CHECK (((refund_percentage >= (0)::numeric) AND (refund_percentage <= (100)::numeric)))
);


ALTER TABLE public.refund_policy_tiers OWNER TO diseuser;

--
-- Name: reviews; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.reviews (
    id uuid NOT NULL,
    booking_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    vehicle_id uuid NOT NULL,
    rating smallint NOT NULL,
    comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_reviews_rating CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.reviews OWNER TO diseuser;

--
-- Name: users; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    name character varying NOT NULL,
    password character varying NOT NULL,
    email character varying NOT NULL,
    avatar_url character varying,
    role public.userrole NOT NULL,
    date_of_birth date,
    is_active boolean NOT NULL,
    is_verified boolean NOT NULL,
    license_number character varying(50),
    license_document_url character varying(500),
    license_status public.licensestatus NOT NULL,
    stripe_customer_id character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO diseuser;

--
-- Name: vehicle_categories; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.vehicle_categories (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


ALTER TABLE public.vehicle_categories OWNER TO diseuser;

--
-- Name: vehicle_images; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.vehicle_images (
    id uuid NOT NULL,
    vehicle_id uuid NOT NULL,
    image_url character varying(500) NOT NULL,
    sort_order smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vehicle_images OWNER TO diseuser;

--
-- Name: vehicles; Type: TABLE; Schema: public; Owner: diseuser
--

CREATE TABLE public.vehicles (
    id uuid NOT NULL,
    category_id uuid NOT NULL,
    location_id uuid NOT NULL,
    owner_id uuid,
    make character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    year smallint NOT NULL,
    license_plate character varying(20) NOT NULL,
    transmission public.transmissiontype NOT NULL,
    fuel_type public.fueltype NOT NULL,
    seats smallint NOT NULL,
    daily_rate numeric(10,2) NOT NULL,
    currency character varying(3) NOT NULL,
    deposit_amount numeric(10,2) NOT NULL,
    requires_approval boolean NOT NULL,
    status public.vehiclestatus NOT NULL,
    odometer_km integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    CONSTRAINT ck_vehicles_deposit CHECK ((deposit_amount >= (0)::numeric)),
    CONSTRAINT ck_vehicles_rate CHECK ((daily_rate >= (0)::numeric)),
    CONSTRAINT ck_vehicles_seats CHECK ((seats > 0)),
    CONSTRAINT ck_vehicles_year CHECK ((year >= 1990))
);


ALTER TABLE public.vehicles OWNER TO diseuser;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.alembic_version (version_num) FROM stdin;
990f8a4dd8d1
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.audit_logs (id, actor_id, action, entity_type, entity_id, metadata, created_at) FROM stdin;
203366dc-a1c8-4d09-8913-883fd7483084	ef71fa88-0015-4934-9fb2-7c2792e2c087	vehicle.created	vehicle	9b9f442d-1e22-44a0-89b2-dfe494d670d4	{"source": "seed_script"}	2026-09-12 15:57:29.168135+00
5b9647f5-9c9a-4c7b-a7bd-fdc5f9c838c2	ef71fa88-0015-4934-9fb2-7c2792e2c087	vehicle.created	vehicle	37ce3599-55c5-4d3c-9603-7e8761f8a17a	{"source": "seed_script"}	2026-09-12 15:57:29.168135+00
61ae560b-33dd-4091-973f-45bdecb80289	ef71fa88-0015-4934-9fb2-7c2792e2c087	vehicle.created	vehicle	ca542f20-1e35-4519-8945-baeced30da36	{"source": "seed_script"}	2026-09-12 15:57:29.168135+00
9d19b628-667b-4fab-9934-72c5a8109c4e	ef71fa88-0015-4934-9fb2-7c2792e2c087	vehicle.created	vehicle	b84fb40f-c174-4c62-919c-43f35408b439	{"source": "seed_script"}	2026-09-12 15:57:29.168135+00
9e3c4473-d616-4940-ac4a-ead9f0cc6048	ef71fa88-0015-4934-9fb2-7c2792e2c087	vehicle.created	vehicle	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	{"source": "seed_script"}	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: booking_status_history; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.booking_status_history (id, booking_id, from_status, to_status, changed_by, reason, created_at) FROM stdin;
0fbbb575-ce1c-4437-9620-04ab839e3600	e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
71c2751d-2f08-474c-94a6-1d09ca80c804	e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	pending_payment	no_show	c9232297-09a1-4248-860b-bb294b31acdc	Booking moved to no_show	2026-09-12 15:57:29.168135+00
1ad7b596-d021-48ad-8241-b03726f3c2ee	7def8530-e8cf-42d0-bd6a-09b751bb8910	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
8e3fc77a-31ca-49b2-b4db-0564c3d71c06	7def8530-e8cf-42d0-bd6a-09b751bb8910	pending_payment	completed	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking moved to completed	2026-09-12 15:57:29.168135+00
41965cf4-0624-4210-a664-ead3fa269920	420d65f8-9a40-4276-8d71-22d5d3c12787	\N	pending_payment	d836a328-7fb9-4a6a-bdcc-d40d04684ddb	Booking created	2026-09-12 15:57:29.168135+00
64003662-df8c-45ed-9a58-37e1c0951e51	420d65f8-9a40-4276-8d71-22d5d3c12787	pending_payment	confirmed	d836a328-7fb9-4a6a-bdcc-d40d04684ddb	Booking moved to confirmed	2026-09-12 15:57:29.168135+00
c3dd0bac-62d2-4ce4-b73f-455b9f2c4c3c	ae79ba9d-49ad-43de-9af9-8c899676a82b	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
0570cf14-211d-4b42-872d-3ee68947207d	ae79ba9d-49ad-43de-9af9-8c899676a82b	pending_payment	active	c9232297-09a1-4248-860b-bb294b31acdc	Booking moved to active	2026-09-12 15:57:29.168135+00
ffac0f83-8c10-41fb-b7de-bad0a072c61b	60feebf9-af9e-4745-b47a-b6d0bda03213	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
e46d0392-2ea8-45eb-9ffc-dfc36ebce6cd	60feebf9-af9e-4745-b47a-b6d0bda03213	pending_payment	completed	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking moved to completed	2026-09-12 15:57:29.168135+00
d5465535-e419-45b3-99b0-165159b3f49f	bcbb3f5b-f7b7-4d09-8a75-c944fb274fde	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
abc7cd60-0612-4be9-89b5-07765bbe67d5	0dcf8712-2662-4ee9-b701-433691f5afe6	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
e2dcaa9c-62db-4343-8894-0cc62734f60f	0dcf8712-2662-4ee9-b701-433691f5afe6	pending_payment	cancelled	c9232297-09a1-4248-860b-bb294b31acdc	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
f9b9794a-203e-48cc-8cb4-a55e9a6f16fb	0f9af52e-01f4-425d-92dc-b8b4f952220a	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
edfefe34-0416-4606-aba9-014def294f71	0f9af52e-01f4-425d-92dc-b8b4f952220a	pending_payment	completed	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking moved to completed	2026-09-12 15:57:29.168135+00
63104b57-7c95-4217-a9ec-4f6c7319a739	4040827c-852c-4b5a-a3c7-501388e16023	\N	pending_payment	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking created	2026-09-12 15:57:29.168135+00
5c74fb65-b940-4f7c-b0d4-09374e731df5	4040827c-852c-4b5a-a3c7-501388e16023	pending_payment	completed	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking moved to completed	2026-09-12 15:57:29.168135+00
f33e3744-5fbb-413f-bb92-814a79805eeb	a8f9df4c-0dfa-4687-9315-9356c676c38f	\N	pending_payment	93021887-e5a8-4858-84c8-d50af662f9c1	Booking created	2026-09-12 15:57:29.168135+00
75cee762-1853-4c3e-adac-4ca4206332d7	a8f9df4c-0dfa-4687-9315-9356c676c38f	pending_payment	cancelled	93021887-e5a8-4858-84c8-d50af662f9c1	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
522548de-3b0e-477a-95c7-d8329a38c5f4	1c00331a-d4ee-4b88-973a-8b16f33e9afe	\N	pending_payment	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking created	2026-09-12 15:57:29.168135+00
53eda767-ba7a-443c-870c-26eb4657a7fc	1c00331a-d4ee-4b88-973a-8b16f33e9afe	pending_payment	completed	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking moved to completed	2026-09-12 15:57:29.168135+00
5f3d3395-b81d-4315-a23f-50085c6465e0	360733a8-cbfb-470a-921c-55172b300908	\N	pending_payment	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking created	2026-09-12 15:57:29.168135+00
c2060c66-42e1-4ca9-9084-1cc790cc6a48	360733a8-cbfb-470a-921c-55172b300908	pending_payment	cancelled	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
4583490a-2437-44ec-8e62-8ef2a2fcad2d	2e162d4c-745b-4b22-b1f5-fd47c67139d0	\N	pending_payment	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking created	2026-09-12 15:57:29.168135+00
4b79e480-d05e-4de4-989d-68fdd89296c3	2e162d4c-745b-4b22-b1f5-fd47c67139d0	pending_payment	no_show	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking moved to no_show	2026-09-12 15:57:29.168135+00
c74b98e6-7439-4a67-95dc-aaffa7bf1b07	11651a9b-1352-4935-913e-604b21f7cfa9	\N	pending_payment	822327ff-c282-46c2-b06d-318f6b581649	Booking created	2026-09-12 15:57:29.168135+00
11af45ae-bc88-4d13-a9c5-76d4f35bd061	1ee1cb10-082c-4985-8dad-7fc0ee40c48f	\N	pending_payment	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking created	2026-09-12 15:57:29.168135+00
109523a6-ab13-4422-a5fd-404fb300e100	1ee1cb10-082c-4985-8dad-7fc0ee40c48f	pending_payment	rejected	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking moved to rejected	2026-09-12 15:57:29.168135+00
05806054-680e-4d5f-8f5c-c51f89123846	94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	\N	pending_payment	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking created	2026-09-12 15:57:29.168135+00
01f1c417-0e89-4ea3-b72c-66d2de1f8b5b	94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	pending_payment	confirmed	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking moved to confirmed	2026-09-12 15:57:29.168135+00
21980787-c1a5-4d0c-a8ac-b1b5a24fcbd8	70db62f6-fe38-48cf-aba8-532240e9ec0f	\N	pending_payment	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking created	2026-09-12 15:57:29.168135+00
12b5f24c-1de1-4010-87da-f613182601f7	70db62f6-fe38-48cf-aba8-532240e9ec0f	pending_payment	completed	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking moved to completed	2026-09-12 15:57:29.168135+00
038c776e-bb82-43d4-9dc1-5ae6455aac19	2f3dbb16-72e0-4a9c-a883-f22ea622c69e	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
067e42e3-ecc1-46fa-80cf-e4e16ef19049	2f3dbb16-72e0-4a9c-a883-f22ea622c69e	pending_payment	active	c9232297-09a1-4248-860b-bb294b31acdc	Booking moved to active	2026-09-12 15:57:29.168135+00
0862b94a-02d7-4c54-a869-ee3bd64025d1	db4c894a-62ab-467e-b7ed-e1b0763d0be9	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
cf0a0fe4-7381-4d1a-bdd8-f4d08f5b72c1	db4c894a-62ab-467e-b7ed-e1b0763d0be9	pending_payment	confirmed	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking moved to confirmed	2026-09-12 15:57:29.168135+00
4d0b3713-44d4-4670-9f9b-4484acf70499	22d3f034-19d3-4714-8704-a69a0c12556c	\N	pending_payment	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking created	2026-09-12 15:57:29.168135+00
747bdf3b-c04f-448a-8703-0f626f1a78b0	323f8831-8f1b-48a3-8e3a-54537cf7682a	\N	pending_payment	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking created	2026-09-12 15:57:29.168135+00
7cf2ffd6-288f-43c0-aac8-5c1ede90c1f3	323f8831-8f1b-48a3-8e3a-54537cf7682a	pending_payment	rejected	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking moved to rejected	2026-09-12 15:57:29.168135+00
07f23dbd-1324-4650-b147-d978ba44f02b	db20597a-2d02-48a5-8f32-9b0691be69ad	\N	pending_payment	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking created	2026-09-12 15:57:29.168135+00
6f861427-6d8a-41b7-a70d-41fb04932b8c	db20597a-2d02-48a5-8f32-9b0691be69ad	pending_payment	active	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking moved to active	2026-09-12 15:57:29.168135+00
c33f5ed8-6637-44b7-be3c-0ad8cf32ec94	89a69d08-3201-403a-9ee0-0ebb6d9b3001	\N	pending_payment	ba4586c1-3529-411f-b185-b0319a2ef01b	Booking created	2026-09-12 15:57:29.168135+00
076cb938-2886-480f-9355-c326c72902df	89a69d08-3201-403a-9ee0-0ebb6d9b3001	pending_payment	cancelled	ba4586c1-3529-411f-b185-b0319a2ef01b	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
7f5ffa5e-558e-45e6-9a37-194a3d64b934	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	\N	pending_payment	5000423e-518c-4b0d-9e7a-068a9bb92591	Booking created	2026-09-12 15:57:29.168135+00
d376927e-35b3-4666-984b-bce7f4e6b9c5	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	pending_payment	completed	5000423e-518c-4b0d-9e7a-068a9bb92591	Booking moved to completed	2026-09-12 15:57:29.168135+00
7d488050-e0bf-4f04-b283-4921fa8167fc	16b54556-db84-4cf1-8f07-f2ea854b9aab	\N	pending_payment	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking created	2026-09-12 15:57:29.168135+00
88d6a3d5-7b99-4fa7-9619-24d1f1efecd4	16b54556-db84-4cf1-8f07-f2ea854b9aab	pending_payment	rejected	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking moved to rejected	2026-09-12 15:57:29.168135+00
123a7895-8128-43ce-9fab-d188d461fea8	ab9de996-7589-4198-a026-ed127977351b	\N	pending_payment	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking created	2026-09-12 15:57:29.168135+00
7f29c26e-3ced-4796-8a98-9167e5598019	ab9de996-7589-4198-a026-ed127977351b	pending_payment	rejected	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking moved to rejected	2026-09-12 15:57:29.168135+00
a880e243-85c6-47d1-b70c-5d53ceafc2fe	8e4f8d6a-8784-402a-b244-b130efdfebfe	\N	pending_payment	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	Booking created	2026-09-12 15:57:29.168135+00
29ff8053-0914-4040-b036-b5cda547ba31	8e4f8d6a-8784-402a-b244-b130efdfebfe	pending_payment	completed	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	Booking moved to completed	2026-09-12 15:57:29.168135+00
152a66b2-41a7-4eff-ac5d-7813b7e75210	ae51a552-0d1e-4b71-b7fe-8bb6b5c93c68	\N	pending_payment	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking created	2026-09-12 15:57:29.168135+00
da58f985-c5e0-491d-b45e-e7375670e4e3	6c6b8c5c-4654-4b05-a3ea-5e90496de399	\N	pending_payment	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking created	2026-09-12 15:57:29.168135+00
f331be09-8bc7-4ea1-a532-ca61d457eee0	6c6b8c5c-4654-4b05-a3ea-5e90496de399	pending_payment	cancelled	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
f8b3f436-4bd2-446d-b80c-2716f2c0bd05	e0ad019e-d25c-4af7-8727-8922a7419d15	\N	pending_payment	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking created	2026-09-12 15:57:29.168135+00
7374e00d-5073-4bfe-9a27-231b24cb6527	e0ad019e-d25c-4af7-8727-8922a7419d15	pending_payment	active	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking moved to active	2026-09-12 15:57:29.168135+00
2a02321d-c454-4ed8-b5df-c6bade3c97f9	7d606a86-fab9-4c36-ba15-bc7cba171e12	\N	pending_payment	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking created	2026-09-12 15:57:29.168135+00
bfc183fb-bdb3-4f79-bf20-bf99e8ef7304	7d606a86-fab9-4c36-ba15-bc7cba171e12	pending_payment	rejected	6edaf56c-24cf-4412-b794-ad83c73ccb41	Booking moved to rejected	2026-09-12 15:57:29.168135+00
4d7b2329-a250-4872-998a-eb7fed4fcbb4	91747042-04ed-4464-b12e-24ba81c68c46	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
872bff2d-86d2-404f-8fa5-ca110ed2947c	6ea6be63-af29-4de8-b818-8aefc62034b5	\N	pending_payment	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking created	2026-09-12 15:57:29.168135+00
6e37d61a-a6fa-4bd6-8e24-6cc2a91d015c	6ea6be63-af29-4de8-b818-8aefc62034b5	pending_payment	no_show	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking moved to no_show	2026-09-12 15:57:29.168135+00
766053a9-6dbc-4402-bcab-979cc7c507ea	7e3301df-a0cd-4b35-b6f9-b58365cdfe7b	\N	pending_payment	ef84c615-f252-4405-9626-ae712e5cdbd0	Booking created	2026-09-12 15:57:29.168135+00
7b6f2488-cdc3-47d0-8a10-a4f9587e303c	481166e1-6952-4a84-b1cf-8a5f30559954	\N	pending_payment	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking created	2026-09-12 15:57:29.168135+00
8f63db69-1f39-46b8-8420-882fab837f52	481166e1-6952-4a84-b1cf-8a5f30559954	pending_payment	completed	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking moved to completed	2026-09-12 15:57:29.168135+00
f6e7e3fb-f802-4766-ad53-78330b1d87fa	e3ec41c8-2dd4-4968-a3be-3afba57a6948	\N	pending_payment	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	Booking created	2026-09-12 15:57:29.168135+00
d6a2a98b-d9a0-4f86-ae8b-8390f2e1b071	e3ec41c8-2dd4-4968-a3be-3afba57a6948	pending_payment	active	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	Booking moved to active	2026-09-12 15:57:29.168135+00
93e3c001-7a80-4b8c-9252-6e757fbdf08e	c06145fe-a7ab-441c-b257-b4c468a24c78	\N	pending_payment	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking created	2026-09-12 15:57:29.168135+00
e7cfc327-2bdf-43ff-99bd-8e0b2927f033	c06145fe-a7ab-441c-b257-b4c468a24c78	pending_payment	completed	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Booking moved to completed	2026-09-12 15:57:29.168135+00
7c0efc24-834f-4807-8d92-f5d7fefa866e	e9461ed3-5a89-4a73-ba13-2c73a99c9c33	\N	pending_payment	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking created	2026-09-12 15:57:29.168135+00
b644fdc2-f713-458e-b73f-ce426d42c6b3	e9461ed3-5a89-4a73-ba13-2c73a99c9c33	pending_payment	no_show	1da230e0-ba99-4fed-b9e4-503c7e595736	Booking moved to no_show	2026-09-12 15:57:29.168135+00
a73e95ab-318f-4925-9664-14e7908238f5	757d77f2-ef53-4759-ae3e-54b4a2d6020e	\N	pending_payment	c9232297-09a1-4248-860b-bb294b31acdc	Booking created	2026-09-12 15:57:29.168135+00
4e7737b2-aa4d-4d06-969f-1cb8200f21f5	5f2ea630-74f8-42be-ac9f-f839ab89b0ae	\N	pending_payment	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking created	2026-09-12 15:57:29.168135+00
30281eca-f9d3-439f-b6ab-689c738d7dd9	5f2ea630-74f8-42be-ac9f-f839ab89b0ae	pending_payment	confirmed	42b01386-1c6d-4efa-9013-0a035eb2fd6a	Booking moved to confirmed	2026-09-12 15:57:29.168135+00
f548f9f6-f830-426d-8004-06ed61409a13	eeac1848-4c4f-4d89-b917-5a60aca959d5	\N	pending_payment	93021887-e5a8-4858-84c8-d50af662f9c1	Booking created	2026-09-12 15:57:29.168135+00
2fdc9f7a-f8ba-4e30-b939-3261242975cf	eeac1848-4c4f-4d89-b917-5a60aca959d5	pending_payment	cancelled	93021887-e5a8-4858-84c8-d50af662f9c1	Booking moved to cancelled	2026-09-12 15:57:29.168135+00
4f078928-b2f2-4301-9ed4-5b70ff9e8001	51f84805-15c3-4ec2-a769-109b0ac4584d	\N	pending_payment	822327ff-c282-46c2-b06d-318f6b581649	Booking created	2026-09-12 16:40:31.978086+00
513053f1-4191-4468-b495-019eeb173018	63382662-b8f8-461e-aacc-ed894b81ecf0	\N	pending_payment	822327ff-c282-46c2-b06d-318f6b581649	Booking created	2026-09-12 16:43:11.301099+00
7561ede7-8f32-42e9-930e-4f4caf6a5a2b	e423f3cf-07a3-4e7d-8090-57275ffb3ed3	\N	pending_payment	b86e2a62-1170-4e1d-83a8-6814cbe9def2	Booking created	2026-09-12 16:45:08.391101+00
\.


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.bookings (id, customer_id, vehicle_id, pickup_location_id, dropoff_location_id, start_date, end_date, status, base_price, discount_amount, total_price, currency, coupon_id, deposit_hold_amount, approval_deadline, created_by, created_at, updated_at, deleted_at) FROM stdin;
e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	c9232297-09a1-4248-860b-bb294b31acdc	ca542f20-1e35-4519-8945-baeced30da36	5171f2c2-2581-4f20-b3f7-331896669bd2	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-07-14	2026-07-20	no_show	54000.00	500.00	53500.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	5000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
7def8530-e8cf-42d0-bd6a-09b751bb8910	ef84c615-f252-4405-9626-ae712e5cdbd0	ca542f20-1e35-4519-8945-baeced30da36	7f4ed45c-31a1-447a-a8b5-94999d854d4d	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-07-26	2026-07-28	completed	18000.00	0.00	18000.00	BDT	\N	5000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
420d65f8-9a40-4276-8d71-22d5d3c12787	d836a328-7fb9-4a6a-bdcc-d40d04684ddb	ca542f20-1e35-4519-8945-baeced30da36	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-07-30	2026-07-31	confirmed	9000.00	900.00	8100.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	5000.00	\N	d836a328-7fb9-4a6a-bdcc-d40d04684ddb	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ae79ba9d-49ad-43de-9af9-8c899676a82b	c9232297-09a1-4248-860b-bb294b31acdc	1960b30d-633d-4913-9cb8-bcd7a77b9766	794cec6a-a6df-4f8a-84be-a742b517aefc	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	2026-08-11	2026-08-16	active	12500.00	0.00	12500.00	BDT	\N	15000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
60feebf9-af9e-4745-b47a-b6d0bda03213	ef84c615-f252-4405-9626-ae712e5cdbd0	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	2026-07-26	2026-07-31	completed	17500.00	0.00	17500.00	BDT	\N	15000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
bcbb3f5b-f7b7-4d09-8a75-c944fb274fde	c9232297-09a1-4248-860b-bb294b31acdc	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	7f4ed45c-31a1-447a-a8b5-94999d854d4d	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-08-03	2026-08-06	pending_payment	15000.00	500.00	14500.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	15000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
0dcf8712-2662-4ee9-b701-433691f5afe6	c9232297-09a1-4248-860b-bb294b31acdc	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	7f4ed45c-31a1-447a-a8b5-94999d854d4d	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-08-09	2026-08-11	cancelled	10000.00	0.00	10000.00	BDT	\N	15000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
0f9af52e-01f4-425d-92dc-b8b4f952220a	ef84c615-f252-4405-9626-ae712e5cdbd0	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-08-18	2026-08-19	completed	5000.00	500.00	4500.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	15000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
4040827c-852c-4b5a-a3c7-501388e16023	42b01386-1c6d-4efa-9013-0a035eb2fd6a	f8e767a7-56a9-4614-abcc-b9071c4e971d	7f4ed45c-31a1-447a-a8b5-94999d854d4d	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-08-05	2026-08-07	completed	3600.00	500.00	3100.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	10000.00	\N	42b01386-1c6d-4efa-9013-0a035eb2fd6a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
a8f9df4c-0dfa-4687-9315-9356c676c38f	93021887-e5a8-4858-84c8-d50af662f9c1	f8e767a7-56a9-4614-abcc-b9071c4e971d	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-08-11	2026-08-13	cancelled	3600.00	0.00	3600.00	BDT	\N	10000.00	\N	93021887-e5a8-4858-84c8-d50af662f9c1	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1c00331a-d4ee-4b88-973a-8b16f33e9afe	6edaf56c-24cf-4412-b794-ad83c73ccb41	f8e767a7-56a9-4614-abcc-b9071c4e971d	7f4ed45c-31a1-447a-a8b5-94999d854d4d	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-08-18	2026-08-24	completed	10800.00	500.00	10300.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	10000.00	\N	6edaf56c-24cf-4412-b794-ad83c73ccb41	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
360733a8-cbfb-470a-921c-55172b300908	6edaf56c-24cf-4412-b794-ad83c73ccb41	d68e56a3-b121-4178-b5c8-a6666534fb53	5171f2c2-2581-4f20-b3f7-331896669bd2	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-07-21	2026-07-26	cancelled	12500.00	0.00	12500.00	BDT	\N	15000.00	\N	6edaf56c-24cf-4412-b794-ad83c73ccb41	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
2e162d4c-745b-4b22-b1f5-fd47c67139d0	1da230e0-ba99-4fed-b9e4-503c7e595736	f0d29664-cfae-48f4-b20f-6d6c538ee82e	794cec6a-a6df-4f8a-84be-a742b517aefc	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-07-23	2026-07-29	no_show	10800.00	1620.00	9180.00	BDT	bc58ee95-4e55-4c7b-9e42-6bf48a827996	10000.00	\N	1da230e0-ba99-4fed-b9e4-503c7e595736	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
11651a9b-1352-4935-913e-604b21f7cfa9	822327ff-c282-46c2-b06d-318f6b581649	f1d03864-52d1-4b39-934d-710e78421c7d	7f4ed45c-31a1-447a-a8b5-94999d854d4d	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-31	2026-08-03	pending_payment	4500.00	500.00	4000.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	5000.00	\N	822327ff-c282-46c2-b06d-318f6b581649	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1ee1cb10-082c-4985-8dad-7fc0ee40c48f	1da230e0-ba99-4fed-b9e4-503c7e595736	f1d03864-52d1-4b39-934d-710e78421c7d	794cec6a-a6df-4f8a-84be-a742b517aefc	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-08-05	2026-08-11	rejected	9000.00	0.00	9000.00	BDT	\N	5000.00	\N	1da230e0-ba99-4fed-b9e4-503c7e595736	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	42b01386-1c6d-4efa-9013-0a035eb2fd6a	f1d03864-52d1-4b39-934d-710e78421c7d	794cec6a-a6df-4f8a-84be-a742b517aefc	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-08-16	2026-08-17	confirmed	1500.00	0.00	1500.00	BDT	\N	5000.00	\N	42b01386-1c6d-4efa-9013-0a035eb2fd6a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
70db62f6-fe38-48cf-aba8-532240e9ec0f	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	0a415e85-8bfa-4336-85a4-469a257e2718	7f4ed45c-31a1-447a-a8b5-94999d854d4d	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-07-27	2026-07-29	completed	18000.00	2700.00	15300.00	BDT	bc58ee95-4e55-4c7b-9e42-6bf48a827996	10000.00	\N	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
2f3dbb16-72e0-4a9c-a883-f22ea622c69e	c9232297-09a1-4248-860b-bb294b31acdc	0a415e85-8bfa-4336-85a4-469a257e2718	794cec6a-a6df-4f8a-84be-a742b517aefc	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-08-03	2026-08-06	active	27000.00	0.00	27000.00	BDT	\N	10000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
db4c894a-62ab-467e-b7ed-e1b0763d0be9	ef84c615-f252-4405-9626-ae712e5cdbd0	0a415e85-8bfa-4336-85a4-469a257e2718	5171f2c2-2581-4f20-b3f7-331896669bd2	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-08-09	2026-08-14	confirmed	45000.00	500.00	44500.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	10000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
22d3f034-19d3-4714-8704-a69a0c12556c	42b01386-1c6d-4efa-9013-0a035eb2fd6a	1dbbf574-4b28-4183-a6f2-86feab15bdb4	5171f2c2-2581-4f20-b3f7-331896669bd2	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-08-13	2026-08-15	pending_payment	18000.00	0.00	18000.00	BDT	\N	5000.00	\N	42b01386-1c6d-4efa-9013-0a035eb2fd6a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
323f8831-8f1b-48a3-8e3a-54537cf7682a	b86e2a62-1170-4e1d-83a8-6814cbe9def2	1dbbf574-4b28-4183-a6f2-86feab15bdb4	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-08-22	2026-08-24	rejected	18000.00	1800.00	16200.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	5000.00	\N	b86e2a62-1170-4e1d-83a8-6814cbe9def2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
db20597a-2d02-48a5-8f32-9b0691be69ad	6edaf56c-24cf-4412-b794-ad83c73ccb41	37ce3599-55c5-4d3c-9603-7e8761f8a17a	794cec6a-a6df-4f8a-84be-a742b517aefc	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-18	2026-07-22	active	7200.00	500.00	6700.00	BDT	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	5000.00	\N	6edaf56c-24cf-4412-b794-ad83c73ccb41	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
89a69d08-3201-403a-9ee0-0ebb6d9b3001	ba4586c1-3529-411f-b185-b0319a2ef01b	117ae621-9e98-4017-aa16-91125ae20555	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-08-03	2026-08-06	cancelled	27000.00	4050.00	22950.00	BDT	bc58ee95-4e55-4c7b-9e42-6bf48a827996	20000.00	\N	ba4586c1-3529-411f-b185-b0319a2ef01b	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
3185cc5f-b6dc-4279-a7dd-ed73c2ded345	5000423e-518c-4b0d-9e7a-068a9bb92591	117ae621-9e98-4017-aa16-91125ae20555	7f4ed45c-31a1-447a-a8b5-94999d854d4d	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-08-08	2026-08-14	completed	54000.00	5400.00	48600.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	20000.00	\N	5000423e-518c-4b0d-9e7a-068a9bb92591	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
16b54556-db84-4cf1-8f07-f2ea854b9aab	b86e2a62-1170-4e1d-83a8-6814cbe9def2	e9b26501-a85d-415d-a03e-c14eb4df584c	7f4ed45c-31a1-447a-a8b5-94999d854d4d	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-07-14	2026-07-17	rejected	27000.00	4050.00	22950.00	BDT	bc58ee95-4e55-4c7b-9e42-6bf48a827996	20000.00	\N	b86e2a62-1170-4e1d-83a8-6814cbe9def2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ab9de996-7589-4198-a026-ed127977351b	b86e2a62-1170-4e1d-83a8-6814cbe9def2	e9b26501-a85d-415d-a03e-c14eb4df584c	5171f2c2-2581-4f20-b3f7-331896669bd2	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-07-19	2026-07-24	rejected	45000.00	0.00	45000.00	BDT	\N	20000.00	\N	b86e2a62-1170-4e1d-83a8-6814cbe9def2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
8e4f8d6a-8784-402a-b244-b130efdfebfe	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	e9b26501-a85d-415d-a03e-c14eb4df584c	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-30	2026-07-31	completed	9000.00	0.00	9000.00	BDT	\N	20000.00	\N	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ae51a552-0d1e-4b71-b7fe-8bb6b5c93c68	42b01386-1c6d-4efa-9013-0a035eb2fd6a	b84fb40f-c174-4c62-919c-43f35408b439	7f4ed45c-31a1-447a-a8b5-94999d854d4d	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-07-31	2026-08-01	pending_payment	1800.00	0.00	1800.00	BDT	\N	5000.00	\N	42b01386-1c6d-4efa-9013-0a035eb2fd6a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
6c6b8c5c-4654-4b05-a3ea-5e90496de399	1da230e0-ba99-4fed-b9e4-503c7e595736	b84fb40f-c174-4c62-919c-43f35408b439	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-08-08	2026-08-14	cancelled	10800.00	0.00	10800.00	BDT	\N	5000.00	\N	1da230e0-ba99-4fed-b9e4-503c7e595736	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
e0ad019e-d25c-4af7-8727-8922a7419d15	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	16071b39-2c5c-4330-a772-7d1043dd6609	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-22	2026-07-25	active	7500.00	0.00	7500.00	BDT	\N	10000.00	\N	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
7d606a86-fab9-4c36-ba15-bc7cba171e12	6edaf56c-24cf-4412-b794-ad83c73ccb41	16071b39-2c5c-4330-a772-7d1043dd6609	794cec6a-a6df-4f8a-84be-a742b517aefc	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-07-31	2026-08-05	rejected	12500.00	0.00	12500.00	BDT	\N	10000.00	\N	6edaf56c-24cf-4412-b794-ad83c73ccb41	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
91747042-04ed-4464-b12e-24ba81c68c46	ef84c615-f252-4405-9626-ae712e5cdbd0	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-08-07	2026-08-11	pending_payment	14000.00	0.00	14000.00	BDT	\N	20000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
6ea6be63-af29-4de8-b818-8aefc62034b5	1da230e0-ba99-4fed-b9e4-503c7e595736	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	5171f2c2-2581-4f20-b3f7-331896669bd2	794cec6a-a6df-4f8a-84be-a742b517aefc	2026-08-17	2026-08-23	no_show	21000.00	0.00	21000.00	BDT	\N	20000.00	\N	1da230e0-ba99-4fed-b9e4-503c7e595736	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
7e3301df-a0cd-4b35-b6f9-b58365cdfe7b	ef84c615-f252-4405-9626-ae712e5cdbd0	9b9f442d-1e22-44a0-89b2-dfe494d670d4	5171f2c2-2581-4f20-b3f7-331896669bd2	7f4ed45c-31a1-447a-a8b5-94999d854d4d	2026-07-28	2026-08-03	pending_payment	10800.00	1080.00	9720.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	10000.00	\N	ef84c615-f252-4405-9626-ae712e5cdbd0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
481166e1-6952-4a84-b1cf-8a5f30559954	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	9b9f442d-1e22-44a0-89b2-dfe494d670d4	5171f2c2-2581-4f20-b3f7-331896669bd2	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-08-10	2026-08-12	completed	3600.00	360.00	3240.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	10000.00	\N	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
e3ec41c8-2dd4-4968-a3be-3afba57a6948	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	fd6eb2d7-d6f0-4931-851b-a489ba528a95	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-07-17	2026-07-18	active	2500.00	0.00	2500.00	BDT	\N	5000.00	\N	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
c06145fe-a7ab-441c-b257-b4c468a24c78	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	fd6eb2d7-d6f0-4931-851b-a489ba528a95	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-23	2026-07-27	completed	10000.00	1000.00	9000.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	5000.00	\N	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
e9461ed3-5a89-4a73-ba13-2c73a99c9c33	1da230e0-ba99-4fed-b9e4-503c7e595736	fd6eb2d7-d6f0-4931-851b-a489ba528a95	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-30	2026-08-01	no_show	5000.00	500.00	4500.00	BDT	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	5000.00	\N	1da230e0-ba99-4fed-b9e4-503c7e595736	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
757d77f2-ef53-4759-ae3e-54b4a2d6020e	c9232297-09a1-4248-860b-bb294b31acdc	39e0155f-af8f-4c38-9a21-969b460b5b4d	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	2026-07-30	2026-08-01	pending_payment	10000.00	0.00	10000.00	BDT	\N	20000.00	\N	c9232297-09a1-4248-860b-bb294b31acdc	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
5f2ea630-74f8-42be-ac9f-f839ab89b0ae	42b01386-1c6d-4efa-9013-0a035eb2fd6a	9cb83739-0b36-41b1-ab4f-c766eb73211b	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-07-18	2026-07-23	confirmed	15000.00	0.00	15000.00	BDT	\N	20000.00	\N	42b01386-1c6d-4efa-9013-0a035eb2fd6a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
eeac1848-4c4f-4d89-b917-5a60aca959d5	93021887-e5a8-4858-84c8-d50af662f9c1	9cb83739-0b36-41b1-ab4f-c766eb73211b	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	5171f2c2-2581-4f20-b3f7-331896669bd2	2026-07-28	2026-07-31	cancelled	9000.00	0.00	9000.00	BDT	\N	20000.00	\N	93021887-e5a8-4858-84c8-d50af662f9c1	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
51f84805-15c3-4ec2-a769-109b0ac4584d	822327ff-c282-46c2-b06d-318f6b581649	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-09-15	2026-09-18	pending_payment	10500.00	0.00	10500.00	BDT	\N	15000.00	\N	822327ff-c282-46c2-b06d-318f6b581649	2026-09-12 16:40:31.978086+00	2026-09-12 16:40:31.978086+00	\N
63382662-b8f8-461e-aacc-ed894b81ecf0	822327ff-c282-46c2-b06d-318f6b581649	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-09-15	2026-09-18	pending_payment	10500.00	0.00	10500.00	BDT	\N	15000.00	\N	822327ff-c282-46c2-b06d-318f6b581649	2026-09-12 16:43:11.301099+00	2026-09-12 16:43:11.301099+00	\N
e423f3cf-07a3-4e7d-8090-57275ffb3ed3	b86e2a62-1170-4e1d-83a8-6814cbe9def2	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	2026-09-15	2026-09-18	pending_payment	10500.00	0.00	10500.00	BDT	\N	15000.00	\N	b86e2a62-1170-4e1d-83a8-6814cbe9def2	2026-09-12 16:45:08.391101+00	2026-09-12 16:45:08.391101+00	\N
\.


--
-- Data for Name: condition_report_images; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.condition_report_images (id, condition_report_id, image_url, created_at) FROM stdin;
0f4ab9cc-d10b-4ee2-86a3-8927659d4c16	8a6ebb95-5d9f-4967-8fc5-9dbd2638c468	https://picsum.photos/seed/8a6ebb95-5d9f-4967-8fc5-9dbd2638c468/800/600	2026-09-12 15:57:29.168135+00
7060e5d4-c16a-4fd5-a40a-2a9aea04e6b6	8294793b-c2e0-462b-b920-f432cac4dfde	https://picsum.photos/seed/8294793b-c2e0-462b-b920-f432cac4dfde/800/600	2026-09-12 15:57:29.168135+00
47fa752b-ec37-4823-b589-ba86504e8115	7367ae5e-c672-40df-aa37-ae3733809c1d	https://picsum.photos/seed/7367ae5e-c672-40df-aa37-ae3733809c1d/800/600	2026-09-12 15:57:29.168135+00
10f53585-0b2a-4db8-86ae-4115d043777a	8aedc95e-63ec-441a-aeef-2b30c6e91dd3	https://picsum.photos/seed/8aedc95e-63ec-441a-aeef-2b30c6e91dd3/800/600	2026-09-12 15:57:29.168135+00
cf5e2b49-1641-443c-b93d-854e8941205e	c3f218c4-35c9-4ce2-b634-4f5a0e0e4e5a	https://picsum.photos/seed/c3f218c4-35c9-4ce2-b634-4f5a0e0e4e5a/800/600	2026-09-12 15:57:29.168135+00
0e517aef-6878-48b8-82ee-16ef19e013ac	24e85df5-7ab2-44a2-b0cc-3427ee0bd14b	https://picsum.photos/seed/24e85df5-7ab2-44a2-b0cc-3427ee0bd14b/800/600	2026-09-12 15:57:29.168135+00
02724ccc-b540-46bb-8c40-c9825213809d	e76a1627-d736-4a28-87a2-c698823231df	https://picsum.photos/seed/e76a1627-d736-4a28-87a2-c698823231df/800/600	2026-09-12 15:57:29.168135+00
915fefb5-d25c-4deb-8f1d-d4c74ccc981b	41ab2bac-075f-4ce5-85dd-463e3f0ab2c1	https://picsum.photos/seed/41ab2bac-075f-4ce5-85dd-463e3f0ab2c1/800/600	2026-09-12 15:57:29.168135+00
9af4f74a-6bae-4cee-b5e4-b5ab1b64d53d	2f1f7b9a-710f-49f2-a1c8-e9f25e3e0492	https://picsum.photos/seed/2f1f7b9a-710f-49f2-a1c8-e9f25e3e0492/800/600	2026-09-12 15:57:29.168135+00
186098a3-7ab3-489b-a83b-119f6c96b265	710689c5-4b17-42ef-a92b-4a3272cf0399	https://picsum.photos/seed/710689c5-4b17-42ef-a92b-4a3272cf0399/800/600	2026-09-12 15:57:29.168135+00
09b2c40c-bbb2-4ff3-8a04-8bbf317e5de2	db6a2ade-73e7-4eb0-8e25-c464fb636d99	https://picsum.photos/seed/db6a2ade-73e7-4eb0-8e25-c464fb636d99/800/600	2026-09-12 15:57:29.168135+00
afa0c88f-aa88-41d5-9349-c5ed0642d546	999a7ccb-b76b-4db7-9aa1-b60f688003f2	https://picsum.photos/seed/999a7ccb-b76b-4db7-9aa1-b60f688003f2/800/600	2026-09-12 15:57:29.168135+00
94f89f37-05ee-4e63-b57b-01617b8952ca	d607dd83-c1b0-4f7e-ae8b-73e82d45a8ee	https://picsum.photos/seed/d607dd83-c1b0-4f7e-ae8b-73e82d45a8ee/800/600	2026-09-12 15:57:29.168135+00
eeffb83c-c988-4723-9f0c-6d670029b2a4	6309f52f-cb2f-4288-bb0c-3b601a4ed1fd	https://picsum.photos/seed/6309f52f-cb2f-4288-bb0c-3b601a4ed1fd/800/600	2026-09-12 15:57:29.168135+00
f1fae9f6-5369-465e-b06c-6fb7bc2c328a	94a70305-67f3-4c72-9974-05036fb09724	https://picsum.photos/seed/94a70305-67f3-4c72-9974-05036fb09724/800/600	2026-09-12 15:57:29.168135+00
a18a7654-982e-47d8-ad7f-c6ddc059f28f	ca502bf2-eb5b-44df-968f-be736802e781	https://picsum.photos/seed/ca502bf2-eb5b-44df-968f-be736802e781/800/600	2026-09-12 15:57:29.168135+00
72a0afa8-2aef-4372-becf-af69c5e02dab	cb85ef49-e90f-445a-a0f5-139d61f1d8f5	https://picsum.photos/seed/cb85ef49-e90f-445a-a0f5-139d61f1d8f5/800/600	2026-09-12 15:57:29.168135+00
7d3f6f41-a2a8-461a-b7ef-94f3862435a5	5ca35503-d5f3-465f-b4b8-532a0211dbe4	https://picsum.photos/seed/5ca35503-d5f3-465f-b4b8-532a0211dbe4/800/600	2026-09-12 15:57:29.168135+00
1f2e83a9-25a3-45c9-8a98-a447ae6546e7	4d90a573-106c-477c-9761-1fe1e6281c8c	https://picsum.photos/seed/4d90a573-106c-477c-9761-1fe1e6281c8c/800/600	2026-09-12 15:57:29.168135+00
313b9651-c58a-4de1-998f-acbfaf59d314	c22f7dec-ec4f-455b-a4b6-6a791cb0e253	https://picsum.photos/seed/c22f7dec-ec4f-455b-a4b6-6a791cb0e253/800/600	2026-09-12 15:57:29.168135+00
5a7a178d-c67c-4c2c-abf7-5d7f3cc0826b	b79eed41-3c27-42a7-80c0-9985bbf190f1	https://picsum.photos/seed/b79eed41-3c27-42a7-80c0-9985bbf190f1/800/600	2026-09-12 15:57:29.168135+00
2666291e-3bf7-4c21-9eb6-787902905067	8b6d5bd1-819d-4faa-9378-85628b548490	https://picsum.photos/seed/8b6d5bd1-819d-4faa-9378-85628b548490/800/600	2026-09-12 15:57:29.168135+00
271265b9-5067-471b-902f-f468641ecc9a	f85a1395-f55a-4174-95fd-457ecb8a3fc5	https://picsum.photos/seed/f85a1395-f55a-4174-95fd-457ecb8a3fc5/800/600	2026-09-12 15:57:29.168135+00
6227c54a-b749-4a3b-ba78-2f1cdbdcb58b	0defdd9c-9a5e-4bee-8a7f-93a6e2a27fc8	https://picsum.photos/seed/0defdd9c-9a5e-4bee-8a7f-93a6e2a27fc8/800/600	2026-09-12 15:57:29.168135+00
f9d5fea9-6ced-4a2e-90d0-b19cfab45ffd	de5fd5e1-2eff-4e26-a552-b55ac370ad4e	https://picsum.photos/seed/de5fd5e1-2eff-4e26-a552-b55ac370ad4e/800/600	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: condition_reports; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.condition_reports (id, booking_id, type, odometer_km, fuel_level_pct, notes, recorded_by, created_at) FROM stdin;
8a6ebb95-5d9f-4967-8fc5-9dbd2638c468	7def8530-e8cf-42d0-bd6a-09b751bb8910	check_in	65069	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
8294793b-c2e0-462b-b920-f432cac4dfde	7def8530-e8cf-42d0-bd6a-09b751bb8910	check_out	65513	75	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
7367ae5e-c672-40df-aa37-ae3733809c1d	ae79ba9d-49ad-43de-9af9-8c899676a82b	check_in	12560	100	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
8aedc95e-63ec-441a-aeef-2b30c6e91dd3	60feebf9-af9e-4745-b47a-b6d0bda03213	check_in	59857	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
c3f218c4-35c9-4ce2-b634-4f5a0e0e4e5a	60feebf9-af9e-4745-b47a-b6d0bda03213	check_out	59910	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
24e85df5-7ab2-44a2-b0cc-3427ee0bd14b	0f9af52e-01f4-425d-92dc-b8b4f952220a	check_in	49139	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
e76a1627-d736-4a28-87a2-c698823231df	0f9af52e-01f4-425d-92dc-b8b4f952220a	check_out	49625	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
41ab2bac-075f-4ce5-85dd-463e3f0ab2c1	4040827c-852c-4b5a-a3c7-501388e16023	check_in	38906	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
2f1f7b9a-710f-49f2-a1c8-e9f25e3e0492	4040827c-852c-4b5a-a3c7-501388e16023	check_out	39068	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
710689c5-4b17-42ef-a92b-4a3272cf0399	1c00331a-d4ee-4b88-973a-8b16f33e9afe	check_in	67125	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
db6a2ade-73e7-4eb0-8e25-c464fb636d99	1c00331a-d4ee-4b88-973a-8b16f33e9afe	check_out	67189	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
999a7ccb-b76b-4db7-9aa1-b60f688003f2	70db62f6-fe38-48cf-aba8-532240e9ec0f	check_in	54057	100	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
d607dd83-c1b0-4f7e-ae8b-73e82d45a8ee	70db62f6-fe38-48cf-aba8-532240e9ec0f	check_out	54454	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
6309f52f-cb2f-4288-bb0c-3b601a4ed1fd	2f3dbb16-72e0-4a9c-a883-f22ea622c69e	check_in	31632	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
94a70305-67f3-4c72-9974-05036fb09724	db20597a-2d02-48a5-8f32-9b0691be69ad	check_in	26728	100	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
ca502bf2-eb5b-44df-968f-be736802e781	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	check_in	13534	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
cb85ef49-e90f-445a-a0f5-139d61f1d8f5	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	check_out	13887	75	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
5ca35503-d5f3-465f-b4b8-532a0211dbe4	8e4f8d6a-8784-402a-b244-b130efdfebfe	check_in	13552	50	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
4d90a573-106c-477c-9761-1fe1e6281c8c	8e4f8d6a-8784-402a-b244-b130efdfebfe	check_out	13931	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
c22f7dec-ec4f-455b-a4b6-6a791cb0e253	e0ad019e-d25c-4af7-8727-8922a7419d15	check_in	27786	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
b79eed41-3c27-42a7-80c0-9985bbf190f1	481166e1-6952-4a84-b1cf-8a5f30559954	check_in	33819	50	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
8b6d5bd1-819d-4faa-9378-85628b548490	481166e1-6952-4a84-b1cf-8a5f30559954	check_out	34002	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
f85a1395-f55a-4174-95fd-457ecb8a3fc5	e3ec41c8-2dd4-4968-a3be-3afba57a6948	check_in	52906	50	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
0defdd9c-9a5e-4bee-8a7f-93a6e2a27fc8	c06145fe-a7ab-441c-b257-b4c468a24c78	check_in	69598	75	Vehicle inspected and handed over to customer.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
de5fd5e1-2eff-4e26-a552-b55ac370ad4e	c06145fe-a7ab-441c-b257-b4c468a24c78	check_out	69820	50	Vehicle returned and inspected after rental.	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: coupon_usages; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.coupon_usages (id, coupon_id, customer_id, booking_id, created_at) FROM stdin;
ee1b5a89-f7f5-4e8f-854d-3841c3977b70	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	c9232297-09a1-4248-860b-bb294b31acdc	e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	2026-09-12 15:57:29.168135+00
e7e50816-dcc8-4786-b866-567138c0f8e8	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	d836a328-7fb9-4a6a-bdcc-d40d04684ddb	420d65f8-9a40-4276-8d71-22d5d3c12787	2026-09-12 15:57:29.168135+00
505757fd-4771-4086-b776-5fa82a38ba7d	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	c9232297-09a1-4248-860b-bb294b31acdc	bcbb3f5b-f7b7-4d09-8a75-c944fb274fde	2026-09-12 15:57:29.168135+00
da71fb81-38ac-4e6b-bfd5-79e912ad2d31	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	ef84c615-f252-4405-9626-ae712e5cdbd0	0f9af52e-01f4-425d-92dc-b8b4f952220a	2026-09-12 15:57:29.168135+00
72b2bcb1-c8e8-4c31-9595-e36b26ccb984	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	42b01386-1c6d-4efa-9013-0a035eb2fd6a	4040827c-852c-4b5a-a3c7-501388e16023	2026-09-12 15:57:29.168135+00
a293d25e-13de-4cae-8d82-61d705ad305f	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	6edaf56c-24cf-4412-b794-ad83c73ccb41	1c00331a-d4ee-4b88-973a-8b16f33e9afe	2026-09-12 15:57:29.168135+00
3c512270-6d24-4039-9cb9-729407ed63e7	bc58ee95-4e55-4c7b-9e42-6bf48a827996	1da230e0-ba99-4fed-b9e4-503c7e595736	2e162d4c-745b-4b22-b1f5-fd47c67139d0	2026-09-12 15:57:29.168135+00
cf679e28-6dce-4557-836f-1716a1d41d78	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	822327ff-c282-46c2-b06d-318f6b581649	11651a9b-1352-4935-913e-604b21f7cfa9	2026-09-12 15:57:29.168135+00
c65ee54a-95db-48ba-9746-0ebe49c1d9d6	bc58ee95-4e55-4c7b-9e42-6bf48a827996	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	70db62f6-fe38-48cf-aba8-532240e9ec0f	2026-09-12 15:57:29.168135+00
4292d938-0348-4543-b30e-4a57a4727fe2	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	ef84c615-f252-4405-9626-ae712e5cdbd0	db4c894a-62ab-467e-b7ed-e1b0763d0be9	2026-09-12 15:57:29.168135+00
14fbf14e-7040-467e-b1be-e9687a313253	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	b86e2a62-1170-4e1d-83a8-6814cbe9def2	323f8831-8f1b-48a3-8e3a-54537cf7682a	2026-09-12 15:57:29.168135+00
c05eadf8-215a-4287-af8d-82c5020257d2	ed6e265d-5d81-4224-8e3a-de1d2eb8103c	6edaf56c-24cf-4412-b794-ad83c73ccb41	db20597a-2d02-48a5-8f32-9b0691be69ad	2026-09-12 15:57:29.168135+00
82639a09-3559-4900-a210-9d0ee051aee3	bc58ee95-4e55-4c7b-9e42-6bf48a827996	ba4586c1-3529-411f-b185-b0319a2ef01b	89a69d08-3201-403a-9ee0-0ebb6d9b3001	2026-09-12 15:57:29.168135+00
1bd8077e-7998-4a95-96d3-baff5e7ccf30	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	5000423e-518c-4b0d-9e7a-068a9bb92591	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	2026-09-12 15:57:29.168135+00
09b55f32-d8f8-4d07-85dc-9c15ad40c540	bc58ee95-4e55-4c7b-9e42-6bf48a827996	b86e2a62-1170-4e1d-83a8-6814cbe9def2	16b54556-db84-4cf1-8f07-f2ea854b9aab	2026-09-12 15:57:29.168135+00
42e081a7-991b-4f80-a1c6-e82377d7d2ca	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	ef84c615-f252-4405-9626-ae712e5cdbd0	7e3301df-a0cd-4b35-b6f9-b58365cdfe7b	2026-09-12 15:57:29.168135+00
7a438ffe-7688-4bb9-bde6-10bb8b5a7dc9	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	481166e1-6952-4a84-b1cf-8a5f30559954	2026-09-12 15:57:29.168135+00
b1dddb4d-d18d-431b-9181-1928a8fd96e9	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	c06145fe-a7ab-441c-b257-b4c468a24c78	2026-09-12 15:57:29.168135+00
86fb6129-95b2-40d2-abe9-e98fbd803bd8	3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	1da230e0-ba99-4fed-b9e4-503c7e595736	e9461ed3-5a89-4a73-ba13-2c73a99c9c33	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: coupons; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.coupons (id, code, discount_type, discount_value, max_usage, usage_count, valid_from, valid_to, is_active, created_at, updated_at, deleted_at) FROM stdin;
3424eb2e-3f1f-4e2d-af1c-95a5aa30a06d	WELCOME10	percentage	10.00	100	8	2026-08-13 15:57:29.194897+00	2026-12-11 15:57:29.194907+00	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
bc58ee95-4e55-4c7b-9e42-6bf48a827996	EID2026	percentage	15.00	100	4	2026-08-13 15:57:29.194987+00	2026-12-11 15:57:29.194988+00	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ed6e265d-5d81-4224-8e3a-de1d2eb8103c	SAVE500	fixed_amount	500.00	100	7	2026-08-13 15:57:29.194967+00	2026-12-11 15:57:29.194969+00	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.locations (id, name, city, address, latitude, longitude, is_active, created_at, updated_at, deleted_at) FROM stdin;
794cec6a-a6df-4f8a-84be-a742b517aefc	Dhaka Downtown Branch	Dhaka	71822 Arroyo Expressway, Dhaka, Bangladesh	23.810300	90.412500	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
5171f2c2-2581-4f20-b3f7-331896669bd2	Chittagong Downtown Branch	Chittagong	963 Jennifer Locks Suite 787, Chittagong, Bangladesh	22.356900	91.783200	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
7f4ed45c-31a1-447a-a8b5-94999d854d4d	Sylhet Downtown Branch	Sylhet	31509 Brianna Avenue, Sylhet, Bangladesh	24.894900	91.868700	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
44da8e10-b7fb-4d09-a0d8-e282b1d30f13	Khulna Downtown Branch	Khulna	031 Michele Cliffs, Khulna, Bangladesh	22.845600	89.540300	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	Rajshahi Downtown Branch	Rajshahi	7382 Sanchez Mountains, Rajshahi, Bangladesh	24.374500	88.604200	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
\.


--
-- Data for Name: maintenance_blocks; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.maintenance_blocks (id, vehicle_id, start_date, end_date, reason, created_by, created_at) FROM stdin;
6a4dcbf4-ece7-48cc-983e-3c244fa714d7	0a415e85-8bfa-4336-85a4-469a257e2718	2026-11-11	2026-11-12	Oil change	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
29884830-90bf-4c56-8500-196aaf6c133a	b84fb40f-c174-4c62-919c-43f35408b439	2026-11-18	2026-11-19	Scheduled service	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
f3196d30-10af-432e-be71-08888d095231	9cb83739-0b36-41b1-ab4f-c766eb73211b	2026-12-05	2026-12-06	Brake inspection	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
81571bea-8ccd-4e6e-aa5d-e921671c95ea	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	2026-11-17	2026-11-18	General maintenance	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
db829b2b-a4e3-436a-8f66-093b2b3280f1	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	2026-11-15	2026-11-17	Brake inspection	c126de50-6239-4399-8e56-f2fb5e034e34	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.notifications (id, user_id, channel, type, payload, status, sent_at, created_at) FROM stdin;
7f7048b1-4d3a-42da-9d3c-605c387d3872	6edaf56c-24cf-4412-b794-ad83c73ccb41	email	booking_status_update	{"status": "rejected", "booking_id": "7d606a86-fab9-4c36-ba15-bc7cba171e12"}	sent	2026-09-12 15:57:29.266087+00	2026-09-12 15:57:29.168135+00
834b772b-5eeb-412c-83ef-ed8b08a361fe	ef84c615-f252-4405-9626-ae712e5cdbd0	sms	booking_status_update	{"status": "completed", "booking_id": "0f9af52e-01f4-425d-92dc-b8b4f952220a"}	sent	2026-09-12 15:57:29.266175+00	2026-09-12 15:57:29.168135+00
a32a41de-de30-4c4d-a0a6-348f75515dca	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	sms	booking_status_update	{"status": "completed", "booking_id": "c06145fe-a7ab-441c-b257-b4c468a24c78"}	queued	\N	2026-09-12 15:57:29.168135+00
dfc3cd7b-1524-4dc5-a58b-a14a9b7458ff	822327ff-c282-46c2-b06d-318f6b581649	email	booking_status_update	{"status": "pending_payment", "booking_id": "11651a9b-1352-4935-913e-604b21f7cfa9"}	sent	2026-09-12 15:57:29.266236+00	2026-09-12 15:57:29.168135+00
3a4cc81a-f356-430e-9986-7647c5c17f98	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	email	booking_status_update	{"status": "active", "booking_id": "e0ad019e-d25c-4af7-8727-8922a7419d15"}	sent	2026-09-12 15:57:29.266257+00	2026-09-12 15:57:29.168135+00
76a20c14-3af2-4575-b237-299fa0336d11	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	push	booking_status_update	{"status": "completed", "booking_id": "70db62f6-fe38-48cf-aba8-532240e9ec0f"}	sent	2026-09-12 15:57:29.266278+00	2026-09-12 15:57:29.168135+00
6db9c277-524a-4752-8732-6b21a2c83eb2	5000423e-518c-4b0d-9e7a-068a9bb92591	push	booking_status_update	{"status": "completed", "booking_id": "3185cc5f-b6dc-4279-a7dd-ed73c2ded345"}	sent	2026-09-12 15:57:29.266298+00	2026-09-12 15:57:29.168135+00
3f650f43-b6e5-42ff-9434-bfbcf3ec7546	6edaf56c-24cf-4412-b794-ad83c73ccb41	sms	booking_status_update	{"status": "completed", "booking_id": "1c00331a-d4ee-4b88-973a-8b16f33e9afe"}	sent	2026-09-12 15:57:29.266318+00	2026-09-12 15:57:29.168135+00
7fb5285d-4b62-43bf-b039-17bb8ec792d6	42b01386-1c6d-4efa-9013-0a035eb2fd6a	push	booking_status_update	{"status": "confirmed", "booking_id": "5f2ea630-74f8-42be-ac9f-f839ab89b0ae"}	queued	\N	2026-09-12 15:57:29.168135+00
e962df64-8aa5-4199-8669-c1437c492773	ef84c615-f252-4405-9626-ae712e5cdbd0	email	booking_status_update	{"status": "pending_payment", "booking_id": "7e3301df-a0cd-4b35-b6f9-b58365cdfe7b"}	sent	2026-09-12 15:57:29.266358+00	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.payments (id, booking_id, type, amount, currency, status, stripe_payment_intent_id, idempotency_key, created_at, updated_at) FROM stdin;
36dda348-ccf9-4c7b-8286-f1b3e1a68f3c	e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	charge	53500.00	BDT	succeeded	pi_6239a0368fd84370a28968a079bd428b	seed_charge_e36c95d6-55a4-40af-a7a7-1d11f54c2bc2	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
f7b4a5ca-ac37-4db6-a1e0-2e5f686c727b	7def8530-e8cf-42d0-bd6a-09b751bb8910	charge	18000.00	BDT	succeeded	pi_3060bd655f8046598e925d4db687253f	seed_charge_7def8530-e8cf-42d0-bd6a-09b751bb8910	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
021cd6f5-2ea4-49e2-af4a-a2cdafda037e	7def8530-e8cf-42d0-bd6a-09b751bb8910	deposit_hold	5000.00	BDT	succeeded	pi_bf9eb2f26fca4f6ab87d88c811c482cd	seed_deposit_7def8530-e8cf-42d0-bd6a-09b751bb8910	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
d79391f9-4368-45d8-b795-b5f1702c0563	7def8530-e8cf-42d0-bd6a-09b751bb8910	deposit_release	5000.00	BDT	succeeded	pi_4eb3ae752063413d91764c33e20e2b34	seed_release_7def8530-e8cf-42d0-bd6a-09b751bb8910	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
6baf0931-7970-4d05-941d-2fd0294dca4a	420d65f8-9a40-4276-8d71-22d5d3c12787	charge	8100.00	BDT	succeeded	pi_c55cc1f6ef554d279a8fa4fd65dab815	seed_charge_420d65f8-9a40-4276-8d71-22d5d3c12787	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
056eec7b-b99e-454b-8a14-5b9f9a2841a3	420d65f8-9a40-4276-8d71-22d5d3c12787	deposit_hold	5000.00	BDT	succeeded	pi_0d2f98efd0bf424fbfaf86bb7b5fbfba	seed_deposit_420d65f8-9a40-4276-8d71-22d5d3c12787	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
fe888d36-a481-4de4-999b-1e3e181cac4f	ae79ba9d-49ad-43de-9af9-8c899676a82b	charge	12500.00	BDT	succeeded	pi_135d6b1e58d04485ae1e87e30f5fc17b	seed_charge_ae79ba9d-49ad-43de-9af9-8c899676a82b	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
e3c1b21a-a4b6-4856-8c8f-b7ffb6118811	ae79ba9d-49ad-43de-9af9-8c899676a82b	deposit_hold	15000.00	BDT	succeeded	pi_23e2135abe7a4cafa896e24b5876f026	seed_deposit_ae79ba9d-49ad-43de-9af9-8c899676a82b	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
92284e2b-f27a-41b9-82ac-461a7ee11643	60feebf9-af9e-4745-b47a-b6d0bda03213	charge	17500.00	BDT	succeeded	pi_7d026ca36cd44ad3b83094ebd0db11dd	seed_charge_60feebf9-af9e-4745-b47a-b6d0bda03213	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
94b15f57-946a-44e3-85dd-adcaa73644e1	60feebf9-af9e-4745-b47a-b6d0bda03213	deposit_hold	15000.00	BDT	succeeded	pi_af039374a49d473fa1b482ef5d4a87e4	seed_deposit_60feebf9-af9e-4745-b47a-b6d0bda03213	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
821e2f3f-b3a8-4152-9225-ac355ce06c12	60feebf9-af9e-4745-b47a-b6d0bda03213	deposit_release	15000.00	BDT	succeeded	pi_05ae5243666f4956b4db7e34257c7ef8	seed_release_60feebf9-af9e-4745-b47a-b6d0bda03213	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
0dc38337-3797-4b8f-a972-5d0f88b4d763	0dcf8712-2662-4ee9-b701-433691f5afe6	charge	10000.00	BDT	failed	pi_a2f376dd63454e03b0366000b533b8f5	seed_charge_0dcf8712-2662-4ee9-b701-433691f5afe6	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
da47f407-6240-46bb-b67c-88a7982d5317	0f9af52e-01f4-425d-92dc-b8b4f952220a	charge	4500.00	BDT	succeeded	pi_9a8a65e41a48419ebd7d0c5f05cfb4c0	seed_charge_0f9af52e-01f4-425d-92dc-b8b4f952220a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
f360e2cb-6c03-4b7e-9488-be307b661944	0f9af52e-01f4-425d-92dc-b8b4f952220a	deposit_hold	15000.00	BDT	succeeded	pi_dce22ed9f1bb4b31a97193d2de2d02ab	seed_deposit_0f9af52e-01f4-425d-92dc-b8b4f952220a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
65a6b0e4-4191-4352-847d-3a5d3274f702	0f9af52e-01f4-425d-92dc-b8b4f952220a	deposit_release	15000.00	BDT	succeeded	pi_375f835a7d824aa7b7fb1143669221b0	seed_release_0f9af52e-01f4-425d-92dc-b8b4f952220a	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
34314b61-9a30-4bc0-b7ac-7acc4a2f22a7	4040827c-852c-4b5a-a3c7-501388e16023	charge	3100.00	BDT	succeeded	pi_55679bf689eb4a0dac2c9262febd3c07	seed_charge_4040827c-852c-4b5a-a3c7-501388e16023	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
b47c1d95-9ecb-4505-8a68-c21a4d1c1b79	4040827c-852c-4b5a-a3c7-501388e16023	deposit_hold	10000.00	BDT	succeeded	pi_193e1b8683fd4fa6af4bdd0c6ea36f71	seed_deposit_4040827c-852c-4b5a-a3c7-501388e16023	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
05944f49-f050-428c-bafc-0449f06107cf	4040827c-852c-4b5a-a3c7-501388e16023	deposit_release	10000.00	BDT	succeeded	pi_380b35a455b94cae8b9714b1d80f60c6	seed_release_4040827c-852c-4b5a-a3c7-501388e16023	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
224e3d19-991b-4fad-8729-93e2bff1e0f1	a8f9df4c-0dfa-4687-9315-9356c676c38f	charge	3600.00	BDT	failed	pi_089f24809b3f4685befb04398c799d33	seed_charge_a8f9df4c-0dfa-4687-9315-9356c676c38f	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
c47371cd-a6f6-418e-b8bd-f3d340187907	1c00331a-d4ee-4b88-973a-8b16f33e9afe	charge	10300.00	BDT	succeeded	pi_cdf4b116bfe9462f82293589a28d826a	seed_charge_1c00331a-d4ee-4b88-973a-8b16f33e9afe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
492bf912-bec7-4612-9f4c-46bdcdc46024	1c00331a-d4ee-4b88-973a-8b16f33e9afe	deposit_hold	10000.00	BDT	succeeded	pi_67dabceb2eb5455f8d1e4e6ec2e15237	seed_deposit_1c00331a-d4ee-4b88-973a-8b16f33e9afe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
43daef90-9be1-47f6-b13a-6566cc2645e5	1c00331a-d4ee-4b88-973a-8b16f33e9afe	deposit_release	10000.00	BDT	succeeded	pi_8d485dd9de71450a9a5c626a688febdd	seed_release_1c00331a-d4ee-4b88-973a-8b16f33e9afe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
80738d45-6303-41e8-a085-0d356d19cccb	360733a8-cbfb-470a-921c-55172b300908	charge	12500.00	BDT	failed	pi_4b1d1f34d85a4d1997fb60cf124dba61	seed_charge_360733a8-cbfb-470a-921c-55172b300908	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
4fd792d9-b462-4209-9bca-956ac3d5aedb	2e162d4c-745b-4b22-b1f5-fd47c67139d0	charge	9180.00	BDT	succeeded	pi_18356d055ad94846806bad863e3369ae	seed_charge_2e162d4c-745b-4b22-b1f5-fd47c67139d0	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
7de17a94-39af-415b-976a-95c58bab964b	94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	charge	1500.00	BDT	succeeded	pi_7e17873d7cc44f58bd1cd095e08632d4	seed_charge_94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
7f434aba-c14a-4425-96a8-1f931b48958b	94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	deposit_hold	5000.00	BDT	succeeded	pi_95564ce2dcc943efac91909fe2c7b25e	seed_deposit_94e322e7-d2d6-41e0-aba8-d1d7828eb9b1	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
b15877a8-a23c-44bf-a672-a8301f822e3f	70db62f6-fe38-48cf-aba8-532240e9ec0f	charge	15300.00	BDT	succeeded	pi_42954212651b4f468106fd811e07f85d	seed_charge_70db62f6-fe38-48cf-aba8-532240e9ec0f	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
ebd3bdbc-409a-4e9b-8c50-9c5265c7d4ce	70db62f6-fe38-48cf-aba8-532240e9ec0f	deposit_hold	10000.00	BDT	succeeded	pi_ce273e1e733d4887b23859c30e0cc050	seed_deposit_70db62f6-fe38-48cf-aba8-532240e9ec0f	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
d4afb377-4439-4d6b-8bf1-a9338b9d5241	70db62f6-fe38-48cf-aba8-532240e9ec0f	deposit_release	10000.00	BDT	succeeded	pi_3026b49a9bf44884834fde0dfdbf73f4	seed_release_70db62f6-fe38-48cf-aba8-532240e9ec0f	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
89739d93-f4e8-44e9-baa9-d305232e5032	2f3dbb16-72e0-4a9c-a883-f22ea622c69e	charge	27000.00	BDT	succeeded	pi_ef1e47d211054a449e257965e9c5cafb	seed_charge_2f3dbb16-72e0-4a9c-a883-f22ea622c69e	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
e3491d30-6f32-4ac5-b9c6-148b98b0c186	2f3dbb16-72e0-4a9c-a883-f22ea622c69e	deposit_hold	10000.00	BDT	succeeded	pi_bf7a9433671b43ec898a3841d8f60a0a	seed_deposit_2f3dbb16-72e0-4a9c-a883-f22ea622c69e	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
57af711c-d52f-46a1-aca8-0e64dd062112	db4c894a-62ab-467e-b7ed-e1b0763d0be9	charge	44500.00	BDT	succeeded	pi_c840b57066a742d0b24774856d2fdab7	seed_charge_db4c894a-62ab-467e-b7ed-e1b0763d0be9	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
e76f74b0-315f-49e0-b65e-95c3474c4a5d	db4c894a-62ab-467e-b7ed-e1b0763d0be9	deposit_hold	10000.00	BDT	succeeded	pi_c887905eadd84ca284a2064c21bd5905	seed_deposit_db4c894a-62ab-467e-b7ed-e1b0763d0be9	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
044eb57d-5370-4f22-a61a-9692a764f643	db20597a-2d02-48a5-8f32-9b0691be69ad	charge	6700.00	BDT	succeeded	pi_cb09367ee974488b8163ccbf9f5984cb	seed_charge_db20597a-2d02-48a5-8f32-9b0691be69ad	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
17b971b7-c167-4997-bd9a-bed9b91caa4d	db20597a-2d02-48a5-8f32-9b0691be69ad	deposit_hold	5000.00	BDT	succeeded	pi_5c7f17de9a374d45920e6c43b1fbd587	seed_deposit_db20597a-2d02-48a5-8f32-9b0691be69ad	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
53fbea9b-7794-4f17-b556-0ed1570df8b6	89a69d08-3201-403a-9ee0-0ebb6d9b3001	charge	22950.00	BDT	failed	pi_d297fc3c8f6449ecb02e87fa0e9991fa	seed_charge_89a69d08-3201-403a-9ee0-0ebb6d9b3001	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
29c9b752-cc43-47ed-adb7-4cee990b579d	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	charge	48600.00	BDT	succeeded	pi_7015ee30f486490f8d1d2361bcab79b7	seed_charge_3185cc5f-b6dc-4279-a7dd-ed73c2ded345	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
c953f0e5-d927-4537-a966-5ea12f8dcadb	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	deposit_hold	20000.00	BDT	succeeded	pi_e024f699347b43e2920c4530c90da74c	seed_deposit_3185cc5f-b6dc-4279-a7dd-ed73c2ded345	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
3fc03aa2-ccdb-4e5b-b4f8-314cd952ab42	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	deposit_release	20000.00	BDT	succeeded	pi_1d58cd569f234148b2850197c4307f30	seed_release_3185cc5f-b6dc-4279-a7dd-ed73c2ded345	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
a84b4e1a-6c95-4783-b515-c827aea79fe0	8e4f8d6a-8784-402a-b244-b130efdfebfe	charge	9000.00	BDT	succeeded	pi_a626f12029f7400a9de288bf76032658	seed_charge_8e4f8d6a-8784-402a-b244-b130efdfebfe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
58e77172-5cf2-4ee9-8bca-70dab091d67b	8e4f8d6a-8784-402a-b244-b130efdfebfe	deposit_hold	20000.00	BDT	succeeded	pi_4ebc7842f0d744d6a3f43498effbb18d	seed_deposit_8e4f8d6a-8784-402a-b244-b130efdfebfe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
94031e5a-ca68-4a0f-a5b6-b59bbc9b85e3	8e4f8d6a-8784-402a-b244-b130efdfebfe	deposit_release	20000.00	BDT	succeeded	pi_1282969c06dd40c880f67359273dab10	seed_release_8e4f8d6a-8784-402a-b244-b130efdfebfe	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
c69df3b7-571d-4a4e-a2e9-3a97a43ede8f	6c6b8c5c-4654-4b05-a3ea-5e90496de399	charge	10800.00	BDT	failed	pi_0aeef66d279f4d0b992f8dbd10671238	seed_charge_6c6b8c5c-4654-4b05-a3ea-5e90496de399	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
3a88463b-e9bb-4c6d-b8e6-3dabc94e13e1	e0ad019e-d25c-4af7-8727-8922a7419d15	charge	7500.00	BDT	succeeded	pi_ffb6bfd4709446f49e2ae068517e0aef	seed_charge_e0ad019e-d25c-4af7-8727-8922a7419d15	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
671c696e-cfea-4714-91f4-3d6a5b06859f	e0ad019e-d25c-4af7-8727-8922a7419d15	deposit_hold	10000.00	BDT	succeeded	pi_c2045f42b6b042cb9794450f0306f70b	seed_deposit_e0ad019e-d25c-4af7-8727-8922a7419d15	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
95b74f46-4463-4ace-a648-2e7105982175	6ea6be63-af29-4de8-b818-8aefc62034b5	charge	21000.00	BDT	succeeded	pi_c2688f0070564f079efb4b768e843649	seed_charge_6ea6be63-af29-4de8-b818-8aefc62034b5	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
05dc8c7e-c334-40d8-8093-1fd4e019304e	481166e1-6952-4a84-b1cf-8a5f30559954	charge	3240.00	BDT	succeeded	pi_15bf9a80bd284f2fa3e7a0c921f42ca0	seed_charge_481166e1-6952-4a84-b1cf-8a5f30559954	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
2c9357b2-0f63-4180-b7a6-e546c0bab975	481166e1-6952-4a84-b1cf-8a5f30559954	deposit_hold	10000.00	BDT	succeeded	pi_680843cd3d6d495ca19cae33c15941fc	seed_deposit_481166e1-6952-4a84-b1cf-8a5f30559954	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
57f356c3-4bf7-4cee-9f06-01f2a88acdc0	481166e1-6952-4a84-b1cf-8a5f30559954	deposit_release	10000.00	BDT	succeeded	pi_2362e5da7ee04a1fbd7e8f0be5733d6e	seed_release_481166e1-6952-4a84-b1cf-8a5f30559954	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
98f78ce5-2ed5-4d0b-bba4-3d89e99687e7	e3ec41c8-2dd4-4968-a3be-3afba57a6948	charge	2500.00	BDT	succeeded	pi_46cdcf11bd2d48dc9f36311a7b0aa590	seed_charge_e3ec41c8-2dd4-4968-a3be-3afba57a6948	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
9c3ea6f5-f577-4a11-9743-cbb8666c8cd0	e3ec41c8-2dd4-4968-a3be-3afba57a6948	deposit_hold	5000.00	BDT	succeeded	pi_fad730a2940d41c28f2dc91434730e6d	seed_deposit_e3ec41c8-2dd4-4968-a3be-3afba57a6948	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
03b02023-f6ba-40b3-a465-b8f63f8a8593	c06145fe-a7ab-441c-b257-b4c468a24c78	charge	9000.00	BDT	succeeded	pi_9833ec49e137473a8edbf1fbac38066a	seed_charge_c06145fe-a7ab-441c-b257-b4c468a24c78	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
811d0ac6-f6c6-46ba-b5b9-ae15cba7305d	c06145fe-a7ab-441c-b257-b4c468a24c78	deposit_hold	5000.00	BDT	succeeded	pi_409c0e74056a4b2589dd4445f2dcfdfb	seed_deposit_c06145fe-a7ab-441c-b257-b4c468a24c78	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
513d4c65-ab41-48b4-9f01-a29bb0bb32d1	c06145fe-a7ab-441c-b257-b4c468a24c78	deposit_release	5000.00	BDT	succeeded	pi_07048e63bbbf44afabee3f1100b97a15	seed_release_c06145fe-a7ab-441c-b257-b4c468a24c78	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
09ec6d06-251f-4623-be9f-a98fb7db5c97	e9461ed3-5a89-4a73-ba13-2c73a99c9c33	charge	4500.00	BDT	succeeded	pi_4a16960668a7442ea0f286a6b2119cc5	seed_charge_e9461ed3-5a89-4a73-ba13-2c73a99c9c33	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
28ac067e-0b01-4db6-8b8b-164f3e9e7b2f	5f2ea630-74f8-42be-ac9f-f839ab89b0ae	charge	15000.00	BDT	succeeded	pi_73cc7dfaa9574c21aae7837f3a5217b5	seed_charge_5f2ea630-74f8-42be-ac9f-f839ab89b0ae	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
1334cc16-1610-4605-9ad9-920cefbdfc4e	5f2ea630-74f8-42be-ac9f-f839ab89b0ae	deposit_hold	20000.00	BDT	succeeded	pi_8270f3c4c7834aca8bd462c9029ee643	seed_deposit_5f2ea630-74f8-42be-ac9f-f839ab89b0ae	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
506987ea-f563-46a8-9772-37b4063dc00e	eeac1848-4c4f-4d89-b917-5a60aca959d5	charge	9000.00	BDT	failed	pi_da2d305ec03b411b8abb779c495cc9ad	seed_charge_eeac1848-4c4f-4d89-b917-5a60aca959d5	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: refund_policy_tiers; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.refund_policy_tiers (id, hours_before_pickup, refund_percentage, is_active, created_at, updated_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.reviews (id, booking_id, customer_id, vehicle_id, rating, comment, created_at) FROM stdin;
e91aa3d4-9d11-4997-8677-a862311a6a6c	7def8530-e8cf-42d0-bd6a-09b751bb8910	ef84c615-f252-4405-9626-ae712e5cdbd0	ca542f20-1e35-4519-8945-baeced30da36	3	Organization people information on mission various daughter respond draw how public feel first sell authority leader.	2026-09-12 15:57:29.168135+00
7e40fa9a-4817-44f0-bcaa-1055b5584d71	0f9af52e-01f4-425d-92dc-b8b4f952220a	ef84c615-f252-4405-9626-ae712e5cdbd0	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	4	You available defense enter value thing these hard citizen street region particularly would pressure account.	2026-09-12 15:57:29.168135+00
5106d4eb-62cb-4a98-90b7-779169683bb2	4040827c-852c-4b5a-a3c7-501388e16023	42b01386-1c6d-4efa-9013-0a035eb2fd6a	f8e767a7-56a9-4614-abcc-b9071c4e971d	5	Federal professional voice care break blood network evening painting response data plant enough major town.	2026-09-12 15:57:29.168135+00
e89ecc9a-6b1e-4eee-99aa-a39b7b19b819	1c00331a-d4ee-4b88-973a-8b16f33e9afe	6edaf56c-24cf-4412-b794-ad83c73ccb41	f8e767a7-56a9-4614-abcc-b9071c4e971d	3	Begin interest everybody about side PM energy.	2026-09-12 15:57:29.168135+00
dbbd97a8-a603-425d-b1a4-ae91dda3f448	70db62f6-fe38-48cf-aba8-532240e9ec0f	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	0a415e85-8bfa-4336-85a4-469a257e2718	5	Necessary into act away third tough nation strong old challenge camera final together.	2026-09-12 15:57:29.168135+00
cd9c6f7d-e30b-4c8d-a6a0-b12776a1b6c0	3185cc5f-b6dc-4279-a7dd-ed73c2ded345	5000423e-518c-4b0d-9e7a-068a9bb92591	117ae621-9e98-4017-aa16-91125ae20555	3	Together decide economic bill sister this image.	2026-09-12 15:57:29.168135+00
6412783a-1287-4568-87d8-1af031aec8a2	8e4f8d6a-8784-402a-b244-b130efdfebfe	3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	e9b26501-a85d-415d-a03e-c14eb4df584c	4	See understand door class son computer include conference under site in prove same easy city red.	2026-09-12 15:57:29.168135+00
a73fe025-9fcf-4cc9-ae4c-e7915b3d34ce	481166e1-6952-4a84-b1cf-8a5f30559954	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	9b9f442d-1e22-44a0-89b2-dfe494d670d4	4	The teach develop staff least figure somebody dinner age cover foreign ten.	2026-09-12 15:57:29.168135+00
7fc1afa4-a80e-4034-9505-e1f18eb5896b	c06145fe-a7ab-441c-b257-b4c468a24c78	b499f28b-ed7f-454c-a514-7e5f0e5c8d57	fd6eb2d7-d6f0-4931-851b-a489ba528a95	3	Go meeting quickly such former agree theory end oil worker although.	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.users (id, name, password, email, avatar_url, role, date_of_birth, is_active, is_verified, license_number, license_document_url, license_status, stripe_customer_id, created_at, updated_at, deleted_at) FROM stdin;
ef71fa88-0015-4934-9fb2-7c2792e2c087	Admin User	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	admin@example.com	\N	admin	1990-07-09	t	t	\N	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
40c6e791-9667-4645-92f9-996ba39fd4d6	Support Agent	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	support@example.com	\N	support	1971-06-22	t	t	\N	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
c126de50-6239-4399-8e56-f2fb5e034e34	Fleet Manager	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	fleet@example.com	\N	fleet_staff	1979-03-23	t	t	\N	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
822327ff-c282-46c2-b06d-318f6b581649	Noah Rhodes	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer1@example.com	\N	customer	2001-09-26	t	t	DL19600133	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
b86e2a62-1170-4e1d-83a8-6814cbe9def2	Alyssa Gonzalez	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer2@example.com	\N	customer	1990-08-04	t	t	DL86379402	\N	pending	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
b499f28b-ed7f-454c-a514-7e5f0e5c8d57	Gina Moore	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer3@example.com	\N	customer	2004-09-23	t	t	DL51161559	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
2320579e-aaf1-49fc-afc5-ed2e56fb83c5	Andrew Stevens	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer4@example.com	\N	customer	1966-06-10	t	t	DL61849593	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
6edaf56c-24cf-4412-b794-ad83c73ccb41	Amber Perez	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer5@example.com	\N	customer	1974-01-04	t	t	\N	\N	unsubmitted	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
5000423e-518c-4b0d-9e7a-068a9bb92591	David Garcia	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer6@example.com	\N	customer	1973-06-26	t	t	DL52553419	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
3dd77303-5e3c-4dd3-abcc-8f23aa11f3b2	Kimberly Sanchez	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer7@example.com	\N	customer	1981-12-17	t	t	DL48350305	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
d836a328-7fb9-4a6a-bdcc-d40d04684ddb	Austin Gentry	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer8@example.com	\N	customer	1986-10-15	t	t	DL53767242	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1da230e0-ba99-4fed-b9e4-503c7e595736	Justin Baker	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer9@example.com	\N	customer	1987-08-03	t	t	\N	\N	unsubmitted	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ef84c615-f252-4405-9626-ae712e5cdbd0	Jennifer Robinson	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer10@example.com	\N	customer	2006-08-01	t	t	\N	\N	unsubmitted	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
c9232297-09a1-4248-860b-bb294b31acdc	Ann Williams	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer11@example.com	\N	customer	1965-09-28	t	t	DL26916697	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
bc9fe324-309b-45ea-a2a9-efd62d7ce31c	Tricia Valencia	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer12@example.com	\N	customer	1961-03-23	t	t	\N	\N	unsubmitted	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
ba4586c1-3529-411f-b185-b0319a2ef01b	Melanie Herrera	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer13@example.com	\N	customer	1972-12-20	t	t	DL51462704	\N	pending	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
93021887-e5a8-4858-84c8-d50af662f9c1	Pamela Romero	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer14@example.com	\N	customer	1965-08-04	t	t	DL48932528	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
42b01386-1c6d-4efa-9013-0a035eb2fd6a	Tammy Sellers	$argon2id$v=19$m=65536,t=3,p=4$PJCBGei79vkzXcjsdDPtPQ$ewnHSDijAWVAh/5o00S5BS2Sy2LoRiWbMi3dG27ktLA	customer15@example.com	\N	customer	1988-03-31	t	t	DL70154303	\N	approved	\N	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
\.


--
-- Data for Name: vehicle_categories; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.vehicle_categories (id, name, description, is_active, created_at, updated_at, deleted_at) FROM stdin;
d8a72275-73da-4595-8d30-939f8484bc0b	Economy	Affordable compact cars for city travel.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
a97b9112-a290-44b7-aa5a-543d34a531b8	Sedan	Comfortable cars for business and family trips.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
c2254a41-fd23-4a67-8cf1-addf981e6238	SUV	Spacious vehicles for longer trips.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
5e687951-d3a7-4017-ae58-233d2e9a6f14	Luxury	Premium vehicles for a comfortable experience.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
d311d891-75e5-40a1-89f6-802d56aeadf6	Van / Minivan	Large vehicles suitable for groups and families.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
6a968f35-5d95-4e82-a31a-2cfabc15d202	Pickup Truck	Utility vehicles for cargo and heavy loads.	t	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
\.


--
-- Data for Name: vehicle_images; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.vehicle_images (id, vehicle_id, image_url, sort_order, created_at) FROM stdin;
44c6e072-7f03-4fa2-baa0-26096cafc7ab	ca542f20-1e35-4519-8945-baeced30da36	https://picsum.photos/seed/ca542f20-1e35-4519-8945-baeced30da36-0/800/600	0	2026-09-12 15:57:29.168135+00
862ec4a4-4571-4ace-ad2d-69fd7d75b1fa	ca542f20-1e35-4519-8945-baeced30da36	https://picsum.photos/seed/ca542f20-1e35-4519-8945-baeced30da36-1/800/600	1	2026-09-12 15:57:29.168135+00
9823c80a-863f-4bba-a19e-122d12b8726e	1960b30d-633d-4913-9cb8-bcd7a77b9766	https://picsum.photos/seed/1960b30d-633d-4913-9cb8-bcd7a77b9766-0/800/600	0	2026-09-12 15:57:29.168135+00
e553b8de-5102-44ff-841a-dd0dfe38327e	1960b30d-633d-4913-9cb8-bcd7a77b9766	https://picsum.photos/seed/1960b30d-633d-4913-9cb8-bcd7a77b9766-1/800/600	1	2026-09-12 15:57:29.168135+00
96a74089-fc6b-4403-80fa-f438c26154c6	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	https://picsum.photos/seed/1a855de9-1784-4a2d-a5fe-b05e2e3476b9-0/800/600	0	2026-09-12 15:57:29.168135+00
d00bdb6a-920e-43ee-86e3-babd46973e63	1a855de9-1784-4a2d-a5fe-b05e2e3476b9	https://picsum.photos/seed/1a855de9-1784-4a2d-a5fe-b05e2e3476b9-1/800/600	1	2026-09-12 15:57:29.168135+00
c882f8df-23be-4a58-90fe-2627d56790d8	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	https://picsum.photos/seed/5d3be2f4-7f58-4e6f-917c-66a53fbb8747-0/800/600	0	2026-09-12 15:57:29.168135+00
a61b4753-f59a-4023-b780-2692198bdbbd	5d3be2f4-7f58-4e6f-917c-66a53fbb8747	https://picsum.photos/seed/5d3be2f4-7f58-4e6f-917c-66a53fbb8747-1/800/600	1	2026-09-12 15:57:29.168135+00
736496df-9a2f-4647-840b-88513dd6bf45	f8e767a7-56a9-4614-abcc-b9071c4e971d	https://picsum.photos/seed/f8e767a7-56a9-4614-abcc-b9071c4e971d-0/800/600	0	2026-09-12 15:57:29.168135+00
d4e9a106-a478-4aaf-a9b9-d06522b20e31	f8e767a7-56a9-4614-abcc-b9071c4e971d	https://picsum.photos/seed/f8e767a7-56a9-4614-abcc-b9071c4e971d-1/800/600	1	2026-09-12 15:57:29.168135+00
d80bb35a-b01e-40d2-ac96-5e0c3c76a14c	d68e56a3-b121-4178-b5c8-a6666534fb53	https://picsum.photos/seed/d68e56a3-b121-4178-b5c8-a6666534fb53-0/800/600	0	2026-09-12 15:57:29.168135+00
ae91eefd-653f-4f57-ae12-cd9d793655c8	d68e56a3-b121-4178-b5c8-a6666534fb53	https://picsum.photos/seed/d68e56a3-b121-4178-b5c8-a6666534fb53-1/800/600	1	2026-09-12 15:57:29.168135+00
a209d025-115e-4a90-83d7-5b720d57e939	f0d29664-cfae-48f4-b20f-6d6c538ee82e	https://picsum.photos/seed/f0d29664-cfae-48f4-b20f-6d6c538ee82e-0/800/600	0	2026-09-12 15:57:29.168135+00
2eff6f9a-4e73-4a63-bcb9-608ae6b3c2b5	f0d29664-cfae-48f4-b20f-6d6c538ee82e	https://picsum.photos/seed/f0d29664-cfae-48f4-b20f-6d6c538ee82e-1/800/600	1	2026-09-12 15:57:29.168135+00
57347fda-7c2e-47f0-ac81-d5827e126c0d	f1d03864-52d1-4b39-934d-710e78421c7d	https://picsum.photos/seed/f1d03864-52d1-4b39-934d-710e78421c7d-0/800/600	0	2026-09-12 15:57:29.168135+00
db7a2091-d9da-42fc-87c8-561446ffe007	f1d03864-52d1-4b39-934d-710e78421c7d	https://picsum.photos/seed/f1d03864-52d1-4b39-934d-710e78421c7d-1/800/600	1	2026-09-12 15:57:29.168135+00
8cb97e07-c415-425a-b028-423e3ad4d82f	0a415e85-8bfa-4336-85a4-469a257e2718	https://picsum.photos/seed/0a415e85-8bfa-4336-85a4-469a257e2718-0/800/600	0	2026-09-12 15:57:29.168135+00
97cfca9d-aa66-4bf0-b42e-abb988fd0e58	0a415e85-8bfa-4336-85a4-469a257e2718	https://picsum.photos/seed/0a415e85-8bfa-4336-85a4-469a257e2718-1/800/600	1	2026-09-12 15:57:29.168135+00
3a9207a6-54c9-42f2-8666-6809fa221fbc	1dbbf574-4b28-4183-a6f2-86feab15bdb4	https://picsum.photos/seed/1dbbf574-4b28-4183-a6f2-86feab15bdb4-0/800/600	0	2026-09-12 15:57:29.168135+00
5411332b-f88f-4b7f-bbc7-5761048794c7	1dbbf574-4b28-4183-a6f2-86feab15bdb4	https://picsum.photos/seed/1dbbf574-4b28-4183-a6f2-86feab15bdb4-1/800/600	1	2026-09-12 15:57:29.168135+00
54702aed-ab47-431c-bb0c-925ec4e0e931	37ce3599-55c5-4d3c-9603-7e8761f8a17a	https://picsum.photos/seed/37ce3599-55c5-4d3c-9603-7e8761f8a17a-0/800/600	0	2026-09-12 15:57:29.168135+00
c3e2fe81-f32e-45e5-a7c4-509495b8e7e3	37ce3599-55c5-4d3c-9603-7e8761f8a17a	https://picsum.photos/seed/37ce3599-55c5-4d3c-9603-7e8761f8a17a-1/800/600	1	2026-09-12 15:57:29.168135+00
90e56fab-6b92-4c52-aa21-a7b9286048e7	117ae621-9e98-4017-aa16-91125ae20555	https://picsum.photos/seed/117ae621-9e98-4017-aa16-91125ae20555-0/800/600	0	2026-09-12 15:57:29.168135+00
59ad6520-bbd5-4643-99c5-540b5107aee3	117ae621-9e98-4017-aa16-91125ae20555	https://picsum.photos/seed/117ae621-9e98-4017-aa16-91125ae20555-1/800/600	1	2026-09-12 15:57:29.168135+00
2a4a8630-c25c-4ebe-bcba-a974079d5eb1	e9b26501-a85d-415d-a03e-c14eb4df584c	https://picsum.photos/seed/e9b26501-a85d-415d-a03e-c14eb4df584c-0/800/600	0	2026-09-12 15:57:29.168135+00
2ee4456e-2024-4e06-927b-04d036fc61b9	e9b26501-a85d-415d-a03e-c14eb4df584c	https://picsum.photos/seed/e9b26501-a85d-415d-a03e-c14eb4df584c-1/800/600	1	2026-09-12 15:57:29.168135+00
ad1b1c23-f067-431b-ab80-1ecdb0c8f9b2	b84fb40f-c174-4c62-919c-43f35408b439	https://picsum.photos/seed/b84fb40f-c174-4c62-919c-43f35408b439-0/800/600	0	2026-09-12 15:57:29.168135+00
80f6cf2d-1274-4467-b2a1-8dc320a7a609	b84fb40f-c174-4c62-919c-43f35408b439	https://picsum.photos/seed/b84fb40f-c174-4c62-919c-43f35408b439-1/800/600	1	2026-09-12 15:57:29.168135+00
0adf45eb-340f-4bf9-8df0-6ffd5e0bb614	16071b39-2c5c-4330-a772-7d1043dd6609	https://picsum.photos/seed/16071b39-2c5c-4330-a772-7d1043dd6609-0/800/600	0	2026-09-12 15:57:29.168135+00
13f13c55-552a-47c9-9fff-cbd944ad4730	16071b39-2c5c-4330-a772-7d1043dd6609	https://picsum.photos/seed/16071b39-2c5c-4330-a772-7d1043dd6609-1/800/600	1	2026-09-12 15:57:29.168135+00
19612c77-92fe-4714-a158-cd9b1772b2b2	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	https://picsum.photos/seed/6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea-0/800/600	0	2026-09-12 15:57:29.168135+00
d263b0ce-1264-4123-bedd-97c05b889c1f	6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	https://picsum.photos/seed/6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea-1/800/600	1	2026-09-12 15:57:29.168135+00
5cc354f9-3b90-4b4a-8fa3-36e13fd79140	9b9f442d-1e22-44a0-89b2-dfe494d670d4	https://picsum.photos/seed/9b9f442d-1e22-44a0-89b2-dfe494d670d4-0/800/600	0	2026-09-12 15:57:29.168135+00
b898cee5-4b1a-4014-9cdc-d41ec86d8e25	9b9f442d-1e22-44a0-89b2-dfe494d670d4	https://picsum.photos/seed/9b9f442d-1e22-44a0-89b2-dfe494d670d4-1/800/600	1	2026-09-12 15:57:29.168135+00
7f1c8311-eb76-41b9-aea1-a3a8ab25b709	fd6eb2d7-d6f0-4931-851b-a489ba528a95	https://picsum.photos/seed/fd6eb2d7-d6f0-4931-851b-a489ba528a95-0/800/600	0	2026-09-12 15:57:29.168135+00
0b2ea6a2-0def-46b2-b660-d56a8537564e	fd6eb2d7-d6f0-4931-851b-a489ba528a95	https://picsum.photos/seed/fd6eb2d7-d6f0-4931-851b-a489ba528a95-1/800/600	1	2026-09-12 15:57:29.168135+00
d4c34306-0e5e-48a9-8f50-e3ddff425f30	39e0155f-af8f-4c38-9a21-969b460b5b4d	https://picsum.photos/seed/39e0155f-af8f-4c38-9a21-969b460b5b4d-0/800/600	0	2026-09-12 15:57:29.168135+00
077baedf-4bcd-4b25-9a02-955ad41fab83	39e0155f-af8f-4c38-9a21-969b460b5b4d	https://picsum.photos/seed/39e0155f-af8f-4c38-9a21-969b460b5b4d-1/800/600	1	2026-09-12 15:57:29.168135+00
cfef8e37-ccd9-4ddb-b1e1-8bd8482ccad4	9cb83739-0b36-41b1-ab4f-c766eb73211b	https://picsum.photos/seed/9cb83739-0b36-41b1-ab4f-c766eb73211b-0/800/600	0	2026-09-12 15:57:29.168135+00
aa6c8d1c-2870-4168-ab87-3e1a3d86270a	9cb83739-0b36-41b1-ab4f-c766eb73211b	https://picsum.photos/seed/9cb83739-0b36-41b1-ab4f-c766eb73211b-1/800/600	1	2026-09-12 15:57:29.168135+00
\.


--
-- Data for Name: vehicles; Type: TABLE DATA; Schema: public; Owner: diseuser
--

COPY public.vehicles (id, category_id, location_id, owner_id, make, model, year, license_plate, transmission, fuel_type, seats, daily_rate, currency, deposit_amount, requires_approval, status, odometer_km, created_at, updated_at, deleted_at) FROM stdin;
ca542f20-1e35-4519-8945-baeced30da36	d8a72275-73da-4595-8d30-939f8484bc0b	7f4ed45c-31a1-447a-a8b5-94999d854d4d	\N	Nissan	X-Trail	2022	DHA-6311	manual	petrol	5	9000.00	BDT	5000.00	t	available	11328	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1960b30d-633d-4913-9cb8-bcd7a77b9766	c2254a41-fd23-4a67-8cf1-addf981e6238	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	\N	Hyundai	Tucson	2022	DHA-6566	automatic	petrol	4	2500.00	BDT	15000.00	f	available	31512	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1a855de9-1784-4a2d-a5fe-b05e2e3476b9	d8a72275-73da-4595-8d30-939f8484bc0b	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	\N	Suzuki	Ertiga	2021	DHA-7010	manual	hybrid	5	3500.00	BDT	15000.00	f	available	35993	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
5d3be2f4-7f58-4e6f-917c-66a53fbb8747	6a968f35-5d95-4e82-a31a-2cfabc15d202	794cec6a-a6df-4f8a-84be-a742b517aefc	\N	Mercedes-Benz	E-Class	2019	DHA-6513	automatic	diesel	5	5000.00	BDT	15000.00	f	available	43504	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
f8e767a7-56a9-4614-abcc-b9071c4e971d	d8a72275-73da-4595-8d30-939f8484bc0b	5171f2c2-2581-4f20-b3f7-331896669bd2	\N	Suzuki	Ertiga	2017	DHA-3387	manual	electric	5	1800.00	BDT	10000.00	f	available	28869	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
d68e56a3-b121-4178-b5c8-a6666534fb53	5e687951-d3a7-4017-ae58-233d2e9a6f14	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	\N	BMW	5 Series	2024	DHA-2624	automatic	hybrid	5	2500.00	BDT	15000.00	t	available	77484	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
f0d29664-cfae-48f4-b20f-6d6c538ee82e	c2254a41-fd23-4a67-8cf1-addf981e6238	5171f2c2-2581-4f20-b3f7-331896669bd2	\N	Nissan	X-Trail	2019	DHA-7317	manual	petrol	4	1800.00	BDT	10000.00	f	available	56333	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
f1d03864-52d1-4b39-934d-710e78421c7d	d8a72275-73da-4595-8d30-939f8484bc0b	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	\N	Mitsubishi	Pajero	2023	DHA-8108	manual	hybrid	7	1500.00	BDT	5000.00	f	available	45587	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
0a415e85-8bfa-4336-85a4-469a257e2718	c2254a41-fd23-4a67-8cf1-addf981e6238	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	\N	Toyota	Premio	2019	DHA-0132	manual	petrol	5	9000.00	BDT	10000.00	f	available	40117	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
1dbbf574-4b28-4183-a6f2-86feab15bdb4	6a968f35-5d95-4e82-a31a-2cfabc15d202	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	\N	Suzuki	Ertiga	2020	DHA-6773	automatic	hybrid	5	9000.00	BDT	5000.00	f	available	65042	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
37ce3599-55c5-4d3c-9603-7e8761f8a17a	d8a72275-73da-4595-8d30-939f8484bc0b	7f4ed45c-31a1-447a-a8b5-94999d854d4d	\N	Toyota	Corolla	2021	DHA-6026	automatic	petrol	5	1800.00	BDT	5000.00	t	available	10071	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
117ae621-9e98-4017-aa16-91125ae20555	d311d891-75e5-40a1-89f6-802d56aeadf6	5171f2c2-2581-4f20-b3f7-331896669bd2	\N	Suzuki	Alto	2019	DHA-0647	manual	diesel	5	9000.00	BDT	20000.00	f	available	71686	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
e9b26501-a85d-415d-a03e-c14eb4df584c	6a968f35-5d95-4e82-a31a-2cfabc15d202	5171f2c2-2581-4f20-b3f7-331896669bd2	\N	Suzuki	Alto	2021	DHA-4687	manual	hybrid	5	9000.00	BDT	20000.00	f	available	33493	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
b84fb40f-c174-4c62-919c-43f35408b439	d8a72275-73da-4595-8d30-939f8484bc0b	7f4ed45c-31a1-447a-a8b5-94999d854d4d	\N	Honda	Civic	2017	DHA-2343	automatic	diesel	4	1800.00	BDT	5000.00	f	available	9834	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
16071b39-2c5c-4330-a772-7d1043dd6609	c2254a41-fd23-4a67-8cf1-addf981e6238	794cec6a-a6df-4f8a-84be-a742b517aefc	\N	Toyota	Corolla	2025	DHA-0980	automatic	hybrid	5	2500.00	BDT	10000.00	t	available	32850	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
6a7d1d9a-6c24-448a-ac20-20a7c5a9fbea	5e687951-d3a7-4017-ae58-233d2e9a6f14	44da8e10-b7fb-4d09-a0d8-e282b1d30f13	\N	Suzuki	Alto	2020	DHA-5009	automatic	petrol	5	3500.00	BDT	20000.00	t	available	62213	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
9b9f442d-1e22-44a0-89b2-dfe494d670d4	6a968f35-5d95-4e82-a31a-2cfabc15d202	794cec6a-a6df-4f8a-84be-a742b517aefc	\N	Suzuki	Ertiga	2018	DHA-7882	automatic	electric	5	1800.00	BDT	10000.00	f	available	25931	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
fd6eb2d7-d6f0-4931-851b-a489ba528a95	5e687951-d3a7-4017-ae58-233d2e9a6f14	5171f2c2-2581-4f20-b3f7-331896669bd2	\N	Hyundai	Tucson	2023	DHA-0812	automatic	hybrid	5	2500.00	BDT	5000.00	t	available	73132	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
39e0155f-af8f-4c38-9a21-969b460b5b4d	d8a72275-73da-4595-8d30-939f8484bc0b	9bb32bf8-28d7-44d6-9e04-2bd89ef676f9	\N	Toyota	Premio	2017	DHA-1913	automatic	diesel	5	5000.00	BDT	20000.00	t	available	29016	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
9cb83739-0b36-41b1-ab4f-c766eb73211b	5e687951-d3a7-4017-ae58-233d2e9a6f14	794cec6a-a6df-4f8a-84be-a742b517aefc	\N	Suzuki	Ertiga	2019	DHA-6193	manual	petrol	5	3000.00	BDT	20000.00	f	available	56444	2026-09-12 15:57:29.168135+00	2026-09-12 15:57:29.168135+00	\N
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_id_key UNIQUE (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: booking_status_history booking_status_history_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.booking_status_history
    ADD CONSTRAINT booking_status_history_id_key UNIQUE (id);


--
-- Name: booking_status_history booking_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.booking_status_history
    ADD CONSTRAINT booking_status_history_pkey PRIMARY KEY (id);


--
-- Name: bookings bookings_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_id_key UNIQUE (id);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: condition_report_images condition_report_images_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_report_images
    ADD CONSTRAINT condition_report_images_id_key UNIQUE (id);


--
-- Name: condition_report_images condition_report_images_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_report_images
    ADD CONSTRAINT condition_report_images_pkey PRIMARY KEY (id);


--
-- Name: condition_reports condition_reports_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_reports
    ADD CONSTRAINT condition_reports_id_key UNIQUE (id);


--
-- Name: condition_reports condition_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_reports
    ADD CONSTRAINT condition_reports_pkey PRIMARY KEY (id);


--
-- Name: coupon_usages coupon_usages_booking_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_booking_id_key UNIQUE (booking_id);


--
-- Name: coupon_usages coupon_usages_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_id_key UNIQUE (id);


--
-- Name: coupon_usages coupon_usages_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_pkey PRIMARY KEY (id);


--
-- Name: coupons coupons_code_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_code_key UNIQUE (code);


--
-- Name: coupons coupons_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_id_key UNIQUE (id);


--
-- Name: coupons coupons_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupons
    ADD CONSTRAINT coupons_pkey PRIMARY KEY (id);


--
-- Name: maintenance_blocks excl_no_overlap_maintenance; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.maintenance_blocks
    ADD CONSTRAINT excl_no_overlap_maintenance EXCLUDE USING gist (vehicle_id WITH =, daterange(start_date, end_date, '[)'::text) WITH &&);


--
-- Name: bookings excl_no_overlapping_confirmed_bookings; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT excl_no_overlapping_confirmed_bookings EXCLUDE USING gist (vehicle_id WITH =, daterange(start_date, end_date, '[)'::text) WITH &&) WHERE (((status = ANY (ARRAY['confirmed'::public.bookingstatus, 'active'::public.bookingstatus])) AND (deleted_at IS NULL)));


--
-- Name: locations locations_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_id_key UNIQUE (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: maintenance_blocks maintenance_blocks_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.maintenance_blocks
    ADD CONSTRAINT maintenance_blocks_id_key UNIQUE (id);


--
-- Name: maintenance_blocks maintenance_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.maintenance_blocks
    ADD CONSTRAINT maintenance_blocks_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_id_key UNIQUE (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: payments payments_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_id_key UNIQUE (id);


--
-- Name: payments payments_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: payments payments_stripe_payment_intent_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_stripe_payment_intent_id_key UNIQUE (stripe_payment_intent_id);


--
-- Name: refund_policy_tiers refund_policy_tiers_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.refund_policy_tiers
    ADD CONSTRAINT refund_policy_tiers_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_booking_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_booking_id_key UNIQUE (booking_id);


--
-- Name: reviews reviews_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_id_key UNIQUE (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: users users_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_key UNIQUE (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_stripe_customer_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_stripe_customer_id_key UNIQUE (stripe_customer_id);


--
-- Name: vehicle_categories vehicle_categories_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_categories
    ADD CONSTRAINT vehicle_categories_id_key UNIQUE (id);


--
-- Name: vehicle_categories vehicle_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_categories
    ADD CONSTRAINT vehicle_categories_name_key UNIQUE (name);


--
-- Name: vehicle_categories vehicle_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_categories
    ADD CONSTRAINT vehicle_categories_pkey PRIMARY KEY (id);


--
-- Name: vehicle_images vehicle_images_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_images
    ADD CONSTRAINT vehicle_images_id_key UNIQUE (id);


--
-- Name: vehicle_images vehicle_images_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_images
    ADD CONSTRAINT vehicle_images_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_id_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_id_key UNIQUE (id);


--
-- Name: vehicles vehicles_license_plate_key; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_license_plate_key UNIQUE (license_plate);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_entity; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_audit_entity ON public.audit_logs USING btree (entity_type, entity_id);


--
-- Name: idx_bookings_vehicle_dates; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_bookings_vehicle_dates ON public.bookings USING btree (vehicle_id, start_date, end_date);


--
-- Name: idx_reviews_vehicle; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_reviews_vehicle ON public.reviews USING btree (vehicle_id);


--
-- Name: idx_users_active; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_users_active ON public.users USING btree (is_active) WHERE (deleted_at IS NULL);


--
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_users_role ON public.users USING btree (role) WHERE (deleted_at IS NULL);


--
-- Name: idx_vehicles_category; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_vehicles_category ON public.vehicles USING btree (category_id);


--
-- Name: idx_vehicles_location_status; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX idx_vehicles_location_status ON public.vehicles USING btree (location_id, status) WHERE (deleted_at IS NULL);


--
-- Name: ix_audit_logs_actor_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_audit_logs_actor_id ON public.audit_logs USING btree (actor_id);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_booking_status_history_booking_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_booking_status_history_booking_id ON public.booking_status_history USING btree (booking_id);


--
-- Name: ix_bookings_customer_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_bookings_customer_id ON public.bookings USING btree (customer_id);


--
-- Name: ix_bookings_status; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_bookings_status ON public.bookings USING btree (status);


--
-- Name: ix_bookings_vehicle_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_bookings_vehicle_id ON public.bookings USING btree (vehicle_id);


--
-- Name: ix_condition_report_images_condition_report_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_condition_report_images_condition_report_id ON public.condition_report_images USING btree (condition_report_id);


--
-- Name: ix_condition_reports_booking_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_condition_reports_booking_id ON public.condition_reports USING btree (booking_id);


--
-- Name: ix_coupon_usages_coupon_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_coupon_usages_coupon_id ON public.coupon_usages USING btree (coupon_id);


--
-- Name: ix_coupon_usages_customer_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_coupon_usages_customer_id ON public.coupon_usages USING btree (customer_id);


--
-- Name: ix_locations_city; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_locations_city ON public.locations USING btree (city);


--
-- Name: ix_maintenance_blocks_vehicle_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_maintenance_blocks_vehicle_id ON public.maintenance_blocks USING btree (vehicle_id);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_payments_booking_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_payments_booking_id ON public.payments USING btree (booking_id);


--
-- Name: ix_payments_status; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_payments_status ON public.payments USING btree (status);


--
-- Name: ix_reviews_customer_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_reviews_customer_id ON public.reviews USING btree (customer_id);


--
-- Name: ix_reviews_vehicle_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_reviews_vehicle_id ON public.reviews USING btree (vehicle_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: ix_vehicle_images_vehicle_id; Type: INDEX; Schema: public; Owner: diseuser
--

CREATE INDEX ix_vehicle_images_vehicle_id ON public.vehicle_images USING btree (vehicle_id);


--
-- Name: audit_logs audit_logs_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: booking_status_history booking_status_history_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.booking_status_history
    ADD CONSTRAINT booking_status_history_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: booking_status_history booking_status_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.booking_status_history
    ADD CONSTRAINT booking_status_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: bookings bookings_coupon_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_coupon_id_fkey FOREIGN KEY (coupon_id) REFERENCES public.coupons(id) ON DELETE SET NULL;


--
-- Name: bookings bookings_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_dropoff_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_dropoff_location_id_fkey FOREIGN KEY (dropoff_location_id) REFERENCES public.locations(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_pickup_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pickup_location_id_fkey FOREIGN KEY (pickup_location_id) REFERENCES public.locations(id) ON DELETE RESTRICT;


--
-- Name: bookings bookings_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE RESTRICT;


--
-- Name: condition_report_images condition_report_images_condition_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_report_images
    ADD CONSTRAINT condition_report_images_condition_report_id_fkey FOREIGN KEY (condition_report_id) REFERENCES public.condition_reports(id) ON DELETE CASCADE;


--
-- Name: condition_reports condition_reports_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_reports
    ADD CONSTRAINT condition_reports_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: condition_reports condition_reports_recorded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.condition_reports
    ADD CONSTRAINT condition_reports_recorded_by_fkey FOREIGN KEY (recorded_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: coupon_usages coupon_usages_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: coupon_usages coupon_usages_coupon_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_coupon_id_fkey FOREIGN KEY (coupon_id) REFERENCES public.coupons(id) ON DELETE CASCADE;


--
-- Name: coupon_usages coupon_usages_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.coupon_usages
    ADD CONSTRAINT coupon_usages_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: maintenance_blocks maintenance_blocks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.maintenance_blocks
    ADD CONSTRAINT maintenance_blocks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: maintenance_blocks maintenance_blocks_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.maintenance_blocks
    ADD CONSTRAINT maintenance_blocks_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payments payments_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE RESTRICT;


--
-- Name: reviews reviews_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id) ON DELETE CASCADE;


--
-- Name: reviews reviews_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: reviews reviews_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicle_images vehicle_images_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicle_images
    ADD CONSTRAINT vehicle_images_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicles vehicles_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.vehicle_categories(id) ON DELETE RESTRICT;


--
-- Name: vehicles vehicles_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE RESTRICT;


--
-- Name: vehicles vehicles_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: diseuser
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict RMi34VPTgKLAH2eDbZdCvRlAv2D7hTgdiL0AhUUbwpTrGX6tgFE3GCYvpmd0Q1c

