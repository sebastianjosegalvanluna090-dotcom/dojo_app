--
-- PostgreSQL database dump
--

\restrict hNVXqQMomN8AnxegrRBCeBDXnPOZZCCf4OoFKSepCh951IKrWlkcwgKcc54XA7D

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-08-13 10:25:28

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 362 (class 1255 OID 25083)
-- Name: fn_expense_insert_movement(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_expense_insert_movement() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

    INSERT INTO account_movements (
        id_destination_account,
        id_movement_type,
        amount,
        payment_date
    )
    VALUES (
        NEW.id_destination_account,
        1,
        NEW.amount,
        NEW.expense_date
    );

    RETURN NEW;

END;
$$;


ALTER FUNCTION public.fn_expense_insert_movement() OWNER TO postgres;

--
-- TOC entry 363 (class 1255 OID 25081)
-- Name: fn_payment_insert_movement(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_payment_insert_movement() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN

    INSERT INTO account_movements (
        id_destination_account,
        id_movement_type,
        amount,
        payment_date,
        reference_table,
        reference_id
    )
    VALUES (
        NEW.id_destination_account,
        2,
        NEW.total_paid,
        NEW.payment_date,
        'payments',
        NEW.id
    );

    RETURN NEW;

END;
$$;


ALTER FUNCTION public.fn_payment_insert_movement() OWNER TO postgres;

--
-- TOC entry 360 (class 1255 OID 24851)
-- Name: fn_students_belts_insert(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_students_belts_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO students_belts_history (
        id_student,
        id_belt,
        action,
        date_changed
    )
    VALUES (
        NEW.id_student,
        NEW.id_belt,
        'asignacion inicial',
        CURRENT_TIMESTAMP
    );

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_students_belts_insert() OWNER TO postgres;

--
-- TOC entry 361 (class 1255 OID 24853)
-- Name: fn_students_belts_update(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_students_belts_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Solo registrar si hay cambio real de cinturón
    IF OLD.id_belt <> NEW.id_belt THEN
        
        INSERT INTO students_belts_history (
            id_student,
            id_belt,
            action,
            date_changed
        )
        VALUES (
            NEW.id_student,
            NEW.id_belt,
            'promocion',
            CURRENT_TIMESTAMP
        );

    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_students_belts_update() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 271 (class 1259 OID 25059)
-- Name: account_movements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.account_movements (
    id integer NOT NULL,
    id_destination_account integer NOT NULL,
    id_movement_type integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.account_movements OWNER TO postgres;

--
-- TOC entry 270 (class 1259 OID 25058)
-- Name: account_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.account_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.account_movements_id_seq OWNER TO postgres;

--
-- TOC entry 6092 (class 0 OID 0)
-- Dependencies: 270
-- Name: account_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.account_movements_id_seq OWNED BY public.account_movements.id;


--
-- TOC entry 247 (class 1259 OID 24831)
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    id_class integer,
    id_student integer,
    status character varying(30) DEFAULT 'present'::character varying,
    check_in_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    note text,
    is_admin_override boolean DEFAULT false NOT NULL,
    override_user_id integer,
    override_reason text,
    CONSTRAINT chk_attendance_override_data CHECK (((is_admin_override = false) OR ((override_user_id IS NOT NULL) AND (NULLIF(btrim(override_reason), ''::text) IS NOT NULL))))
);


ALTER TABLE public.attendance OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 24830)
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_id_seq OWNER TO postgres;

--
-- TOC entry 6093 (class 0 OID 0)
-- Dependencies: 246
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- TOC entry 285 (class 1259 OID 32846)
-- Name: belt_requirements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.belt_requirements (
    id integer NOT NULL,
    belt_id integer,
    requirement text NOT NULL,
    id_type_requeriments integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.belt_requirements OWNER TO postgres;

--
-- TOC entry 284 (class 1259 OID 32845)
-- Name: belt_requirements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.belt_requirements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.belt_requirements_id_seq OWNER TO postgres;

--
-- TOC entry 6094 (class 0 OID 0)
-- Dependencies: 284
-- Name: belt_requirements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.belt_requirements_id_seq OWNED BY public.belt_requirements.id;


--
-- TOC entry 228 (class 1259 OID 24614)
-- Name: belts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.belts (
    id bigint NOT NULL,
    name character varying(75) NOT NULL,
    id_martial_art integer NOT NULL,
    orden integer NOT NULL,
    color character varying(20),
    pre_color character varying(20),
    grades integer DEFAULT 0,
    grade_color character varying(20) DEFAULT '#FFFFFF'::character varying,
    level_type character varying(40) DEFAULT 'belt'::character varying,
    icon_key character varying(60),
    is_initial boolean DEFAULT false NOT NULL,
    is_final boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    display_name character varying(100),
    metadata jsonb DEFAULT '{}'::jsonb,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    minimum_age integer,
    maximum_age integer,
    age_restriction_note character varying(250),
    CONSTRAINT belts_age_range_check CHECK (((minimum_age IS NULL) OR (maximum_age IS NULL) OR (maximum_age >= minimum_age))),
    CONSTRAINT belts_maximum_age_check CHECK (((maximum_age IS NULL) OR (maximum_age >= 0))),
    CONSTRAINT belts_minimum_age_check CHECK (((minimum_age IS NULL) OR (minimum_age >= 0)))
);


ALTER TABLE public.belts OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 24613)
-- Name: belts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.belts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.belts_id_seq OWNER TO postgres;

--
-- TOC entry 6095 (class 0 OID 0)
-- Dependencies: 227
-- Name: belts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.belts_id_seq OWNED BY public.belts.id;


--
-- TOC entry 224 (class 1259 OID 24587)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id bigint NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 24586)
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- TOC entry 6096 (class 0 OID 0)
-- Dependencies: 223
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- TOC entry 245 (class 1259 OID 24808)
-- Name: classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    id_schedule integer,
    id_instructor integer,
    date date,
    status character varying(30) DEFAULT 'scheduled'::character varying,
    note text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    guest_count integer DEFAULT 0 NOT NULL,
    guest_names character varying(500),
    CONSTRAINT chk_classes_guest_count_nonnegative CHECK ((guest_count >= 0))
);


ALTER TABLE public.classes OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 24807)
-- Name: classes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classes_id_seq OWNER TO postgres;

--
-- TOC entry 6097 (class 0 OID 0)
-- Dependencies: 244
-- Name: classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classes_id_seq OWNED BY public.classes.id;


--
-- TOC entry 277 (class 1259 OID 32777)
-- Name: codes_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.codes_users (
    id bigint NOT NULL,
    code text NOT NULL,
    id_role integer NOT NULL
);


ALTER TABLE public.codes_users OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 32776)
-- Name: codes_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.codes_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.codes_users_id_seq OWNER TO postgres;

--
-- TOC entry 6098 (class 0 OID 0)
-- Dependencies: 276
-- Name: codes_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.codes_users_id_seq OWNED BY public.codes_users.id;


--
-- TOC entry 337 (class 1259 OID 41651)
-- Name: collection_account_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_account_items (
    id integer CONSTRAINT collection_account_items_id_not_null1 NOT NULL,
    collection_account_id integer,
    activity_type character varying(50),
    description text NOT NULL,
    quantity numeric(8,2) DEFAULT 1,
    unit_price numeric(12,2) DEFAULT 0,
    subtotal numeric(12,2) DEFAULT 0,
    activity_date date,
    penalty boolean DEFAULT false
);


ALTER TABLE public.collection_account_items OWNER TO postgres;

--
-- TOC entry 329 (class 1259 OID 41550)
-- Name: collection_account_items_old; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_account_items_old (
    id integer CONSTRAINT collection_account_items_id_not_null NOT NULL,
    account_id integer CONSTRAINT collection_account_items_account_id_not_null NOT NULL,
    name character varying(180) CONSTRAINT collection_account_items_name_not_null NOT NULL,
    description text DEFAULT ''::text,
    quantity integer DEFAULT 1 CONSTRAINT collection_account_items_quantity_not_null NOT NULL,
    unit_price numeric(12,2) DEFAULT 0 CONSTRAINT collection_account_items_unit_price_not_null NOT NULL,
    discount numeric(12,2) DEFAULT 0 CONSTRAINT collection_account_items_discount_not_null NOT NULL,
    subtotal numeric(12,2) DEFAULT 0 CONSTRAINT collection_account_items_subtotal_not_null NOT NULL
);


ALTER TABLE public.collection_account_items_old OWNER TO postgres;

--
-- TOC entry 328 (class 1259 OID 41549)
-- Name: collection_account_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_account_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_account_items_id_seq OWNER TO postgres;

--
-- TOC entry 6099 (class 0 OID 0)
-- Dependencies: 328
-- Name: collection_account_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_account_items_id_seq OWNED BY public.collection_account_items_old.id;


--
-- TOC entry 336 (class 1259 OID 41650)
-- Name: collection_account_items_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_account_items_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_account_items_id_seq1 OWNER TO postgres;

--
-- TOC entry 6100 (class 0 OID 0)
-- Dependencies: 336
-- Name: collection_account_items_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_account_items_id_seq1 OWNED BY public.collection_account_items.id;


--
-- TOC entry 335 (class 1259 OID 41625)
-- Name: collection_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_accounts (
    id integer CONSTRAINT collection_accounts_id_not_null1 NOT NULL,
    person_id integer,
    person_name character varying(200),
    concept text NOT NULL,
    total_amount numeric(12,2) DEFAULT 0 NOT NULL,
    status character varying(30) DEFAULT '''draft'''::character varying,
    due_date date,
    issued_date date DEFAULT CURRENT_DATE,
    notes text,
    scholarship_id integer,
    period_month integer,
    period_year integer,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.collection_accounts OWNER TO postgres;

--
-- TOC entry 327 (class 1259 OID 41515)
-- Name: collection_accounts_old; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_accounts_old (
    id integer CONSTRAINT collection_accounts_id_not_null NOT NULL,
    client_name character varying(180) CONSTRAINT collection_accounts_client_name_not_null NOT NULL,
    client_person_id integer,
    client_document character varying(50) DEFAULT ''::character varying,
    client_email character varying(150) DEFAULT ''::character varying,
    client_phone character varying(50) DEFAULT ''::character varying,
    account_date date DEFAULT CURRENT_DATE CONSTRAINT collection_accounts_account_date_not_null NOT NULL,
    due_date date,
    subtotal numeric(12,2) DEFAULT 0 CONSTRAINT collection_accounts_subtotal_not_null NOT NULL,
    scholarship_id integer,
    scholarship_discount numeric(12,2) DEFAULT 0 CONSTRAINT collection_accounts_scholarship_discount_not_null NOT NULL,
    total numeric(12,2) DEFAULT 0 CONSTRAINT collection_accounts_total_not_null NOT NULL,
    total_paid numeric(12,2) DEFAULT 0 CONSTRAINT collection_accounts_total_paid_not_null NOT NULL,
    pending_amount numeric(12,2) DEFAULT 0 CONSTRAINT collection_accounts_pending_amount_not_null NOT NULL,
    status character varying(30) DEFAULT 'pending'::character varying CONSTRAINT collection_accounts_status_not_null NOT NULL,
    note text DEFAULT ''::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.collection_accounts_old OWNER TO postgres;

--
-- TOC entry 326 (class 1259 OID 41514)
-- Name: collection_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_accounts_id_seq OWNER TO postgres;

--
-- TOC entry 6101 (class 0 OID 0)
-- Dependencies: 326
-- Name: collection_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_accounts_id_seq OWNED BY public.collection_accounts_old.id;


--
-- TOC entry 334 (class 1259 OID 41624)
-- Name: collection_accounts_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_accounts_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.collection_accounts_id_seq1 OWNER TO postgres;

--
-- TOC entry 6102 (class 0 OID 0)
-- Dependencies: 334
-- Name: collection_accounts_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_accounts_id_seq1 OWNED BY public.collection_accounts.id;


--
-- TOC entry 253 (class 1259 OID 24878)
-- Name: destination_account; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.destination_account (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    account_number integer NOT NULL
);


ALTER TABLE public.destination_account OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 24877)
-- Name: destination_account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.destination_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.destination_account_id_seq OWNER TO postgres;

--
-- TOC entry 6103 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.destination_account_id_seq OWNED BY public.destination_account.id;


--
-- TOC entry 359 (class 1259 OID 49506)
-- Name: discipline_exercises; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.discipline_exercises (
    id bigint NOT NULL,
    martial_art_id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    exercise_type character varying(60),
    difficulty character varying(30),
    duration_minutes integer,
    sort_order integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    image_path text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_discipline_exercise_duration CHECK (((duration_minutes IS NULL) OR (duration_minutes > 0)))
);


ALTER TABLE public.discipline_exercises OWNER TO postgres;

--
-- TOC entry 358 (class 1259 OID 49505)
-- Name: discipline_exercises_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.discipline_exercises ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.discipline_exercises_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 341 (class 1259 OID 49224)
-- Name: event_followers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_followers (
    id bigint NOT NULL,
    event_id integer NOT NULL,
    user_id integer NOT NULL,
    notifications_enabled boolean DEFAULT true NOT NULL,
    followed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.event_followers OWNER TO postgres;

--
-- TOC entry 340 (class 1259 OID 49223)
-- Name: event_followers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.event_followers ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.event_followers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 343 (class 1259 OID 49251)
-- Name: event_interest; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_interest (
    id bigint NOT NULL,
    event_id integer NOT NULL,
    user_id integer NOT NULL,
    response character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_event_interest_response CHECK (((response)::text = ANY ((ARRAY['interested'::character varying, 'attending'::character varying])::text[])))
);


ALTER TABLE public.event_interest OWNER TO postgres;

--
-- TOC entry 342 (class 1259 OID 49250)
-- Name: event_interest_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.event_interest ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.event_interest_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 349 (class 1259 OID 49339)
-- Name: event_posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_posts (
    id bigint NOT NULL,
    event_id integer NOT NULL,
    author_user_id integer,
    content text NOT NULL,
    image_path text,
    is_pinned boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_event_post_content CHECK ((NULLIF(btrim(content), ''::text) IS NOT NULL))
);


ALTER TABLE public.event_posts OWNER TO postgres;

--
-- TOC entry 348 (class 1259 OID 49338)
-- Name: event_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.event_posts ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.event_posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 345 (class 1259 OID 49278)
-- Name: event_registrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_registrations (
    id bigint NOT NULL,
    event_id integer NOT NULL,
    user_id integer NOT NULL,
    student_id integer,
    registration_status character varying(30) DEFAULT 'pending'::character varying NOT NULL,
    payment_status character varying(30) DEFAULT 'not_required'::character varying NOT NULL,
    notes text,
    registered_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_event_payment_status CHECK (((payment_status)::text = ANY ((ARRAY['not_required'::character varying, 'pending'::character varying, 'partial'::character varying, 'paid'::character varying, 'refunded'::character varying])::text[]))),
    CONSTRAINT chk_event_registration_status CHECK (((registration_status)::text = ANY ((ARRAY['pending'::character varying, 'confirmed'::character varying, 'waitlist'::character varying, 'cancelled'::character varying, 'rejected'::character varying, 'attended'::character varying])::text[])))
);


ALTER TABLE public.event_registrations OWNER TO postgres;

--
-- TOC entry 344 (class 1259 OID 49277)
-- Name: event_registrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.event_registrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.event_registrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 347 (class 1259 OID 49315)
-- Name: event_schedule_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_schedule_items (
    id bigint NOT NULL,
    event_id integer NOT NULL,
    title character varying(180) NOT NULL,
    description text,
    starts_at timestamp without time zone NOT NULL,
    ends_at timestamp without time zone,
    location character varying(160),
    sort_order integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_event_schedule_time CHECK (((ends_at IS NULL) OR (ends_at > starts_at)))
);


ALTER TABLE public.event_schedule_items OWNER TO postgres;

--
-- TOC entry 346 (class 1259 OID 49314)
-- Name: event_schedule_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.event_schedule_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.event_schedule_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 289 (class 1259 OID 40972)
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    event_date date NOT NULL,
    event_type character varying(50),
    description text,
    color character varying(20) DEFAULT '#3B82F6'::character varying,
    start_time time without time zone,
    end_time time without time zone,
    location character varying(120),
    is_important boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    short_description character varying(280),
    organizer_user_id integer,
    martial_art_id integer,
    end_date date,
    venue_name character varying(160),
    address character varying(250),
    city character varying(100),
    country character varying(100),
    cover_image_path text,
    capacity integer,
    registration_deadline timestamp without time zone,
    price numeric(12,2) DEFAULT 0,
    status character varying(30) DEFAULT 'draft'::character varying,
    visibility character varying(30) DEFAULT 'internal'::character varying,
    is_featured boolean DEFAULT false,
    registration_enabled boolean DEFAULT false,
    published_at timestamp without time zone,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_events_capacity CHECK (((capacity IS NULL) OR (capacity > 0))),
    CONSTRAINT chk_events_end_date CHECK (((end_date IS NULL) OR (end_date >= event_date))),
    CONSTRAINT chk_events_price CHECK ((price >= (0)::numeric))
);


ALTER TABLE public.events OWNER TO postgres;

--
-- TOC entry 288 (class 1259 OID 40971)
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.events ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 267 (class 1259 OID 25020)
-- Name: expense_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.expense_categories OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 25019)
-- Name: expense_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expense_categories_id_seq OWNER TO postgres;

--
-- TOC entry 6104 (class 0 OID 0)
-- Dependencies: 266
-- Name: expense_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_categories_id_seq OWNED BY public.expense_categories.id;


--
-- TOC entry 269 (class 1259 OID 25033)
-- Name: expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    id_expense_category integer NOT NULL,
    id_destination_account integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    expense_date date NOT NULL,
    description text,
    invoice_number character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.expenses OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 25032)
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expenses_id_seq OWNER TO postgres;

--
-- TOC entry 6105 (class 0 OID 0)
-- Dependencies: 268
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- TOC entry 315 (class 1259 OID 41366)
-- Name: finance_expense_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_expense_categories (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text DEFAULT ''::text,
    expense_type character varying(20) DEFAULT 'variable'::character varying
);


ALTER TABLE public.finance_expense_categories OWNER TO postgres;

--
-- TOC entry 314 (class 1259 OID 41365)
-- Name: finance_expense_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_expense_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_expense_categories_id_seq OWNER TO postgres;

--
-- TOC entry 6106 (class 0 OID 0)
-- Dependencies: 314
-- Name: finance_expense_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_expense_categories_id_seq OWNED BY public.finance_expense_categories.id;


--
-- TOC entry 321 (class 1259 OID 41427)
-- Name: finance_expense_inventory_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_expense_inventory_items (
    id integer NOT NULL,
    expense_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    total_cost numeric(12,2) NOT NULL
);


ALTER TABLE public.finance_expense_inventory_items OWNER TO postgres;

--
-- TOC entry 320 (class 1259 OID 41426)
-- Name: finance_expense_inventory_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_expense_inventory_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_expense_inventory_items_id_seq OWNER TO postgres;

--
-- TOC entry 6107 (class 0 OID 0)
-- Dependencies: 320
-- Name: finance_expense_inventory_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_expense_inventory_items_id_seq OWNED BY public.finance_expense_inventory_items.id;


--
-- TOC entry 317 (class 1259 OID 41380)
-- Name: finance_expense_subcategories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_expense_subcategories (
    id integer NOT NULL,
    category_id integer NOT NULL,
    name character varying(120) NOT NULL,
    description text DEFAULT ''::text
);


ALTER TABLE public.finance_expense_subcategories OWNER TO postgres;

--
-- TOC entry 316 (class 1259 OID 41379)
-- Name: finance_expense_subcategories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_expense_subcategories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_expense_subcategories_id_seq OWNER TO postgres;

--
-- TOC entry 6108 (class 0 OID 0)
-- Dependencies: 316
-- Name: finance_expense_subcategories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_expense_subcategories_id_seq OWNED BY public.finance_expense_subcategories.id;


--
-- TOC entry 319 (class 1259 OID 41400)
-- Name: finance_expenses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_expenses (
    id integer NOT NULL,
    category_id integer,
    subcategory_id integer,
    expense_date date NOT NULL,
    amount numeric(12,2) NOT NULL,
    description text DEFAULT ''::text,
    supplier_name character varying(180) DEFAULT ''::character varying,
    invoice_number character varying(100) DEFAULT ''::character varying,
    payment_method_id integer,
    destination_account_id integer,
    affects_inventory boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expense_type character varying(20) DEFAULT 'variable'::character varying
);


ALTER TABLE public.finance_expenses OWNER TO postgres;

--
-- TOC entry 318 (class 1259 OID 41399)
-- Name: finance_expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_expenses_id_seq OWNER TO postgres;

--
-- TOC entry 6109 (class 0 OID 0)
-- Dependencies: 318
-- Name: finance_expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_expenses_id_seq OWNED BY public.finance_expenses.id;


--
-- TOC entry 305 (class 1259 OID 41225)
-- Name: finance_income; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_income (
    id integer NOT NULL,
    payer_person_id integer,
    payer_name character varying(180) DEFAULT ''::character varying,
    payer_type character varying(30) DEFAULT 'third_party'::character varying NOT NULL,
    income_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subtotal numeric(12,2) DEFAULT 0 NOT NULL,
    discount numeric(12,2) DEFAULT 0 NOT NULL,
    total numeric(12,2) DEFAULT 0 NOT NULL,
    total_paid numeric(12,2) DEFAULT 0 NOT NULL,
    pending_amount numeric(12,2) DEFAULT 0 NOT NULL,
    payment_method_id integer,
    destination_account_id integer,
    status character varying(30) DEFAULT 'paid'::character varying NOT NULL,
    note text DEFAULT ''::text,
    agreement_note text DEFAULT ''::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    payer_document character varying(80) DEFAULT ''::character varying,
    payer_email character varying(160) DEFAULT ''::character varying,
    payer_phone character varying(60) DEFAULT ''::character varying,
    receipt_number character varying(30),
    receipt_pdf_path text,
    receipt_generated_at timestamp without time zone
);


ALTER TABLE public.finance_income OWNER TO postgres;

--
-- TOC entry 304 (class 1259 OID 41224)
-- Name: finance_income_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_income_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_income_id_seq OWNER TO postgres;

--
-- TOC entry 6110 (class 0 OID 0)
-- Dependencies: 304
-- Name: finance_income_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_income_id_seq OWNED BY public.finance_income.id;


--
-- TOC entry 307 (class 1259 OID 41259)
-- Name: finance_income_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_income_items (
    id integer NOT NULL,
    income_id integer NOT NULL,
    item_type character varying(40) NOT NULL,
    reference_id integer,
    name character varying(180) NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    unit_price numeric(12,2) DEFAULT 0 NOT NULL,
    discount numeric(12,2) DEFAULT 0 NOT NULL,
    subtotal numeric(12,2) DEFAULT 0 NOT NULL,
    details text DEFAULT ''::text
);


ALTER TABLE public.finance_income_items OWNER TO postgres;

--
-- TOC entry 306 (class 1259 OID 41258)
-- Name: finance_income_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_income_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_income_items_id_seq OWNER TO postgres;

--
-- TOC entry 6111 (class 0 OID 0)
-- Dependencies: 306
-- Name: finance_income_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_income_items_id_seq OWNED BY public.finance_income_items.id;


--
-- TOC entry 309 (class 1259 OID 41283)
-- Name: finance_income_participants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_income_participants (
    id integer NOT NULL,
    income_id integer NOT NULL,
    person_id integer,
    display_name character varying(180) NOT NULL,
    expected_amount numeric(12,2) DEFAULT 0 NOT NULL,
    paid_amount numeric(12,2) DEFAULT 0 NOT NULL,
    pending_amount numeric(12,2) DEFAULT 0 NOT NULL,
    due_date date,
    note text DEFAULT ''::text
);


ALTER TABLE public.finance_income_participants OWNER TO postgres;

--
-- TOC entry 308 (class 1259 OID 41282)
-- Name: finance_income_participants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_income_participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_income_participants_id_seq OWNER TO postgres;

--
-- TOC entry 6112 (class 0 OID 0)
-- Dependencies: 308
-- Name: finance_income_participants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_income_participants_id_seq OWNED BY public.finance_income_participants.id;


--
-- TOC entry 313 (class 1259 OID 41347)
-- Name: finance_receivable_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_receivable_payments (
    id integer NOT NULL,
    receivable_id integer NOT NULL,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    amount numeric(12,2) NOT NULL,
    payment_method_id integer,
    destination_account_id integer,
    note text DEFAULT ''::text
);


ALTER TABLE public.finance_receivable_payments OWNER TO postgres;

--
-- TOC entry 312 (class 1259 OID 41346)
-- Name: finance_receivable_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_receivable_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_receivable_payments_id_seq OWNER TO postgres;

--
-- TOC entry 6113 (class 0 OID 0)
-- Dependencies: 312
-- Name: finance_receivable_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_receivable_payments_id_seq OWNED BY public.finance_receivable_payments.id;


--
-- TOC entry 311 (class 1259 OID 41312)
-- Name: finance_receivables; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_receivables (
    id integer NOT NULL,
    person_id integer,
    debtor_name character varying(180) NOT NULL,
    source_income_id integer,
    source_participant_id integer,
    source_type character varying(40) DEFAULT 'income_pending'::character varying,
    original_amount numeric(12,2) NOT NULL,
    paid_amount numeric(12,2) DEFAULT 0 NOT NULL,
    pending_amount numeric(12,2) NOT NULL,
    due_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status character varying(30) DEFAULT 'open'::character varying NOT NULL,
    note text DEFAULT ''::text
);


ALTER TABLE public.finance_receivables OWNER TO postgres;

--
-- TOC entry 310 (class 1259 OID 41311)
-- Name: finance_receivables_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.finance_receivables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.finance_receivables_id_seq OWNER TO postgres;

--
-- TOC entry 6114 (class 0 OID 0)
-- Dependencies: 310
-- Name: finance_receivables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.finance_receivables_id_seq OWNED BY public.finance_receivables.id;


--
-- TOC entry 291 (class 1259 OID 41029)
-- Name: instructor_belts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instructor_belts (
    id integer NOT NULL,
    id_instructor integer NOT NULL,
    id_martial_art integer NOT NULL,
    id_belt bigint NOT NULL,
    assigned_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.instructor_belts OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 41028)
-- Name: instructor_belts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.instructor_belts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.instructor_belts_id_seq OWNER TO postgres;

--
-- TOC entry 6115 (class 0 OID 0)
-- Dependencies: 290
-- Name: instructor_belts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.instructor_belts_id_seq OWNED BY public.instructor_belts.id;


--
-- TOC entry 287 (class 1259 OID 32868)
-- Name: instructor_martial_arts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instructor_martial_arts (
    id integer NOT NULL,
    id_instructor integer NOT NULL,
    id_martial_art integer NOT NULL,
    can_promote boolean DEFAULT false NOT NULL
);


ALTER TABLE public.instructor_martial_arts OWNER TO postgres;

--
-- TOC entry 286 (class 1259 OID 32867)
-- Name: instructor_martial_arts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.instructor_martial_arts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.instructor_martial_arts_id_seq OWNER TO postgres;

--
-- TOC entry 6116 (class 0 OID 0)
-- Dependencies: 286
-- Name: instructor_martial_arts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.instructor_martial_arts_id_seq OWNED BY public.instructor_martial_arts.id;


--
-- TOC entry 237 (class 1259 OID 24743)
-- Name: instructors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.instructors (
    id integer NOT NULL,
    id_person integer,
    is_sensei boolean DEFAULT false NOT NULL
);


ALTER TABLE public.instructors OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 24742)
-- Name: instructors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.instructors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.instructors_id_seq OWNER TO postgres;

--
-- TOC entry 6117 (class 0 OID 0)
-- Dependencies: 236
-- Name: instructors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.instructors_id_seq OWNED BY public.instructors.id;


--
-- TOC entry 297 (class 1259 OID 41144)
-- Name: inventory_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.inventory_categories OWNER TO postgres;

--
-- TOC entry 296 (class 1259 OID 41143)
-- Name: inventory_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_categories_id_seq OWNER TO postgres;

--
-- TOC entry 6118 (class 0 OID 0)
-- Dependencies: 296
-- Name: inventory_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_categories_id_seq OWNED BY public.inventory_categories.id;


--
-- TOC entry 353 (class 1259 OID 49429)
-- Name: martial_art_initial_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.martial_art_initial_levels (
    id bigint NOT NULL,
    martial_art_id integer NOT NULL,
    level_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.martial_art_initial_levels OWNER TO postgres;

--
-- TOC entry 352 (class 1259 OID 49428)
-- Name: martial_art_initial_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.martial_art_initial_levels ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.martial_art_initial_levels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 351 (class 1259 OID 49394)
-- Name: martial_art_promotion_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.martial_art_promotion_rules (
    id bigint NOT NULL,
    martial_art_id integer NOT NULL,
    from_level_id bigint,
    to_level_id bigint NOT NULL,
    is_allowed boolean DEFAULT true NOT NULL,
    requires_all_grades boolean DEFAULT false NOT NULL,
    minimum_grade integer,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.martial_art_promotion_rules OWNER TO postgres;

--
-- TOC entry 350 (class 1259 OID 49393)
-- Name: martial_art_promotion_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.martial_art_promotion_rules ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.martial_art_promotion_rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 226 (class 1259 OID 24603)
-- Name: martial_arts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.martial_arts (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    icon_key character varying(60),
    accent_color character varying(20) DEFAULT '#C8102E'::character varying,
    progression_enabled boolean DEFAULT true NOT NULL,
    progression_system character varying(40) DEFAULT 'belt'::character varying,
    progression_label_singular character varying(60) DEFAULT 'Cinturón'::character varying,
    progression_label_plural character varying(60) DEFAULT 'Cinturones'::character varying,
    promotion_mode character varying(40) DEFAULT 'sequential'::character varying,
    allow_level_skips boolean DEFAULT false NOT NULL,
    initial_assignment_mode character varying(40) DEFAULT 'first_only'::character varying,
    template_key character varying(60),
    is_active boolean DEFAULT true NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    description text,
    training_focus text,
    CONSTRAINT chk_martial_arts_initial_assignment CHECK (((initial_assignment_mode)::text = ANY ((ARRAY['first_only'::character varying, 'any_level'::character varying, 'configured_levels'::character varying])::text[]))),
    CONSTRAINT chk_martial_arts_progression_system CHECK (((progression_system)::text = ANY ((ARRAY['none'::character varying, 'belt'::character varying, 'sash'::character varying, 'shirt'::character varying, 'bracelet'::character varying, 'level'::character varying, 'grade'::character varying, 'custom'::character varying])::text[]))),
    CONSTRAINT chk_martial_arts_promotion_mode CHECK (((promotion_mode)::text = ANY ((ARRAY['sequential'::character varying, 'sequential_with_grades'::character varying, 'manual'::character varying, 'custom_rules'::character varying])::text[])))
);


ALTER TABLE public.martial_arts OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 24602)
-- Name: martial_arts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.martial_arts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.martial_arts_id_seq OWNER TO postgres;

--
-- TOC entry 6119 (class 0 OID 0)
-- Dependencies: 225
-- Name: martial_arts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.martial_arts_id_seq OWNED BY public.martial_arts.id;


--
-- TOC entry 299 (class 1259 OID 41161)
-- Name: membership_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.membership_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.membership_categories OWNER TO postgres;

--
-- TOC entry 298 (class 1259 OID 41160)
-- Name: membership_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.membership_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.membership_categories_id_seq OWNER TO postgres;

--
-- TOC entry 6120 (class 0 OID 0)
-- Dependencies: 298
-- Name: membership_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.membership_categories_id_seq OWNED BY public.membership_categories.id;


--
-- TOC entry 259 (class 1259 OID 24916)
-- Name: membership_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.membership_plans (
    id integer NOT NULL,
    id_type_product integer,
    name character varying(150) NOT NULL,
    monthly_fee numeric(12,2) NOT NULL,
    discount numeric(12,2) DEFAULT 0,
    discount_by_person boolean DEFAULT false,
    classes_per_week integer,
    weekly_classes integer DEFAULT 0,
    is_unlimited boolean DEFAULT false,
    description text DEFAULT ''::text,
    benefits text DEFAULT ''::text,
    id_membership_category integer,
    plan_type character varying(20) DEFAULT 'individual'::character varying,
    group_capacity integer DEFAULT 1,
    discount_type character varying(20) DEFAULT 'percent'::character varying
);


ALTER TABLE public.membership_plans OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 24915)
-- Name: membership_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.membership_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.membership_plans_id_seq OWNER TO postgres;

--
-- TOC entry 6121 (class 0 OID 0)
-- Dependencies: 258
-- Name: membership_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.membership_plans_id_seq OWNED BY public.membership_plans.id;


--
-- TOC entry 251 (class 1259 OID 24867)
-- Name: movement_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.movement_type (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.movement_type OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 24866)
-- Name: movement_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.movement_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movement_type_id_seq OWNER TO postgres;

--
-- TOC entry 6122 (class 0 OID 0)
-- Dependencies: 250
-- Name: movement_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.movement_type_id_seq OWNED BY public.movement_type.id;


--
-- TOC entry 265 (class 1259 OID 24991)
-- Name: payment_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_items (
    id integer NOT NULL,
    id_payments integer NOT NULL,
    id_product integer,
    id_membership_plan integer,
    quantity integer DEFAULT 1 NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    subtotal numeric(12,2) NOT NULL,
    CONSTRAINT chk_payment_item_source CHECK ((((id_product IS NOT NULL) AND (id_membership_plan IS NULL)) OR ((id_product IS NULL) AND (id_membership_plan IS NOT NULL))))
);


ALTER TABLE public.payment_items OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 24990)
-- Name: payment_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_items_id_seq OWNER TO postgres;

--
-- TOC entry 6123 (class 0 OID 0)
-- Dependencies: 264
-- Name: payment_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_items_id_seq OWNED BY public.payment_items.id;


--
-- TOC entry 249 (class 1259 OID 24856)
-- Name: payment_method; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_method (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.payment_method OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 24855)
-- Name: payment_method_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payment_method_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payment_method_id_seq OWNER TO postgres;

--
-- TOC entry 6124 (class 0 OID 0)
-- Dependencies: 248
-- Name: payment_method_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payment_method_id_seq OWNED BY public.payment_method.id;


--
-- TOC entry 263 (class 1259 OID 24957)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    id_person integer NOT NULL,
    total numeric(12,2) NOT NULL,
    total_paid numeric(12,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_payment_method integer NOT NULL,
    id_destination_account integer NOT NULL,
    description text,
    note text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 24956)
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_id_seq OWNER TO postgres;

--
-- TOC entry 6125 (class 0 OID 0)
-- Dependencies: 262
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- TOC entry 230 (class 1259 OID 24674)
-- Name: people; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.people (
    id integer NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    phone character varying(20),
    email character varying(100),
    birthdate date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id_code_users integer,
    photo_path text,
    address_line character varying(180),
    residence_city character varying(100),
    residence_country character varying(100),
    birth_city character varying(100),
    birth_country character varying(100),
    neighborhood character varying(150) DEFAULT ''::character varying,
    socioeconomic_stratum smallint,
    profession character varying(150) DEFAULT ''::character varying,
    residence_details text DEFAULT ''::text,
    CONSTRAINT people_socioeconomic_stratum_check CHECK (((socioeconomic_stratum IS NULL) OR ((socioeconomic_stratum >= 1) AND (socioeconomic_stratum <= 6))))
);


ALTER TABLE public.people OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 24673)
-- Name: people_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.people_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.people_id_seq OWNER TO postgres;

--
-- TOC entry 6126 (class 0 OID 0)
-- Dependencies: 229
-- Name: people_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.people_id_seq OWNED BY public.people.id;


--
-- TOC entry 233 (class 1259 OID 24694)
-- Name: person_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.person_roles (
    id_person integer,
    id_role integer
);


ALTER TABLE public.person_roles OWNER TO postgres;

--
-- TOC entry 301 (class 1259 OID 41172)
-- Name: product_purchase_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_purchase_history (
    id integer NOT NULL,
    id_product integer NOT NULL,
    buyer_name character varying(150) NOT NULL,
    purchase_date date NOT NULL,
    quantity integer NOT NULL,
    total_price numeric(12,2) NOT NULL,
    note text DEFAULT ''::text
);


ALTER TABLE public.product_purchase_history OWNER TO postgres;

--
-- TOC entry 300 (class 1259 OID 41171)
-- Name: product_purchase_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_purchase_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_purchase_history_id_seq OWNER TO postgres;

--
-- TOC entry 6127 (class 0 OID 0)
-- Dependencies: 300
-- Name: product_purchase_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_purchase_history_id_seq OWNED BY public.product_purchase_history.id;


--
-- TOC entry 257 (class 1259 OID 24898)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    id_type_product integer NOT NULL,
    name character varying(150) NOT NULL,
    sale_price numeric(12,2) NOT NULL,
    stock integer DEFAULT 0 NOT NULL,
    id_inventory_category integer,
    cost_price numeric(12,2) DEFAULT 0,
    image_path text DEFAULT ''::text
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 24897)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 6128 (class 0 OID 0)
-- Dependencies: 256
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 357 (class 1259 OID 49472)
-- Name: progression_template_levels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.progression_template_levels (
    id bigint NOT NULL,
    template_id bigint NOT NULL,
    name character varying(100) NOT NULL,
    orden integer NOT NULL,
    color character varying(20),
    pre_color character varying(20),
    grades integer DEFAULT 0 NOT NULL,
    grade_color character varying(20) DEFAULT '#FFFFFF'::character varying,
    icon_key character varying(60),
    is_initial boolean DEFAULT false NOT NULL,
    is_final boolean DEFAULT false NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.progression_template_levels OWNER TO postgres;

--
-- TOC entry 356 (class 1259 OID 49471)
-- Name: progression_template_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.progression_template_levels ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.progression_template_levels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 355 (class 1259 OID 49452)
-- Name: progression_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.progression_templates (
    id bigint NOT NULL,
    template_key character varying(60) NOT NULL,
    name character varying(120) NOT NULL,
    description text,
    system_type character varying(40) NOT NULL,
    icon_key character varying(60),
    is_builtin boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.progression_templates OWNER TO postgres;

--
-- TOC entry 354 (class 1259 OID 49451)
-- Name: progression_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.progression_templates ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.progression_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 232 (class 1259 OID 24685)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(50)
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 24684)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- TOC entry 6129 (class 0 OID 0)
-- Dependencies: 231
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 243 (class 1259 OID 24795)
-- Name: schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule (
    id integer NOT NULL,
    id_martial_art integer,
    name character varying(100),
    id_instructor integer,
    day_of_week integer,
    start_time time without time zone,
    end_time time without time zone,
    capacity integer,
    location character varying(120),
    color character varying(20),
    status character varying(30) DEFAULT 'active'::character varying,
    repeat_type character varying(30) DEFAULT 'weekly'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_schedule_day_of_week CHECK (((day_of_week >= 0) AND (day_of_week <= 6))),
    CONSTRAINT chk_schedule_time CHECK ((start_time < end_time))
);


ALTER TABLE public.schedule OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 24794)
-- Name: schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_id_seq OWNER TO postgres;

--
-- TOC entry 6130 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


--
-- TOC entry 333 (class 1259 OID 41600)
-- Name: scholarships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scholarships (
    id integer CONSTRAINT scholarships_id_not_null1 NOT NULL,
    person_id integer,
    monthly_fee numeric(12,2) DEFAULT 0 NOT NULL,
    start_date date DEFAULT CURRENT_DATE NOT NULL,
    end_date date,
    status character varying(20) DEFAULT '''active'''::character varying,
    rate_class numeric(12,2) DEFAULT 25000,
    rate_deep_clean numeric(12,2) DEFAULT 50000,
    rate_maintenance numeric(12,2) DEFAULT 25000,
    penalty_per_miss numeric(12,2) DEFAULT 25000,
    notes text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.scholarships OWNER TO postgres;

--
-- TOC entry 331 (class 1259 OID 41576)
-- Name: scholarships_old; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scholarships_old (
    id integer CONSTRAINT scholarships_id_not_null NOT NULL,
    name character varying(120) CONSTRAINT scholarships_name_not_null NOT NULL,
    description text DEFAULT ''::text,
    discount_percent numeric(5,2) DEFAULT 0 CONSTRAINT scholarships_discount_percent_not_null NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.scholarships_old OWNER TO postgres;

--
-- TOC entry 330 (class 1259 OID 41575)
-- Name: scholarships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scholarships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scholarships_id_seq OWNER TO postgres;

--
-- TOC entry 6131 (class 0 OID 0)
-- Dependencies: 330
-- Name: scholarships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scholarships_id_seq OWNED BY public.scholarships_old.id;


--
-- TOC entry 332 (class 1259 OID 41599)
-- Name: scholarships_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scholarships_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scholarships_id_seq1 OWNER TO postgres;

--
-- TOC entry 6132 (class 0 OID 0)
-- Dependencies: 332
-- Name: scholarships_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scholarships_id_seq1 OWNED BY public.scholarships.id;


--
-- TOC entry 303 (class 1259 OID 41210)
-- Name: services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    description text DEFAULT ''::text,
    price numeric(12,2) DEFAULT 0,
    icon character varying(50) DEFAULT '🚀'::character varying,
    accent_color character varying(20) DEFAULT '#3B82F6'::character varying,
    is_active boolean DEFAULT true
);


ALTER TABLE public.services OWNER TO postgres;

--
-- TOC entry 302 (class 1259 OID 41209)
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.services ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.services_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 222 (class 1259 OID 16435)
-- Name: status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.status (
    id bigint NOT NULL,
    status character varying(50)
);


ALTER TABLE public.status OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16434)
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_id_seq OWNER TO postgres;

--
-- TOC entry 6133 (class 0 OID 0)
-- Dependencies: 221
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;


--
-- TOC entry 325 (class 1259 OID 41490)
-- Name: student_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_documents (
    id integer NOT NULL,
    id_student integer NOT NULL,
    doc_type character varying(50) NOT NULL,
    file_path character varying(500) NOT NULL,
    uploaded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.student_documents OWNER TO postgres;

--
-- TOC entry 324 (class 1259 OID 41489)
-- Name: student_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_documents_id_seq OWNER TO postgres;

--
-- TOC entry 6134 (class 0 OID 0)
-- Dependencies: 324
-- Name: student_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_documents_id_seq OWNED BY public.student_documents.id;


--
-- TOC entry 295 (class 1259 OID 41121)
-- Name: student_emergency_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_emergency_contacts (
    id integer NOT NULL,
    id_student integer NOT NULL,
    full_name character varying(160) NOT NULL,
    phone character varying(30) NOT NULL,
    email character varying(120),
    relationship character varying(60),
    note text,
    is_primary boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.student_emergency_contacts OWNER TO postgres;

--
-- TOC entry 294 (class 1259 OID 41120)
-- Name: student_emergency_contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_emergency_contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_emergency_contacts_id_seq OWNER TO postgres;

--
-- TOC entry 6135 (class 0 OID 0)
-- Dependencies: 294
-- Name: student_emergency_contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_emergency_contacts_id_seq OWNED BY public.student_emergency_contacts.id;


--
-- TOC entry 293 (class 1259 OID 41101)
-- Name: student_guardians; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_guardians (
    id integer NOT NULL,
    id_student integer NOT NULL,
    full_name character varying(160) NOT NULL,
    phone character varying(30) NOT NULL,
    email character varying(120),
    relationship character varying(60) NOT NULL,
    is_primary boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    document character varying(50) DEFAULT ''::character varying,
    profession character varying(150) DEFAULT ''::character varying
);


ALTER TABLE public.student_guardians OWNER TO postgres;

--
-- TOC entry 292 (class 1259 OID 41100)
-- Name: student_guardians_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_guardians_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_guardians_id_seq OWNER TO postgres;

--
-- TOC entry 6136 (class 0 OID 0)
-- Dependencies: 292
-- Name: student_guardians_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_guardians_id_seq OWNED BY public.student_guardians.id;


--
-- TOC entry 323 (class 1259 OID 41465)
-- Name: student_health_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_health_info (
    id integer NOT NULL,
    id_student integer NOT NULL,
    eps character varying(150) DEFAULT ''::character varying,
    ips character varying(150) DEFAULT ''::character varying,
    blood_type character varying(5) DEFAULT ''::character varying,
    allergies text DEFAULT ''::text,
    medical_conditions text DEFAULT ''::text,
    notes text DEFAULT ''::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.student_health_info OWNER TO postgres;

--
-- TOC entry 322 (class 1259 OID 41464)
-- Name: student_health_info_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_health_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_health_info_id_seq OWNER TO postgres;

--
-- TOC entry 6137 (class 0 OID 0)
-- Dependencies: 322
-- Name: student_health_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_health_info_id_seq OWNED BY public.student_health_info.id;


--
-- TOC entry 261 (class 1259 OID 24935)
-- Name: student_memberships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_memberships (
    id integer NOT NULL,
    id_student integer NOT NULL,
    id_membership_plan integer NOT NULL,
    custom_fee numeric(12,2),
    status character varying(30) NOT NULL,
    start_date date NOT NULL,
    end_date date
);


ALTER TABLE public.student_memberships OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 24934)
-- Name: student_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_memberships_id_seq OWNER TO postgres;

--
-- TOC entry 6138 (class 0 OID 0)
-- Dependencies: 260
-- Name: student_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_memberships_id_seq OWNED BY public.student_memberships.id;


--
-- TOC entry 235 (class 1259 OID 24713)
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    id_person integer,
    id_type_document integer,
    document character varying(50),
    category_id integer,
    id_status integer,
    joined_date date,
    school_name character varying(200) DEFAULT ''::character varying
);


ALTER TABLE public.students OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 24758)
-- Name: students_belts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students_belts (
    id integer NOT NULL,
    id_student integer,
    id_belt integer
);


ALTER TABLE public.students_belts OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 24776)
-- Name: students_belts_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students_belts_history (
    id integer NOT NULL,
    id_student integer,
    id_belt integer,
    action character varying(20),
    date_changed timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.students_belts_history OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24775)
-- Name: students_belts_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_belts_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_belts_history_id_seq OWNER TO postgres;

--
-- TOC entry 6139 (class 0 OID 0)
-- Dependencies: 240
-- Name: students_belts_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_belts_history_id_seq OWNED BY public.students_belts_history.id;


--
-- TOC entry 238 (class 1259 OID 24757)
-- Name: students_belts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_belts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_belts_id_seq OWNER TO postgres;

--
-- TOC entry 6140 (class 0 OID 0)
-- Dependencies: 238
-- Name: students_belts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_belts_id_seq OWNED BY public.students_belts.id;


--
-- TOC entry 234 (class 1259 OID 24712)
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO postgres;

--
-- TOC entry 6141 (class 0 OID 0)
-- Dependencies: 234
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- TOC entry 281 (class 1259 OID 32805)
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    task character varying(500) NOT NULL,
    id_type_task integer,
    limit_date date
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- TOC entry 280 (class 1259 OID 32804)
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tasks_id_seq OWNER TO postgres;

--
-- TOC entry 6142 (class 0 OID 0)
-- Dependencies: 280
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- TOC entry 220 (class 1259 OID 16427)
-- Name: type_document; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_document (
    id bigint NOT NULL,
    type_document character varying(50)
);


ALTER TABLE public.type_document OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16426)
-- Name: type_document_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_document_id_seq OWNER TO postgres;

--
-- TOC entry 6143 (class 0 OID 0)
-- Dependencies: 219
-- Name: type_document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_document_id_seq OWNED BY public.type_document.id;


--
-- TOC entry 255 (class 1259 OID 24887)
-- Name: type_products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_products (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.type_products OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 24886)
-- Name: type_products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_products_id_seq OWNER TO postgres;

--
-- TOC entry 6144 (class 0 OID 0)
-- Dependencies: 254
-- Name: type_products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_products_id_seq OWNED BY public.type_products.id;


--
-- TOC entry 283 (class 1259 OID 32821)
-- Name: type_requirements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_requirements (
    id integer NOT NULL,
    type_requirement character varying(500)
);


ALTER TABLE public.type_requirements OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 32820)
-- Name: type_requirements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_requirements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_requirements_id_seq OWNER TO postgres;

--
-- TOC entry 6145 (class 0 OID 0)
-- Dependencies: 282
-- Name: type_requirements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_requirements_id_seq OWNED BY public.type_requirements.id;


--
-- TOC entry 275 (class 1259 OID 32769)
-- Name: type_student; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_student (
    id integer NOT NULL,
    name character varying(50)
);


ALTER TABLE public.type_student OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 32768)
-- Name: type_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_student_id_seq OWNER TO postgres;

--
-- TOC entry 6146 (class 0 OID 0)
-- Dependencies: 274
-- Name: type_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_student_id_seq OWNED BY public.type_student.id;


--
-- TOC entry 279 (class 1259 OID 32797)
-- Name: type_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.type_task (
    id integer NOT NULL,
    name character varying(100)
);


ALTER TABLE public.type_task OWNER TO postgres;

--
-- TOC entry 278 (class 1259 OID 32796)
-- Name: type_task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.type_task_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.type_task_id_seq OWNER TO postgres;

--
-- TOC entry 6147 (class 0 OID 0)
-- Dependencies: 278
-- Name: type_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_task_id_seq OWNED BY public.type_task.id;


--
-- TOC entry 339 (class 1259 OID 49153)
-- Name: user_notification_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_notification_preferences (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    classes_enabled boolean DEFAULT true NOT NULL,
    classes_in_app boolean DEFAULT true NOT NULL,
    classes_windows boolean DEFAULT true NOT NULL,
    classes_minutes_before integer DEFAULT 15 NOT NULL,
    classes_notify_at_start boolean DEFAULT true NOT NULL,
    events_enabled boolean DEFAULT true NOT NULL,
    events_in_app boolean DEFAULT true NOT NULL,
    events_windows boolean DEFAULT true NOT NULL,
    events_minutes_before integer DEFAULT 1440 NOT NULL,
    events_notify_at_start boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_classes_minutes_before CHECK ((classes_minutes_before = ANY (ARRAY[5, 10, 15, 30, 60]))),
    CONSTRAINT chk_events_minutes_before CHECK ((events_minutes_before = ANY (ARRAY[15, 30, 60, 180, 720, 1440, 2880, 10080])))
);


ALTER TABLE public.user_notification_preferences OWNER TO postgres;

--
-- TOC entry 338 (class 1259 OID 49152)
-- Name: user_notification_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.user_notification_preferences ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.user_notification_preferences_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 273 (class 1259 OID 25086)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    id_person integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 25085)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 6148 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 5284 (class 2604 OID 25062)
-- Name: account_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements ALTER COLUMN id SET DEFAULT nextval('public.account_movements_id_seq'::regclass);


--
-- TOC entry 5253 (class 2604 OID 24834)
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- TOC entry 5294 (class 2604 OID 32849)
-- Name: belt_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements ALTER COLUMN id SET DEFAULT nextval('public.belt_requirements_id_seq'::regclass);


--
-- TOC entry 5223 (class 2604 OID 24617)
-- Name: belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts ALTER COLUMN id SET DEFAULT nextval('public.belts_id_seq'::regclass);


--
-- TOC entry 5211 (class 2604 OID 24590)
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- TOC entry 5249 (class 2604 OID 24811)
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- TOC entry 5290 (class 2604 OID 32780)
-- Name: codes_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users ALTER COLUMN id SET DEFAULT nextval('public.codes_users_id_seq'::regclass);


--
-- TOC entry 5424 (class 2604 OID 41654)
-- Name: collection_account_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items ALTER COLUMN id SET DEFAULT nextval('public.collection_account_items_id_seq1'::regclass);


--
-- TOC entry 5399 (class 2604 OID 41553)
-- Name: collection_account_items_old id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items_old ALTER COLUMN id SET DEFAULT nextval('public.collection_account_items_id_seq'::regclass);


--
-- TOC entry 5419 (class 2604 OID 41628)
-- Name: collection_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts ALTER COLUMN id SET DEFAULT nextval('public.collection_accounts_id_seq1'::regclass);


--
-- TOC entry 5386 (class 2604 OID 41518)
-- Name: collection_accounts_old id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts_old ALTER COLUMN id SET DEFAULT nextval('public.collection_accounts_id_seq'::regclass);


--
-- TOC entry 5259 (class 2604 OID 24881)
-- Name: destination_account id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account ALTER COLUMN id SET DEFAULT nextval('public.destination_account_id_seq'::regclass);


--
-- TOC entry 5281 (class 2604 OID 25023)
-- Name: expense_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories ALTER COLUMN id SET DEFAULT nextval('public.expense_categories_id_seq'::regclass);


--
-- TOC entry 5282 (class 2604 OID 25036)
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- TOC entry 5362 (class 2604 OID 41369)
-- Name: finance_expense_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_categories_id_seq'::regclass);


--
-- TOC entry 5374 (class 2604 OID 41430)
-- Name: finance_expense_inventory_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_inventory_items_id_seq'::regclass);


--
-- TOC entry 5365 (class 2604 OID 41383)
-- Name: finance_expense_subcategories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_subcategories_id_seq'::regclass);


--
-- TOC entry 5367 (class 2604 OID 41403)
-- Name: finance_expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses ALTER COLUMN id SET DEFAULT nextval('public.finance_expenses_id_seq'::regclass);


--
-- TOC entry 5326 (class 2604 OID 41228)
-- Name: finance_income id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income ALTER COLUMN id SET DEFAULT nextval('public.finance_income_id_seq'::regclass);


--
-- TOC entry 5342 (class 2604 OID 41262)
-- Name: finance_income_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items ALTER COLUMN id SET DEFAULT nextval('public.finance_income_items_id_seq'::regclass);


--
-- TOC entry 5348 (class 2604 OID 41286)
-- Name: finance_income_participants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants ALTER COLUMN id SET DEFAULT nextval('public.finance_income_participants_id_seq'::regclass);


--
-- TOC entry 5359 (class 2604 OID 41350)
-- Name: finance_receivable_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments ALTER COLUMN id SET DEFAULT nextval('public.finance_receivable_payments_id_seq'::regclass);


--
-- TOC entry 5353 (class 2604 OID 41315)
-- Name: finance_receivables id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables ALTER COLUMN id SET DEFAULT nextval('public.finance_receivables_id_seq'::regclass);


--
-- TOC entry 5307 (class 2604 OID 41032)
-- Name: instructor_belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts ALTER COLUMN id SET DEFAULT nextval('public.instructor_belts_id_seq'::regclass);


--
-- TOC entry 5296 (class 2604 OID 32871)
-- Name: instructor_martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts ALTER COLUMN id SET DEFAULT nextval('public.instructor_martial_arts_id_seq'::regclass);


--
-- TOC entry 5240 (class 2604 OID 24746)
-- Name: instructors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors ALTER COLUMN id SET DEFAULT nextval('public.instructors_id_seq'::regclass);


--
-- TOC entry 5317 (class 2604 OID 41147)
-- Name: inventory_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories ALTER COLUMN id SET DEFAULT nextval('public.inventory_categories_id_seq'::regclass);


--
-- TOC entry 5212 (class 2604 OID 24606)
-- Name: martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts ALTER COLUMN id SET DEFAULT nextval('public.martial_arts_id_seq'::regclass);


--
-- TOC entry 5318 (class 2604 OID 41164)
-- Name: membership_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories ALTER COLUMN id SET DEFAULT nextval('public.membership_categories_id_seq'::regclass);


--
-- TOC entry 5265 (class 2604 OID 24919)
-- Name: membership_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans ALTER COLUMN id SET DEFAULT nextval('public.membership_plans_id_seq'::regclass);


--
-- TOC entry 5258 (class 2604 OID 24870)
-- Name: movement_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type ALTER COLUMN id SET DEFAULT nextval('public.movement_type_id_seq'::regclass);


--
-- TOC entry 5279 (class 2604 OID 24994)
-- Name: payment_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items ALTER COLUMN id SET DEFAULT nextval('public.payment_items_id_seq'::regclass);


--
-- TOC entry 5257 (class 2604 OID 24859)
-- Name: payment_method id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method ALTER COLUMN id SET DEFAULT nextval('public.payment_method_id_seq'::regclass);


--
-- TOC entry 5276 (class 2604 OID 24960)
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- TOC entry 5232 (class 2604 OID 24677)
-- Name: people id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people ALTER COLUMN id SET DEFAULT nextval('public.people_id_seq'::regclass);


--
-- TOC entry 5319 (class 2604 OID 41175)
-- Name: product_purchase_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history ALTER COLUMN id SET DEFAULT nextval('public.product_purchase_history_id_seq'::regclass);


--
-- TOC entry 5261 (class 2604 OID 24901)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 5237 (class 2604 OID 24688)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 5245 (class 2604 OID 24798)
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- TOC entry 5410 (class 2604 OID 41603)
-- Name: scholarships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships ALTER COLUMN id SET DEFAULT nextval('public.scholarships_id_seq1'::regclass);


--
-- TOC entry 5405 (class 2604 OID 41579)
-- Name: scholarships_old id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships_old ALTER COLUMN id SET DEFAULT nextval('public.scholarships_id_seq'::regclass);


--
-- TOC entry 5210 (class 2604 OID 16438)
-- Name: status id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);


--
-- TOC entry 5384 (class 2604 OID 41493)
-- Name: student_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents ALTER COLUMN id SET DEFAULT nextval('public.student_documents_id_seq'::regclass);


--
-- TOC entry 5314 (class 2604 OID 41124)
-- Name: student_emergency_contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts ALTER COLUMN id SET DEFAULT nextval('public.student_emergency_contacts_id_seq'::regclass);


--
-- TOC entry 5309 (class 2604 OID 41104)
-- Name: student_guardians id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians ALTER COLUMN id SET DEFAULT nextval('public.student_guardians_id_seq'::regclass);


--
-- TOC entry 5375 (class 2604 OID 41468)
-- Name: student_health_info id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info ALTER COLUMN id SET DEFAULT nextval('public.student_health_info_id_seq'::regclass);


--
-- TOC entry 5275 (class 2604 OID 24938)
-- Name: student_memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships ALTER COLUMN id SET DEFAULT nextval('public.student_memberships_id_seq'::regclass);


--
-- TOC entry 5238 (class 2604 OID 24716)
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- TOC entry 5242 (class 2604 OID 24761)
-- Name: students_belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts ALTER COLUMN id SET DEFAULT nextval('public.students_belts_id_seq'::regclass);


--
-- TOC entry 5243 (class 2604 OID 24779)
-- Name: students_belts_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history ALTER COLUMN id SET DEFAULT nextval('public.students_belts_history_id_seq'::regclass);


--
-- TOC entry 5292 (class 2604 OID 32808)
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 5209 (class 2604 OID 16430)
-- Name: type_document id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document ALTER COLUMN id SET DEFAULT nextval('public.type_document_id_seq'::regclass);


--
-- TOC entry 5260 (class 2604 OID 24890)
-- Name: type_products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products ALTER COLUMN id SET DEFAULT nextval('public.type_products_id_seq'::regclass);


--
-- TOC entry 5293 (class 2604 OID 32824)
-- Name: type_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements ALTER COLUMN id SET DEFAULT nextval('public.type_requirements_id_seq'::regclass);


--
-- TOC entry 5289 (class 2604 OID 32772)
-- Name: type_student id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student ALTER COLUMN id SET DEFAULT nextval('public.type_student_id_seq'::regclass);


--
-- TOC entry 5291 (class 2604 OID 32800)
-- Name: type_task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task ALTER COLUMN id SET DEFAULT nextval('public.type_task_id_seq'::regclass);


--
-- TOC entry 5286 (class 2604 OID 25089)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5998 (class 0 OID 25059)
-- Dependencies: 271
-- Data for Name: account_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_movements (id, id_destination_account, id_movement_type, amount, payment_date) FROM stdin;
\.


--
-- TOC entry 5974 (class 0 OID 24831)
-- Dependencies: 247
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance (id, id_class, id_student, status, check_in_time, note, is_admin_override, override_user_id, override_reason) FROM stdin;
4	5	8	present	2026-07-17 00:50:07.262765	\N	f	\N	\N
\.


--
-- TOC entry 6012 (class 0 OID 32846)
-- Dependencies: 285
-- Data for Name: belt_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belt_requirements (id, belt_id, requirement, id_type_requeriments, created_at) FROM stdin;
3	2	fsljfdods	1	2026-08-01 20:49:24.172224
\.


--
-- TOC entry 5955 (class 0 OID 24614)
-- Dependencies: 228
-- Data for Name: belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belts (id, name, id_martial_art, orden, color, pre_color, grades, grade_color, level_type, icon_key, is_initial, is_final, is_active, display_name, metadata, updated_at, minimum_age, maximum_age, age_restriction_note) FROM stdin;
1	White	1	1	#FFFFFF	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
2	White	3	1	#FFFFFF	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
4	Pre-naranja	1	2	#FFFFFF	#FF5500	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
5	Naranja	1	3	#FF5500	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
6	Pre-azul	1	4	#FF5500	#0000FF	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
7	Azul	1	5	#0000FF	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
8	Pre-amarillo	1	6	#0000FF	#FFFF00	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
9	Amarillo	1	7	#FFD710	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
10	Pre-verde	1	8	#F3CD0F	#005500	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
11	Verde	1	9	#005500	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
12	Pre-marron	1	10	#005500	#623307	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
14	Negro nacional	1	12	#000000	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
16	Blanco 1° GRADO	3	2	#FFFFFF	\N	1	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
17	Blanco 2° GRADO	3	3	#FFFFFF	\N	2	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
21	Blanco 3° GRADO	3	4	#FFFFFF	\N	3	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
22	Blanco 4° Grado	3	5	#FFFFFF	\N	4	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
24	Azul	3	6	#00007F	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
25	Azul 1° Grado	3	7	#00007F	\N	1	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
26	Azul 2° GRADO	3	8	#00007F	\N	2	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
27	Azul 3° GRADO	3	9	#00007F	\N	3	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
28	Azul 4° GRADO	3	10	#00007F	\N	4	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
30	Morado	3	11	#8B0350	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
33	Negro 1° DAN	1	13	#000000	\N	1	#FFFF00	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
34	Negro 2° DAN	1	14	#000000	\N	2	#FFFF00	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
35	Negro 3° DAN	1	15	#000000	\N	3	#FFFF00	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
36	Negro 4° DAN	1	16	#000000	\N	4	#FFFF00	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
31	Morado 1° GRADO	3	12	#8b0350	\N	1	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
37	Morado 2° GRADO	3	13	#8b0350	\N	2	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
38	Modaro 3° GRADO	3	14	#8b0350	\N	3	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
13	Marron	1	11	#623307	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
42	Marron	3	16	#623307	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
43	Marron 1° Grado	3	17	#623307	\N	1	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
44	Marron 2° GRADO	3	18	#623307	\N	2	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
45	Marron 3° GRADO	3	19	#623307	\N	3	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
46	Marron 4° Grado	3	20	#623307	\N	4	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
47	Negro	3	21	#000000	\N	0	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
48	Negro 1° GRADO	3	22	#000000	\N	1	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
39	Morado 4° GRADO	3	15	#8b0350	\N	4	#FFFFFF	belt	\N	f	f	t	\N	{}	2026-07-22 00:13:15.128479	\N	\N	\N
50	Blanca	2	1	#FFFFFF	\N	0	#333333	shirt	\N	t	f	t	\N	{}	2026-08-02 01:30:17.709592	\N	\N	\N
54	Azul	2	5	#3B82F6	\N	0	#FFFFFF	shirt	\N	f	f	t	\N	{}	2026-08-02 01:30:17.713552	\N	\N	\N
55	Negra	2	6	#1A1A1A	\N	0	#FFFFFF	shirt	\N	f	t	t	\N	{}	2026-08-02 01:30:17.714547	\N	\N	\N
\.


--
-- TOC entry 5951 (class 0 OID 24587)
-- Dependencies: 224
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name) FROM stdin;
1	SCHOLARSHIP
2	KID
3	YOUTH
4	ADULT
\.


--
-- TOC entry 5972 (class 0 OID 24808)
-- Dependencies: 245
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (id, id_schedule, id_instructor, date, status, note, created_at, guest_count, guest_names) FROM stdin;
4	25	13	2026-06-25	scheduled	\N	2026-06-25 22:35:34.035838	0	\N
5	27	11	2026-07-16	scheduled	\N	2026-07-17 00:49:25.957211	0	\N
6	24	13	2026-07-24	scheduled	\N	2026-07-20 01:28:36.159266	0	\N
7	22	13	2026-07-23	scheduled	\N	2026-07-20 12:58:01.340309	0	\N
8	18	13	2026-07-22	scheduled	\N	2026-07-20 14:09:39.944158	0	\N
9	14	13	2026-07-21	scheduled	\N	2026-07-20 14:20:18.938714	0	\N
10	11	13	2026-07-20	scheduled	\N	2026-07-20 14:52:05.534299	0	\N
12	13	13	2026-07-20	scheduled	\N	2026-07-20 22:07:01.82747	0	\N
11	12	11	2026-07-20	completed	\N	2026-07-20 22:06:12.825491	0	\N
13	14	13	2026-07-28	scheduled	\N	2026-07-28 21:27:25.198321	0	\N
\.


--
-- TOC entry 6004 (class 0 OID 32777)
-- Dependencies: 277
-- Data for Name: codes_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.codes_users (id, code, id_role) FROM stdin;
1	Kyokushin4life	1
2	Padressenshipres	2
3	SenshiFightAcademy	3
4	instructOr2026-1	4
5	Sppresente2026-06	5
\.


--
-- TOC entry 6064 (class 0 OID 41651)
-- Dependencies: 337
-- Data for Name: collection_account_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collection_account_items (id, collection_account_id, activity_type, description, quantity, unit_price, subtotal, activity_date, penalty) FROM stdin;
\.


--
-- TOC entry 6056 (class 0 OID 41550)
-- Dependencies: 329
-- Data for Name: collection_account_items_old; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collection_account_items_old (id, account_id, name, description, quantity, unit_price, discount, subtotal) FROM stdin;
\.


--
-- TOC entry 6062 (class 0 OID 41625)
-- Dependencies: 335
-- Data for Name: collection_accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collection_accounts (id, person_id, person_name, concept, total_amount, status, due_date, issued_date, notes, scholarship_id, period_month, period_year, created_at) FROM stdin;
\.


--
-- TOC entry 6054 (class 0 OID 41515)
-- Dependencies: 327
-- Data for Name: collection_accounts_old; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.collection_accounts_old (id, client_name, client_person_id, client_document, client_email, client_phone, account_date, due_date, subtotal, scholarship_id, scholarship_discount, total, total_paid, pending_amount, status, note, created_at) FROM stdin;
\.


--
-- TOC entry 5980 (class 0 OID 24878)
-- Dependencies: 253
-- Data for Name: destination_account; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.destination_account (id, name, account_number) FROM stdin;
\.


--
-- TOC entry 6086 (class 0 OID 49506)
-- Dependencies: 359
-- Data for Name: discipline_exercises; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.discipline_exercises (id, martial_art_id, name, description, exercise_type, difficulty, duration_minutes, sort_order, is_active, image_path, created_at, updated_at) FROM stdin;
1	4	dfasfsa	fasdfsa	Fuerza	Basico	\N	0	t	C:\\Users\\Sebastian Galvan\\AppData\\Roaming\\python\\media\\exercises\\2d4855a533f84dfbacdb7f63683906b9.png	2026-08-01 23:19:02.334819	2026-08-01 23:40:13.035085
\.


--
-- TOC entry 6068 (class 0 OID 49224)
-- Dependencies: 341
-- Data for Name: event_followers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_followers (id, event_id, user_id, notifications_enabled, followed_at) FROM stdin;
\.


--
-- TOC entry 6070 (class 0 OID 49251)
-- Dependencies: 343
-- Data for Name: event_interest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_interest (id, event_id, user_id, response, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 6076 (class 0 OID 49339)
-- Dependencies: 349
-- Data for Name: event_posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_posts (id, event_id, author_user_id, content, image_path, is_pinned, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 6072 (class 0 OID 49278)
-- Dependencies: 345
-- Data for Name: event_registrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_registrations (id, event_id, user_id, student_id, registration_status, payment_status, notes, registered_at, updated_at) FROM stdin;
\.


--
-- TOC entry 6074 (class 0 OID 49315)
-- Dependencies: 347
-- Data for Name: event_schedule_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_schedule_items (id, event_id, title, description, starts_at, ends_at, location, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 6016 (class 0 OID 40972)
-- Dependencies: 289
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, name, event_date, event_type, description, color, start_time, end_time, location, is_important, created_at, short_description, organizer_user_id, martial_art_id, end_date, venue_name, address, city, country, cover_image_path, capacity, registration_deadline, price, status, visibility, is_featured, registration_enabled, published_at, updated_at) FROM stdin;
1	torneo	2026-06-27	torneo	\N	#3B82F6	\N	\N	\N	f	2026-06-23 15:07:41.642051	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	draft	internal	f	f	\N	2026-07-21 00:32:52.537069
2	torneo	2026-07-21	torneo	bahjksldoiuyhgbhnm,loiuhbnmkiujh	#3B82F6	09:00:00	17:00:00	dojo	f	2026-07-21 01:59:02.279352	hjksd	1	\N	2026-07-21	tatami			Colombia	C:\\Users\\Sebastian Galvan\\AppData\\Local\\SenshiFightAcademy\\DojoAdmin\\media\\events\\31a44063123342a090ab695583686a3b.png	\N	\N	0.00	published	internal	f	f	2026-07-21 01:59:02.279352	2026-07-21 02:31:03.912981
3	mayita	2026-07-28	torneo	dasffsdafsafsdf	#3B82F6	09:00:00	17:00:00	fhkads	f	2026-07-28 21:11:57.966836	dsafdsadf	1	\N	2026-07-28	akjdsfj	fsadfs		Colombia	C:\\Users\\Sebastian Galvan\\AppData\\Local\\SenshiFightAcademy\\DojoAdmin\\media\\events\\1f5ebdb3d1fc4a5baa3db9fe9bde3c2e.png	\N	2026-07-28 00:00:00	0.00	registration_open	public	f	t	2026-07-28 21:11:57.966836	2026-07-28 21:11:57.966836
\.


--
-- TOC entry 5994 (class 0 OID 25020)
-- Dependencies: 267
-- Data for Name: expense_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_categories (id, name, description) FROM stdin;
\.


--
-- TOC entry 5996 (class 0 OID 25033)
-- Dependencies: 269
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, id_expense_category, id_destination_account, amount, expense_date, description, invoice_number, created_at) FROM stdin;
\.


--
-- TOC entry 6042 (class 0 OID 41366)
-- Dependencies: 315
-- Data for Name: finance_expense_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_categories (id, name, description, expense_type) FROM stdin;
2	Gasto variable	Gastos no recurrentes	variable
3	Compra inventario	Compra de productos para inventario	variable
\.


--
-- TOC entry 6048 (class 0 OID 41427)
-- Dependencies: 321
-- Data for Name: finance_expense_inventory_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_inventory_items (id, expense_id, product_id, quantity, unit_cost, total_cost) FROM stdin;
\.


--
-- TOC entry 6044 (class 0 OID 41380)
-- Dependencies: 317
-- Data for Name: finance_expense_subcategories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_subcategories (id, category_id, name, description) FROM stdin;
\.


--
-- TOC entry 6046 (class 0 OID 41400)
-- Dependencies: 319
-- Data for Name: finance_expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expenses (id, category_id, subcategory_id, expense_date, amount, description, supplier_name, invoice_number, payment_method_id, destination_account_id, affects_inventory, created_at, expense_type) FROM stdin;
\.


--
-- TOC entry 6032 (class 0 OID 41225)
-- Dependencies: 305
-- Data for Name: finance_income; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_income (id, payer_person_id, payer_name, payer_type, income_date, subtotal, discount, total, total_paid, pending_amount, payment_method_id, destination_account_id, status, note, agreement_note, created_at, payer_document, payer_email, payer_phone, receipt_number, receipt_pdf_path, receipt_generated_at) FROM stdin;
2	\N	.	guardian	2026-07-01 00:00:00	255000.00	0.00	255000.00	255000.00	0.00	\N	\N	paid			2026-07-04 14:36:19.467588			.	\N	\N	\N
4	21	Brenda Rodríguez Barrios	student	2026-06-30 00:00:00	551000.00	12000.00	539000.00	434000.00	105000.00	\N	\N	partial	Le estoy pasando\nMatrícula 85.000\nMensualidad 213.000 (cuando se paga los primeros 10 días del mes)\nUniforme anticipo 136.000 mi hija es talla 4	Cartera por concepto:\n- DOGI talla 22: total $253.000, pagado $136.000, pendiente $117.000\n- 1 vez x semana: total $213.000, pagado $213.000, pendiente $0\n- Matricula Nuevos: total $85.000, pagado $85.000, pendiente $0	2026-07-04 23:50:56.789375	1234100989	rodriguezbrendaj28@gmail.com	3244385822	\N	\N	\N
5	22	Marielsa Ortiz Parra Ortiz	student	2026-07-03 00:00:00	675000.00	0.00	675000.00	675000.00	0.00	\N	\N	paid			2026-07-05 18:01:28.912409	1147696311	marielsa.milagro@gmail.com	+573227111205	\N	\N	\N
8	23	Eugenio Díaz	guardian	2026-07-04 00:00:00	213000.00	0.00	213000.00	213000.00	0.00	\N	\N	paid			2026-07-16 01:47:06.889713	1043710614	leoacere@gmail.com	3107261786	\N	\N	\N
9	23	Eugenio Díaz	guardian	2026-07-04 00:00:00	273000.00	0.00	273000.00	273000.00	0.00	\N	\N	paid			2026-07-16 01:50:43.527731	1043710614	leoacere@gmail.com	3107261786	\N	\N	\N
10	24	Lina Barros J	guardian	2026-07-05 00:00:00	213000.00	0.00	213000.00	213000.00	0.00	\N	\N	paid			2026-07-16 01:57:39.602459	1044237201	princesahorus@gmail.com	3003582114	\N	\N	\N
\.


--
-- TOC entry 6034 (class 0 OID 41259)
-- Dependencies: 307
-- Data for Name: finance_income_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_income_items (id, income_id, item_type, reference_id, name, quantity, unit_price, discount, subtotal, details) FROM stdin;
2	2	membership	5	2 veces x semana — Mes: Enero 2026	1	255000.00	0.00	255000.00	
13	4	inventory	8	DOGI talla 22	1	253000.00	0.00	253000.00	__wallet_distribution__={"paid": 136000.0, "pending": 117000.0}
14	4	membership	4	1 vez x semana — Mes: Julio 2026	1	225000.00	12000.00	213000.00	__wallet_distribution__={"paid": 213000.0, "pending": 0.0}
15	4	service	2	Matricula Nuevos — Año matrícula: 2026	1	85000.00	0.00	85000.00	__wallet_distribution__={"paid": 85000.0, "pending": 0.0}
16	5	membership	9	X3 meses adelantados — Meses: Julio → Agosto → Septiembre 2026	1	620000.00	30000.00	590000.00	__wallet_distribution__={"paid": 52.0, "pending": 589948.0}
17	5	service	2	Matricula Nuevos — Año matrícula: 2026	1	85000.00	0.00	85000.00	__wallet_distribution__={"paid": 8.0, "pending": 84992.0}
28	8	membership	4	1 vez x semana — Mes: Julio 2026	1	225000.00	12000.00	213000.00	__wallet_distribution__={"paid": 20.0, "pending": 212980.0}
29	9	inventory	9	DOGI talla 26	1	273000.00	0.00	273000.00	__wallet_distribution__={"paid": 2.0, "pending": 272998.0}
30	10	membership	4	1 vez x semana — Mes: Julio 2026	1	225000.00	12000.00	213000.00	__wallet_distribution__={"paid": 2.0, "pending": 212998.0}
\.


--
-- TOC entry 6036 (class 0 OID 41283)
-- Dependencies: 309
-- Data for Name: finance_income_participants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_income_participants (id, income_id, person_id, display_name, expected_amount, paid_amount, pending_amount, due_date, note) FROM stdin;
2	2	20	Juan Diego Barriga	0.00	0.00	0.00	\N	
8	4	21	Victoria Salomé Rodríguez Barrios	0.00	0.00	0.00	\N	
9	4	21	Brenda Rodríguez Barrios	539000.00	434000.00	105000.00	2026-07-15	
10	5	22	Marielsa Ortiz Parra Ortiz	0.00	0.00	0.00	\N	
22	8	23	Leonardo Mario Díaz Mendoza	0.00	0.00	0.00	\N	
23	9	23	Leonardo Mario Díaz Mendoza	0.00	0.00	0.00	\N	
24	10	24	Kiram Pinzon Barros	0.00	0.00	0.00	\N	
\.


--
-- TOC entry 6040 (class 0 OID 41347)
-- Dependencies: 313
-- Data for Name: finance_receivable_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_receivable_payments (id, receivable_id, payment_date, amount, payment_method_id, destination_account_id, note) FROM stdin;
\.


--
-- TOC entry 6038 (class 0 OID 41312)
-- Dependencies: 311
-- Data for Name: finance_receivables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_receivables (id, person_id, debtor_name, source_income_id, source_participant_id, source_type, original_amount, paid_amount, pending_amount, due_date, created_at, status, note) FROM stdin;
2	\N	Brenda Rodríguez Barrios	4	9	income_pending	539000.00	434000.00	105000.00	2026-07-15	2026-07-05 14:31:59.567623	open	
\.


--
-- TOC entry 6018 (class 0 OID 41029)
-- Dependencies: 291
-- Data for Name: instructor_belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructor_belts (id, id_instructor, id_martial_art, id_belt, assigned_at) FROM stdin;
1	13	1	36	2026-06-26 11:41:05.892307
2	14	3	48	2026-06-29 17:24:45.321253
\.


--
-- TOC entry 6014 (class 0 OID 32868)
-- Dependencies: 287
-- Data for Name: instructor_martial_arts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructor_martial_arts (id, id_instructor, id_martial_art, can_promote) FROM stdin;
11	14	3	t
12	13	2	t
14	13	1	t
15	13	4	t
16	13	3	t
17	14	2	f
18	2	4	f
19	2	2	f
20	2	1	f
21	11	3	f
22	11	4	f
23	11	1	f
24	11	2	f
\.


--
-- TOC entry 5964 (class 0 OID 24743)
-- Dependencies: 237
-- Data for Name: instructors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructors (id, id_person, is_sensei) FROM stdin;
2	6	f
11	1	f
13	14	t
14	15	f
\.


--
-- TOC entry 6024 (class 0 OID 41144)
-- Dependencies: 297
-- Data for Name: inventory_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory_categories (id, name) FROM stdin;
1	PROTECCION
3	UNIFORMES
\.


--
-- TOC entry 6080 (class 0 OID 49429)
-- Dependencies: 353
-- Data for Name: martial_art_initial_levels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martial_art_initial_levels (id, martial_art_id, level_id, created_at) FROM stdin;
\.


--
-- TOC entry 6078 (class 0 OID 49394)
-- Dependencies: 351
-- Data for Name: martial_art_promotion_rules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martial_art_promotion_rules (id, martial_art_id, from_level_id, to_level_id, is_allowed, requires_all_grades, minimum_grade, notes, created_at, updated_at) FROM stdin;
5	2	54	55	t	f	\N	\N	2026-08-02 01:30:17.723603	2026-08-02 01:30:17.723603
\.


--
-- TOC entry 5953 (class 0 OID 24603)
-- Dependencies: 226
-- Data for Name: martial_arts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martial_arts (id, name, icon_key, accent_color, progression_enabled, progression_system, progression_label_singular, progression_label_plural, promotion_mode, allow_level_skips, initial_assignment_mode, template_key, is_active, updated_at, description, training_focus) FROM stdin;
1	Karate Kyokushin	patada	#C8102E	t	belt	Cinturón	Cinturones	sequential	f	first_only	karate_traditional	t	2026-07-25 04:08:27.147523	\N	\N
3	Brazilian Jiu-Jitsu	judo1	#C8102E	t	belt	Cinturón	Cinturones	sequential	f	first_only	bjj_adult	t	2026-07-25 19:32:36.322274	\N	\N
4	Functional Trainning	pesos	#C8102E	f	none	Cinturón	Cinturones	sequential	f	first_only	no_progression	t	2026-07-27 01:50:34.453696	\N	\N
2	Kick Boxing	guantes-de-boxeo	#C8102E	t	shirt	Camisa	Camisas	sequential	f	first_only	shirt_levels	t	2026-08-02 01:30:17.715564	\N	\N
\.


--
-- TOC entry 6026 (class 0 OID 41161)
-- Dependencies: 299
-- Data for Name: membership_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membership_categories (id, name) FROM stdin;
1	PROTECCION
2	GRUPAL
\.


--
-- TOC entry 5986 (class 0 OID 24916)
-- Dependencies: 259
-- Data for Name: membership_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membership_plans (id, id_type_product, name, monthly_fee, discount, discount_by_person, classes_per_week, weekly_classes, is_unlimited, description, benefits, id_membership_category, plan_type, group_capacity, discount_type) FROM stdin;
4	\N	1 vez x semana	225000.00	12000.00	f	\N	1	f		Entrar a cualquier clase (solo una 1 por semana)\nAcceso a la app para estudiantes	\N	individual	1	amount
5	\N	2 veces x semana	255000.00	13000.00	f	\N	2	f		Entrar a cualquier clase (solo 2 veces por semana)\nAcceso a la app para estudiantes	\N	individual	1	amount
6	\N	3 veces x semana	270000.00	14000.00	f	\N	3	f		Entrar a cualquier clase (solo 3 veces por semana)\nAcceso a la app para estudiantes	\N	individual	1	amount
7	\N	Asistir libre a la semana	321000.00	16000.00	f	\N	0	t		Asistir a cualquier clase sin limite\nAcceso a la app para estudiantes	\N	individual	1	amount
8	\N	Grupal X2 personas	453000.00	23000.00	f	\N	0	t		Asistir a cualquier clase sin limite\nAccesos a la app para estudiantes\nasistir a clase con 1 amigo	\N	group	2	amount
9	\N	X3 meses adelantados	620000.00	30000.00	f	\N	0	t			\N	individual	1	amount
\.


--
-- TOC entry 5978 (class 0 OID 24867)
-- Dependencies: 251
-- Data for Name: movement_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.movement_type (id, name) FROM stdin;
1	expenses
2	payments
\.


--
-- TOC entry 5992 (class 0 OID 24991)
-- Dependencies: 265
-- Data for Name: payment_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_items (id, id_payments, id_product, id_membership_plan, quantity, unit_price, subtotal) FROM stdin;
\.


--
-- TOC entry 5976 (class 0 OID 24856)
-- Dependencies: 249
-- Data for Name: payment_method; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_method (id, name) FROM stdin;
\.


--
-- TOC entry 5990 (class 0 OID 24957)
-- Dependencies: 263
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, id_person, total, total_paid, payment_date, id_payment_method, id_destination_account, description, note, created_at) FROM stdin;
\.


--
-- TOC entry 5957 (class 0 OID 24674)
-- Dependencies: 230
-- Data for Name: people; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.people (id, first_name, last_name, phone, email, birthdate, created_at, id_code_users, photo_path, address_line, residence_city, residence_country, birth_city, birth_country, neighborhood, socioeconomic_stratum, profession, residence_details) FROM stdin;
10	Abraham	Lara	+573002167962	abrahamlrpz@gmail.com	2000-12-13	2026-06-23 10:52:29.51703	\N	\N	\N	\N	\N	\N	\N		\N		
12	Efrain	Carillo Rodrigez	+573016264534	efraincarrillorodriguez2024@gmail.com	1991-12-09	2026-06-23 11:05:44.242613	\N	\N	\N	\N	\N	\N	\N		\N		
9	Alberto Enrique	Santiago Hernandez	+573005171615	albertosan_94@hotmail.com	1994-07-28	2026-06-23 09:49:06.088552	\N	\N	\N	\N	\N	\N	\N		\N		
11	Angélica Patricia	Muñoz montesino	+573215561149	Munozmontesinoa@gmail.com	1997-12-13	2026-06-23 10:58:03.277975	\N	\N	\N	\N	\N	\N	\N		\N		
14	Álvaro	Oviedo Villamil	3043825879	aitovi@gmail.com	\N	2026-06-25 19:13:26.584248	\N	\N	\N	\N	\N	\N	\N		\N		
15	Salomón	Watnik	3022411296	\N	\N	2026-06-25 19:22:13.357851	\N	\N	\N	\N	\N	\N	\N		\N		
16	Enzo	Hernandez Fonseca	+573014696321	enzohernandezfonseca@gmail.com	1989-08-23	2026-06-27 17:29:59.678197	\N	\N	\N	\N	\N	\N	\N		\N		
8	Robert Alejandro	Manotas Hernandez	+573218939391	robert.alejandro.manotas@gmail.com	1998-11-08	2026-06-23 09:18:48.291503	\N	\N	\N	\N	\N	\N	\N		\N		
17	Alvaro	Mendez vargas	+573158999565	almevar@gmail.com	1969-06-30	2026-06-27 17:34:22.98005	\N	\N	\N	\N	\N	\N	\N		\N		
18	Claudia Patricia	Gamboa Fajardo	+573165137797	maz.gamboa@gmail.com	1971-06-29	2026-06-27 17:36:53.549105	\N	\N	\N	\N	\N	\N	\N		\N		
19	Sara Victoria	Ilias Solano	\N	\N	2003-09-17	2026-06-27 17:38:20.607559	\N	\N	\N	\N	\N	\N	\N		\N		
20	Juan Diego	Barriga	\N	\N	2008-07-04	2026-07-04 14:30:58.952813	\N	\N	\N	\N	\N	\N	\N		\N		
22	Marielsa Ortiz	Parra Ortiz	+573227111205	marielsa.milagro@gmail.com	1997-02-06	2026-07-05 17:58:48.643035	\N	\N	Carrera 42H #80-167	Barranquilla	Colombia	Maracaibo	Venezuela	Ciudad Jardín	\N	Diseñadora Gráfica e Ilustradora	Apto 503, Edificio Jardín Plaza
23	Leonardo Mario	Díaz Mendoza	\N	\N	2020-02-26	2026-07-16 01:45:40.763355	\N	\N	CARRERA 45 # 82 - 146	Barranquilla	Colombia	Barranquilla	Colombia	Granadillo	\N	\N	\N
24	Kiram	Pinzon Barros	\N	\N	2022-05-21	2026-07-16 01:56:09.308543	\N	\N	CARRERA 8 # 128 - 21	Barranquilla	Colombia	Barranquilla	Colombia	Caribe verde	\N	\N	\N
21	Victoria Salomé	Rodríguez Barrios	\N	\N	2023-01-27	2026-07-04 23:35:46.014584	\N	\N	Calle 69-D #38-138	Barranquilla	Colombia	Caracas	Venezuela	Las Delicias	\N	\N	\N
1	Sebastian	Galvan	+573218005837	sebastianjosegalvanluna090@gmail.com	2006-08-18	2026-06-17 15:59:39.383749	\N	C:/Users/Sebastian Galvan/Pictures/Screenshots/Captura de pantalla 2025-09-03 081857.png	\N	\N	\N	\N	\N	\N	\N	Estudiante	\N
6	Maya	Oviedo Granados	\N	mayaoviedo1@gmail.com	2008-06-29	2026-06-20 00:55:52.873194	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 5960 (class 0 OID 24694)
-- Dependencies: 233
-- Data for Name: person_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.person_roles (id_person, id_role) FROM stdin;
8	5
9	5
10	5
11	5
12	5
1	1
1	5
1	4
14	4
15	4
16	5
17	5
18	5
19	5
6	1
6	4
6	5
20	5
21	5
22	5
23	5
24	5
\.


--
-- TOC entry 6028 (class 0 OID 41172)
-- Dependencies: 301
-- Data for Name: product_purchase_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_purchase_history (id, id_product, buyer_name, purchase_date, quantity, total_price, note) FROM stdin;
\.


--
-- TOC entry 5984 (class 0 OID 24898)
-- Dependencies: 257
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, id_type_product, name, sale_price, stock, id_inventory_category, cost_price, image_path) FROM stdin;
8	1	DOGI talla 22	253000.00	0	3	105000.00	
9	1	DOGI talla 26	273000.00	0	3	111000.00	
\.


--
-- TOC entry 6084 (class 0 OID 49472)
-- Dependencies: 357
-- Data for Name: progression_template_levels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.progression_template_levels (id, template_id, name, orden, color, pre_color, grades, grade_color, icon_key, is_initial, is_final, metadata) FROM stdin;
1	1	Blanco	1	#FFFFFF	\N	0	#333333	\N	t	f	{}
2	1	Amarillo	2	#FFD700	\N	0	#333333	\N	f	f	{}
3	1	Naranja	3	#FF8C00	\N	0	#333333	\N	f	f	{}
4	1	Verde	4	#22C55E	\N	0	#333333	\N	f	f	{}
5	1	Azul	5	#3B82F6	\N	0	#FFFFFF	\N	f	f	{}
6	1	Marrón	6	#8B4513	\N	0	#FFFFFF	\N	f	f	{}
7	1	Negro	7	#1A1A1A	\N	0	#FFFFFF	\N	f	t	{}
8	2	Blanco	1	#FFFFFF	\N	4	#1A1A1A	\N	t	f	{}
9	2	Azul	2	#3B82F6	\N	4	#FFFFFF	\N	f	f	{}
10	2	Morado	3	#7E22CE	\N	4	#FFFFFF	\N	f	f	{}
11	2	Marrón	4	#8B4513	\N	4	#FFFFFF	\N	f	f	{}
12	2	Negro	5	#1A1A1A	\N	0	#FFFFFF	\N	f	t	{}
13	3	Blanco	1	#FFFFFF	\N	0	#333333	\N	t	f	{}
14	3	Amarillo	2	#FFD700	\N	0	#333333	\N	f	f	{}
15	3	Verde	3	#22C55E	\N	0	#333333	\N	f	f	{}
16	3	Azul	4	#3B82F6	\N	0	#FFFFFF	\N	f	f	{}
17	3	Rojo	5	#C8102E	\N	0	#FFFFFF	\N	f	t	{}
18	4	Blanca	1	#FFFFFF	\N	0	#333333	\N	t	f	{}
19	4	Amarilla	2	#FFD700	\N	0	#333333	\N	f	f	{}
20	4	Naranja	3	#FF8C00	\N	0	#333333	\N	f	f	{}
21	4	Verde	4	#22C55E	\N	0	#333333	\N	f	f	{}
22	4	Azul	5	#3B82F6	\N	0	#FFFFFF	\N	f	f	{}
23	4	Negra	6	#1A1A1A	\N	0	#FFFFFF	\N	f	t	{}
\.


--
-- TOC entry 6082 (class 0 OID 49452)
-- Dependencies: 355
-- Data for Name: progression_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.progression_templates (id, template_key, name, description, system_type, icon_key, is_builtin, is_active, created_at) FROM stdin;
1	karate_traditional	Karate tradicional	Sistema de cinturones clásico para karate.	belt	karate	t	t	2026-07-22 00:13:15.128479
2	bjj_adult	BJJ adulto	Sistema de cinturones para Brazilian Jiu-Jitsu.	belt	bjj	t	t	2026-07-22 00:13:15.128479
3	muay_thai_prajiad	Muay Thai - Brazaletes	Plantilla de brazaletes/niveles para Muay Thai.	bracelet	muay-thai	t	t	2026-07-22 00:13:15.128479
4	shirt_levels	Camisas por nivel	Sistema de camisas de colores para artes marciales.	shirt	shirt	t	t	2026-07-22 00:13:15.128479
5	no_progression	Sin progresión	Sin niveles. Ideal para entrenamiento funcional.	none	functional-training	t	t	2026-07-22 00:13:15.128479
6	custom	Personalizado	Plantilla editable desde cero.	custom	generic-martial-art	t	t	2026-07-22 00:13:15.128479
\.


--
-- TOC entry 5959 (class 0 OID 24685)
-- Dependencies: 232
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name) FROM stdin;
1	admin
2	acudent
3	visit
4	instructor
5	student
\.


--
-- TOC entry 5970 (class 0 OID 24795)
-- Dependencies: 243
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule (id, id_martial_art, name, id_instructor, day_of_week, start_time, end_time, capacity, location, color, status, repeat_type, created_at) FROM stdin;
13	1	KYOKUSHIN KARATE	13	0	19:30:00	20:30:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:17:45.153203
14	1	KYOKUSHIN KARATE AM	13	1	06:00:00	07:00:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:18:25.547491
15	1	KIDS A	13	1	16:30:00	17:30:00	\N	\N	#ffff00	active	weekly	2026-06-25 19:20:04.908589
16	2	SENSHI KICKBOXING	13	1	18:30:00	19:30:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:21:29.511764
17	3	BRAZILIAN JIU-JITSU	14	1	19:30:00	20:30:00	\N	\N	#55007f	active	weekly	2026-06-25 19:24:13.482748
18	2	SENSHI KICKBOXING AM	13	2	06:00:00	07:00:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:28:03.202436
19	1	KIDS B	11	2	17:30:00	18:30:00	\N	\N	#ffff00	active	weekly	2026-06-25 19:28:48.136171
12	4	FUNCTIONAL TRAINING	11	0	18:30:00	19:30:00	\N	\N	#00ff00	active	weekly	2026-06-25 19:17:12.43924
20	4	FUNCTIONAL TRAINING	11	2	18:30:00	19:30:00	\N	\N	#00ff00	active	weekly	2026-06-25 19:29:21.449893
21	1	KYOKUSHIN KARATE	13	2	19:30:00	20:30:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:31:16.685157
22	1	KYOKUSHIN KARATE AM	13	3	06:00:00	07:00:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:31:49.983753
23	1	KYOKUSHIN KARATE AM	\N	3	06:00:00	07:00:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:32:17.973343
24	2	SENSHI KICKBOXING AM	13	4	06:00:00	07:00:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:33:13.660137
25	1	KIDS A	13	3	16:30:00	17:30:00	\N	\N	#ffff00	active	weekly	2026-06-25 19:34:07.914541
27	3	BRAZILIAN JIU-JITSU	14	3	19:30:00	20:30:00	\N	\N	#55007f	active	weekly	2026-06-25 19:36:12.174232
29	4	FUNCTIONAL TRAINING	11	4	18:30:00	19:30:00	\N	\N	#00ff00	active	weekly	2026-06-25 19:37:39.225449
30	1	KYOKUSHIN KARATE	13	4	19:30:00	20:30:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:38:42.64588
31	1	KIDS A + B	13	5	10:00:00	11:00:00	\N	\N	#ffff00	active	weekly	2026-06-25 19:39:23.817312
32	1	KYOKUSHIN KARATE	13	5	11:00:00	12:00:00	\N	\N	#aa0000	active	weekly	2026-06-25 19:40:04.185741
33	2	SENSHI KICKBOXING	13	5	12:00:00	13:00:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:40:43.461749
34	3	BRAZILIAN JIU-JITSU	14	5	13:00:00	14:00:00	\N	\N	#55007f	active	weekly	2026-06-25 19:41:28.686794
26	2	SENSHI KICKBOXING	13	3	18:30:00	19:30:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:35:19.918052
28	1	KIDS B	11	4	17:30:00	18:30:00	\N	\N	#ffff00	active	weekly	2026-06-25 19:36:46.956523
11	2	SENSHI KICKBOXING AM	13	0	06:00:00	07:00:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:15:49.210585
\.


--
-- TOC entry 6060 (class 0 OID 41600)
-- Dependencies: 333
-- Data for Name: scholarships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scholarships (id, person_id, monthly_fee, start_date, end_date, status, rate_class, rate_deep_clean, rate_maintenance, penalty_per_miss, notes, created_at) FROM stdin;
1	1	0.00	2026-07-16	2027-07-16	active	25000.00	50000.00	25000.00	25000.00		2026-07-16 02:52:23.050378
\.


--
-- TOC entry 6058 (class 0 OID 41576)
-- Dependencies: 331
-- Data for Name: scholarships_old; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scholarships_old (id, name, description, discount_percent, is_active, created_at) FROM stdin;
2	Beca Académica	Descuento por excelencia académica	15.00	t	2026-07-16 01:30:07.829916
\.


--
-- TOC entry 6030 (class 0 OID 41210)
-- Dependencies: 303
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.services (id, name, description, price, icon, accent_color, is_active) FROM stdin;
4	Examen Pre-marron	examen de pre-marron kyokushin karate	350000.00	💪	#aa0000	t
2	Matricula Nuevos	Matricula para los estudiantes nuevos	85000.00	📋	#ffff00	t
3	Examen de Ascenso	Evaluación para cambio de cinturón	25000.00	🚀	#3B82F6	f
5	Clase Personalizada	Clase uno a uno con instructor	45000.00	🚀	#3B82F6	f
1	Matrícula Anual	Cobertura anual de matrícula	50000.00	🚀	#3B82F6	f
\.


--
-- TOC entry 5949 (class 0 OID 16435)
-- Dependencies: 222
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status (id, status) FROM stdin;
1	ACTIVE
2	RETIRED
3	INACTIVE
\.


--
-- TOC entry 6052 (class 0 OID 41490)
-- Dependencies: 325
-- Data for Name: student_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_documents (id, id_student, doc_type, file_path, uploaded_at) FROM stdin;
2	8	eps_certificate	C:/Users/Sebastian Galvan/Downloads/firme may.pdf	2026-07-18 22:51:35.057412
\.


--
-- TOC entry 6022 (class 0 OID 41121)
-- Dependencies: 295
-- Data for Name: student_emergency_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_emergency_contacts (id, id_student, full_name, phone, email, relationship, note, is_primary, created_at) FROM stdin;
1	16	Marielsa Ortiz	+57 304 4628037	\N	Madre	\N	t	2026-07-05 17:58:49.099914
\.


--
-- TOC entry 6020 (class 0 OID 41101)
-- Dependencies: 293
-- Data for Name: student_guardians; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_guardians (id, id_student, full_name, phone, email, relationship, is_primary, created_at, document, profession) FROM stdin;
1	14	.	.	\N	.	t	2026-07-04 14:30:59.161484		
3	17	Eugenio Díaz	3107261786	leoacere@gmail.com	ABUELO	t	2026-07-16 01:45:40.971831	3726969	\N
4	18	Lina Barros J	3003582114	princesahorus@gmail.com	MADRE	t	2026-07-16 01:56:09.513752	55222023	ING. INDUSTRIAL
2	15	Brenda Rodríguez Barrios	3244385822	rodriguezbrendaj28@gmail.com	MADRE	t	2026-07-04 23:35:46.43902	1234095584	Consultor de Recursos humanos - Reclutador Internacional
\.


--
-- TOC entry 6050 (class 0 OID 41465)
-- Dependencies: 323
-- Data for Name: student_health_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_health_info (id, id_student, eps, ips, blood_type, allergies, medical_conditions, notes, created_at, updated_at) FROM stdin;
3	16	Sura	\N	B+	Ninguna	Discapacidad auditiva y visión monocular	\N	2026-07-05 17:58:49.106078	2026-07-05 17:58:49.106078
4	17	Sanitas	\N	O+	\N	\N	\N	2026-07-16 01:45:40.973001	2026-07-16 01:45:40.973001
5	18	Sanitas	\N	O+	\N	\N	\N	2026-07-16 01:56:09.515219	2026-07-16 01:56:09.515219
2	15	\N	\N	\N	Ninguna	Ninguna	\N	2026-07-05 01:46:06.136654	2026-07-18 22:00:42.344038
7	8	\N	\N	O+	\N	\N	\N	2026-07-18 22:51:35.05239	2026-07-19 01:30:46.549844
10	13	\N	\N	\N	\N	\N	\N	2026-07-20 15:23:33.967813	2026-07-20 15:23:33.967813
\.


--
-- TOC entry 5988 (class 0 OID 24935)
-- Dependencies: 261
-- Data for Name: student_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_memberships (id, id_student, id_membership_plan, custom_fee, status, start_date, end_date) FROM stdin;
\.


--
-- TOC entry 5962 (class 0 OID 24713)
-- Dependencies: 235
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, id_person, id_type_document, document, category_id, id_status, joined_date, school_name) FROM stdin;
5	10	3	1002156683	4	3	2025-08-01	
7	12	3	1140846453	4	1	2025-01-01	
4	9	3	1140870388	4	1	2026-01-31	
6	11	3	1042457203	4	3	2026-02-01	
9	16	3	1045682243	4	1	2022-10-03	
3	8	3	1045755940	4	1	2025-05-31	
10	17	3	79486427	4	3	2025-01-01	
11	18	3	52618381	4	3	2025-01-01	
12	19	3	\N	\N	\N	2026-06-27	
14	20	\N	\N	2	1	2026-07-04	
16	22	3	1147696311	4	1	2026-07-03	\N
17	23	1	1043710614	2	1	2026-06-02	Colegio Nuevo del prado
18	24	1	1044237201	2	1	2026-05-30	Centro Educativo del Country
15	21	5	1234100989	2	1	2026-07-01	\N
8	1	3	1043442653	1	1	2026-06-24	\N
13	6	3	\N	1	1	2026-06-29	\N
\.


--
-- TOC entry 5966 (class 0 OID 24758)
-- Dependencies: 239
-- Data for Name: students_belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_belts (id, id_student, id_belt) FROM stdin;
4	3	17
5	4	1
6	3	5
7	8	17
8	8	11
9	9	12
10	13	13
\.


--
-- TOC entry 5968 (class 0 OID 24776)
-- Dependencies: 241
-- Data for Name: students_belts_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_belts_history (id, id_student, id_belt, action, date_changed) FROM stdin;
11	3	17	asignacion inicial	2026-06-23 09:49:41.208724
12	3	17	promotion	2026-06-23 09:49:41.208724
13	4	1	asignacion inicial	2026-06-23 09:50:18.989583
14	4	1	promotion	2026-06-23 09:50:18.989583
15	3	5	asignacion inicial	2026-06-23 09:51:23.004934
16	3	5	promotion	2026-06-23 09:51:23.004934
17	8	17	asignacion inicial	2026-06-24 23:50:31.866779
18	8	17	promotion	2026-06-24 23:50:31.866779
19	8	11	asignacion inicial	2026-06-27 01:28:36.568433
20	8	11	promotion	2026-06-27 01:28:36.568433
21	9	12	asignacion inicial	2026-06-27 17:30:58.134207
22	9	12	promotion	2026-06-27 17:30:58.134207
23	13	13	asignacion inicial	2026-06-29 18:08:34.503966
24	13	13	promotion	2026-06-29 18:08:34.588632
\.


--
-- TOC entry 6008 (class 0 OID 32805)
-- Dependencies: 281
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, task, id_type_task, limit_date) FROM stdin;
1	terminar el app del dajo	\N	2026-06-21
\.


--
-- TOC entry 5947 (class 0 OID 16427)
-- Dependencies: 220
-- Data for Name: type_document; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_document (id, type_document) FROM stdin;
1	T.I
2	C.E
3	C.C
5	R.C
\.


--
-- TOC entry 5982 (class 0 OID 24887)
-- Dependencies: 255
-- Data for Name: type_products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_products (id, name) FROM stdin;
1	PROTECCION
2	GRUPAL
\.


--
-- TOC entry 6010 (class 0 OID 32821)
-- Dependencies: 283
-- Data for Name: type_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_requirements (id, type_requirement) FROM stdin;
1	Tecnico
\.


--
-- TOC entry 6002 (class 0 OID 32769)
-- Dependencies: 275
-- Data for Name: type_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_student (id, name) FROM stdin;
\.


--
-- TOC entry 6006 (class 0 OID 32797)
-- Dependencies: 279
-- Data for Name: type_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_task (id, name) FROM stdin;
\.


--
-- TOC entry 6066 (class 0 OID 49153)
-- Dependencies: 339
-- Data for Name: user_notification_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_notification_preferences (id, user_id, classes_enabled, classes_in_app, classes_windows, classes_minutes_before, classes_notify_at_start, events_enabled, events_in_app, events_windows, events_minutes_before, events_notify_at_start, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 6000 (class 0 OID 25086)
-- Dependencies: 273
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, id_person, username, password_hash, is_active, created_at) FROM stdin;
7	10	abraham.lara	$2b$12$hQZZtkUnpBk5N/s2Qn8mt.ClCrAFJA8/omfdK/pgdmh090zBD1aAO	t	2026-06-23 10:52:29.51703
9	12	efrain.carrillo	$2b$12$VXMgG4jxquiI/rM7CcVDpeWrVV/Jq3bXteUMYcZaz3YFwu6tQ.ZMy	t	2026-06-23 11:05:44.242613
6	9	alberto.enrique	$2b$12$G6t1d5xnh2g1UZK3XXRhxOpmXitKFWDBYUKrB0K.deD6s2SIaUP6u	t	2026-06-23 09:49:06.088552
8	11	angelica.muñoz	$2b$12$AUbXRd7p7pZ.tbaVGexxAuxI5i4SvM0rxH/kmiCWUnbkkqqIQM.g6	t	2026-06-23 10:58:03.277975
10	16	1045682243	$2b$12$QNHXIPmXxFyOHs5a2CXYDullgGofsjkH7U4eVQ7ZJiReeW0G/sPX2	t	2026-06-27 17:29:59.678197
5	8	1045755940	$2b$12$0rF0z0ZZTQNHcQ9IpG8KVOhxJY1bT7dIivgGMFU1bbS8JpNC8k/ae	t	2026-06-23 09:18:48.291503
11	17	79486427	$2b$12$MSADWUxt03WcD9S9FyzvEOmFPIIY0Wvct0N.GVE5hIIUqxUSKK6uW	t	2026-06-27 17:34:22.98005
12	18	52618381	$2b$12$LE2jcslw52hn8gOapjwQxeSQDTk5qGdmo3ryxeoiCIrdZhOF6qvv6	t	2026-06-27 17:36:53.549105
13	19	saravictoria.iliassolano	$2b$12$yZ2gw4cSH4TQ/vjjqw5enOwlFTv2FrH59hsrRC7w1z4IMEvB3aKQi	t	2026-06-27 17:38:20.607559
14	20	juandiego.barriga	$2b$12$e03J6nb4.aS5QpYOmWEtoevHfwys6mdPkwgyW5Aaw988mQ9sw1pXW	t	2026-07-04 14:30:59.156493
15	21	1234100989	$2b$12$REnvxlVR/oj0xmiWRy4cpuGYk.8V7uWyZ7PcSjPrFEIQoqn9Nc7JG	t	2026-07-04 23:35:46.389394
16	22	1147696311	$2b$12$nx1yB2/weVxa461gXYcKNe2AQAwawm.NNenEHqDP1oim23L68kkYa	t	2026-07-05 17:58:49.041289
17	23	1043710614	$2b$12$XmavSbIitorlFhKbQAvN1OT93GcUXEYGw9TBIjFrf3VSV46wW56JK	t	2026-07-16 01:45:40.967704
18	24	1044237201	$2b$12$WODvIDMViLu.7Hx8Y/Fx2ef/fMCk5PMUcxfaTwBpo7Fil8hOXP3lG	t	2026-07-16 01:56:09.510679
1	1	Sebastiangalvan	$2b$12$C9ASqUYqmRpqGOnHNYHK1uPHfNxwxzZ9tciuMuuC1ZJOy18Z4b7bS	t	2026-06-18 11:52:07.102197
4	6	maya.oviedo	$2b$12$9BVmGgNBLsuR4usEAZu9ueXzXx7xa0a3zIh2w1JZglYKa/aI7rqp6	t	2026-06-20 00:55:52.873194
\.


--
-- TOC entry 6149 (class 0 OID 0)
-- Dependencies: 270
-- Name: account_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.account_movements_id_seq', 1, false);


--
-- TOC entry 6150 (class 0 OID 0)
-- Dependencies: 246
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_id_seq', 5, true);


--
-- TOC entry 6151 (class 0 OID 0)
-- Dependencies: 284
-- Name: belt_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belt_requirements_id_seq', 3, true);


--
-- TOC entry 6152 (class 0 OID 0)
-- Dependencies: 227
-- Name: belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belts_id_seq', 55, true);


--
-- TOC entry 6153 (class 0 OID 0)
-- Dependencies: 223
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 4, true);


--
-- TOC entry 6154 (class 0 OID 0)
-- Dependencies: 244
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classes_id_seq', 13, true);


--
-- TOC entry 6155 (class 0 OID 0)
-- Dependencies: 276
-- Name: codes_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.codes_users_id_seq', 5, true);


--
-- TOC entry 6156 (class 0 OID 0)
-- Dependencies: 328
-- Name: collection_account_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_account_items_id_seq', 1, false);


--
-- TOC entry 6157 (class 0 OID 0)
-- Dependencies: 336
-- Name: collection_account_items_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_account_items_id_seq1', 1, false);


--
-- TOC entry 6158 (class 0 OID 0)
-- Dependencies: 326
-- Name: collection_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_accounts_id_seq', 1, false);


--
-- TOC entry 6159 (class 0 OID 0)
-- Dependencies: 334
-- Name: collection_accounts_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.collection_accounts_id_seq1', 1, false);


--
-- TOC entry 6160 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.destination_account_id_seq', 1, false);


--
-- TOC entry 6161 (class 0 OID 0)
-- Dependencies: 358
-- Name: discipline_exercises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.discipline_exercises_id_seq', 1, true);


--
-- TOC entry 6162 (class 0 OID 0)
-- Dependencies: 340
-- Name: event_followers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_followers_id_seq', 1, false);


--
-- TOC entry 6163 (class 0 OID 0)
-- Dependencies: 342
-- Name: event_interest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_interest_id_seq', 1, false);


--
-- TOC entry 6164 (class 0 OID 0)
-- Dependencies: 348
-- Name: event_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_posts_id_seq', 1, false);


--
-- TOC entry 6165 (class 0 OID 0)
-- Dependencies: 344
-- Name: event_registrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_registrations_id_seq', 1, false);


--
-- TOC entry 6166 (class 0 OID 0)
-- Dependencies: 346
-- Name: event_schedule_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_schedule_items_id_seq', 1, false);


--
-- TOC entry 6167 (class 0 OID 0)
-- Dependencies: 288
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 3, true);


--
-- TOC entry 6168 (class 0 OID 0)
-- Dependencies: 266
-- Name: expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_categories_id_seq', 1, false);


--
-- TOC entry 6169 (class 0 OID 0)
-- Dependencies: 268
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- TOC entry 6170 (class 0 OID 0)
-- Dependencies: 314
-- Name: finance_expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_categories_id_seq', 4, true);


--
-- TOC entry 6171 (class 0 OID 0)
-- Dependencies: 320
-- Name: finance_expense_inventory_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_inventory_items_id_seq', 1, false);


--
-- TOC entry 6172 (class 0 OID 0)
-- Dependencies: 316
-- Name: finance_expense_subcategories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_subcategories_id_seq', 1, true);


--
-- TOC entry 6173 (class 0 OID 0)
-- Dependencies: 318
-- Name: finance_expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expenses_id_seq', 1, true);


--
-- TOC entry 6174 (class 0 OID 0)
-- Dependencies: 304
-- Name: finance_income_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_id_seq', 10, true);


--
-- TOC entry 6175 (class 0 OID 0)
-- Dependencies: 306
-- Name: finance_income_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_items_id_seq', 30, true);


--
-- TOC entry 6176 (class 0 OID 0)
-- Dependencies: 308
-- Name: finance_income_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_participants_id_seq', 24, true);


--
-- TOC entry 6177 (class 0 OID 0)
-- Dependencies: 312
-- Name: finance_receivable_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_receivable_payments_id_seq', 1, false);


--
-- TOC entry 6178 (class 0 OID 0)
-- Dependencies: 310
-- Name: finance_receivables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_receivables_id_seq', 3, true);


--
-- TOC entry 6179 (class 0 OID 0)
-- Dependencies: 290
-- Name: instructor_belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructor_belts_id_seq', 2, true);


--
-- TOC entry 6180 (class 0 OID 0)
-- Dependencies: 286
-- Name: instructor_martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructor_martial_arts_id_seq', 24, true);


--
-- TOC entry 6181 (class 0 OID 0)
-- Dependencies: 236
-- Name: instructors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructors_id_seq', 14, true);


--
-- TOC entry 6182 (class 0 OID 0)
-- Dependencies: 296
-- Name: inventory_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_categories_id_seq', 3, true);


--
-- TOC entry 6183 (class 0 OID 0)
-- Dependencies: 352
-- Name: martial_art_initial_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martial_art_initial_levels_id_seq', 1, false);


--
-- TOC entry 6184 (class 0 OID 0)
-- Dependencies: 350
-- Name: martial_art_promotion_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martial_art_promotion_rules_id_seq', 5, true);


--
-- TOC entry 6185 (class 0 OID 0)
-- Dependencies: 225
-- Name: martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martial_arts_id_seq', 4, true);


--
-- TOC entry 6186 (class 0 OID 0)
-- Dependencies: 298
-- Name: membership_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_categories_id_seq', 2, true);


--
-- TOC entry 6187 (class 0 OID 0)
-- Dependencies: 258
-- Name: membership_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_plans_id_seq', 9, true);


--
-- TOC entry 6188 (class 0 OID 0)
-- Dependencies: 250
-- Name: movement_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movement_type_id_seq', 2, true);


--
-- TOC entry 6189 (class 0 OID 0)
-- Dependencies: 264
-- Name: payment_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_items_id_seq', 1, false);


--
-- TOC entry 6190 (class 0 OID 0)
-- Dependencies: 248
-- Name: payment_method_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_method_id_seq', 1, false);


--
-- TOC entry 6191 (class 0 OID 0)
-- Dependencies: 262
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- TOC entry 6192 (class 0 OID 0)
-- Dependencies: 229
-- Name: people_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.people_id_seq', 24, true);


--
-- TOC entry 6193 (class 0 OID 0)
-- Dependencies: 300
-- Name: product_purchase_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_purchase_history_id_seq', 1, false);


--
-- TOC entry 6194 (class 0 OID 0)
-- Dependencies: 256
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 9, true);


--
-- TOC entry 6195 (class 0 OID 0)
-- Dependencies: 356
-- Name: progression_template_levels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.progression_template_levels_id_seq', 23, true);


--
-- TOC entry 6196 (class 0 OID 0)
-- Dependencies: 354
-- Name: progression_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.progression_templates_id_seq', 6, true);


--
-- TOC entry 6197 (class 0 OID 0)
-- Dependencies: 231
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 5, true);


--
-- TOC entry 6198 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_id_seq', 34, true);


--
-- TOC entry 6199 (class 0 OID 0)
-- Dependencies: 330
-- Name: scholarships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scholarships_id_seq', 3, true);


--
-- TOC entry 6200 (class 0 OID 0)
-- Dependencies: 332
-- Name: scholarships_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scholarships_id_seq1', 1, true);


--
-- TOC entry 6201 (class 0 OID 0)
-- Dependencies: 302
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.services_id_seq', 5, true);


--
-- TOC entry 6202 (class 0 OID 0)
-- Dependencies: 221
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.status_id_seq', 33, true);


--
-- TOC entry 6203 (class 0 OID 0)
-- Dependencies: 324
-- Name: student_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_documents_id_seq', 2, true);


--
-- TOC entry 6204 (class 0 OID 0)
-- Dependencies: 294
-- Name: student_emergency_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_emergency_contacts_id_seq', 1, true);


--
-- TOC entry 6205 (class 0 OID 0)
-- Dependencies: 292
-- Name: student_guardians_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_guardians_id_seq', 4, true);


--
-- TOC entry 6206 (class 0 OID 0)
-- Dependencies: 322
-- Name: student_health_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_health_info_id_seq', 10, true);


--
-- TOC entry 6207 (class 0 OID 0)
-- Dependencies: 260
-- Name: student_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_memberships_id_seq', 1, false);


--
-- TOC entry 6208 (class 0 OID 0)
-- Dependencies: 240
-- Name: students_belts_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_history_id_seq', 24, true);


--
-- TOC entry 6209 (class 0 OID 0)
-- Dependencies: 238
-- Name: students_belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_id_seq', 10, true);


--
-- TOC entry 6210 (class 0 OID 0)
-- Dependencies: 234
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 18, true);


--
-- TOC entry 6211 (class 0 OID 0)
-- Dependencies: 280
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, true);


--
-- TOC entry 6212 (class 0 OID 0)
-- Dependencies: 219
-- Name: type_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_document_id_seq', 5, true);


--
-- TOC entry 6213 (class 0 OID 0)
-- Dependencies: 254
-- Name: type_products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_products_id_seq', 2, true);


--
-- TOC entry 6214 (class 0 OID 0)
-- Dependencies: 282
-- Name: type_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_requirements_id_seq', 1, true);


--
-- TOC entry 6215 (class 0 OID 0)
-- Dependencies: 274
-- Name: type_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_student_id_seq', 1, false);


--
-- TOC entry 6216 (class 0 OID 0)
-- Dependencies: 278
-- Name: type_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_task_id_seq', 1, false);


--
-- TOC entry 6217 (class 0 OID 0)
-- Dependencies: 338
-- Name: user_notification_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_notification_preferences_id_seq', 1, false);


--
-- TOC entry 6218 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- TOC entry 5572 (class 2606 OID 25070)
-- Name: account_movements account_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT account_movements_pkey PRIMARY KEY (id);


--
-- TOC entry 5536 (class 2606 OID 24839)
-- Name: attendance attendance_id_class_id_student_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_id_student_key UNIQUE (id_class, id_student);


--
-- TOC entry 5538 (class 2606 OID 24837)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 5591 (class 2606 OID 32856)
-- Name: belt_requirements belt_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5508 (class 2606 OID 24622)
-- Name: belts belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5500 (class 2606 OID 24596)
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- TOC entry 5502 (class 2606 OID 24594)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5534 (class 2606 OID 24814)
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- TOC entry 5582 (class 2606 OID 32787)
-- Name: codes_users codes_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users
    ADD CONSTRAINT codes_users_pkey PRIMARY KEY (id, id_role);


--
-- TOC entry 5654 (class 2606 OID 41569)
-- Name: collection_account_items_old collection_account_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items_old
    ADD CONSTRAINT collection_account_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5663 (class 2606 OID 41664)
-- Name: collection_account_items collection_account_items_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items
    ADD CONSTRAINT collection_account_items_pkey1 PRIMARY KEY (id);


--
-- TOC entry 5650 (class 2606 OID 41543)
-- Name: collection_accounts_old collection_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts_old
    ADD CONSTRAINT collection_accounts_pkey PRIMARY KEY (id);


--
-- TOC entry 5661 (class 2606 OID 41639)
-- Name: collection_accounts collection_accounts_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts
    ADD CONSTRAINT collection_accounts_pkey1 PRIMARY KEY (id);


--
-- TOC entry 5550 (class 2606 OID 24885)
-- Name: destination_account destination_account_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account
    ADD CONSTRAINT destination_account_pkey PRIMARY KEY (id);


--
-- TOC entry 5702 (class 2606 OID 49524)
-- Name: discipline_exercises discipline_exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discipline_exercises
    ADD CONSTRAINT discipline_exercises_pkey PRIMARY KEY (id);


--
-- TOC entry 5670 (class 2606 OID 49235)
-- Name: event_followers event_followers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_followers
    ADD CONSTRAINT event_followers_pkey PRIMARY KEY (id);


--
-- TOC entry 5676 (class 2606 OID 49264)
-- Name: event_interest event_interest_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_interest
    ADD CONSTRAINT event_interest_pkey PRIMARY KEY (id);


--
-- TOC entry 5685 (class 2606 OID 49355)
-- Name: event_posts event_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_posts
    ADD CONSTRAINT event_posts_pkey PRIMARY KEY (id);


--
-- TOC entry 5680 (class 2606 OID 49297)
-- Name: event_registrations event_registrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_registrations
    ADD CONSTRAINT event_registrations_pkey PRIMARY KEY (id);


--
-- TOC entry 5683 (class 2606 OID 49332)
-- Name: event_schedule_items event_schedule_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_schedule_items
    ADD CONSTRAINT event_schedule_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5597 (class 2606 OID 40984)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- TOC entry 5566 (class 2606 OID 25031)
-- Name: expense_categories expense_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_name_key UNIQUE (name);


--
-- TOC entry 5568 (class 2606 OID 25029)
-- Name: expense_categories expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5570 (class 2606 OID 25047)
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- TOC entry 5631 (class 2606 OID 41378)
-- Name: finance_expense_categories finance_expense_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories
    ADD CONSTRAINT finance_expense_categories_name_key UNIQUE (name);


--
-- TOC entry 5633 (class 2606 OID 41376)
-- Name: finance_expense_categories finance_expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories
    ADD CONSTRAINT finance_expense_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5641 (class 2606 OID 41438)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5635 (class 2606 OID 41393)
-- Name: finance_expense_subcategories finance_expense_subcategories_category_id_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_category_id_name_key UNIQUE (category_id, name);


--
-- TOC entry 5637 (class 2606 OID 41391)
-- Name: finance_expense_subcategories finance_expense_subcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_pkey PRIMARY KEY (id);


--
-- TOC entry 5639 (class 2606 OID 41415)
-- Name: finance_expenses finance_expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_pkey PRIMARY KEY (id);


--
-- TOC entry 5623 (class 2606 OID 41276)
-- Name: finance_income_items finance_income_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items
    ADD CONSTRAINT finance_income_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5625 (class 2606 OID 41300)
-- Name: finance_income_participants finance_income_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_pkey PRIMARY KEY (id);


--
-- TOC entry 5621 (class 2606 OID 41252)
-- Name: finance_income finance_income_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income
    ADD CONSTRAINT finance_income_pkey PRIMARY KEY (id);


--
-- TOC entry 5629 (class 2606 OID 41359)
-- Name: finance_receivable_payments finance_receivable_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments
    ADD CONSTRAINT finance_receivable_payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5627 (class 2606 OID 41330)
-- Name: finance_receivables finance_receivables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_pkey PRIMARY KEY (id);


--
-- TOC entry 5599 (class 2606 OID 41039)
-- Name: instructor_belts instructor_belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT instructor_belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5593 (class 2606 OID 32880)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_id_martial_art_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_id_martial_art_key UNIQUE (id_instructor, id_martial_art);


--
-- TOC entry 5595 (class 2606 OID 32878)
-- Name: instructor_martial_arts instructor_martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5523 (class 2606 OID 24751)
-- Name: instructors instructors_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_key UNIQUE (id_person);


--
-- TOC entry 5525 (class 2606 OID 24749)
-- Name: instructors instructors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_pkey PRIMARY KEY (id);


--
-- TOC entry 5609 (class 2606 OID 41153)
-- Name: inventory_categories inventory_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories
    ADD CONSTRAINT inventory_categories_name_key UNIQUE (name);


--
-- TOC entry 5611 (class 2606 OID 41151)
-- Name: inventory_categories inventory_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories
    ADD CONSTRAINT inventory_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5690 (class 2606 OID 49438)
-- Name: martial_art_initial_levels martial_art_initial_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_initial_levels
    ADD CONSTRAINT martial_art_initial_levels_pkey PRIMARY KEY (id);


--
-- TOC entry 5687 (class 2606 OID 49411)
-- Name: martial_art_promotion_rules martial_art_promotion_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_promotion_rules
    ADD CONSTRAINT martial_art_promotion_rules_pkey PRIMARY KEY (id);


--
-- TOC entry 5504 (class 2606 OID 24612)
-- Name: martial_arts martial_arts_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_name_key UNIQUE (name);


--
-- TOC entry 5506 (class 2606 OID 24610)
-- Name: martial_arts martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5613 (class 2606 OID 41170)
-- Name: membership_categories membership_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories
    ADD CONSTRAINT membership_categories_name_key UNIQUE (name);


--
-- TOC entry 5615 (class 2606 OID 41168)
-- Name: membership_categories membership_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories
    ADD CONSTRAINT membership_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5558 (class 2606 OID 24928)
-- Name: membership_plans membership_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT membership_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 5546 (class 2606 OID 24876)
-- Name: movement_type movement_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_name_key UNIQUE (name);


--
-- TOC entry 5548 (class 2606 OID 24874)
-- Name: movement_type movement_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_pkey PRIMARY KEY (id);


--
-- TOC entry 5564 (class 2606 OID 25003)
-- Name: payment_items payment_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT payment_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5542 (class 2606 OID 24865)
-- Name: payment_method payment_method_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_name_key UNIQUE (name);


--
-- TOC entry 5544 (class 2606 OID 24863)
-- Name: payment_method payment_method_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_pkey PRIMARY KEY (id);


--
-- TOC entry 5562 (class 2606 OID 24974)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5511 (class 2606 OID 24683)
-- Name: people people_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_email_key UNIQUE (email);


--
-- TOC entry 5513 (class 2606 OID 24681)
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (id);


--
-- TOC entry 5617 (class 2606 OID 41186)
-- Name: product_purchase_history product_purchase_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history
    ADD CONSTRAINT product_purchase_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5556 (class 2606 OID 24909)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 5698 (class 2606 OID 49490)
-- Name: progression_template_levels progression_template_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progression_template_levels
    ADD CONSTRAINT progression_template_levels_pkey PRIMARY KEY (id);


--
-- TOC entry 5694 (class 2606 OID 49468)
-- Name: progression_templates progression_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progression_templates
    ADD CONSTRAINT progression_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 5696 (class 2606 OID 49470)
-- Name: progression_templates progression_templates_template_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progression_templates
    ADD CONSTRAINT progression_templates_template_key_key UNIQUE (template_key);


--
-- TOC entry 5515 (class 2606 OID 24693)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 5517 (class 2606 OID 24691)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5532 (class 2606 OID 24801)
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- TOC entry 5657 (class 2606 OID 41590)
-- Name: scholarships_old scholarships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships_old
    ADD CONSTRAINT scholarships_pkey PRIMARY KEY (id);


--
-- TOC entry 5659 (class 2606 OID 41618)
-- Name: scholarships scholarships_pkey1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships
    ADD CONSTRAINT scholarships_pkey1 PRIMARY KEY (id);


--
-- TOC entry 5619 (class 2606 OID 41223)
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- TOC entry 5498 (class 2606 OID 16441)
-- Name: status status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- TOC entry 5646 (class 2606 OID 41502)
-- Name: student_documents student_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5606 (class 2606 OID 41135)
-- Name: student_emergency_contacts student_emergency_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts
    ADD CONSTRAINT student_emergency_contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 5603 (class 2606 OID 41114)
-- Name: student_guardians student_guardians_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians
    ADD CONSTRAINT student_guardians_pkey PRIMARY KEY (id);


--
-- TOC entry 5644 (class 2606 OID 41482)
-- Name: student_health_info student_health_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info
    ADD CONSTRAINT student_health_info_pkey PRIMARY KEY (id);


--
-- TOC entry 5560 (class 2606 OID 24945)
-- Name: student_memberships student_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT student_memberships_pkey PRIMARY KEY (id);


--
-- TOC entry 5530 (class 2606 OID 24783)
-- Name: students_belts_history students_belts_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5528 (class 2606 OID 24764)
-- Name: students_belts students_belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5519 (class 2606 OID 24721)
-- Name: students students_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_key UNIQUE (id_person);


--
-- TOC entry 5521 (class 2606 OID 24719)
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- TOC entry 5586 (class 2606 OID 32814)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 5496 (class 2606 OID 16433)
-- Name: type_document type_document_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document
    ADD CONSTRAINT type_document_pkey PRIMARY KEY (id);


--
-- TOC entry 5552 (class 2606 OID 24896)
-- Name: type_products type_products_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_name_key UNIQUE (name);


--
-- TOC entry 5554 (class 2606 OID 24894)
-- Name: type_products type_products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_pkey PRIMARY KEY (id);


--
-- TOC entry 5588 (class 2606 OID 32827)
-- Name: type_requirements type_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements
    ADD CONSTRAINT type_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5580 (class 2606 OID 32775)
-- Name: type_student type_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student
    ADD CONSTRAINT type_student_pkey PRIMARY KEY (id);


--
-- TOC entry 5584 (class 2606 OID 32803)
-- Name: type_task type_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task
    ADD CONSTRAINT type_task_pkey PRIMARY KEY (id);


--
-- TOC entry 5674 (class 2606 OID 49237)
-- Name: event_followers uq_event_follower; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_followers
    ADD CONSTRAINT uq_event_follower UNIQUE (event_id, user_id);


--
-- TOC entry 5678 (class 2606 OID 49266)
-- Name: event_interest uq_event_interest; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_interest
    ADD CONSTRAINT uq_event_interest UNIQUE (event_id, user_id);


--
-- TOC entry 5601 (class 2606 OID 41041)
-- Name: instructor_belts uq_instructor_belt_per_art; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT uq_instructor_belt_per_art UNIQUE (id_instructor, id_martial_art);


--
-- TOC entry 5692 (class 2606 OID 49440)
-- Name: martial_art_initial_levels uq_martial_art_initial_level; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_initial_levels
    ADD CONSTRAINT uq_martial_art_initial_level UNIQUE (martial_art_id, level_id);


--
-- TOC entry 5648 (class 2606 OID 41504)
-- Name: student_documents uq_student_doc_type; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT uq_student_doc_type UNIQUE (id_student, doc_type);


--
-- TOC entry 5700 (class 2606 OID 49492)
-- Name: progression_template_levels uq_template_level_order; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progression_template_levels
    ADD CONSTRAINT uq_template_level_order UNIQUE (template_id, orden);


--
-- TOC entry 5666 (class 2606 OID 49185)
-- Name: user_notification_preferences user_notification_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_notification_preferences
    ADD CONSTRAINT user_notification_preferences_pkey PRIMARY KEY (id);


--
-- TOC entry 5668 (class 2606 OID 49187)
-- Name: user_notification_preferences user_notification_preferences_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_notification_preferences
    ADD CONSTRAINT user_notification_preferences_user_id_key UNIQUE (user_id);


--
-- TOC entry 5574 (class 2606 OID 25101)
-- Name: users users_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_key UNIQUE (id_person);


--
-- TOC entry 5576 (class 2606 OID 25099)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5578 (class 2606 OID 25103)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 5539 (class 1259 OID 49203)
-- Name: idx_attendance_override; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_override ON public.attendance USING btree (is_admin_override);


--
-- TOC entry 5540 (class 1259 OID 49202)
-- Name: idx_attendance_student_check_in; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_student_check_in ON public.attendance USING btree (id_student, check_in_time);


--
-- TOC entry 5655 (class 1259 OID 41598)
-- Name: idx_collection_account_items_account; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_account_items_account ON public.collection_account_items_old USING btree (account_id);


--
-- TOC entry 5651 (class 1259 OID 41597)
-- Name: idx_collection_accounts_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_accounts_date ON public.collection_accounts_old USING btree (account_date DESC);


--
-- TOC entry 5652 (class 1259 OID 41596)
-- Name: idx_collection_accounts_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_collection_accounts_status ON public.collection_accounts_old USING btree (status);


--
-- TOC entry 5703 (class 1259 OID 49531)
-- Name: idx_discipline_exercises_active_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_discipline_exercises_active_order ON public.discipline_exercises USING btree (martial_art_id, is_active, sort_order);


--
-- TOC entry 5704 (class 1259 OID 49530)
-- Name: idx_discipline_exercises_martial_art; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_discipline_exercises_martial_art ON public.discipline_exercises USING btree (martial_art_id);


--
-- TOC entry 5671 (class 1259 OID 49248)
-- Name: idx_event_followers_event; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_event_followers_event ON public.event_followers USING btree (event_id);


--
-- TOC entry 5672 (class 1259 OID 49249)
-- Name: idx_event_followers_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_event_followers_user ON public.event_followers USING btree (user_id);


--
-- TOC entry 5642 (class 1259 OID 41488)
-- Name: idx_student_health_info_id_student; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_student_health_info_id_student ON public.student_health_info USING btree (id_student);


--
-- TOC entry 5664 (class 1259 OID 49193)
-- Name: idx_user_notification_preferences_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_notification_preferences_user_id ON public.user_notification_preferences USING btree (user_id);


--
-- TOC entry 5509 (class 1259 OID 49498)
-- Name: uq_belts_martial_art_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_belts_martial_art_order ON public.belts USING btree (id_martial_art, orden) WHERE (orden IS NOT NULL);


--
-- TOC entry 5681 (class 1259 OID 49313)
-- Name: uq_event_registration_student; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_event_registration_student ON public.event_registrations USING btree (event_id, student_id) WHERE ((student_id IS NOT NULL) AND ((registration_status)::text <> 'cancelled'::text));


--
-- TOC entry 5688 (class 1259 OID 49427)
-- Name: uq_martial_art_promotion_rule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_martial_art_promotion_rule ON public.martial_art_promotion_rules USING btree (martial_art_id, COALESCE(from_level_id, (0)::bigint), to_level_id);


--
-- TOC entry 5589 (class 1259 OID 49499)
-- Name: uq_type_requirements_name_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_type_requirements_name_ci ON public.type_requirements USING btree (lower(btrim((type_requirement)::text)));


--
-- TOC entry 5526 (class 1259 OID 40998)
-- Name: ux_instructors_only_one_sensei; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_instructors_only_one_sensei ON public.instructors USING btree (is_sensei) WHERE (is_sensei = true);


--
-- TOC entry 5607 (class 1259 OID 41142)
-- Name: ux_student_one_primary_emergency_contact; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_student_one_primary_emergency_contact ON public.student_emergency_contacts USING btree (id_student) WHERE (is_primary = true);


--
-- TOC entry 5604 (class 1259 OID 41141)
-- Name: ux_student_one_primary_guardian; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_student_one_primary_guardian ON public.student_guardians USING btree (id_student) WHERE (is_primary = true);


--
-- TOC entry 5795 (class 2620 OID 24852)
-- Name: students_belts tg_students_belts_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_insert AFTER INSERT ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_insert();


--
-- TOC entry 5796 (class 2620 OID 24854)
-- Name: students_belts tg_students_belts_update; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_update AFTER UPDATE ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_update();


--
-- TOC entry 5798 (class 2620 OID 25084)
-- Name: expenses trg_expense_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_expense_insert_movement AFTER INSERT ON public.expenses FOR EACH ROW EXECUTE FUNCTION public.fn_expense_insert_movement();


--
-- TOC entry 5797 (class 2620 OID 25082)
-- Name: payments trg_payment_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_payment_insert_movement AFTER INSERT ON public.payments FOR EACH ROW EXECUTE FUNCTION public.fn_payment_insert_movement();


--
-- TOC entry 5722 (class 2606 OID 24840)
-- Name: attendance attendance_id_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_fkey FOREIGN KEY (id_class) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- TOC entry 5723 (class 2606 OID 24845)
-- Name: attendance attendance_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5724 (class 2606 OID 49196)
-- Name: attendance attendance_override_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_override_user_fkey FOREIGN KEY (override_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5743 (class 2606 OID 32857)
-- Name: belt_requirements belt_requirements_belt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_belt_id_fkey FOREIGN KEY (belt_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5744 (class 2606 OID 32862)
-- Name: belt_requirements belt_requirements_id_type_requeriments_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_id_type_requeriments_fkey FOREIGN KEY (id_type_requeriments) REFERENCES public.type_requirements(id) ON DELETE CASCADE;


--
-- TOC entry 5720 (class 2606 OID 24825)
-- Name: classes classes_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5721 (class 2606 OID 24820)
-- Name: classes classes_id_schedule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_schedule_fkey FOREIGN KEY (id_schedule) REFERENCES public.schedule(id);


--
-- TOC entry 5772 (class 2606 OID 41570)
-- Name: collection_account_items_old collection_account_items_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items_old
    ADD CONSTRAINT collection_account_items_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.collection_accounts_old(id) ON DELETE CASCADE;


--
-- TOC entry 5776 (class 2606 OID 41665)
-- Name: collection_account_items collection_account_items_collection_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_account_items
    ADD CONSTRAINT collection_account_items_collection_account_id_fkey FOREIGN KEY (collection_account_id) REFERENCES public.collection_accounts(id) ON DELETE CASCADE;


--
-- TOC entry 5770 (class 2606 OID 41544)
-- Name: collection_accounts_old collection_accounts_client_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts_old
    ADD CONSTRAINT collection_accounts_client_person_id_fkey FOREIGN KEY (client_person_id) REFERENCES public.people(id);


--
-- TOC entry 5774 (class 2606 OID 41640)
-- Name: collection_accounts collection_accounts_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts
    ADD CONSTRAINT collection_accounts_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5775 (class 2606 OID 41645)
-- Name: collection_accounts collection_accounts_scholarship_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts
    ADD CONSTRAINT collection_accounts_scholarship_id_fkey FOREIGN KEY (scholarship_id) REFERENCES public.scholarships(id);


--
-- TOC entry 5766 (class 2606 OID 41439)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.finance_expenses(id) ON DELETE CASCADE;


--
-- TOC entry 5767 (class 2606 OID 41444)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 5763 (class 2606 OID 41394)
-- Name: finance_expense_subcategories finance_expense_subcategories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_expense_categories(id) ON DELETE CASCADE;


--
-- TOC entry 5764 (class 2606 OID 41416)
-- Name: finance_expenses finance_expenses_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_expense_categories(id);


--
-- TOC entry 5765 (class 2606 OID 41421)
-- Name: finance_expenses finance_expenses_subcategory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_subcategory_id_fkey FOREIGN KEY (subcategory_id) REFERENCES public.finance_expense_subcategories(id);


--
-- TOC entry 5756 (class 2606 OID 41277)
-- Name: finance_income_items finance_income_items_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items
    ADD CONSTRAINT finance_income_items_income_id_fkey FOREIGN KEY (income_id) REFERENCES public.finance_income(id) ON DELETE CASCADE;


--
-- TOC entry 5757 (class 2606 OID 41301)
-- Name: finance_income_participants finance_income_participants_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_income_id_fkey FOREIGN KEY (income_id) REFERENCES public.finance_income(id) ON DELETE CASCADE;


--
-- TOC entry 5758 (class 2606 OID 41306)
-- Name: finance_income_participants finance_income_participants_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5755 (class 2606 OID 41253)
-- Name: finance_income finance_income_payer_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income
    ADD CONSTRAINT finance_income_payer_person_id_fkey FOREIGN KEY (payer_person_id) REFERENCES public.people(id);


--
-- TOC entry 5762 (class 2606 OID 41360)
-- Name: finance_receivable_payments finance_receivable_payments_receivable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments
    ADD CONSTRAINT finance_receivable_payments_receivable_id_fkey FOREIGN KEY (receivable_id) REFERENCES public.finance_receivables(id) ON DELETE CASCADE;


--
-- TOC entry 5759 (class 2606 OID 41331)
-- Name: finance_receivables finance_receivables_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5760 (class 2606 OID 41336)
-- Name: finance_receivables finance_receivables_source_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_source_income_id_fkey FOREIGN KEY (source_income_id) REFERENCES public.finance_income(id);


--
-- TOC entry 5761 (class 2606 OID 41341)
-- Name: finance_receivables finance_receivables_source_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_source_participant_id_fkey FOREIGN KEY (source_participant_id) REFERENCES public.finance_income_participants(id);


--
-- TOC entry 5739 (class 2606 OID 25071)
-- Name: account_movements fk_account_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5740 (class 2606 OID 25076)
-- Name: account_movements fk_account_movement_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_movement_type FOREIGN KEY (id_movement_type) REFERENCES public.movement_type(id);


--
-- TOC entry 5771 (class 2606 OID 41591)
-- Name: collection_accounts_old fk_collection_accounts_scholarship; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_accounts_old
    ADD CONSTRAINT fk_collection_accounts_scholarship FOREIGN KEY (scholarship_id) REFERENCES public.scholarships_old(id) ON DELETE SET NULL;


--
-- TOC entry 5794 (class 2606 OID 49525)
-- Name: discipline_exercises fk_discipline_exercises_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discipline_exercises
    ADD CONSTRAINT fk_discipline_exercises_martial_art FOREIGN KEY (martial_art_id) REFERENCES public.martial_arts(id) ON DELETE CASCADE;


--
-- TOC entry 5778 (class 2606 OID 49238)
-- Name: event_followers fk_event_followers_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_followers
    ADD CONSTRAINT fk_event_followers_event FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- TOC entry 5779 (class 2606 OID 49243)
-- Name: event_followers fk_event_followers_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_followers
    ADD CONSTRAINT fk_event_followers_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5780 (class 2606 OID 49267)
-- Name: event_interest fk_event_interest_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_interest
    ADD CONSTRAINT fk_event_interest_event FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- TOC entry 5781 (class 2606 OID 49272)
-- Name: event_interest fk_event_interest_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_interest
    ADD CONSTRAINT fk_event_interest_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5786 (class 2606 OID 49361)
-- Name: event_posts fk_event_posts_author; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_posts
    ADD CONSTRAINT fk_event_posts_author FOREIGN KEY (author_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5787 (class 2606 OID 49356)
-- Name: event_posts fk_event_posts_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_posts
    ADD CONSTRAINT fk_event_posts_event FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- TOC entry 5782 (class 2606 OID 49298)
-- Name: event_registrations fk_event_registrations_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_registrations
    ADD CONSTRAINT fk_event_registrations_event FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- TOC entry 5783 (class 2606 OID 49308)
-- Name: event_registrations fk_event_registrations_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_registrations
    ADD CONSTRAINT fk_event_registrations_student FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE SET NULL;


--
-- TOC entry 5784 (class 2606 OID 49303)
-- Name: event_registrations fk_event_registrations_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_registrations
    ADD CONSTRAINT fk_event_registrations_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5785 (class 2606 OID 49333)
-- Name: event_schedule_items fk_event_schedule_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_schedule_items
    ADD CONSTRAINT fk_event_schedule_event FOREIGN KEY (event_id) REFERENCES public.events(id) ON DELETE CASCADE;


--
-- TOC entry 5747 (class 2606 OID 49215)
-- Name: events fk_events_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT fk_events_martial_art FOREIGN KEY (martial_art_id) REFERENCES public.martial_arts(id) ON DELETE SET NULL;


--
-- TOC entry 5748 (class 2606 OID 49210)
-- Name: events fk_events_organizer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT fk_events_organizer FOREIGN KEY (organizer_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5737 (class 2606 OID 25048)
-- Name: expenses fk_expense_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_category FOREIGN KEY (id_expense_category) REFERENCES public.expense_categories(id);


--
-- TOC entry 5738 (class 2606 OID 25053)
-- Name: expenses fk_expense_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5742 (class 2606 OID 32815)
-- Name: tasks fk_id_type_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_id_type_task FOREIGN KEY (id_type_task) REFERENCES public.type_task(id) NOT VALID;


--
-- TOC entry 5791 (class 2606 OID 49446)
-- Name: martial_art_initial_levels fk_initial_level_level; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_initial_levels
    ADD CONSTRAINT fk_initial_level_level FOREIGN KEY (level_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5792 (class 2606 OID 49441)
-- Name: martial_art_initial_levels fk_initial_level_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_initial_levels
    ADD CONSTRAINT fk_initial_level_martial_art FOREIGN KEY (martial_art_id) REFERENCES public.martial_arts(id) ON DELETE CASCADE;


--
-- TOC entry 5749 (class 2606 OID 41052)
-- Name: instructor_belts fk_instructor_belts_belt; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_belt FOREIGN KEY (id_belt) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5750 (class 2606 OID 41042)
-- Name: instructor_belts fk_instructor_belts_instructor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_instructor FOREIGN KEY (id_instructor) REFERENCES public.instructors(id) ON DELETE CASCADE;


--
-- TOC entry 5751 (class 2606 OID 41047)
-- Name: instructor_belts fk_instructor_belts_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_martial_art FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id) ON DELETE CASCADE;


--
-- TOC entry 5705 (class 2606 OID 24625)
-- Name: belts fk_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT fk_martial_art FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5727 (class 2606 OID 41194)
-- Name: membership_plans fk_membership_plans_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT fk_membership_plans_category FOREIGN KEY (id_membership_category) REFERENCES public.membership_categories(id);


--
-- TOC entry 5728 (class 2606 OID 24929)
-- Name: membership_plans fk_membership_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT fk_membership_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5777 (class 2606 OID 49188)
-- Name: user_notification_preferences fk_notification_preferences_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_notification_preferences
    ADD CONSTRAINT fk_notification_preferences_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5731 (class 2606 OID 24980)
-- Name: payments fk_payment_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5734 (class 2606 OID 25014)
-- Name: payment_items fk_payment_items_membership; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_membership FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5735 (class 2606 OID 25004)
-- Name: payment_items fk_payment_items_payment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_payment FOREIGN KEY (id_payments) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- TOC entry 5736 (class 2606 OID 25009)
-- Name: payment_items fk_payment_items_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_product FOREIGN KEY (id_product) REFERENCES public.products(id);


--
-- TOC entry 5732 (class 2606 OID 24975)
-- Name: payments fk_payment_method; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_method FOREIGN KEY (id_payment_method) REFERENCES public.payment_method(id);


--
-- TOC entry 5733 (class 2606 OID 24985)
-- Name: payments fk_people; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_people FOREIGN KEY (id_person) REFERENCES public.people(id);


--
-- TOC entry 5706 (class 2606 OID 32788)
-- Name: people fk_people_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT fk_people_users FOREIGN KEY (id_code_users) REFERENCES public.users(id);


--
-- TOC entry 5725 (class 2606 OID 41189)
-- Name: products fk_products_inventory_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_inventory_category FOREIGN KEY (id_inventory_category) REFERENCES public.inventory_categories(id);


--
-- TOC entry 5726 (class 2606 OID 24910)
-- Name: products fk_products_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5788 (class 2606 OID 49417)
-- Name: martial_art_promotion_rules fk_promotion_rule_from_level; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_promotion_rules
    ADD CONSTRAINT fk_promotion_rule_from_level FOREIGN KEY (from_level_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5789 (class 2606 OID 49412)
-- Name: martial_art_promotion_rules fk_promotion_rule_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_promotion_rules
    ADD CONSTRAINT fk_promotion_rule_martial_art FOREIGN KEY (martial_art_id) REFERENCES public.martial_arts(id) ON DELETE CASCADE;


--
-- TOC entry 5790 (class 2606 OID 49422)
-- Name: martial_art_promotion_rules fk_promotion_rule_to_level; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_art_promotion_rules
    ADD CONSTRAINT fk_promotion_rule_to_level FOREIGN KEY (to_level_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5754 (class 2606 OID 41199)
-- Name: product_purchase_history fk_purchase_history_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history
    ADD CONSTRAINT fk_purchase_history_product FOREIGN KEY (id_product) REFERENCES public.products(id);


--
-- TOC entry 5729 (class 2606 OID 24951)
-- Name: student_memberships fk_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student FOREIGN KEY (id_student) REFERENCES public.students(id);


--
-- TOC entry 5753 (class 2606 OID 41136)
-- Name: student_emergency_contacts fk_student_emergency_contacts_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts
    ADD CONSTRAINT fk_student_emergency_contacts_student FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5752 (class 2606 OID 41115)
-- Name: student_guardians fk_student_guardians_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians
    ADD CONSTRAINT fk_student_guardians_student FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5730 (class 2606 OID 24946)
-- Name: student_memberships fk_student_membership_plan; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student_membership_plan FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5793 (class 2606 OID 49493)
-- Name: progression_template_levels fk_template_level_template; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.progression_template_levels
    ADD CONSTRAINT fk_template_level_template FOREIGN KEY (template_id) REFERENCES public.progression_templates(id) ON DELETE CASCADE;


--
-- TOC entry 5745 (class 2606 OID 32881)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5746 (class 2606 OID 32886)
-- Name: instructor_martial_arts instructor_martial_arts_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5713 (class 2606 OID 24752)
-- Name: instructors instructors_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5707 (class 2606 OID 24697)
-- Name: person_roles person_roles_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5708 (class 2606 OID 24702)
-- Name: person_roles person_roles_id_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_role_fkey FOREIGN KEY (id_role) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 5718 (class 2606 OID 40964)
-- Name: schedule schedule_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5719 (class 2606 OID 24802)
-- Name: schedule schedule_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5773 (class 2606 OID 41619)
-- Name: scholarships scholarships_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scholarships
    ADD CONSTRAINT scholarships_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5769 (class 2606 OID 41505)
-- Name: student_documents student_documents_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5768 (class 2606 OID 41483)
-- Name: student_health_info student_health_info_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info
    ADD CONSTRAINT student_health_info_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5716 (class 2606 OID 24789)
-- Name: students_belts_history students_belts_history_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5717 (class 2606 OID 24784)
-- Name: students_belts_history students_belts_history_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5714 (class 2606 OID 24770)
-- Name: students_belts students_belts_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5715 (class 2606 OID 24765)
-- Name: students_belts students_belts_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5709 (class 2606 OID 24732)
-- Name: students students_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- TOC entry 5710 (class 2606 OID 24722)
-- Name: students students_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5711 (class 2606 OID 24737)
-- Name: students students_id_status_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.status(id);


--
-- TOC entry 5712 (class 2606 OID 24727)
-- Name: students students_id_type_document_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_type_document_fkey FOREIGN KEY (id_type_document) REFERENCES public.type_document(id);


--
-- TOC entry 5741 (class 2606 OID 25104)
-- Name: users users_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id);


-- Completed on 2026-08-13 10:25:29

--
-- PostgreSQL database dump complete
--

\unrestrict hNVXqQMomN8AnxegrRBCeBDXnPOZZCCf4OoFKSepCh951IKrWlkcwgKcc54XA7D

