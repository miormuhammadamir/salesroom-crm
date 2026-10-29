BEGIN;
--
-- Create model AuditLog
--
CREATE TABLE "crm_auditlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(30) NOT NULL, "entity" varchar(50) NOT NULL, "object_id" bigint unsigned NOT NULL CHECK ("object_id" >= 0), "label" varchar(250) NOT NULL, "created_at" datetime NOT NULL, "actor_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Customer
--
CREATE TABLE "crm_customer" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(160) NOT NULL, "company" varchar(160) NOT NULL, "email" varchar(254) NOT NULL, "phone" varchar(40) NOT NULL, "address" text NOT NULL, "source" varchar(80) NOT NULL, "stage" varchar(20) NOT NULL, "estimated_value" decimal NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model FollowUp
--
CREATE TABLE "crm_followup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "subject" varchar(200) NOT NULL, "kind" varchar(20) NOT NULL, "due_at" datetime NOT NULL, "priority" varchar(10) NOT NULL, "status" varchar(15) NOT NULL, "notes" text NOT NULL, "completed_at" datetime NULL, "customer_id" bigint NOT NULL REFERENCES "crm_customer" ("id") DEFERRABLE INITIALLY DEFERRED, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model JourneyEvent
--
CREATE TABLE "crm_journeyevent" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_stage" varchar(20) NOT NULL, "to_stage" varchar(20) NOT NULL, "note" varchar(250) NOT NULL, "created_at" datetime NOT NULL, "actor_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "customer_id" bigint NOT NULL REFERENCES "crm_customer" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Order
--
CREATE TABLE "crm_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "order_date" date NOT NULL, "due_date" date NULL, "discount" decimal NOT NULL, "tax_percent" decimal NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "customer_id" bigint NOT NULL REFERENCES "crm_customer" ("id") DEFERRABLE INITIALLY DEFERRED, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Payment
--
CREATE TABLE "crm_payment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "amount" decimal NOT NULL, "paid_on" date NOT NULL, "method" varchar(20) NOT NULL, "reference" varchar(100) NOT NULL, "order_id" bigint NOT NULL REFERENCES "crm_order" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Product
--
CREATE TABLE "crm_product" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(160) NOT NULL, "sku" varchar(40) NOT NULL UNIQUE, "price" decimal NOT NULL, "active" bool NOT NULL, CONSTRAINT "product_price_nonnegative" CHECK ("price" >= '0'));
--
-- Create model OrderItem
--
CREATE TABLE "crm_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(200) NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "unit_price" decimal NOT NULL, "order_id" bigint NOT NULL REFERENCES "crm_order" ("id") DEFERRABLE INITIALLY DEFERRED, "product_id" bigint NULL REFERENCES "crm_product" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model SalesTarget
--
CREATE TABLE "crm_salestarget" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "month" date NOT NULL, "amount" decimal NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create constraint customer_value_nonnegative on model customer
--
CREATE TABLE "new__crm_customer" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(160) NOT NULL, "company" varchar(160) NOT NULL, "email" varchar(254) NOT NULL, "phone" varchar(40) NOT NULL, "address" text NOT NULL, "source" varchar(80) NOT NULL, "stage" varchar(20) NOT NULL, "estimated_value" decimal NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "customer_value_nonnegative" CHECK ("estimated_value" >= '0'));
INSERT INTO "new__crm_customer" ("id", "name", "company", "email", "phone", "address", "source", "stage", "estimated_value", "notes", "created_at", "updated_at", "owner_id") SELECT "id", "name", "company", "email", "phone", "address", "source", "stage", "estimated_value", "notes", "created_at", "updated_at", "owner_id" FROM "crm_customer";
DROP TABLE "crm_customer";
ALTER TABLE "new__crm_customer" RENAME TO "crm_customer";
CREATE INDEX "crm_auditlog_created_at_70952dac" ON "crm_auditlog" ("created_at");
CREATE INDEX "crm_auditlog_actor_id_4382924f" ON "crm_auditlog" ("actor_id");
CREATE INDEX "crm_followup_due_at_beae4fb2" ON "crm_followup" ("due_at");
CREATE INDEX "crm_followup_status_9bc01139" ON "crm_followup" ("status");
CREATE INDEX "crm_followup_customer_id_b684eda4" ON "crm_followup" ("customer_id");
CREATE INDEX "crm_followup_owner_id_7a0879b2" ON "crm_followup" ("owner_id");
CREATE INDEX "crm_journeyevent_actor_id_26f645fb" ON "crm_journeyevent" ("actor_id");
CREATE INDEX "crm_journeyevent_customer_id_e79b94d0" ON "crm_journeyevent" ("customer_id");
CREATE INDEX "crm_order_status_abe5b8ba" ON "crm_order" ("status");
CREATE INDEX "crm_order_order_date_f6ceef8b" ON "crm_order" ("order_date");
CREATE INDEX "crm_order_customer_id_7231c78d" ON "crm_order" ("customer_id");
CREATE INDEX "crm_order_owner_id_4c22bafa" ON "crm_order" ("owner_id");
CREATE INDEX "crm_payment_order_id_a4f2b3e1" ON "crm_payment" ("order_id");
CREATE INDEX "crm_orderitem_order_id_7ec9f773" ON "crm_orderitem" ("order_id");
CREATE INDEX "crm_orderitem_product_id_1c9b94b3" ON "crm_orderitem" ("product_id");
CREATE INDEX "crm_salestarget_user_id_4b1784d8" ON "crm_salestarget" ("user_id");
CREATE INDEX "crm_customer_stage_e8ce3532" ON "crm_customer" ("stage");
CREATE INDEX "crm_customer_owner_id_cb8a50e2" ON "crm_customer" ("owner_id");
--
-- Create constraint discount_nonnegative on model order
--
CREATE TABLE "new__crm_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "order_date" date NOT NULL, "due_date" date NULL, "discount" decimal NOT NULL, "tax_percent" decimal NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "customer_id" bigint NOT NULL REFERENCES "crm_customer" ("id") DEFERRABLE INITIALLY DEFERRED, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "discount_nonnegative" CHECK ("discount" >= '0'));
INSERT INTO "new__crm_order" ("id", "status", "order_date", "due_date", "discount", "tax_percent", "notes", "created_at", "updated_at", "customer_id", "owner_id") SELECT "id", "status", "order_date", "due_date", "discount", "tax_percent", "notes", "created_at", "updated_at", "customer_id", "owner_id" FROM "crm_order";
DROP TABLE "crm_order";
ALTER TABLE "new__crm_order" RENAME TO "crm_order";
CREATE INDEX "crm_order_status_abe5b8ba" ON "crm_order" ("status");
CREATE INDEX "crm_order_order_date_f6ceef8b" ON "crm_order" ("order_date");
CREATE INDEX "crm_order_customer_id_7231c78d" ON "crm_order" ("customer_id");
CREATE INDEX "crm_order_owner_id_4c22bafa" ON "crm_order" ("owner_id");
--
-- Create constraint tax_valid on model order
--
CREATE TABLE "new__crm_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "order_date" date NOT NULL, "due_date" date NULL, "discount" decimal NOT NULL, "tax_percent" decimal NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "customer_id" bigint NOT NULL REFERENCES "crm_customer" ("id") DEFERRABLE INITIALLY DEFERRED, "owner_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "discount_nonnegative" CHECK ("discount" >= '0'), CONSTRAINT "tax_valid" CHECK (("tax_percent" >= '0' AND "tax_percent" <= '100')));
INSERT INTO "new__crm_order" ("id", "status", "order_date", "due_date", "discount", "tax_percent", "notes", "created_at", "updated_at", "customer_id", "owner_id") SELECT "id", "status", "order_date", "due_date", "discount", "tax_percent", "notes", "created_at", "updated_at", "customer_id", "owner_id" FROM "crm_order";
DROP TABLE "crm_order";
ALTER TABLE "new__crm_order" RENAME TO "crm_order";
CREATE INDEX "crm_order_status_abe5b8ba" ON "crm_order" ("status");
CREATE INDEX "crm_order_order_date_f6ceef8b" ON "crm_order" ("order_date");
CREATE INDEX "crm_order_customer_id_7231c78d" ON "crm_order" ("customer_id");
CREATE INDEX "crm_order_owner_id_4c22bafa" ON "crm_order" ("owner_id");
--
-- Create constraint payment_positive on model payment
--
CREATE TABLE "new__crm_payment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "amount" decimal NOT NULL, "paid_on" date NOT NULL, "method" varchar(20) NOT NULL, "reference" varchar(100) NOT NULL, "order_id" bigint NOT NULL REFERENCES "crm_order" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "payment_positive" CHECK ("amount" > '0'));
INSERT INTO "new__crm_payment" ("id", "amount", "paid_on", "method", "reference", "order_id") SELECT "id", "amount", "paid_on", "method", "reference", "order_id" FROM "crm_payment";
DROP TABLE "crm_payment";
ALTER TABLE "new__crm_payment" RENAME TO "crm_payment";
CREATE INDEX "crm_payment_order_id_a4f2b3e1" ON "crm_payment" ("order_id");
--
-- Create constraint item_quantity_positive on model orderitem
--
CREATE TABLE "new__crm_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(200) NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "unit_price" decimal NOT NULL, "order_id" bigint NOT NULL REFERENCES "crm_order" ("id") DEFERRABLE INITIALLY DEFERRED, "product_id" bigint NULL REFERENCES "crm_product" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "item_quantity_positive" CHECK ("quantity" >= 1));
INSERT INTO "new__crm_orderitem" ("id", "description", "quantity", "unit_price", "order_id", "product_id") SELECT "id", "description", "quantity", "unit_price", "order_id", "product_id" FROM "crm_orderitem";
DROP TABLE "crm_orderitem";
ALTER TABLE "new__crm_orderitem" RENAME TO "crm_orderitem";
CREATE INDEX "crm_orderitem_order_id_7ec9f773" ON "crm_orderitem" ("order_id");
CREATE INDEX "crm_orderitem_product_id_1c9b94b3" ON "crm_orderitem" ("product_id");
--
-- Create constraint item_price_nonnegative on model orderitem
--
CREATE TABLE "new__crm_orderitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(200) NOT NULL, "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), "unit_price" decimal NOT NULL, "order_id" bigint NOT NULL REFERENCES "crm_order" ("id") DEFERRABLE INITIALLY DEFERRED, "product_id" bigint NULL REFERENCES "crm_product" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "item_quantity_positive" CHECK ("quantity" >= 1), CONSTRAINT "item_price_nonnegative" CHECK ("unit_price" >= '0'));
INSERT INTO "new__crm_orderitem" ("id", "description", "quantity", "unit_price", "order_id", "product_id") SELECT "id", "description", "quantity", "unit_price", "order_id", "product_id" FROM "crm_orderitem";
DROP TABLE "crm_orderitem";
ALTER TABLE "new__crm_orderitem" RENAME TO "crm_orderitem";
CREATE INDEX "crm_orderitem_order_id_7ec9f773" ON "crm_orderitem" ("order_id");
CREATE INDEX "crm_orderitem_product_id_1c9b94b3" ON "crm_orderitem" ("product_id");
--
-- Create constraint unique_monthly_target on model salestarget
--
CREATE TABLE "new__crm_salestarget" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "month" date NOT NULL, "amount" decimal NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "unique_monthly_target" UNIQUE ("user_id", "month"));
INSERT INTO "new__crm_salestarget" ("id", "month", "amount", "user_id") SELECT "id", "month", "amount", "user_id" FROM "crm_salestarget";
DROP TABLE "crm_salestarget";
ALTER TABLE "new__crm_salestarget" RENAME TO "crm_salestarget";
CREATE INDEX "crm_salestarget_user_id_4b1784d8" ON "crm_salestarget" ("user_id");
--
-- Create constraint target_positive on model salestarget
--
CREATE TABLE "new__crm_salestarget" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "month" date NOT NULL, "amount" decimal NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "unique_monthly_target" UNIQUE ("user_id", "month"), CONSTRAINT "target_positive" CHECK ("amount" > '0'));
INSERT INTO "new__crm_salestarget" ("id", "month", "amount", "user_id") SELECT "id", "month", "amount", "user_id" FROM "crm_salestarget";
DROP TABLE "crm_salestarget";
ALTER TABLE "new__crm_salestarget" RENAME TO "crm_salestarget";
CREATE INDEX "crm_salestarget_user_id_4b1784d8" ON "crm_salestarget" ("user_id");
COMMIT;
