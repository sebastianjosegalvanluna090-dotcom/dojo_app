--
-- PostgreSQL database dump
--

\restrict saswbFMlOTwYOT1efRY5oouM7imsWBxwqXKzjrKyiLGX7ejC2e2FjKeHbTzb79y

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-07-05 21:59:20

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
-- TOC entry 328 (class 1255 OID 25083)
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
-- TOC entry 329 (class 1255 OID 25081)
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
-- TOC entry 326 (class 1255 OID 24851)
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
-- TOC entry 327 (class 1255 OID 24853)
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
-- TOC entry 5756 (class 0 OID 0)
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
    note text
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
-- TOC entry 5757 (class 0 OID 0)
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
-- TOC entry 5758 (class 0 OID 0)
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
    grade_color character varying(20) DEFAULT '#FFFFFF'::character varying
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
-- TOC entry 5759 (class 0 OID 0)
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
-- TOC entry 5760 (class 0 OID 0)
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
-- TOC entry 5761 (class 0 OID 0)
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
-- TOC entry 5762 (class 0 OID 0)
-- Dependencies: 276
-- Name: codes_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.codes_users_id_seq OWNED BY public.codes_users.id;


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
-- TOC entry 5763 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.destination_account_id_seq OWNED BY public.destination_account.id;


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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- TOC entry 5764 (class 0 OID 0)
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
-- TOC entry 5765 (class 0 OID 0)
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
    description text DEFAULT ''::text
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
-- TOC entry 5766 (class 0 OID 0)
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
-- TOC entry 5767 (class 0 OID 0)
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
-- TOC entry 5768 (class 0 OID 0)
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- TOC entry 5769 (class 0 OID 0)
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
-- TOC entry 5770 (class 0 OID 0)
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
-- TOC entry 5771 (class 0 OID 0)
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
-- TOC entry 5772 (class 0 OID 0)
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
-- TOC entry 5773 (class 0 OID 0)
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
-- TOC entry 5774 (class 0 OID 0)
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
-- TOC entry 5775 (class 0 OID 0)
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
-- TOC entry 5776 (class 0 OID 0)
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
-- TOC entry 5777 (class 0 OID 0)
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
-- TOC entry 5778 (class 0 OID 0)
-- Dependencies: 296
-- Name: inventory_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_categories_id_seq OWNED BY public.inventory_categories.id;


--
-- TOC entry 226 (class 1259 OID 24603)
-- Name: martial_arts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.martial_arts (
    id integer NOT NULL,
    name character varying(50) NOT NULL
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
-- TOC entry 5779 (class 0 OID 0)
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
-- TOC entry 5780 (class 0 OID 0)
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
-- TOC entry 5781 (class 0 OID 0)
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
-- TOC entry 5782 (class 0 OID 0)
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
-- TOC entry 5783 (class 0 OID 0)
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
-- TOC entry 5784 (class 0 OID 0)
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
-- TOC entry 5785 (class 0 OID 0)
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
-- TOC entry 5786 (class 0 OID 0)
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
-- TOC entry 5787 (class 0 OID 0)
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
-- TOC entry 5788 (class 0 OID 0)
-- Dependencies: 256
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


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
-- TOC entry 5789 (class 0 OID 0)
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
-- TOC entry 5790 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


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
-- TOC entry 5791 (class 0 OID 0)
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
-- TOC entry 5792 (class 0 OID 0)
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
-- TOC entry 5793 (class 0 OID 0)
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
-- TOC entry 5794 (class 0 OID 0)
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
-- TOC entry 5795 (class 0 OID 0)
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
-- TOC entry 5796 (class 0 OID 0)
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
-- TOC entry 5797 (class 0 OID 0)
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
-- TOC entry 5798 (class 0 OID 0)
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
-- TOC entry 5799 (class 0 OID 0)
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
-- TOC entry 5800 (class 0 OID 0)
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
-- TOC entry 5801 (class 0 OID 0)
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
-- TOC entry 5802 (class 0 OID 0)
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
-- TOC entry 5803 (class 0 OID 0)
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
-- TOC entry 5804 (class 0 OID 0)
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
-- TOC entry 5805 (class 0 OID 0)
-- Dependencies: 278
-- Name: type_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.type_task_id_seq OWNED BY public.type_task.id;


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
-- TOC entry 5806 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 5182 (class 2604 OID 25062)
-- Name: account_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements ALTER COLUMN id SET DEFAULT nextval('public.account_movements_id_seq'::regclass);


--
-- TOC entry 5152 (class 2604 OID 24834)
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- TOC entry 5192 (class 2604 OID 32849)
-- Name: belt_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements ALTER COLUMN id SET DEFAULT nextval('public.belt_requirements_id_seq'::regclass);


--
-- TOC entry 5128 (class 2604 OID 24617)
-- Name: belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts ALTER COLUMN id SET DEFAULT nextval('public.belts_id_seq'::regclass);


--
-- TOC entry 5126 (class 2604 OID 24590)
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- TOC entry 5148 (class 2604 OID 24811)
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- TOC entry 5188 (class 2604 OID 32780)
-- Name: codes_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users ALTER COLUMN id SET DEFAULT nextval('public.codes_users_id_seq'::regclass);


--
-- TOC entry 5157 (class 2604 OID 24881)
-- Name: destination_account id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account ALTER COLUMN id SET DEFAULT nextval('public.destination_account_id_seq'::regclass);


--
-- TOC entry 5179 (class 2604 OID 25023)
-- Name: expense_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories ALTER COLUMN id SET DEFAULT nextval('public.expense_categories_id_seq'::regclass);


--
-- TOC entry 5180 (class 2604 OID 25036)
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- TOC entry 5254 (class 2604 OID 41369)
-- Name: finance_expense_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_categories_id_seq'::regclass);


--
-- TOC entry 5264 (class 2604 OID 41430)
-- Name: finance_expense_inventory_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_inventory_items_id_seq'::regclass);


--
-- TOC entry 5256 (class 2604 OID 41383)
-- Name: finance_expense_subcategories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories ALTER COLUMN id SET DEFAULT nextval('public.finance_expense_subcategories_id_seq'::regclass);


--
-- TOC entry 5258 (class 2604 OID 41403)
-- Name: finance_expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses ALTER COLUMN id SET DEFAULT nextval('public.finance_expenses_id_seq'::regclass);


--
-- TOC entry 5218 (class 2604 OID 41228)
-- Name: finance_income id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income ALTER COLUMN id SET DEFAULT nextval('public.finance_income_id_seq'::regclass);


--
-- TOC entry 5234 (class 2604 OID 41262)
-- Name: finance_income_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items ALTER COLUMN id SET DEFAULT nextval('public.finance_income_items_id_seq'::regclass);


--
-- TOC entry 5240 (class 2604 OID 41286)
-- Name: finance_income_participants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants ALTER COLUMN id SET DEFAULT nextval('public.finance_income_participants_id_seq'::regclass);


--
-- TOC entry 5251 (class 2604 OID 41350)
-- Name: finance_receivable_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments ALTER COLUMN id SET DEFAULT nextval('public.finance_receivable_payments_id_seq'::regclass);


--
-- TOC entry 5245 (class 2604 OID 41315)
-- Name: finance_receivables id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables ALTER COLUMN id SET DEFAULT nextval('public.finance_receivables_id_seq'::regclass);


--
-- TOC entry 5199 (class 2604 OID 41032)
-- Name: instructor_belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts ALTER COLUMN id SET DEFAULT nextval('public.instructor_belts_id_seq'::regclass);


--
-- TOC entry 5194 (class 2604 OID 32871)
-- Name: instructor_martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts ALTER COLUMN id SET DEFAULT nextval('public.instructor_martial_arts_id_seq'::regclass);


--
-- TOC entry 5139 (class 2604 OID 24746)
-- Name: instructors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors ALTER COLUMN id SET DEFAULT nextval('public.instructors_id_seq'::regclass);


--
-- TOC entry 5209 (class 2604 OID 41147)
-- Name: inventory_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories ALTER COLUMN id SET DEFAULT nextval('public.inventory_categories_id_seq'::regclass);


--
-- TOC entry 5127 (class 2604 OID 24606)
-- Name: martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts ALTER COLUMN id SET DEFAULT nextval('public.martial_arts_id_seq'::regclass);


--
-- TOC entry 5210 (class 2604 OID 41164)
-- Name: membership_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories ALTER COLUMN id SET DEFAULT nextval('public.membership_categories_id_seq'::regclass);


--
-- TOC entry 5163 (class 2604 OID 24919)
-- Name: membership_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans ALTER COLUMN id SET DEFAULT nextval('public.membership_plans_id_seq'::regclass);


--
-- TOC entry 5156 (class 2604 OID 24870)
-- Name: movement_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type ALTER COLUMN id SET DEFAULT nextval('public.movement_type_id_seq'::regclass);


--
-- TOC entry 5177 (class 2604 OID 24994)
-- Name: payment_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items ALTER COLUMN id SET DEFAULT nextval('public.payment_items_id_seq'::regclass);


--
-- TOC entry 5155 (class 2604 OID 24859)
-- Name: payment_method id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method ALTER COLUMN id SET DEFAULT nextval('public.payment_method_id_seq'::regclass);


--
-- TOC entry 5174 (class 2604 OID 24960)
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- TOC entry 5131 (class 2604 OID 24677)
-- Name: people id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people ALTER COLUMN id SET DEFAULT nextval('public.people_id_seq'::regclass);


--
-- TOC entry 5211 (class 2604 OID 41175)
-- Name: product_purchase_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history ALTER COLUMN id SET DEFAULT nextval('public.product_purchase_history_id_seq'::regclass);


--
-- TOC entry 5159 (class 2604 OID 24901)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 5136 (class 2604 OID 24688)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 5144 (class 2604 OID 24798)
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- TOC entry 5125 (class 2604 OID 16438)
-- Name: status id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);


--
-- TOC entry 5274 (class 2604 OID 41493)
-- Name: student_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents ALTER COLUMN id SET DEFAULT nextval('public.student_documents_id_seq'::regclass);


--
-- TOC entry 5206 (class 2604 OID 41124)
-- Name: student_emergency_contacts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts ALTER COLUMN id SET DEFAULT nextval('public.student_emergency_contacts_id_seq'::regclass);


--
-- TOC entry 5201 (class 2604 OID 41104)
-- Name: student_guardians id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians ALTER COLUMN id SET DEFAULT nextval('public.student_guardians_id_seq'::regclass);


--
-- TOC entry 5265 (class 2604 OID 41468)
-- Name: student_health_info id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info ALTER COLUMN id SET DEFAULT nextval('public.student_health_info_id_seq'::regclass);


--
-- TOC entry 5173 (class 2604 OID 24938)
-- Name: student_memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships ALTER COLUMN id SET DEFAULT nextval('public.student_memberships_id_seq'::regclass);


--
-- TOC entry 5137 (class 2604 OID 24716)
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- TOC entry 5141 (class 2604 OID 24761)
-- Name: students_belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts ALTER COLUMN id SET DEFAULT nextval('public.students_belts_id_seq'::regclass);


--
-- TOC entry 5142 (class 2604 OID 24779)
-- Name: students_belts_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history ALTER COLUMN id SET DEFAULT nextval('public.students_belts_history_id_seq'::regclass);


--
-- TOC entry 5190 (class 2604 OID 32808)
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 5124 (class 2604 OID 16430)
-- Name: type_document id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document ALTER COLUMN id SET DEFAULT nextval('public.type_document_id_seq'::regclass);


--
-- TOC entry 5158 (class 2604 OID 24890)
-- Name: type_products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products ALTER COLUMN id SET DEFAULT nextval('public.type_products_id_seq'::regclass);


--
-- TOC entry 5191 (class 2604 OID 32824)
-- Name: type_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements ALTER COLUMN id SET DEFAULT nextval('public.type_requirements_id_seq'::regclass);


--
-- TOC entry 5187 (class 2604 OID 32772)
-- Name: type_student id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student ALTER COLUMN id SET DEFAULT nextval('public.type_student_id_seq'::regclass);


--
-- TOC entry 5189 (class 2604 OID 32800)
-- Name: type_task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task ALTER COLUMN id SET DEFAULT nextval('public.type_task_id_seq'::regclass);


--
-- TOC entry 5184 (class 2604 OID 25089)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5696 (class 0 OID 25059)
-- Dependencies: 271
-- Data for Name: account_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_movements (id, id_destination_account, id_movement_type, amount, payment_date) FROM stdin;
\.


--
-- TOC entry 5672 (class 0 OID 24831)
-- Dependencies: 247
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance (id, id_class, id_student, status, check_in_time, note) FROM stdin;
\.


--
-- TOC entry 5710 (class 0 OID 32846)
-- Dependencies: 285
-- Data for Name: belt_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belt_requirements (id, belt_id, requirement, id_type_requeriments, created_at) FROM stdin;
\.


--
-- TOC entry 5653 (class 0 OID 24614)
-- Dependencies: 228
-- Data for Name: belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belts (id, name, id_martial_art, orden, color, pre_color, grades, grade_color) FROM stdin;
1	White	1	1	#FFFFFF	\N	0	#FFFFFF
2	White	3	1	#FFFFFF	\N	0	#FFFFFF
4	Pre-naranja	1	2	#FFFFFF	#FF5500	0	#FFFFFF
5	Naranja	1	3	#FF5500	\N	0	#FFFFFF
6	Pre-azul	1	4	#FF5500	#0000FF	0	#FFFFFF
7	Azul	1	5	#0000FF	\N	0	#FFFFFF
8	Pre-amarillo	1	6	#0000FF	#FFFF00	0	#FFFFFF
9	Amarillo	1	7	#FFD710	\N	0	#FFFFFF
10	Pre-verde	1	8	#F3CD0F	#005500	0	#FFFFFF
11	Verde	1	9	#005500	\N	0	#FFFFFF
12	Pre-marron	1	10	#005500	#623307	0	#FFFFFF
14	Negro nacional	1	12	#000000	\N	0	#FFFFFF
16	Blanco 1° GRADO	3	2	#FFFFFF	\N	1	#FFFFFF
17	Blanco 2° GRADO	3	3	#FFFFFF	\N	2	#FFFFFF
21	Blanco 3° GRADO	3	4	#FFFFFF	\N	3	#FFFFFF
22	Blanco 4° Grado	3	5	#FFFFFF	\N	4	#FFFFFF
24	Azul	3	6	#00007F	\N	0	#FFFFFF
25	Azul 1° Grado	3	7	#00007F	\N	1	#FFFFFF
26	Azul 2° GRADO	3	8	#00007F	\N	2	#FFFFFF
27	Azul 3° GRADO	3	9	#00007F	\N	3	#FFFFFF
28	Azul 4° GRADO	3	10	#00007F	\N	4	#FFFFFF
30	Morado	3	11	#8B0350	\N	0	#FFFFFF
33	Negro 1° DAN	1	13	#000000	\N	1	#FFFF00
34	Negro 2° DAN	1	14	#000000	\N	2	#FFFF00
35	Negro 3° DAN	1	15	#000000	\N	3	#FFFF00
36	Negro 4° DAN	1	16	#000000	\N	4	#FFFF00
31	Morado 1° GRADO	3	12	#8b0350	\N	1	#FFFFFF
37	Morado 2° GRADO	3	13	#8b0350	\N	2	#FFFFFF
38	Modaro 3° GRADO	3	14	#8b0350	\N	3	#FFFFFF
39	Morado 4° GRADO	3	14	#8b0350	\N	4	#FFFFFF
13	Marron	1	11	#623307	\N	0	#FFFFFF
42	Marron	3	16	#623307	\N	0	#FFFFFF
43	Marron 1° Grado	3	17	#623307	\N	1	#FFFFFF
44	Marron 2° GRADO	3	18	#623307	\N	2	#FFFFFF
45	Marron 3° GRADO	3	19	#623307	\N	3	#FFFFFF
46	Marron 4° Grado	3	20	#623307	\N	4	#FFFFFF
47	Negro	3	21	#000000	\N	0	#FFFFFF
48	Negro 1° GRADO	3	22	#000000	\N	1	#FFFFFF
\.


--
-- TOC entry 5649 (class 0 OID 24587)
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
-- TOC entry 5670 (class 0 OID 24808)
-- Dependencies: 245
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (id, id_schedule, id_instructor, date, status, note, created_at, guest_count, guest_names) FROM stdin;
4	25	13	2026-06-25	scheduled	\N	2026-06-25 22:35:34.035838	0	\N
\.


--
-- TOC entry 5702 (class 0 OID 32777)
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
-- TOC entry 5678 (class 0 OID 24878)
-- Dependencies: 253
-- Data for Name: destination_account; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.destination_account (id, name, account_number) FROM stdin;
\.


--
-- TOC entry 5714 (class 0 OID 40972)
-- Dependencies: 289
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, name, event_date, event_type, description, color, start_time, end_time, location, is_important, created_at) FROM stdin;
1	torneo	2026-06-27	torneo	\N	#3B82F6	\N	\N	\N	f	2026-06-23 15:07:41.642051
\.


--
-- TOC entry 5692 (class 0 OID 25020)
-- Dependencies: 267
-- Data for Name: expense_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_categories (id, name, description) FROM stdin;
\.


--
-- TOC entry 5694 (class 0 OID 25033)
-- Dependencies: 269
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, id_expense_category, id_destination_account, amount, expense_date, description, invoice_number, created_at) FROM stdin;
\.


--
-- TOC entry 5740 (class 0 OID 41366)
-- Dependencies: 315
-- Data for Name: finance_expense_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_categories (id, name, description) FROM stdin;
1	Gasto fijo	Gastos recurrentes mensuales
2	Gasto variable	Gastos no recurrentes
3	Compra inventario	Compra de productos para inventario
4	Nómina	Pagos a instructores y personal
\.


--
-- TOC entry 5746 (class 0 OID 41427)
-- Dependencies: 321
-- Data for Name: finance_expense_inventory_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_inventory_items (id, expense_id, product_id, quantity, unit_cost, total_cost) FROM stdin;
\.


--
-- TOC entry 5742 (class 0 OID 41380)
-- Dependencies: 317
-- Data for Name: finance_expense_subcategories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expense_subcategories (id, category_id, name, description) FROM stdin;
\.


--
-- TOC entry 5744 (class 0 OID 41400)
-- Dependencies: 319
-- Data for Name: finance_expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_expenses (id, category_id, subcategory_id, expense_date, amount, description, supplier_name, invoice_number, payment_method_id, destination_account_id, affects_inventory, created_at) FROM stdin;
\.


--
-- TOC entry 5730 (class 0 OID 41225)
-- Dependencies: 305
-- Data for Name: finance_income; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_income (id, payer_person_id, payer_name, payer_type, income_date, subtotal, discount, total, total_paid, pending_amount, payment_method_id, destination_account_id, status, note, agreement_note, created_at, payer_document, payer_email, payer_phone, receipt_number, receipt_pdf_path, receipt_generated_at) FROM stdin;
2	\N	.	guardian	2026-07-01 00:00:00	255000.00	0.00	255000.00	255000.00	0.00	\N	\N	paid			2026-07-04 14:36:19.467588			.	\N	\N	\N
4	21	Brenda Rodríguez Barrios	student	2026-06-30 00:00:00	551000.00	12000.00	539000.00	434000.00	105000.00	\N	\N	partial	Le estoy pasando\nMatrícula 85.000\nMensualidad 213.000 (cuando se paga los primeros 10 días del mes)\nUniforme anticipo 136.000 mi hija es talla 4	Cartera por concepto:\n- DOGI talla 22: total $253.000, pagado $136.000, pendiente $117.000\n- 1 vez x semana: total $213.000, pagado $213.000, pendiente $0\n- Matricula Nuevos: total $85.000, pagado $85.000, pendiente $0	2026-07-04 23:50:56.789375	1234100989	rodriguezbrendaj28@gmail.com	3244385822	\N	\N	\N
5	22	Marielsa Ortiz Parra Ortiz	student	2026-07-03 00:00:00	675000.00	0.00	675000.00	675000.00	0.00	\N	\N	paid			2026-07-05 18:01:28.912409	1147696311	marielsa.milagro@gmail.com	+573227111205	\N	\N	\N
\.


--
-- TOC entry 5732 (class 0 OID 41259)
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
\.


--
-- TOC entry 5734 (class 0 OID 41283)
-- Dependencies: 309
-- Data for Name: finance_income_participants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_income_participants (id, income_id, person_id, display_name, expected_amount, paid_amount, pending_amount, due_date, note) FROM stdin;
2	2	20	Juan Diego Barriga	0.00	0.00	0.00	\N	
8	4	21	Victoria Salomé Rodríguez Barrios	0.00	0.00	0.00	\N	
9	4	21	Brenda Rodríguez Barrios	539000.00	434000.00	105000.00	2026-07-15	
10	5	22	Marielsa Ortiz Parra Ortiz	0.00	0.00	0.00	\N	
\.


--
-- TOC entry 5738 (class 0 OID 41347)
-- Dependencies: 313
-- Data for Name: finance_receivable_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_receivable_payments (id, receivable_id, payment_date, amount, payment_method_id, destination_account_id, note) FROM stdin;
\.


--
-- TOC entry 5736 (class 0 OID 41312)
-- Dependencies: 311
-- Data for Name: finance_receivables; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_receivables (id, person_id, debtor_name, source_income_id, source_participant_id, source_type, original_amount, paid_amount, pending_amount, due_date, created_at, status, note) FROM stdin;
2	\N	Brenda Rodríguez Barrios	4	9	income_pending	539000.00	434000.00	105000.00	2026-07-15	2026-07-05 14:31:59.567623	open	
\.


--
-- TOC entry 5716 (class 0 OID 41029)
-- Dependencies: 291
-- Data for Name: instructor_belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructor_belts (id, id_instructor, id_martial_art, id_belt, assigned_at) FROM stdin;
1	13	1	36	2026-06-26 11:41:05.892307
2	14	3	48	2026-06-29 17:24:45.321253
\.


--
-- TOC entry 5712 (class 0 OID 32868)
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
-- TOC entry 5662 (class 0 OID 24743)
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
-- TOC entry 5722 (class 0 OID 41144)
-- Dependencies: 297
-- Data for Name: inventory_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventory_categories (id, name) FROM stdin;
1	PROTECCION
3	UNIFORMES
\.


--
-- TOC entry 5651 (class 0 OID 24603)
-- Dependencies: 226
-- Data for Name: martial_arts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martial_arts (id, name) FROM stdin;
1	Karate Kyokushin
3	Brazilian Jiu-Jitsu
4	Functional Trainning
2	Kick Boxing
\.


--
-- TOC entry 5724 (class 0 OID 41161)
-- Dependencies: 299
-- Data for Name: membership_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membership_categories (id, name) FROM stdin;
1	PROTECCION
2	GRUPAL
\.


--
-- TOC entry 5684 (class 0 OID 24916)
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
-- TOC entry 5676 (class 0 OID 24867)
-- Dependencies: 251
-- Data for Name: movement_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.movement_type (id, name) FROM stdin;
1	expenses
2	payments
\.


--
-- TOC entry 5690 (class 0 OID 24991)
-- Dependencies: 265
-- Data for Name: payment_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_items (id, id_payments, id_product, id_membership_plan, quantity, unit_price, subtotal) FROM stdin;
\.


--
-- TOC entry 5674 (class 0 OID 24856)
-- Dependencies: 249
-- Data for Name: payment_method; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_method (id, name) FROM stdin;
\.


--
-- TOC entry 5688 (class 0 OID 24957)
-- Dependencies: 263
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, id_person, total, total_paid, payment_date, id_payment_method, id_destination_account, description, note, created_at) FROM stdin;
\.


--
-- TOC entry 5655 (class 0 OID 24674)
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
1	Sebastian	Galvan	+573218005837	sebastianjosegalvanluna090@gmail.com	2006-08-18	2026-06-17 15:59:39.383749	\N	C:/Users/Sebastian Galvan/Pictures/Screenshots/Captura de pantalla 2025-09-03 081857.png	\N	\N	\N	\N	\N		\N		
16	Enzo	Hernandez Fonseca	+573014696321	enzohernandezfonseca@gmail.com	1989-08-23	2026-06-27 17:29:59.678197	\N	\N	\N	\N	\N	\N	\N		\N		
8	Robert Alejandro	Manotas Hernandez	+573218939391	robert.alejandro.manotas@gmail.com	1998-11-08	2026-06-23 09:18:48.291503	\N	\N	\N	\N	\N	\N	\N		\N		
17	Alvaro	Mendez vargas	+573158999565	almevar@gmail.com	1969-06-30	2026-06-27 17:34:22.98005	\N	\N	\N	\N	\N	\N	\N		\N		
18	Claudia Patricia	Gamboa Fajardo	+573165137797	maz.gamboa@gmail.com	1971-06-29	2026-06-27 17:36:53.549105	\N	\N	\N	\N	\N	\N	\N		\N		
19	Sara Victoria	Ilias Solano	\N	\N	2003-09-17	2026-06-27 17:38:20.607559	\N	\N	\N	\N	\N	\N	\N		\N		
6	Maya	Oviedo Granados	\N	mayaoviedo1@gmail.com	2008-06-29	2026-06-20 00:55:52.873194	1	\N	\N	\N	\N	\N	\N		\N		
20	Juan Diego	Barriga	\N	\N	2008-07-04	2026-07-04 14:30:58.952813	\N	\N	\N	\N	\N	\N	\N		\N		
21	Victoria Salomé	Rodríguez Barrios	\N	\N	2023-01-27	2026-07-04 23:35:46.014584	\N	\N	Calle 69-D #38-138	Barranquilla	Colombia	Caracas	Venezuela	Las Delicias	\N		
22	Marielsa Ortiz	Parra Ortiz	+573227111205	marielsa.milagro@gmail.com	1997-02-06	2026-07-05 17:58:48.643035	\N	\N	Carrera 42H #80-167	Barranquilla	Colombia	Maracaibo	Venezuela	Ciudad Jardín	\N	Diseñadora Gráfica e Ilustradora	Apto 503, Edificio Jardín Plaza
\.


--
-- TOC entry 5658 (class 0 OID 24694)
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
\.


--
-- TOC entry 5726 (class 0 OID 41172)
-- Dependencies: 301
-- Data for Name: product_purchase_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_purchase_history (id, id_product, buyer_name, purchase_date, quantity, total_price, note) FROM stdin;
\.


--
-- TOC entry 5682 (class 0 OID 24898)
-- Dependencies: 257
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, id_type_product, name, sale_price, stock, id_inventory_category, cost_price, image_path) FROM stdin;
8	1	DOGI talla 22	253000.00	0	3	105000.00	
\.


--
-- TOC entry 5657 (class 0 OID 24685)
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
-- TOC entry 5668 (class 0 OID 24795)
-- Dependencies: 243
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule (id, id_martial_art, name, id_instructor, day_of_week, start_time, end_time, capacity, location, color, status, repeat_type, created_at) FROM stdin;
11	2	SENSHI KICKBOXING AM	13	0	06:00:00	07:00:00	\N	\N	#0000ff	active	weekly	2026-06-25 19:15:49.210585
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
\.


--
-- TOC entry 5728 (class 0 OID 41210)
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
-- TOC entry 5647 (class 0 OID 16435)
-- Dependencies: 222
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status (id, status) FROM stdin;
1	ACTIVE
2	RETIRED
3	INACTIVE
\.


--
-- TOC entry 5750 (class 0 OID 41490)
-- Dependencies: 325
-- Data for Name: student_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_documents (id, id_student, doc_type, file_path, uploaded_at) FROM stdin;
\.


--
-- TOC entry 5720 (class 0 OID 41121)
-- Dependencies: 295
-- Data for Name: student_emergency_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_emergency_contacts (id, id_student, full_name, phone, email, relationship, note, is_primary, created_at) FROM stdin;
1	16	Marielsa Ortiz	+57 304 4628037	\N	Madre	\N	t	2026-07-05 17:58:49.099914
\.


--
-- TOC entry 5718 (class 0 OID 41101)
-- Dependencies: 293
-- Data for Name: student_guardians; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_guardians (id, id_student, full_name, phone, email, relationship, is_primary, created_at, document, profession) FROM stdin;
1	14	.	.	\N	.	t	2026-07-04 14:30:59.161484		
2	15	Brenda Rodríguez Barrios	3244385822	rodriguezbrendaj28@gmail.com	MADRE	t	2026-07-04 23:35:46.43902	1234095584	Consultor de Recursos humanos - Reclutador Internacional
\.


--
-- TOC entry 5748 (class 0 OID 41465)
-- Dependencies: 323
-- Data for Name: student_health_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_health_info (id, id_student, eps, ips, blood_type, allergies, medical_conditions, notes, created_at, updated_at) FROM stdin;
2	15	Salud Total	\N	\N	Ninguna	Ninguna	\N	2026-07-05 01:46:06.136654	2026-07-05 01:46:06.136654
3	16	Sura	\N	B+	Ninguna	Discapacidad auditiva y visión monocular	\N	2026-07-05 17:58:49.106078	2026-07-05 17:58:49.106078
\.


--
-- TOC entry 5686 (class 0 OID 24935)
-- Dependencies: 261
-- Data for Name: student_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_memberships (id, id_student, id_membership_plan, custom_fee, status, start_date, end_date) FROM stdin;
\.


--
-- TOC entry 5660 (class 0 OID 24713)
-- Dependencies: 235
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, id_person, id_type_document, document, category_id, id_status, joined_date, school_name) FROM stdin;
5	10	3	1002156683	4	3	2025-08-01	
7	12	3	1140846453	4	1	2025-01-01	
4	9	3	1140870388	4	1	2026-01-31	
8	1	3	1043442653	1	1	2026-06-24	
6	11	3	1042457203	4	3	2026-02-01	
9	16	3	1045682243	4	1	2022-10-03	
3	8	3	1045755940	4	1	2025-05-31	
10	17	3	79486427	4	3	2025-01-01	
11	18	3	52618381	4	3	2025-01-01	
12	19	3	\N	\N	\N	2026-06-27	
13	6	1	\N	\N	1	2026-06-29	
14	20	\N	\N	2	1	2026-07-04	
15	21	5	1234100989	2	1	2026-07-01	\N
16	22	3	1147696311	4	1	2026-07-03	\N
\.


--
-- TOC entry 5664 (class 0 OID 24758)
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
-- TOC entry 5666 (class 0 OID 24776)
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
-- TOC entry 5706 (class 0 OID 32805)
-- Dependencies: 281
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, task, id_type_task, limit_date) FROM stdin;
1	terminar el app del dajo	\N	2026-06-21
\.


--
-- TOC entry 5645 (class 0 OID 16427)
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
-- TOC entry 5680 (class 0 OID 24887)
-- Dependencies: 255
-- Data for Name: type_products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_products (id, name) FROM stdin;
1	PROTECCION
2	GRUPAL
\.


--
-- TOC entry 5708 (class 0 OID 32821)
-- Dependencies: 283
-- Data for Name: type_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_requirements (id, type_requirement) FROM stdin;
\.


--
-- TOC entry 5700 (class 0 OID 32769)
-- Dependencies: 275
-- Data for Name: type_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_student (id, name) FROM stdin;
\.


--
-- TOC entry 5704 (class 0 OID 32797)
-- Dependencies: 279
-- Data for Name: type_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_task (id, name) FROM stdin;
\.


--
-- TOC entry 5698 (class 0 OID 25086)
-- Dependencies: 273
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, id_person, username, password_hash, is_active, created_at) FROM stdin;
7	10	abraham.lara	$2b$12$hQZZtkUnpBk5N/s2Qn8mt.ClCrAFJA8/omfdK/pgdmh090zBD1aAO	t	2026-06-23 10:52:29.51703
9	12	efrain.carrillo	$2b$12$VXMgG4jxquiI/rM7CcVDpeWrVV/Jq3bXteUMYcZaz3YFwu6tQ.ZMy	t	2026-06-23 11:05:44.242613
6	9	alberto.enrique	$2b$12$G6t1d5xnh2g1UZK3XXRhxOpmXitKFWDBYUKrB0K.deD6s2SIaUP6u	t	2026-06-23 09:49:06.088552
1	1	Sebastiangalvan	$2b$12$C9ASqUYqmRpqGOnHNYHK1uPHfNxwxzZ9tciuMuuC1ZJOy18Z4b7bS	t	2026-06-18 11:52:07.102197
8	11	angelica.muñoz	$2b$12$AUbXRd7p7pZ.tbaVGexxAuxI5i4SvM0rxH/kmiCWUnbkkqqIQM.g6	t	2026-06-23 10:58:03.277975
10	16	1045682243	$2b$12$QNHXIPmXxFyOHs5a2CXYDullgGofsjkH7U4eVQ7ZJiReeW0G/sPX2	t	2026-06-27 17:29:59.678197
5	8	1045755940	$2b$12$0rF0z0ZZTQNHcQ9IpG8KVOhxJY1bT7dIivgGMFU1bbS8JpNC8k/ae	t	2026-06-23 09:18:48.291503
11	17	79486427	$2b$12$MSADWUxt03WcD9S9FyzvEOmFPIIY0Wvct0N.GVE5hIIUqxUSKK6uW	t	2026-06-27 17:34:22.98005
12	18	52618381	$2b$12$LE2jcslw52hn8gOapjwQxeSQDTk5qGdmo3ryxeoiCIrdZhOF6qvv6	t	2026-06-27 17:36:53.549105
13	19	saravictoria.iliassolano	$2b$12$yZ2gw4cSH4TQ/vjjqw5enOwlFTv2FrH59hsrRC7w1z4IMEvB3aKQi	t	2026-06-27 17:38:20.607559
4	6	maya.oviedo	$2b$12$9BVmGgNBLsuR4usEAZu9ueXzXx7xa0a3zIh2w1JZglYKa/aI7rqp6	t	2026-06-20 00:55:52.873194
14	20	juandiego.barriga	$2b$12$e03J6nb4.aS5QpYOmWEtoevHfwys6mdPkwgyW5Aaw988mQ9sw1pXW	t	2026-07-04 14:30:59.156493
15	21	1234100989	$2b$12$REnvxlVR/oj0xmiWRy4cpuGYk.8V7uWyZ7PcSjPrFEIQoqn9Nc7JG	t	2026-07-04 23:35:46.389394
16	22	1147696311	$2b$12$nx1yB2/weVxa461gXYcKNe2AQAwawm.NNenEHqDP1oim23L68kkYa	t	2026-07-05 17:58:49.041289
\.


--
-- TOC entry 5807 (class 0 OID 0)
-- Dependencies: 270
-- Name: account_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.account_movements_id_seq', 1, false);


--
-- TOC entry 5808 (class 0 OID 0)
-- Dependencies: 246
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_id_seq', 3, true);


--
-- TOC entry 5809 (class 0 OID 0)
-- Dependencies: 284
-- Name: belt_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belt_requirements_id_seq', 1, true);


--
-- TOC entry 5810 (class 0 OID 0)
-- Dependencies: 227
-- Name: belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belts_id_seq', 48, true);


--
-- TOC entry 5811 (class 0 OID 0)
-- Dependencies: 223
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 4, true);


--
-- TOC entry 5812 (class 0 OID 0)
-- Dependencies: 244
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classes_id_seq', 4, true);


--
-- TOC entry 5813 (class 0 OID 0)
-- Dependencies: 276
-- Name: codes_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.codes_users_id_seq', 5, true);


--
-- TOC entry 5814 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.destination_account_id_seq', 1, false);


--
-- TOC entry 5815 (class 0 OID 0)
-- Dependencies: 288
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 1, true);


--
-- TOC entry 5816 (class 0 OID 0)
-- Dependencies: 266
-- Name: expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_categories_id_seq', 1, false);


--
-- TOC entry 5817 (class 0 OID 0)
-- Dependencies: 268
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- TOC entry 5818 (class 0 OID 0)
-- Dependencies: 314
-- Name: finance_expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_categories_id_seq', 4, true);


--
-- TOC entry 5819 (class 0 OID 0)
-- Dependencies: 320
-- Name: finance_expense_inventory_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_inventory_items_id_seq', 1, false);


--
-- TOC entry 5820 (class 0 OID 0)
-- Dependencies: 316
-- Name: finance_expense_subcategories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expense_subcategories_id_seq', 1, false);


--
-- TOC entry 5821 (class 0 OID 0)
-- Dependencies: 318
-- Name: finance_expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_expenses_id_seq', 1, false);


--
-- TOC entry 5822 (class 0 OID 0)
-- Dependencies: 304
-- Name: finance_income_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_id_seq', 5, true);


--
-- TOC entry 5823 (class 0 OID 0)
-- Dependencies: 306
-- Name: finance_income_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_items_id_seq', 17, true);


--
-- TOC entry 5824 (class 0 OID 0)
-- Dependencies: 308
-- Name: finance_income_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_income_participants_id_seq', 10, true);


--
-- TOC entry 5825 (class 0 OID 0)
-- Dependencies: 312
-- Name: finance_receivable_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_receivable_payments_id_seq', 1, false);


--
-- TOC entry 5826 (class 0 OID 0)
-- Dependencies: 310
-- Name: finance_receivables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_receivables_id_seq', 2, true);


--
-- TOC entry 5827 (class 0 OID 0)
-- Dependencies: 290
-- Name: instructor_belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructor_belts_id_seq', 2, true);


--
-- TOC entry 5828 (class 0 OID 0)
-- Dependencies: 286
-- Name: instructor_martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructor_martial_arts_id_seq', 24, true);


--
-- TOC entry 5829 (class 0 OID 0)
-- Dependencies: 236
-- Name: instructors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructors_id_seq', 14, true);


--
-- TOC entry 5830 (class 0 OID 0)
-- Dependencies: 296
-- Name: inventory_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_categories_id_seq', 3, true);


--
-- TOC entry 5831 (class 0 OID 0)
-- Dependencies: 225
-- Name: martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martial_arts_id_seq', 4, true);


--
-- TOC entry 5832 (class 0 OID 0)
-- Dependencies: 298
-- Name: membership_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_categories_id_seq', 2, true);


--
-- TOC entry 5833 (class 0 OID 0)
-- Dependencies: 258
-- Name: membership_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_plans_id_seq', 9, true);


--
-- TOC entry 5834 (class 0 OID 0)
-- Dependencies: 250
-- Name: movement_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movement_type_id_seq', 2, true);


--
-- TOC entry 5835 (class 0 OID 0)
-- Dependencies: 264
-- Name: payment_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_items_id_seq', 1, false);


--
-- TOC entry 5836 (class 0 OID 0)
-- Dependencies: 248
-- Name: payment_method_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_method_id_seq', 1, false);


--
-- TOC entry 5837 (class 0 OID 0)
-- Dependencies: 262
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- TOC entry 5838 (class 0 OID 0)
-- Dependencies: 229
-- Name: people_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.people_id_seq', 22, true);


--
-- TOC entry 5839 (class 0 OID 0)
-- Dependencies: 300
-- Name: product_purchase_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_purchase_history_id_seq', 1, false);


--
-- TOC entry 5840 (class 0 OID 0)
-- Dependencies: 256
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 8, true);


--
-- TOC entry 5841 (class 0 OID 0)
-- Dependencies: 231
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 5, true);


--
-- TOC entry 5842 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_id_seq', 34, true);


--
-- TOC entry 5843 (class 0 OID 0)
-- Dependencies: 302
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.services_id_seq', 5, true);


--
-- TOC entry 5844 (class 0 OID 0)
-- Dependencies: 221
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.status_id_seq', 33, true);


--
-- TOC entry 5845 (class 0 OID 0)
-- Dependencies: 324
-- Name: student_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_documents_id_seq', 1, true);


--
-- TOC entry 5846 (class 0 OID 0)
-- Dependencies: 294
-- Name: student_emergency_contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_emergency_contacts_id_seq', 1, true);


--
-- TOC entry 5847 (class 0 OID 0)
-- Dependencies: 292
-- Name: student_guardians_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_guardians_id_seq', 2, true);


--
-- TOC entry 5848 (class 0 OID 0)
-- Dependencies: 322
-- Name: student_health_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_health_info_id_seq', 3, true);


--
-- TOC entry 5849 (class 0 OID 0)
-- Dependencies: 260
-- Name: student_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_memberships_id_seq', 1, false);


--
-- TOC entry 5850 (class 0 OID 0)
-- Dependencies: 240
-- Name: students_belts_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_history_id_seq', 24, true);


--
-- TOC entry 5851 (class 0 OID 0)
-- Dependencies: 238
-- Name: students_belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_id_seq', 10, true);


--
-- TOC entry 5852 (class 0 OID 0)
-- Dependencies: 234
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 16, true);


--
-- TOC entry 5853 (class 0 OID 0)
-- Dependencies: 280
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, true);


--
-- TOC entry 5854 (class 0 OID 0)
-- Dependencies: 219
-- Name: type_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_document_id_seq', 5, true);


--
-- TOC entry 5855 (class 0 OID 0)
-- Dependencies: 254
-- Name: type_products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_products_id_seq', 2, true);


--
-- TOC entry 5856 (class 0 OID 0)
-- Dependencies: 282
-- Name: type_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_requirements_id_seq', 1, false);


--
-- TOC entry 5857 (class 0 OID 0)
-- Dependencies: 274
-- Name: type_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_student_id_seq', 1, false);


--
-- TOC entry 5858 (class 0 OID 0)
-- Dependencies: 278
-- Name: type_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_task_id_seq', 1, false);


--
-- TOC entry 5859 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 16, true);


--
-- TOC entry 5355 (class 2606 OID 25070)
-- Name: account_movements account_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT account_movements_pkey PRIMARY KEY (id);


--
-- TOC entry 5321 (class 2606 OID 24839)
-- Name: attendance attendance_id_class_id_student_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_id_student_key UNIQUE (id_class, id_student);


--
-- TOC entry 5323 (class 2606 OID 24837)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 5373 (class 2606 OID 32856)
-- Name: belt_requirements belt_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5294 (class 2606 OID 24622)
-- Name: belts belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5286 (class 2606 OID 24596)
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- TOC entry 5288 (class 2606 OID 24594)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5319 (class 2606 OID 24814)
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- TOC entry 5365 (class 2606 OID 32787)
-- Name: codes_users codes_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users
    ADD CONSTRAINT codes_users_pkey PRIMARY KEY (id, id_role);


--
-- TOC entry 5333 (class 2606 OID 24885)
-- Name: destination_account destination_account_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account
    ADD CONSTRAINT destination_account_pkey PRIMARY KEY (id);


--
-- TOC entry 5379 (class 2606 OID 40984)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- TOC entry 5349 (class 2606 OID 25031)
-- Name: expense_categories expense_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_name_key UNIQUE (name);


--
-- TOC entry 5351 (class 2606 OID 25029)
-- Name: expense_categories expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5353 (class 2606 OID 25047)
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- TOC entry 5413 (class 2606 OID 41378)
-- Name: finance_expense_categories finance_expense_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories
    ADD CONSTRAINT finance_expense_categories_name_key UNIQUE (name);


--
-- TOC entry 5415 (class 2606 OID 41376)
-- Name: finance_expense_categories finance_expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_categories
    ADD CONSTRAINT finance_expense_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5423 (class 2606 OID 41438)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5417 (class 2606 OID 41393)
-- Name: finance_expense_subcategories finance_expense_subcategories_category_id_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_category_id_name_key UNIQUE (category_id, name);


--
-- TOC entry 5419 (class 2606 OID 41391)
-- Name: finance_expense_subcategories finance_expense_subcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_pkey PRIMARY KEY (id);


--
-- TOC entry 5421 (class 2606 OID 41415)
-- Name: finance_expenses finance_expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_pkey PRIMARY KEY (id);


--
-- TOC entry 5405 (class 2606 OID 41276)
-- Name: finance_income_items finance_income_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items
    ADD CONSTRAINT finance_income_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5407 (class 2606 OID 41300)
-- Name: finance_income_participants finance_income_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_pkey PRIMARY KEY (id);


--
-- TOC entry 5403 (class 2606 OID 41252)
-- Name: finance_income finance_income_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income
    ADD CONSTRAINT finance_income_pkey PRIMARY KEY (id);


--
-- TOC entry 5411 (class 2606 OID 41359)
-- Name: finance_receivable_payments finance_receivable_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments
    ADD CONSTRAINT finance_receivable_payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5409 (class 2606 OID 41330)
-- Name: finance_receivables finance_receivables_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_pkey PRIMARY KEY (id);


--
-- TOC entry 5381 (class 2606 OID 41039)
-- Name: instructor_belts instructor_belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT instructor_belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5375 (class 2606 OID 32880)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_id_martial_art_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_id_martial_art_key UNIQUE (id_instructor, id_martial_art);


--
-- TOC entry 5377 (class 2606 OID 32878)
-- Name: instructor_martial_arts instructor_martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5308 (class 2606 OID 24751)
-- Name: instructors instructors_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_key UNIQUE (id_person);


--
-- TOC entry 5310 (class 2606 OID 24749)
-- Name: instructors instructors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_pkey PRIMARY KEY (id);


--
-- TOC entry 5391 (class 2606 OID 41153)
-- Name: inventory_categories inventory_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories
    ADD CONSTRAINT inventory_categories_name_key UNIQUE (name);


--
-- TOC entry 5393 (class 2606 OID 41151)
-- Name: inventory_categories inventory_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory_categories
    ADD CONSTRAINT inventory_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5290 (class 2606 OID 24612)
-- Name: martial_arts martial_arts_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_name_key UNIQUE (name);


--
-- TOC entry 5292 (class 2606 OID 24610)
-- Name: martial_arts martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5395 (class 2606 OID 41170)
-- Name: membership_categories membership_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories
    ADD CONSTRAINT membership_categories_name_key UNIQUE (name);


--
-- TOC entry 5397 (class 2606 OID 41168)
-- Name: membership_categories membership_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_categories
    ADD CONSTRAINT membership_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5341 (class 2606 OID 24928)
-- Name: membership_plans membership_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT membership_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 5329 (class 2606 OID 24876)
-- Name: movement_type movement_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_name_key UNIQUE (name);


--
-- TOC entry 5331 (class 2606 OID 24874)
-- Name: movement_type movement_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_pkey PRIMARY KEY (id);


--
-- TOC entry 5347 (class 2606 OID 25003)
-- Name: payment_items payment_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT payment_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5325 (class 2606 OID 24865)
-- Name: payment_method payment_method_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_name_key UNIQUE (name);


--
-- TOC entry 5327 (class 2606 OID 24863)
-- Name: payment_method payment_method_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_pkey PRIMARY KEY (id);


--
-- TOC entry 5345 (class 2606 OID 24974)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5296 (class 2606 OID 24683)
-- Name: people people_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_email_key UNIQUE (email);


--
-- TOC entry 5298 (class 2606 OID 24681)
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (id);


--
-- TOC entry 5399 (class 2606 OID 41186)
-- Name: product_purchase_history product_purchase_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history
    ADD CONSTRAINT product_purchase_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5339 (class 2606 OID 24909)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 5300 (class 2606 OID 24693)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 5302 (class 2606 OID 24691)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5317 (class 2606 OID 24801)
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- TOC entry 5401 (class 2606 OID 41223)
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- TOC entry 5284 (class 2606 OID 16441)
-- Name: status status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- TOC entry 5428 (class 2606 OID 41502)
-- Name: student_documents student_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5388 (class 2606 OID 41135)
-- Name: student_emergency_contacts student_emergency_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts
    ADD CONSTRAINT student_emergency_contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 5385 (class 2606 OID 41114)
-- Name: student_guardians student_guardians_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians
    ADD CONSTRAINT student_guardians_pkey PRIMARY KEY (id);


--
-- TOC entry 5426 (class 2606 OID 41482)
-- Name: student_health_info student_health_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info
    ADD CONSTRAINT student_health_info_pkey PRIMARY KEY (id);


--
-- TOC entry 5343 (class 2606 OID 24945)
-- Name: student_memberships student_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT student_memberships_pkey PRIMARY KEY (id);


--
-- TOC entry 5315 (class 2606 OID 24783)
-- Name: students_belts_history students_belts_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5313 (class 2606 OID 24764)
-- Name: students_belts students_belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5304 (class 2606 OID 24721)
-- Name: students students_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_key UNIQUE (id_person);


--
-- TOC entry 5306 (class 2606 OID 24719)
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- TOC entry 5369 (class 2606 OID 32814)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 5282 (class 2606 OID 16433)
-- Name: type_document type_document_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document
    ADD CONSTRAINT type_document_pkey PRIMARY KEY (id);


--
-- TOC entry 5335 (class 2606 OID 24896)
-- Name: type_products type_products_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_name_key UNIQUE (name);


--
-- TOC entry 5337 (class 2606 OID 24894)
-- Name: type_products type_products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_pkey PRIMARY KEY (id);


--
-- TOC entry 5371 (class 2606 OID 32827)
-- Name: type_requirements type_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements
    ADD CONSTRAINT type_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5363 (class 2606 OID 32775)
-- Name: type_student type_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student
    ADD CONSTRAINT type_student_pkey PRIMARY KEY (id);


--
-- TOC entry 5367 (class 2606 OID 32803)
-- Name: type_task type_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task
    ADD CONSTRAINT type_task_pkey PRIMARY KEY (id);


--
-- TOC entry 5383 (class 2606 OID 41041)
-- Name: instructor_belts uq_instructor_belt_per_art; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT uq_instructor_belt_per_art UNIQUE (id_instructor, id_martial_art);


--
-- TOC entry 5430 (class 2606 OID 41504)
-- Name: student_documents uq_student_doc_type; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT uq_student_doc_type UNIQUE (id_student, doc_type);


--
-- TOC entry 5357 (class 2606 OID 25101)
-- Name: users users_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_key UNIQUE (id_person);


--
-- TOC entry 5359 (class 2606 OID 25099)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5361 (class 2606 OID 25103)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 5424 (class 1259 OID 41488)
-- Name: idx_student_health_info_id_student; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_student_health_info_id_student ON public.student_health_info USING btree (id_student);


--
-- TOC entry 5311 (class 1259 OID 40998)
-- Name: ux_instructors_only_one_sensei; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_instructors_only_one_sensei ON public.instructors USING btree (is_sensei) WHERE (is_sensei = true);


--
-- TOC entry 5389 (class 1259 OID 41142)
-- Name: ux_student_one_primary_emergency_contact; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_student_one_primary_emergency_contact ON public.student_emergency_contacts USING btree (id_student) WHERE (is_primary = true);


--
-- TOC entry 5386 (class 1259 OID 41141)
-- Name: ux_student_one_primary_guardian; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_student_one_primary_guardian ON public.student_guardians USING btree (id_student) WHERE (is_primary = true);


--
-- TOC entry 5493 (class 2620 OID 24852)
-- Name: students_belts tg_students_belts_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_insert AFTER INSERT ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_insert();


--
-- TOC entry 5494 (class 2620 OID 24854)
-- Name: students_belts tg_students_belts_update; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_update AFTER UPDATE ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_update();


--
-- TOC entry 5496 (class 2620 OID 25084)
-- Name: expenses trg_expense_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_expense_insert_movement AFTER INSERT ON public.expenses FOR EACH ROW EXECUTE FUNCTION public.fn_expense_insert_movement();


--
-- TOC entry 5495 (class 2620 OID 25082)
-- Name: payments trg_payment_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_payment_insert_movement AFTER INSERT ON public.payments FOR EACH ROW EXECUTE FUNCTION public.fn_payment_insert_movement();


--
-- TOC entry 5448 (class 2606 OID 24840)
-- Name: attendance attendance_id_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_fkey FOREIGN KEY (id_class) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- TOC entry 5449 (class 2606 OID 24845)
-- Name: attendance attendance_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5468 (class 2606 OID 32857)
-- Name: belt_requirements belt_requirements_belt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_belt_id_fkey FOREIGN KEY (belt_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5469 (class 2606 OID 32862)
-- Name: belt_requirements belt_requirements_id_type_requeriments_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_id_type_requeriments_fkey FOREIGN KEY (id_type_requeriments) REFERENCES public.type_requirements(id) ON DELETE CASCADE;


--
-- TOC entry 5446 (class 2606 OID 24825)
-- Name: classes classes_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5447 (class 2606 OID 24820)
-- Name: classes classes_id_schedule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_schedule_fkey FOREIGN KEY (id_schedule) REFERENCES public.schedule(id);


--
-- TOC entry 5489 (class 2606 OID 41439)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_expense_id_fkey FOREIGN KEY (expense_id) REFERENCES public.finance_expenses(id) ON DELETE CASCADE;


--
-- TOC entry 5490 (class 2606 OID 41444)
-- Name: finance_expense_inventory_items finance_expense_inventory_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_inventory_items
    ADD CONSTRAINT finance_expense_inventory_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 5486 (class 2606 OID 41394)
-- Name: finance_expense_subcategories finance_expense_subcategories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expense_subcategories
    ADD CONSTRAINT finance_expense_subcategories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_expense_categories(id) ON DELETE CASCADE;


--
-- TOC entry 5487 (class 2606 OID 41416)
-- Name: finance_expenses finance_expenses_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_expense_categories(id);


--
-- TOC entry 5488 (class 2606 OID 41421)
-- Name: finance_expenses finance_expenses_subcategory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_expenses
    ADD CONSTRAINT finance_expenses_subcategory_id_fkey FOREIGN KEY (subcategory_id) REFERENCES public.finance_expense_subcategories(id);


--
-- TOC entry 5479 (class 2606 OID 41277)
-- Name: finance_income_items finance_income_items_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_items
    ADD CONSTRAINT finance_income_items_income_id_fkey FOREIGN KEY (income_id) REFERENCES public.finance_income(id) ON DELETE CASCADE;


--
-- TOC entry 5480 (class 2606 OID 41301)
-- Name: finance_income_participants finance_income_participants_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_income_id_fkey FOREIGN KEY (income_id) REFERENCES public.finance_income(id) ON DELETE CASCADE;


--
-- TOC entry 5481 (class 2606 OID 41306)
-- Name: finance_income_participants finance_income_participants_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income_participants
    ADD CONSTRAINT finance_income_participants_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5478 (class 2606 OID 41253)
-- Name: finance_income finance_income_payer_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_income
    ADD CONSTRAINT finance_income_payer_person_id_fkey FOREIGN KEY (payer_person_id) REFERENCES public.people(id);


--
-- TOC entry 5485 (class 2606 OID 41360)
-- Name: finance_receivable_payments finance_receivable_payments_receivable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivable_payments
    ADD CONSTRAINT finance_receivable_payments_receivable_id_fkey FOREIGN KEY (receivable_id) REFERENCES public.finance_receivables(id) ON DELETE CASCADE;


--
-- TOC entry 5482 (class 2606 OID 41331)
-- Name: finance_receivables finance_receivables_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.people(id);


--
-- TOC entry 5483 (class 2606 OID 41336)
-- Name: finance_receivables finance_receivables_source_income_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_source_income_id_fkey FOREIGN KEY (source_income_id) REFERENCES public.finance_income(id);


--
-- TOC entry 5484 (class 2606 OID 41341)
-- Name: finance_receivables finance_receivables_source_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_receivables
    ADD CONSTRAINT finance_receivables_source_participant_id_fkey FOREIGN KEY (source_participant_id) REFERENCES public.finance_income_participants(id);


--
-- TOC entry 5464 (class 2606 OID 25071)
-- Name: account_movements fk_account_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5465 (class 2606 OID 25076)
-- Name: account_movements fk_account_movement_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_movement_type FOREIGN KEY (id_movement_type) REFERENCES public.movement_type(id);


--
-- TOC entry 5462 (class 2606 OID 25048)
-- Name: expenses fk_expense_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_category FOREIGN KEY (id_expense_category) REFERENCES public.expense_categories(id);


--
-- TOC entry 5463 (class 2606 OID 25053)
-- Name: expenses fk_expense_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5467 (class 2606 OID 32815)
-- Name: tasks fk_id_type_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_id_type_task FOREIGN KEY (id_type_task) REFERENCES public.type_task(id) NOT VALID;


--
-- TOC entry 5472 (class 2606 OID 41052)
-- Name: instructor_belts fk_instructor_belts_belt; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_belt FOREIGN KEY (id_belt) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5473 (class 2606 OID 41042)
-- Name: instructor_belts fk_instructor_belts_instructor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_instructor FOREIGN KEY (id_instructor) REFERENCES public.instructors(id) ON DELETE CASCADE;


--
-- TOC entry 5474 (class 2606 OID 41047)
-- Name: instructor_belts fk_instructor_belts_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_belts
    ADD CONSTRAINT fk_instructor_belts_martial_art FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id) ON DELETE CASCADE;


--
-- TOC entry 5431 (class 2606 OID 24625)
-- Name: belts fk_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT fk_martial_art FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5452 (class 2606 OID 41194)
-- Name: membership_plans fk_membership_plans_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT fk_membership_plans_category FOREIGN KEY (id_membership_category) REFERENCES public.membership_categories(id);


--
-- TOC entry 5453 (class 2606 OID 24929)
-- Name: membership_plans fk_membership_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT fk_membership_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5456 (class 2606 OID 24980)
-- Name: payments fk_payment_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5459 (class 2606 OID 25014)
-- Name: payment_items fk_payment_items_membership; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_membership FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5460 (class 2606 OID 25004)
-- Name: payment_items fk_payment_items_payment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_payment FOREIGN KEY (id_payments) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- TOC entry 5461 (class 2606 OID 25009)
-- Name: payment_items fk_payment_items_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_product FOREIGN KEY (id_product) REFERENCES public.products(id);


--
-- TOC entry 5457 (class 2606 OID 24975)
-- Name: payments fk_payment_method; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_method FOREIGN KEY (id_payment_method) REFERENCES public.payment_method(id);


--
-- TOC entry 5458 (class 2606 OID 24985)
-- Name: payments fk_people; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_people FOREIGN KEY (id_person) REFERENCES public.people(id);


--
-- TOC entry 5432 (class 2606 OID 32788)
-- Name: people fk_people_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT fk_people_users FOREIGN KEY (id_code_users) REFERENCES public.users(id);


--
-- TOC entry 5450 (class 2606 OID 41189)
-- Name: products fk_products_inventory_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_inventory_category FOREIGN KEY (id_inventory_category) REFERENCES public.inventory_categories(id);


--
-- TOC entry 5451 (class 2606 OID 24910)
-- Name: products fk_products_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5477 (class 2606 OID 41199)
-- Name: product_purchase_history fk_purchase_history_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_purchase_history
    ADD CONSTRAINT fk_purchase_history_product FOREIGN KEY (id_product) REFERENCES public.products(id);


--
-- TOC entry 5454 (class 2606 OID 24951)
-- Name: student_memberships fk_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student FOREIGN KEY (id_student) REFERENCES public.students(id);


--
-- TOC entry 5476 (class 2606 OID 41136)
-- Name: student_emergency_contacts fk_student_emergency_contacts_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_emergency_contacts
    ADD CONSTRAINT fk_student_emergency_contacts_student FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5475 (class 2606 OID 41115)
-- Name: student_guardians fk_student_guardians_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_guardians
    ADD CONSTRAINT fk_student_guardians_student FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5455 (class 2606 OID 24946)
-- Name: student_memberships fk_student_membership_plan; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student_membership_plan FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5470 (class 2606 OID 32881)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5471 (class 2606 OID 32886)
-- Name: instructor_martial_arts instructor_martial_arts_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5439 (class 2606 OID 24752)
-- Name: instructors instructors_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5433 (class 2606 OID 24697)
-- Name: person_roles person_roles_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5434 (class 2606 OID 24702)
-- Name: person_roles person_roles_id_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_role_fkey FOREIGN KEY (id_role) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 5444 (class 2606 OID 40964)
-- Name: schedule schedule_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5445 (class 2606 OID 24802)
-- Name: schedule schedule_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5492 (class 2606 OID 41505)
-- Name: student_documents student_documents_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5491 (class 2606 OID 41483)
-- Name: student_health_info student_health_info_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_health_info
    ADD CONSTRAINT student_health_info_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5442 (class 2606 OID 24789)
-- Name: students_belts_history students_belts_history_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5443 (class 2606 OID 24784)
-- Name: students_belts_history students_belts_history_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5440 (class 2606 OID 24770)
-- Name: students_belts students_belts_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5441 (class 2606 OID 24765)
-- Name: students_belts students_belts_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5435 (class 2606 OID 24732)
-- Name: students students_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- TOC entry 5436 (class 2606 OID 24722)
-- Name: students students_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5437 (class 2606 OID 24737)
-- Name: students students_id_status_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.status(id);


--
-- TOC entry 5438 (class 2606 OID 24727)
-- Name: students students_id_type_document_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_type_document_fkey FOREIGN KEY (id_type_document) REFERENCES public.type_document(id);


--
-- TOC entry 5466 (class 2606 OID 25104)
-- Name: users users_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id);


-- Completed on 2026-07-05 21:59:20

--
-- PostgreSQL database dump complete
--

\unrestrict saswbFMlOTwYOT1efRY5oouM7imsWBxwqXKzjrKyiLGX7ejC2e2FjKeHbTzb79y

