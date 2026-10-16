-- =============================================================================
-- Кондитерская: схема БД (PostgreSQL 18)
--
-- Соглашения
--   * PK            : bigint GENERATED ALWAYS AS IDENTITY
--   * время         : timestamptz (хранится в UTC, показывается в Asia/Bishkek)
--   * деньги        : numeric(10, 2); валюта - orders.currency (ISO 4217, снимок на момент
--                     заказа), одна на магазин, значение берётся из настроек приложения;
--                     язык интерфейса (locale) на валюту не влияет
--   * статусы       : varchar + CHECK, значения совпадают с StrEnum в backend/src/app/domain
--   * переводы      : отдельная таблица <entity>_translation (PK = сущность + locale)
--   * FK            : Postgres НЕ создаёт индексы на внешние ключи сам - создаём явно
--   * имена индексов: <table>_<column>_idx
--
-- Источник правды для миграций - модели SQLAlchemy + Alembic. Этот файл - проект
-- схемы для ревью и обучения; его можно прогнать в psql на пустой БД.
-- =============================================================================


-- =============================================================================
-- Справочники
-- =============================================================================

-- Локали сайта (ru, en, fr). Должны совпадать с SUPPORTED_LOCALES в domain/locale.py
CREATE TABLE locale (
    code varchar(5) PRIMARY KEY
);

-- Категории (дерево: "Торты" -> "Бенто-торты")
CREATE TABLE category (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parent_id  bigint REFERENCES category (id) ON DELETE RESTRICT,
    slug       varchar(100) NOT NULL UNIQUE,   -- для URL: /catalog/cakes
    sort_order integer      NOT NULL DEFAULT 0,
    is_active  boolean      NOT NULL DEFAULT true,
    CONSTRAINT category_not_own_parent CHECK (parent_id IS NULL OR parent_id <> id)
);
CREATE INDEX category_parent_id_idx ON category (parent_id);

CREATE TABLE category_translation (
    category_id bigint       NOT NULL REFERENCES category (id) ON DELETE CASCADE,
    locale      varchar(5)   NOT NULL REFERENCES locale (code),
    name        varchar(100) NOT NULL,
    description text,
    PRIMARY KEY (category_id, locale)
);

-- Аллергены (глютен, орехи, молоко, яйца ...). Фиксированный список: названия
-- переводятся на фронтенде по code, отдельной таблицы переводов нет.
CREATE TABLE allergen (
    id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code varchar(50) NOT NULL UNIQUE
);



-- =============================================================================
-- Каталог
-- =============================================================================

CREATE TABLE product (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id bigint       NOT NULL REFERENCES category (id) ON DELETE RESTRICT,
    slug        varchar(150) NOT NULL UNIQUE,
    sort_order  integer      NOT NULL DEFAULT 0,
    is_active   boolean      NOT NULL DEFAULT true,   -- "удаление" = is_active = false
    created_at  timestamptz  NOT NULL DEFAULT now(),
    updated_at  timestamptz  NOT NULL DEFAULT now()
);
CREATE INDEX product_category_id_idx ON product (category_id);

CREATE TABLE product_translation (
    product_id  bigint       NOT NULL REFERENCES product (id) ON DELETE CASCADE,
    locale      varchar(5)   NOT NULL REFERENCES locale (code),
    name        varchar(150) NOT NULL,
    description text,
    PRIMARY KEY (product_id, locale)
);

-- Вариант товара (размер/набор). Цена живёт ТОЛЬКО здесь.
-- Простой товар = один вариант. Торт = несколько (1 кг, 2 кг ...).
-- Инвариант "у активного товара есть хотя бы один вариант" проверяет приложение.
CREATE TABLE product_variant (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id bigint        NOT NULL REFERENCES product (id) ON DELETE CASCADE,
    weight_g   integer       CHECK (weight_g > 0),   -- граммы
    pieces     integer       CHECK (pieces > 0),     -- штук в наборе
    price      numeric(10,2) NOT NULL CHECK (price >= 0),
    sort_order integer       NOT NULL DEFAULT 0,
    is_active  boolean       NOT NULL DEFAULT true,
    -- NULLS NOT DISTINCT (PG15+): два варианта (NULL, NULL) тоже считаются дублем
    UNIQUE NULLS NOT DISTINCT (product_id, weight_g, pieces)
);
CREATE INDEX product_variant_product_id_idx ON product_variant (product_id);

CREATE TABLE product_image (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id bigint  NOT NULL REFERENCES product (id) ON DELETE CASCADE,
    path       text    NOT NULL,
    sort_order integer NOT NULL DEFAULT 0     -- первое по порядку = главное фото
);
CREATE INDEX product_image_product_id_idx ON product_image (product_id);

-- Связь многие-ко-многим: товар <-> аллерген
CREATE TABLE product_allergen (
    product_id  bigint NOT NULL REFERENCES product (id)  ON DELETE CASCADE,
    allergen_id bigint NOT NULL REFERENCES allergen (id) ON DELETE RESTRICT,
    PRIMARY KEY (product_id, allergen_id)
);
CREATE INDEX product_allergen_allergen_id_idx ON product_allergen (allergen_id);

-- Портфолио: галерея выполненных работ
CREATE TABLE portfolio_item (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id  bigint REFERENCES category (id) ON DELETE SET NULL,
    image_path   text        NOT NULL,
    sort_order   integer     NOT NULL DEFAULT 0,
    is_published boolean     NOT NULL DEFAULT true,
    created_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX portfolio_item_category_id_idx ON portfolio_item (category_id);

CREATE TABLE portfolio_item_translation (
    portfolio_item_id bigint       NOT NULL REFERENCES portfolio_item (id) ON DELETE CASCADE,
    locale            varchar(5)   NOT NULL REFERENCES locale (code),
    title             varchar(150) NOT NULL,
    description       text,
    PRIMARY KEY (portfolio_item_id, locale)
);


-- =============================================================================
-- Люди
-- =============================================================================

-- Клиент. Телефон - в формате E.164 (+996555123456, +33612345678); нормализует приложение.
CREATE TABLE customer (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name              varchar(100) NOT NULL,
    phone             varchar(16)  NOT NULL UNIQUE
                      CHECK (phone ~ '^\+[1-9][0-9]{7,14}$'),
    email             varchar(255) CHECK (email ~ '^[^@\s]+@[^@\s]+$'),
    preferred_contact varchar(20)
                      CHECK (preferred_contact IN ('phone', 'telegram', 'whatsapp', 'email')),
    locale            varchar(5)   NOT NULL DEFAULT 'ru' REFERENCES locale (code),
    birthday          date,
    notes             text,
    is_active         boolean      NOT NULL DEFAULT true,
    created_at        timestamptz  NOT NULL DEFAULT now(),
    updated_at        timestamptz  NOT NULL DEFAULT now()
);
-- уникальный email без учёта регистра; NULL-ы друг другу не мешают
CREATE UNIQUE INDEX customer_email_lower_key ON customer (lower(email));

-- Сотрудники (вход в админку)
CREATE TABLE staff_user (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email         varchar(255) NOT NULL CHECK (email ~ '^[^@\s]+@[^@\s]+$'),
    password_hash text         NOT NULL,           -- argon2/bcrypt, НИКОГДА не пароль
    name          varchar(100) NOT NULL,
    role          varchar(20)  NOT NULL DEFAULT 'admin' CHECK (role IN ('admin', 'baker')),
    is_active     boolean      NOT NULL DEFAULT true,
    created_at    timestamptz  NOT NULL DEFAULT now(),
    last_login_at timestamptz
);
CREATE UNIQUE INDEX staff_user_email_lower_key ON staff_user (lower(email));


-- =============================================================================
-- Заказы
-- =============================================================================

CREATE TABLE orders (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- публичный идентификатор для ссылок "отследить заказ": id перебирать нельзя
    public_id     uuid          NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    customer_id   bigint        NOT NULL REFERENCES customer (id) ON DELETE RESTRICT,
    status        varchar(20)   NOT NULL DEFAULT 'new'
                  CHECK (status IN ('new', 'confirmed', 'in_production', 'ready',
                                    'out_for_delivery', 'completed', 'cancelled')),
    delivery_type varchar(20)   NOT NULL CHECK (delivery_type IN ('pickup', 'delivery')),
    -- снимок итога на момент оформления: сумма позиций + стоимость доставки
    total_amount  numeric(10,2) NOT NULL CHECK (total_amount >= 0),
    currency      char(3)       NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),  -- ISO 4217: KGS, EUR ...
    -- к какому времени нужен заказ (самовывоз или приезд курьера)
    desired_at    timestamptz   NOT NULL,
    comment       text,
    created_at    timestamptz   NOT NULL DEFAULT now(),
    updated_at    timestamptz   NOT NULL DEFAULT now()
);
CREATE INDEX orders_customer_id_idx    ON orders (customer_id);
CREATE INDEX orders_status_desired_idx ON orders (status, desired_at);  -- доска кондитера

CREATE TABLE order_item (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id       bigint        NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    variant_id     bigint        NOT NULL REFERENCES product_variant (id) ON DELETE RESTRICT,
    quantity       integer       NOT NULL CHECK (quantity > 0),
    price_at_order numeric(10,2) NOT NULL CHECK (price_at_order >= 0),
    -- снимки названий: товар могут переименовать, а в старом заказе должно остаться как было
    product_name   varchar(150)  NOT NULL,
    variant_label  varchar(100),                 -- "1 кг", "набор 6 шт"
    comment        text,                         -- надпись на торте, пожелания
    UNIQUE (order_id, variant_id)
);
CREATE INDEX order_item_variant_id_idx ON order_item (variant_id);

CREATE TABLE order_status_history (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   bigint      NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    status     varchar(20) NOT NULL
               CHECK (status IN ('new', 'confirmed', 'in_production', 'ready',
                                 'out_for_delivery', 'completed', 'cancelled')),
    changed_by bigint      REFERENCES staff_user (id) ON DELETE SET NULL,  -- NULL = система/клиент
    comment    text,
    changed_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX order_status_history_order_idx ON order_status_history (order_id, changed_at);


-- =============================================================================
-- Оплата и доставка
-- =============================================================================

-- Платежей у заказа может быть несколько (предоплата + остаток, возврат)
CREATE TABLE payment (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    bigint        NOT NULL REFERENCES orders (id) ON DELETE RESTRICT,
    amount      numeric(10,2) NOT NULL CHECK (amount > 0),
    method      varchar(20)   NOT NULL CHECK (method IN ('cash', 'card', 'transfer', 'qr')),
    status      varchar(20)   NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'paid', 'failed', 'refunded')),
    external_id varchar(100),                    -- id транзакции у платёжного провайдера
    paid_at     timestamptz,
    created_at  timestamptz   NOT NULL DEFAULT now(),
    CONSTRAINT payment_paid_has_date CHECK (status <> 'paid' OR paid_at IS NOT NULL)
);
CREATE INDEX payment_order_id_idx ON payment (order_id);
-- защита от двойной обработки одного и того же вебхука
CREATE UNIQUE INDEX payment_method_external_id_key
    ON payment (method, external_id) WHERE external_id IS NOT NULL;

-- Данные доставки: строка есть только у заказов с delivery_type = 'delivery'
CREATE TABLE delivery (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id  bigint        NOT NULL UNIQUE REFERENCES orders (id) ON DELETE CASCADE,
    address   text          NOT NULL,
    recipient varchar(100)  NOT NULL,
    phone     varchar(16)   NOT NULL CHECK (phone ~ '^\+[1-9][0-9]{7,14}$'),
    cost      numeric(10,2) NOT NULL DEFAULT 0 CHECK (cost >= 0),
    comment   text                                  -- подъезд, этаж, домофон
);


-- =============================================================================
-- Лиды (заявки на индивидуальный заказ)
-- =============================================================================

CREATE TABLE lead (
    id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status             varchar(20)   NOT NULL DEFAULT 'new'
                       CHECK (status IN ('new', 'in_progress', 'converted', 'rejected')),
    customer_id        bigint        REFERENCES customer (id) ON DELETE SET NULL,
    converted_order_id bigint        REFERENCES orders (id)   ON DELETE SET NULL,
    name               varchar(100)  NOT NULL,
    phone              varchar(16)   NOT NULL CHECK (phone ~ '^\+[1-9][0-9]{7,14}$'),
    email              varchar(255)  CHECK (email ~ '^[^@\s]+@[^@\s]+$'),
    comment            text,
    -- поля индивидуального заказа
    desired_date       date,
    servings           integer       CHECK (servings > 0),
    budget             numeric(10,2) CHECK (budget >= 0),
    decor              varchar(200),
    design_description text,
    created_at         timestamptz   NOT NULL DEFAULT now(),
    updated_at         timestamptz   NOT NULL DEFAULT now()
);
CREATE INDEX lead_phone_idx              ON lead (phone);
CREATE INDEX lead_customer_id_idx        ON lead (customer_id);
CREATE INDEX lead_converted_order_id_idx ON lead (converted_order_id);
CREATE INDEX lead_status_created_idx     ON lead (status, created_at);

-- Референсы-картинки, которые клиент прикрепил к заявке
CREATE TABLE lead_attachment (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lead_id       bigint      NOT NULL REFERENCES lead (id) ON DELETE CASCADE,
    path          text        NOT NULL,
    original_name varchar(255),
    created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX lead_attachment_lead_id_idx ON lead_attachment (lead_id);


-- =============================================================================
-- Отзывы
-- =============================================================================

-- Отзыв на магазин в целом (product_id IS NULL) или на конкретный товар.
-- Публикуется только после модерации.
CREATE TABLE review (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  bigint       REFERENCES customer (id) ON DELETE SET NULL,
    order_id     bigint       REFERENCES orders (id)   ON DELETE SET NULL,
    product_id   bigint       REFERENCES product (id)  ON DELETE SET NULL,
    author_name  varchar(100) NOT NULL,
    rating       smallint     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body         text         NOT NULL,
    is_published boolean      NOT NULL DEFAULT false,
    created_at   timestamptz  NOT NULL DEFAULT now()
);
CREATE INDEX review_product_published_idx ON review (product_id) WHERE is_published;
CREATE INDEX review_customer_id_idx       ON review (customer_id);
CREATE INDEX review_order_id_idx          ON review (order_id);


-- =============================================================================
-- Начальные данные (в проекте поедут в Alembic-миграцию)
-- =============================================================================

INSERT INTO locale (code) VALUES ('ru'), ('en'), ('fr');
