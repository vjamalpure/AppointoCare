-- =============================================================================
-- APPOINTO CARE MULTI-TENANT ARCHITECTURE MIGRATION
-- LAYER 1: Meta WhatsApp Business API & Razorpay Route Split Integration Schema
-- =============================================================================

-- 1. Create Enums idempotently
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_status_enum') THEN
        CREATE TYPE service_status_enum AS ENUM ('ACTIVE', 'SUSPENDED', 'INACTIVE');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'meta_credit_line_status_enum') THEN
        CREATE TYPE meta_credit_line_status_enum AS ENUM ('SHARED_MASTER', 'DIRECT_CLIENT', 'SUSPENDED');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'razorpay_onboarding_status_enum') THEN
        CREATE TYPE razorpay_onboarding_status_enum AS ENUM ('PENDING', 'LINKED', 'VERIFIED', 'REJECTED');
    END IF;
END $$;

-- 2. Ensure Primary Multi-Tenant Table (Organizations / Tenants)
-- Note: In AppointoCare, 'organizations' acts as the root tenant table.
-- We ensure all multi-tenant core columns exist and create a convenience view 'tenants'.
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    sector VARCHAR(50) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(30),
    address VARCHAR(255),
    logo_url VARCHAR(255),
    whatsapp_enabled BOOLEAN DEFAULT TRUE,
    whatsapp_monthly_limit INT DEFAULT 1000,
    whatsapp_messages_used INT DEFAULT 0,
    booking_flow_enabled BOOLEAN DEFAULT TRUE,
    auto_welcome_enabled BOOLEAN DEFAULT TRUE,
    reminders_enabled BOOLEAN DEFAULT TRUE,
    campaigns_enabled BOOLEAN DEFAULT TRUE,
    subscription_status VARCHAR(50) DEFAULT 'Active',
    subscription_plan VARCHAR(100) DEFAULT 'Basic',
    subscription_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subscription_end TIMESTAMP,
    next_billing_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW tenants AS 
SELECT 
    id AS tenant_id,
    name,
    code AS tenant_slug,
    sector,
    username,
    email,
    phone,
    subscription_status,
    subscription_plan,
    created_at,
    updated_at
FROM organizations;

-- 3. WhatsApp Multi-Tenant Configurations Table
-- Isolated per tenant; binds tenant's WABA, Phone Number ID, and encrypted access token.
-- Billed centrally via SuperAdmin Master Credit Line in Meta Business Manager.
CREATE TABLE IF NOT EXISTS whatsapp_configs (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Meta WABA & WhatsApp Phone Credentials (via Embedded Signup)
    waba_id VARCHAR(100),
    phone_number_id VARCHAR(100),
    business_account_id VARCHAR(100),
    display_phone_number VARCHAR(50),
    verified_name VARCHAR(200),
    quality_rating VARCHAR(50) DEFAULT 'GREEN',
    
    -- Credentials & Tokens (Encrypted at rest)
    access_token_encrypted TEXT,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    webhook_verify_token VARCHAR(255),
    
    -- Feature Flags & SuperAdmin Service Controls
    service_status service_status_enum NOT NULL DEFAULT 'INACTIVE',
    suspension_reason VARCHAR(255),
    meta_credit_line_status meta_credit_line_status_enum NOT NULL DEFAULT 'SHARED_MASTER',
    
    -- Rate Limiting & Usage Tracking
    monthly_limit INT NOT NULL DEFAULT 1000,
    messages_sent_this_month INT NOT NULL DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Razorpay Partner / Route Multi-Tenant Configurations Table
-- Stores tenant sub-account credentials and dynamic split commission rules.
CREATE TABLE IF NOT EXISTS payment_configs (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Razorpay Connected Sub-Account Details
    razorpay_account_id VARCHAR(100), -- acc_xxxx
    merchant_name VARCHAR(200),
    merchant_email VARCHAR(150),
    onboarding_status razorpay_onboarding_status_enum NOT NULL DEFAULT 'PENDING',
    
    -- SuperAdmin Service Controls
    service_status service_status_enum NOT NULL DEFAULT 'INACTIVE',
    suspension_reason VARCHAR(255),
    
    -- Revenue Split Settings (Default 5% Platform Commission)
    platform_commission_rate NUMERIC(5, 4) NOT NULL DEFAULT 0.0500,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    auto_capture BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- OAuth Tokens for Razorpay Partner Gateway (Encrypted at rest)
    oauth_access_token_encrypted TEXT,
    oauth_refresh_token_encrypted TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. High-Performance B-Tree Indexes for Multi-Tenant Lookups & Route Guards
CREATE INDEX IF NOT EXISTS idx_whatsapp_configs_tenant_id ON whatsapp_configs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_configs_waba_id ON whatsapp_configs(waba_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_configs_phone_number_id ON whatsapp_configs(phone_number_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_configs_status ON whatsapp_configs(service_status);

CREATE INDEX IF NOT EXISTS idx_payment_configs_tenant_id ON payment_configs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_configs_account_id ON payment_configs(razorpay_account_id);
CREATE INDEX IF NOT EXISTS idx_payment_configs_status ON payment_configs(service_status);

-- 6. Trigger for Automatic updated_at Timestamps
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_whatsapp_configs_updated_at ON whatsapp_configs;
CREATE TRIGGER trg_whatsapp_configs_updated_at
BEFORE UPDATE ON whatsapp_configs
FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();

DROP TRIGGER IF EXISTS trg_payment_configs_updated_at ON payment_configs;
CREATE TRIGGER trg_payment_configs_updated_at
BEFORE UPDATE ON payment_configs
FOR EACH ROW EXECUTE FUNCTION update_timestamp_column();
