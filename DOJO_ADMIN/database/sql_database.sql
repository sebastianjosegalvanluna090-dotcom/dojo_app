--
-- PostgreSQL database dump
--

\restrict WSygcKUEqavyJhzhDXRqe6aZnfO2yBhRz3JiVyW0UkHxMPxa6NFpLdmExy3ogSP

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-06-23 12:00:10

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
-- TOC entry 290 (class 1255 OID 25083)
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
-- TOC entry 291 (class 1255 OID 25081)
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
-- TOC entry 288 (class 1255 OID 24851)
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
-- TOC entry 289 (class 1255 OID 24853)
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
-- TOC entry 5439 (class 0 OID 0)
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
    id_student integer
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
-- TOC entry 5440 (class 0 OID 0)
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
-- TOC entry 5441 (class 0 OID 0)
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
-- TOC entry 5442 (class 0 OID 0)
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
-- TOC entry 5443 (class 0 OID 0)
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
    date date
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
-- TOC entry 5444 (class 0 OID 0)
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
-- TOC entry 5445 (class 0 OID 0)
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
-- TOC entry 5446 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.destination_account_id_seq OWNED BY public.destination_account.id;


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
-- TOC entry 5447 (class 0 OID 0)
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
-- TOC entry 5448 (class 0 OID 0)
-- Dependencies: 268
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


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
-- TOC entry 5449 (class 0 OID 0)
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
    id_person integer
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
-- TOC entry 5450 (class 0 OID 0)
-- Dependencies: 236
-- Name: instructors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.instructors_id_seq OWNED BY public.instructors.id;


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
-- TOC entry 5451 (class 0 OID 0)
-- Dependencies: 225
-- Name: martial_arts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.martial_arts_id_seq OWNED BY public.martial_arts.id;


--
-- TOC entry 259 (class 1259 OID 24916)
-- Name: membership_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.membership_plans (
    id integer NOT NULL,
    id_type_product integer NOT NULL,
    name character varying(150) NOT NULL,
    monthly_fee numeric(12,2) NOT NULL,
    discount numeric(12,2) DEFAULT 0,
    discount_by_person boolean DEFAULT false,
    classes_per_week integer NOT NULL
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
-- TOC entry 5452 (class 0 OID 0)
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
-- TOC entry 5453 (class 0 OID 0)
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
-- TOC entry 5454 (class 0 OID 0)
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
-- TOC entry 5455 (class 0 OID 0)
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
-- TOC entry 5456 (class 0 OID 0)
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
    photo_path text
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
-- TOC entry 5457 (class 0 OID 0)
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
-- TOC entry 257 (class 1259 OID 24898)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    id_type_product integer NOT NULL,
    name character varying(150) NOT NULL,
    sale_price numeric(12,2) NOT NULL,
    stock integer DEFAULT 0 NOT NULL
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
-- TOC entry 5458 (class 0 OID 0)
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
-- TOC entry 5459 (class 0 OID 0)
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
    name character varying(100)
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
-- TOC entry 5460 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


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
-- TOC entry 5461 (class 0 OID 0)
-- Dependencies: 221
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;


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
-- TOC entry 5462 (class 0 OID 0)
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
    joined_date date
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
-- TOC entry 5463 (class 0 OID 0)
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
-- TOC entry 5464 (class 0 OID 0)
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
-- TOC entry 5465 (class 0 OID 0)
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
-- TOC entry 5466 (class 0 OID 0)
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
-- TOC entry 5467 (class 0 OID 0)
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
-- TOC entry 5468 (class 0 OID 0)
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
-- TOC entry 5469 (class 0 OID 0)
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
-- TOC entry 5470 (class 0 OID 0)
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
-- TOC entry 5471 (class 0 OID 0)
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
-- TOC entry 5472 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 5065 (class 2604 OID 25062)
-- Name: account_movements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements ALTER COLUMN id SET DEFAULT nextval('public.account_movements_id_seq'::regclass);


--
-- TOC entry 5046 (class 2604 OID 24834)
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- TOC entry 5075 (class 2604 OID 32849)
-- Name: belt_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements ALTER COLUMN id SET DEFAULT nextval('public.belt_requirements_id_seq'::regclass);


--
-- TOC entry 5033 (class 2604 OID 24617)
-- Name: belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts ALTER COLUMN id SET DEFAULT nextval('public.belts_id_seq'::regclass);


--
-- TOC entry 5031 (class 2604 OID 24590)
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- TOC entry 5045 (class 2604 OID 24811)
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- TOC entry 5071 (class 2604 OID 32780)
-- Name: codes_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users ALTER COLUMN id SET DEFAULT nextval('public.codes_users_id_seq'::regclass);


--
-- TOC entry 5049 (class 2604 OID 24881)
-- Name: destination_account id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account ALTER COLUMN id SET DEFAULT nextval('public.destination_account_id_seq'::regclass);


--
-- TOC entry 5062 (class 2604 OID 25023)
-- Name: expense_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories ALTER COLUMN id SET DEFAULT nextval('public.expense_categories_id_seq'::regclass);


--
-- TOC entry 5063 (class 2604 OID 25036)
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- TOC entry 5077 (class 2604 OID 32871)
-- Name: instructor_martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts ALTER COLUMN id SET DEFAULT nextval('public.instructor_martial_arts_id_seq'::regclass);


--
-- TOC entry 5040 (class 2604 OID 24746)
-- Name: instructors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors ALTER COLUMN id SET DEFAULT nextval('public.instructors_id_seq'::regclass);


--
-- TOC entry 5032 (class 2604 OID 24606)
-- Name: martial_arts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts ALTER COLUMN id SET DEFAULT nextval('public.martial_arts_id_seq'::regclass);


--
-- TOC entry 5053 (class 2604 OID 24919)
-- Name: membership_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans ALTER COLUMN id SET DEFAULT nextval('public.membership_plans_id_seq'::regclass);


--
-- TOC entry 5048 (class 2604 OID 24870)
-- Name: movement_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type ALTER COLUMN id SET DEFAULT nextval('public.movement_type_id_seq'::regclass);


--
-- TOC entry 5060 (class 2604 OID 24994)
-- Name: payment_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items ALTER COLUMN id SET DEFAULT nextval('public.payment_items_id_seq'::regclass);


--
-- TOC entry 5047 (class 2604 OID 24859)
-- Name: payment_method id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method ALTER COLUMN id SET DEFAULT nextval('public.payment_method_id_seq'::regclass);


--
-- TOC entry 5057 (class 2604 OID 24960)
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- TOC entry 5036 (class 2604 OID 24677)
-- Name: people id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people ALTER COLUMN id SET DEFAULT nextval('public.people_id_seq'::regclass);


--
-- TOC entry 5051 (class 2604 OID 24901)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 5038 (class 2604 OID 24688)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 5044 (class 2604 OID 24798)
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- TOC entry 5030 (class 2604 OID 16438)
-- Name: status id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);


--
-- TOC entry 5056 (class 2604 OID 24938)
-- Name: student_memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships ALTER COLUMN id SET DEFAULT nextval('public.student_memberships_id_seq'::regclass);


--
-- TOC entry 5039 (class 2604 OID 24716)
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- TOC entry 5041 (class 2604 OID 24761)
-- Name: students_belts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts ALTER COLUMN id SET DEFAULT nextval('public.students_belts_id_seq'::regclass);


--
-- TOC entry 5042 (class 2604 OID 24779)
-- Name: students_belts_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history ALTER COLUMN id SET DEFAULT nextval('public.students_belts_history_id_seq'::regclass);


--
-- TOC entry 5073 (class 2604 OID 32808)
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- TOC entry 5029 (class 2604 OID 16430)
-- Name: type_document id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document ALTER COLUMN id SET DEFAULT nextval('public.type_document_id_seq'::regclass);


--
-- TOC entry 5050 (class 2604 OID 24890)
-- Name: type_products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products ALTER COLUMN id SET DEFAULT nextval('public.type_products_id_seq'::regclass);


--
-- TOC entry 5074 (class 2604 OID 32824)
-- Name: type_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements ALTER COLUMN id SET DEFAULT nextval('public.type_requirements_id_seq'::regclass);


--
-- TOC entry 5070 (class 2604 OID 32772)
-- Name: type_student id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student ALTER COLUMN id SET DEFAULT nextval('public.type_student_id_seq'::regclass);


--
-- TOC entry 5072 (class 2604 OID 32800)
-- Name: type_task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task ALTER COLUMN id SET DEFAULT nextval('public.type_task_id_seq'::regclass);


--
-- TOC entry 5067 (class 2604 OID 25089)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5417 (class 0 OID 25059)
-- Dependencies: 271
-- Data for Name: account_movements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_movements (id, id_destination_account, id_movement_type, amount, payment_date) FROM stdin;
\.


--
-- TOC entry 5393 (class 0 OID 24831)
-- Dependencies: 247
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance (id, id_class, id_student) FROM stdin;
\.


--
-- TOC entry 5431 (class 0 OID 32846)
-- Dependencies: 285
-- Data for Name: belt_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.belt_requirements (id, belt_id, requirement, id_type_requeriments, created_at) FROM stdin;
\.


--
-- TOC entry 5374 (class 0 OID 24614)
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
13	Marron	1	11	#623307	\N	0	#FFFFFF
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
31	Morado 1° GRADO	3	12	#8b0350	\N	1	#FFFFFF
33	Negro 1° DAN	1	13	#000000	\N	1	#FFFF00
34	Negro 2° DAN	1	14	#000000	\N	2	#FFFF00
35	Negro 3° DAN	1	15	#000000	\N	3	#FFFF00
36	Negro 4° DAN	1	16	#000000	\N	4	#FFFF00
\.


--
-- TOC entry 5370 (class 0 OID 24587)
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
-- TOC entry 5391 (class 0 OID 24808)
-- Dependencies: 245
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (id, id_schedule, id_instructor, date) FROM stdin;
\.


--
-- TOC entry 5423 (class 0 OID 32777)
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
-- TOC entry 5399 (class 0 OID 24878)
-- Dependencies: 253
-- Data for Name: destination_account; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.destination_account (id, name, account_number) FROM stdin;
\.


--
-- TOC entry 5413 (class 0 OID 25020)
-- Dependencies: 267
-- Data for Name: expense_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_categories (id, name, description) FROM stdin;
\.


--
-- TOC entry 5415 (class 0 OID 25033)
-- Dependencies: 269
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expenses (id, id_expense_category, id_destination_account, amount, expense_date, description, invoice_number, created_at) FROM stdin;
\.


--
-- TOC entry 5433 (class 0 OID 32868)
-- Dependencies: 287
-- Data for Name: instructor_martial_arts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructor_martial_arts (id, id_instructor, id_martial_art, can_promote) FROM stdin;
5	1	3	t
6	1	4	t
7	1	1	t
8	1	2	t
\.


--
-- TOC entry 5383 (class 0 OID 24743)
-- Dependencies: 237
-- Data for Name: instructors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.instructors (id, id_person) FROM stdin;
1	7
2	6
\.


--
-- TOC entry 5372 (class 0 OID 24603)
-- Dependencies: 226
-- Data for Name: martial_arts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.martial_arts (id, name) FROM stdin;
1	Karate Kyokushin
2	Kick Boxing
3	Brazilian Jiu-Jitsu
4	Functional Trainning
\.


--
-- TOC entry 5405 (class 0 OID 24916)
-- Dependencies: 259
-- Data for Name: membership_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membership_plans (id, id_type_product, name, monthly_fee, discount, discount_by_person, classes_per_week) FROM stdin;
\.


--
-- TOC entry 5397 (class 0 OID 24867)
-- Dependencies: 251
-- Data for Name: movement_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.movement_type (id, name) FROM stdin;
1	expenses
2	payments
\.


--
-- TOC entry 5411 (class 0 OID 24991)
-- Dependencies: 265
-- Data for Name: payment_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_items (id, id_payments, id_product, id_membership_plan, quantity, unit_price, subtotal) FROM stdin;
\.


--
-- TOC entry 5395 (class 0 OID 24856)
-- Dependencies: 249
-- Data for Name: payment_method; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_method (id, name) FROM stdin;
\.


--
-- TOC entry 5409 (class 0 OID 24957)
-- Dependencies: 263
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, id_person, total, total_paid, payment_date, id_payment_method, id_destination_account, description, note, created_at) FROM stdin;
\.


--
-- TOC entry 5376 (class 0 OID 24674)
-- Dependencies: 230
-- Data for Name: people; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.people (id, first_name, last_name, phone, email, birthdate, created_at, id_code_users, photo_path) FROM stdin;
1	Sebastian	Galvan	+57 3218005837	sebastianjosegalvanluna090@gmail.com	2006-08-18	2026-06-17 15:59:39.383749	\N	\N
6	Maya	Oviedo Granados	\N	mayaoviedo1@gmail.com	\N	2026-06-20 00:55:52.873194	1	\N
3	Maya	Oviedo Granados	+573507531819	mayaoviedo@gmail.com	2005-02-13	2026-06-19 13:33:18.552078	\N	C:/Users/Sebastian Galvan/Pictures/Screenshots/Captura de pantalla 2026-02-21 233410.png
7	Sebastian Jose	Galvan Luna	+573218005837	paramipaxd@gmail.com	2006-08-18	2026-06-20 02:23:30.987013	\N	C:/Users/Sebastian Galvan/Pictures/Screenshots/Captura de pantalla 2026-06-03 011301.png
8	Robert Alejandro	Manotas Hernandez	+573218939391	robert.alejandro.manotas@gmail.com	1998-11-08	2026-06-23 09:18:48.291503	\N	\N
9	Alberto Enrique	Santiago Hernandez	+573005171615	albertosan_94@hotmail.com	1994-07-28	2026-06-23 09:49:06.088552	\N	\N
10	Abraham	Lara	+573002167962	abrahamlrpz@gmail.com	2000-12-13	2026-06-23 10:52:29.51703	\N	\N
11	Angélica Patricia	Muñoz montesino	+573215561149	Munozmontesinoa@gmail.com	1997-12-13	2026-06-23 10:58:03.277975	\N	\N
12	Efrain	Carillo Rodrigez	+573016264534	efraincarrillorodriguez2024@gmail.com	1991-12-09	2026-06-23 11:05:44.242613	\N	\N
\.


--
-- TOC entry 5379 (class 0 OID 24694)
-- Dependencies: 233
-- Data for Name: person_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.person_roles (id_person, id_role) FROM stdin;
1	1
6	1
8	5
9	5
10	5
11	5
12	5
\.


--
-- TOC entry 5403 (class 0 OID 24898)
-- Dependencies: 257
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, id_type_product, name, sale_price, stock) FROM stdin;
\.


--
-- TOC entry 5378 (class 0 OID 24685)
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
-- TOC entry 5389 (class 0 OID 24795)
-- Dependencies: 243
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule (id, id_martial_art, name) FROM stdin;
\.


--
-- TOC entry 5368 (class 0 OID 16435)
-- Dependencies: 222
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.status (id, status) FROM stdin;
1	ACTIVE
2	RETIRED
3	INACTIVE
\.


--
-- TOC entry 5407 (class 0 OID 24935)
-- Dependencies: 261
-- Data for Name: student_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_memberships (id, id_student, id_membership_plan, custom_fee, status, start_date, end_date) FROM stdin;
\.


--
-- TOC entry 5381 (class 0 OID 24713)
-- Dependencies: 235
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, id_person, id_type_document, document, category_id, id_status, joined_date) FROM stdin;
1	3	3	1034397119	4	1	\N
2	7	3	1043442653	4	1	2025-09-08
3	8	3	1045755940	4	1	2025-05-31
4	9	1	1140870388	4	1	2026-01-31
5	10	3	1002156683	4	3	2025-08-01
6	11	3	1042457203	4	3	2026-02-01
7	12	3	1140846453	4	1	2025-01-01
\.


--
-- TOC entry 5385 (class 0 OID 24758)
-- Dependencies: 239
-- Data for Name: students_belts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_belts (id, id_student, id_belt) FROM stdin;
1	1	13
2	2	17
3	2	11
4	3	17
5	4	1
6	3	5
\.


--
-- TOC entry 5387 (class 0 OID 24776)
-- Dependencies: 241
-- Data for Name: students_belts_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_belts_history (id, id_student, id_belt, action, date_changed) FROM stdin;
1	1	1	asignacion inicial	2026-06-22 02:09:14.318792
2	1	1	promotion	2026-06-22 02:09:14.318792
3	1	13	promocion	2026-06-22 02:10:06.088234
4	1	13	promotion	2026-06-22 02:10:06.088234
5	2	11	asignacion inicial	2026-06-22 11:25:46.952889
6	2	11	promotion	2026-06-22 11:25:46.952889
7	2	17	promocion	2026-06-22 17:03:46.800431
8	2	17	promotion	2026-06-22 17:03:46.800431
9	2	11	asignacion inicial	2026-06-23 08:33:43.3039
10	2	11	promotion	2026-06-23 08:33:43.3039
11	3	17	asignacion inicial	2026-06-23 09:49:41.208724
12	3	17	promotion	2026-06-23 09:49:41.208724
13	4	1	asignacion inicial	2026-06-23 09:50:18.989583
14	4	1	promotion	2026-06-23 09:50:18.989583
15	3	5	asignacion inicial	2026-06-23 09:51:23.004934
16	3	5	promotion	2026-06-23 09:51:23.004934
\.


--
-- TOC entry 5427 (class 0 OID 32805)
-- Dependencies: 281
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, task, id_type_task, limit_date) FROM stdin;
1	terminar el app del dajo	\N	2026-06-21
\.


--
-- TOC entry 5366 (class 0 OID 16427)
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
-- TOC entry 5401 (class 0 OID 24887)
-- Dependencies: 255
-- Data for Name: type_products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_products (id, name) FROM stdin;
\.


--
-- TOC entry 5429 (class 0 OID 32821)
-- Dependencies: 283
-- Data for Name: type_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_requirements (id, type_requirement) FROM stdin;
\.


--
-- TOC entry 5421 (class 0 OID 32769)
-- Dependencies: 275
-- Data for Name: type_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_student (id, name) FROM stdin;
\.


--
-- TOC entry 5425 (class 0 OID 32797)
-- Dependencies: 279
-- Data for Name: type_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.type_task (id, name) FROM stdin;
\.


--
-- TOC entry 5419 (class 0 OID 25086)
-- Dependencies: 273
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, id_person, username, password_hash, is_active, created_at) FROM stdin;
1	1	Sebastiangalvan	$2b$12$C9ASqUYqmRpqGOnHNYHK1uPHfNxwxzZ9tciuMuuC1ZJOy18Z4b7bS	t	2026-06-18 11:52:07.102197
4	6	maya.oviedo	$2b$12$9BVmGgNBLsuR4usEAZu9ueXzXx7xa0a3zIh2w1JZglYKa/aI7rqp6	t	2026-06-20 00:55:52.873194
5	8	1045755940	$2b$12$0rF0z0ZZTQNHcQ9IpG8KVOhxJY1bT7dIivgGMFU1bbS8JpNC8k/ae	t	2026-06-23 09:18:48.291503
6	9	alberto.enrique	$2b$12$G6t1d5xnh2g1UZK3XXRhxOpmXitKFWDBYUKrB0K.deD6s2SIaUP6u	t	2026-06-23 09:49:06.088552
7	10	abraham.lara	$2b$12$hQZZtkUnpBk5N/s2Qn8mt.ClCrAFJA8/omfdK/pgdmh090zBD1aAO	t	2026-06-23 10:52:29.51703
8	11	angelica.muñoz	$2b$12$AUbXRd7p7pZ.tbaVGexxAuxI5i4SvM0rxH/kmiCWUnbkkqqIQM.g6	t	2026-06-23 10:58:03.277975
9	12	efrain.carrillo	$2b$12$VXMgG4jxquiI/rM7CcVDpeWrVV/Jq3bXteUMYcZaz3YFwu6tQ.ZMy	t	2026-06-23 11:05:44.242613
\.


--
-- TOC entry 5473 (class 0 OID 0)
-- Dependencies: 270
-- Name: account_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.account_movements_id_seq', 1, false);


--
-- TOC entry 5474 (class 0 OID 0)
-- Dependencies: 246
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_id_seq', 1, false);


--
-- TOC entry 5475 (class 0 OID 0)
-- Dependencies: 284
-- Name: belt_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belt_requirements_id_seq', 1, false);


--
-- TOC entry 5476 (class 0 OID 0)
-- Dependencies: 227
-- Name: belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.belts_id_seq', 36, true);


--
-- TOC entry 5477 (class 0 OID 0)
-- Dependencies: 223
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 4, true);


--
-- TOC entry 5478 (class 0 OID 0)
-- Dependencies: 244
-- Name: classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classes_id_seq', 1, false);


--
-- TOC entry 5479 (class 0 OID 0)
-- Dependencies: 276
-- Name: codes_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.codes_users_id_seq', 5, true);


--
-- TOC entry 5480 (class 0 OID 0)
-- Dependencies: 252
-- Name: destination_account_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.destination_account_id_seq', 1, false);


--
-- TOC entry 5481 (class 0 OID 0)
-- Dependencies: 266
-- Name: expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_categories_id_seq', 1, false);


--
-- TOC entry 5482 (class 0 OID 0)
-- Dependencies: 268
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expenses_id_seq', 1, false);


--
-- TOC entry 5483 (class 0 OID 0)
-- Dependencies: 286
-- Name: instructor_martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructor_martial_arts_id_seq', 8, true);


--
-- TOC entry 5484 (class 0 OID 0)
-- Dependencies: 236
-- Name: instructors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.instructors_id_seq', 2, true);


--
-- TOC entry 5485 (class 0 OID 0)
-- Dependencies: 225
-- Name: martial_arts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.martial_arts_id_seq', 4, true);


--
-- TOC entry 5486 (class 0 OID 0)
-- Dependencies: 258
-- Name: membership_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_plans_id_seq', 1, false);


--
-- TOC entry 5487 (class 0 OID 0)
-- Dependencies: 250
-- Name: movement_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.movement_type_id_seq', 2, true);


--
-- TOC entry 5488 (class 0 OID 0)
-- Dependencies: 264
-- Name: payment_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_items_id_seq', 1, false);


--
-- TOC entry 5489 (class 0 OID 0)
-- Dependencies: 248
-- Name: payment_method_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payment_method_id_seq', 1, false);


--
-- TOC entry 5490 (class 0 OID 0)
-- Dependencies: 262
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- TOC entry 5491 (class 0 OID 0)
-- Dependencies: 229
-- Name: people_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.people_id_seq', 12, true);


--
-- TOC entry 5492 (class 0 OID 0)
-- Dependencies: 256
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- TOC entry 5493 (class 0 OID 0)
-- Dependencies: 231
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 5, true);


--
-- TOC entry 5494 (class 0 OID 0)
-- Dependencies: 242
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_id_seq', 1, false);


--
-- TOC entry 5495 (class 0 OID 0)
-- Dependencies: 221
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.status_id_seq', 33, true);


--
-- TOC entry 5496 (class 0 OID 0)
-- Dependencies: 260
-- Name: student_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_memberships_id_seq', 1, false);


--
-- TOC entry 5497 (class 0 OID 0)
-- Dependencies: 240
-- Name: students_belts_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_history_id_seq', 16, true);


--
-- TOC entry 5498 (class 0 OID 0)
-- Dependencies: 238
-- Name: students_belts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_belts_id_seq', 6, true);


--
-- TOC entry 5499 (class 0 OID 0)
-- Dependencies: 234
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 7, true);


--
-- TOC entry 5500 (class 0 OID 0)
-- Dependencies: 280
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, true);


--
-- TOC entry 5501 (class 0 OID 0)
-- Dependencies: 219
-- Name: type_document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_document_id_seq', 5, true);


--
-- TOC entry 5502 (class 0 OID 0)
-- Dependencies: 254
-- Name: type_products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_products_id_seq', 1, false);


--
-- TOC entry 5503 (class 0 OID 0)
-- Dependencies: 282
-- Name: type_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_requirements_id_seq', 1, false);


--
-- TOC entry 5504 (class 0 OID 0)
-- Dependencies: 274
-- Name: type_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_student_id_seq', 1, false);


--
-- TOC entry 5505 (class 0 OID 0)
-- Dependencies: 278
-- Name: type_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.type_task_id_seq', 1, false);


--
-- TOC entry 5506 (class 0 OID 0)
-- Dependencies: 272
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 9, true);


--
-- TOC entry 5153 (class 2606 OID 25070)
-- Name: account_movements account_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT account_movements_pkey PRIMARY KEY (id);


--
-- TOC entry 5119 (class 2606 OID 24839)
-- Name: attendance attendance_id_class_id_student_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_id_student_key UNIQUE (id_class, id_student);


--
-- TOC entry 5121 (class 2606 OID 24837)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- TOC entry 5171 (class 2606 OID 32856)
-- Name: belt_requirements belt_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5093 (class 2606 OID 24622)
-- Name: belts belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5085 (class 2606 OID 24596)
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- TOC entry 5087 (class 2606 OID 24594)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5117 (class 2606 OID 24814)
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- TOC entry 5163 (class 2606 OID 32787)
-- Name: codes_users codes_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes_users
    ADD CONSTRAINT codes_users_pkey PRIMARY KEY (id, id_role);


--
-- TOC entry 5131 (class 2606 OID 24885)
-- Name: destination_account destination_account_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.destination_account
    ADD CONSTRAINT destination_account_pkey PRIMARY KEY (id);


--
-- TOC entry 5147 (class 2606 OID 25031)
-- Name: expense_categories expense_categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_name_key UNIQUE (name);


--
-- TOC entry 5149 (class 2606 OID 25029)
-- Name: expense_categories expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5151 (class 2606 OID 25047)
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- TOC entry 5173 (class 2606 OID 32880)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_id_martial_art_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_id_martial_art_key UNIQUE (id_instructor, id_martial_art);


--
-- TOC entry 5175 (class 2606 OID 32878)
-- Name: instructor_martial_arts instructor_martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5107 (class 2606 OID 24751)
-- Name: instructors instructors_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_key UNIQUE (id_person);


--
-- TOC entry 5109 (class 2606 OID 24749)
-- Name: instructors instructors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_pkey PRIMARY KEY (id);


--
-- TOC entry 5089 (class 2606 OID 24612)
-- Name: martial_arts martial_arts_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_name_key UNIQUE (name);


--
-- TOC entry 5091 (class 2606 OID 24610)
-- Name: martial_arts martial_arts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.martial_arts
    ADD CONSTRAINT martial_arts_pkey PRIMARY KEY (id);


--
-- TOC entry 5139 (class 2606 OID 24928)
-- Name: membership_plans membership_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT membership_plans_pkey PRIMARY KEY (id);


--
-- TOC entry 5127 (class 2606 OID 24876)
-- Name: movement_type movement_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_name_key UNIQUE (name);


--
-- TOC entry 5129 (class 2606 OID 24874)
-- Name: movement_type movement_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.movement_type
    ADD CONSTRAINT movement_type_pkey PRIMARY KEY (id);


--
-- TOC entry 5145 (class 2606 OID 25003)
-- Name: payment_items payment_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT payment_items_pkey PRIMARY KEY (id);


--
-- TOC entry 5123 (class 2606 OID 24865)
-- Name: payment_method payment_method_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_name_key UNIQUE (name);


--
-- TOC entry 5125 (class 2606 OID 24863)
-- Name: payment_method payment_method_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_method
    ADD CONSTRAINT payment_method_pkey PRIMARY KEY (id);


--
-- TOC entry 5143 (class 2606 OID 24974)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 5095 (class 2606 OID 24683)
-- Name: people people_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_email_key UNIQUE (email);


--
-- TOC entry 5097 (class 2606 OID 24681)
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (id);


--
-- TOC entry 5137 (class 2606 OID 24909)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 5099 (class 2606 OID 24693)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 5101 (class 2606 OID 24691)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 5115 (class 2606 OID 24801)
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- TOC entry 5083 (class 2606 OID 16441)
-- Name: status status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- TOC entry 5141 (class 2606 OID 24945)
-- Name: student_memberships student_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT student_memberships_pkey PRIMARY KEY (id);


--
-- TOC entry 5113 (class 2606 OID 24783)
-- Name: students_belts_history students_belts_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_pkey PRIMARY KEY (id);


--
-- TOC entry 5111 (class 2606 OID 24764)
-- Name: students_belts students_belts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_pkey PRIMARY KEY (id);


--
-- TOC entry 5103 (class 2606 OID 24721)
-- Name: students students_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_key UNIQUE (id_person);


--
-- TOC entry 5105 (class 2606 OID 24719)
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- TOC entry 5167 (class 2606 OID 32814)
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- TOC entry 5081 (class 2606 OID 16433)
-- Name: type_document type_document_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_document
    ADD CONSTRAINT type_document_pkey PRIMARY KEY (id);


--
-- TOC entry 5133 (class 2606 OID 24896)
-- Name: type_products type_products_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_name_key UNIQUE (name);


--
-- TOC entry 5135 (class 2606 OID 24894)
-- Name: type_products type_products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_products
    ADD CONSTRAINT type_products_pkey PRIMARY KEY (id);


--
-- TOC entry 5169 (class 2606 OID 32827)
-- Name: type_requirements type_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_requirements
    ADD CONSTRAINT type_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 5161 (class 2606 OID 32775)
-- Name: type_student type_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_student
    ADD CONSTRAINT type_student_pkey PRIMARY KEY (id);


--
-- TOC entry 5165 (class 2606 OID 32803)
-- Name: type_task type_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.type_task
    ADD CONSTRAINT type_task_pkey PRIMARY KEY (id);


--
-- TOC entry 5155 (class 2606 OID 25101)
-- Name: users users_id_person_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_key UNIQUE (id_person);


--
-- TOC entry 5157 (class 2606 OID 25099)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 5159 (class 2606 OID 25103)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 5214 (class 2620 OID 24852)
-- Name: students_belts tg_students_belts_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_insert AFTER INSERT ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_insert();


--
-- TOC entry 5215 (class 2620 OID 24854)
-- Name: students_belts tg_students_belts_update; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tg_students_belts_update AFTER UPDATE ON public.students_belts FOR EACH ROW EXECUTE FUNCTION public.fn_students_belts_update();


--
-- TOC entry 5217 (class 2620 OID 25084)
-- Name: expenses trg_expense_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_expense_insert_movement AFTER INSERT ON public.expenses FOR EACH ROW EXECUTE FUNCTION public.fn_expense_insert_movement();


--
-- TOC entry 5216 (class 2620 OID 25082)
-- Name: payments trg_payment_insert_movement; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_payment_insert_movement AFTER INSERT ON public.payments FOR EACH ROW EXECUTE FUNCTION public.fn_payment_insert_movement();


--
-- TOC entry 5192 (class 2606 OID 24840)
-- Name: attendance attendance_id_class_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_class_fkey FOREIGN KEY (id_class) REFERENCES public.classes(id) ON DELETE CASCADE;


--
-- TOC entry 5193 (class 2606 OID 24845)
-- Name: attendance attendance_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5210 (class 2606 OID 32857)
-- Name: belt_requirements belt_requirements_belt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_belt_id_fkey FOREIGN KEY (belt_id) REFERENCES public.belts(id) ON DELETE CASCADE;


--
-- TOC entry 5211 (class 2606 OID 32862)
-- Name: belt_requirements belt_requirements_id_type_requeriments_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belt_requirements
    ADD CONSTRAINT belt_requirements_id_type_requeriments_fkey FOREIGN KEY (id_type_requeriments) REFERENCES public.type_requirements(id) ON DELETE CASCADE;


--
-- TOC entry 5190 (class 2606 OID 24825)
-- Name: classes classes_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5191 (class 2606 OID 24820)
-- Name: classes classes_id_schedule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_schedule_fkey FOREIGN KEY (id_schedule) REFERENCES public.schedule(id);


--
-- TOC entry 5206 (class 2606 OID 25071)
-- Name: account_movements fk_account_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5207 (class 2606 OID 25076)
-- Name: account_movements fk_account_movement_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_movements
    ADD CONSTRAINT fk_account_movement_type FOREIGN KEY (id_movement_type) REFERENCES public.movement_type(id);


--
-- TOC entry 5204 (class 2606 OID 25048)
-- Name: expenses fk_expense_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_category FOREIGN KEY (id_expense_category) REFERENCES public.expense_categories(id);


--
-- TOC entry 5205 (class 2606 OID 25053)
-- Name: expenses fk_expense_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT fk_expense_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5209 (class 2606 OID 32815)
-- Name: tasks fk_id_type_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_id_type_task FOREIGN KEY (id_type_task) REFERENCES public.type_task(id) NOT VALID;


--
-- TOC entry 5176 (class 2606 OID 24625)
-- Name: belts fk_martial_art; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.belts
    ADD CONSTRAINT fk_martial_art FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5195 (class 2606 OID 24929)
-- Name: membership_plans fk_membership_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_plans
    ADD CONSTRAINT fk_membership_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5198 (class 2606 OID 24980)
-- Name: payments fk_payment_destination; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_destination FOREIGN KEY (id_destination_account) REFERENCES public.destination_account(id);


--
-- TOC entry 5201 (class 2606 OID 25014)
-- Name: payment_items fk_payment_items_membership; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_membership FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5202 (class 2606 OID 25004)
-- Name: payment_items fk_payment_items_payment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_payment FOREIGN KEY (id_payments) REFERENCES public.payments(id) ON DELETE CASCADE;


--
-- TOC entry 5203 (class 2606 OID 25009)
-- Name: payment_items fk_payment_items_product; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_items
    ADD CONSTRAINT fk_payment_items_product FOREIGN KEY (id_product) REFERENCES public.products(id);


--
-- TOC entry 5199 (class 2606 OID 24975)
-- Name: payments fk_payment_method; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payment_method FOREIGN KEY (id_payment_method) REFERENCES public.payment_method(id);


--
-- TOC entry 5200 (class 2606 OID 24985)
-- Name: payments fk_people; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_people FOREIGN KEY (id_person) REFERENCES public.people(id);


--
-- TOC entry 5177 (class 2606 OID 32788)
-- Name: people fk_people_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT fk_people_users FOREIGN KEY (id_code_users) REFERENCES public.users(id);


--
-- TOC entry 5194 (class 2606 OID 24910)
-- Name: products fk_products_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_type FOREIGN KEY (id_type_product) REFERENCES public.type_products(id);


--
-- TOC entry 5196 (class 2606 OID 24951)
-- Name: student_memberships fk_student; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student FOREIGN KEY (id_student) REFERENCES public.students(id);


--
-- TOC entry 5197 (class 2606 OID 24946)
-- Name: student_memberships fk_student_membership_plan; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_memberships
    ADD CONSTRAINT fk_student_membership_plan FOREIGN KEY (id_membership_plan) REFERENCES public.membership_plans(id);


--
-- TOC entry 5212 (class 2606 OID 32881)
-- Name: instructor_martial_arts instructor_martial_arts_id_instructor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_instructor_fkey FOREIGN KEY (id_instructor) REFERENCES public.instructors(id);


--
-- TOC entry 5213 (class 2606 OID 32886)
-- Name: instructor_martial_arts instructor_martial_arts_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructor_martial_arts
    ADD CONSTRAINT instructor_martial_arts_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5184 (class 2606 OID 24752)
-- Name: instructors instructors_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.instructors
    ADD CONSTRAINT instructors_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5178 (class 2606 OID 24697)
-- Name: person_roles person_roles_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5179 (class 2606 OID 24702)
-- Name: person_roles person_roles_id_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_roles
    ADD CONSTRAINT person_roles_id_role_fkey FOREIGN KEY (id_role) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- TOC entry 5189 (class 2606 OID 24802)
-- Name: schedule schedule_id_martial_art_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_id_martial_art_fkey FOREIGN KEY (id_martial_art) REFERENCES public.martial_arts(id);


--
-- TOC entry 5187 (class 2606 OID 24789)
-- Name: students_belts_history students_belts_history_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5188 (class 2606 OID 24784)
-- Name: students_belts_history students_belts_history_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts_history
    ADD CONSTRAINT students_belts_history_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5185 (class 2606 OID 24770)
-- Name: students_belts students_belts_id_belt_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_belt_fkey FOREIGN KEY (id_belt) REFERENCES public.belts(id);


--
-- TOC entry 5186 (class 2606 OID 24765)
-- Name: students_belts students_belts_id_student_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_belts
    ADD CONSTRAINT students_belts_id_student_fkey FOREIGN KEY (id_student) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- TOC entry 5180 (class 2606 OID 24732)
-- Name: students students_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- TOC entry 5181 (class 2606 OID 24722)
-- Name: students students_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id) ON DELETE CASCADE;


--
-- TOC entry 5182 (class 2606 OID 24737)
-- Name: students students_id_status_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.status(id);


--
-- TOC entry 5183 (class 2606 OID 24727)
-- Name: students students_id_type_document_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_id_type_document_fkey FOREIGN KEY (id_type_document) REFERENCES public.type_document(id);


--
-- TOC entry 5208 (class 2606 OID 25104)
-- Name: users users_id_person_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_person_fkey FOREIGN KEY (id_person) REFERENCES public.people(id);


-- Completed on 2026-06-23 12:00:10

--
-- PostgreSQL database dump complete
--

\unrestrict WSygcKUEqavyJhzhDXRqe6aZnfO2yBhRz3JiVyW0UkHxMPxa6NFpLdmExy3ogSP

