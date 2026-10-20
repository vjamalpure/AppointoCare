import sys
import hmac
import hashlib
from datetime import datetime
from app import create_app
from app.models import db, Organization, WhatsAppConfig, PaymentConfig, ServiceStatus, Appointment, AppointmentTransaction, AuditLog
from app.utils.crypto_helper import encrypt_token, decrypt_token

app = create_app()

with app.app_context():
    client = app.test_client()
    passed = 0
    failed = 0
    errors = []

    def check(name, condition, details=""):
        global passed, failed, errors
        if condition:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            failed += 1
            msg = f"  [FAIL] {name} - {details}"
            print(msg)
            errors.append(msg)

    print("============================================================")
    print("TESTING 4-LAYER MULTI-TENANT ARCHITECTURE (META & RAZORPAY)")
    print("============================================================")

    # 0. Setup SuperAdmin Token & Tenant 1 Token
    res_admin = client.post('/auth/login', json={'username': 'superadmin', 'password': 'Admin@12345'})
    admin_token = res_admin.get_json()['access_token']
    admin_hdr = {'Authorization': f'Bearer {admin_token}'}

    res_org = client.post('/auth/login', json={'username': 'org1', 'password': 'Org@12345', 'code': 'ORG1'})
    org_token = res_org.get_json()['access_token']
    org_hdr = {'Authorization': f'Bearer {org_token}'}

    # ------------------------------------------------------------
    # LAYER 1: Database Migration Schema & Crypto Helper Verification
    # ------------------------------------------------------------
    print("\n>>> LAYER 1: Database Schema & Token Encryption")
    sample_token = "EAAG_Meta_Super_Secret_Access_Token_998877"
    enc = encrypt_token(sample_token)
    dec = decrypt_token(enc)
    check("Token Encryption and Decryption Roundtrip", dec == sample_token and enc != sample_token)

    # Verify tables exist in DB
    w_count = WhatsAppConfig.query.count()
    p_count = PaymentConfig.query.count()
    check("WhatsAppConfig & PaymentConfig Tables Queryable", w_count >= 0 and p_count >= 0)

    # ------------------------------------------------------------
    # LAYER 3: Meta Embedded Signup Callback & Template Messaging
    # ------------------------------------------------------------
    print("\n>>> LAYER 3: Meta WhatsApp Embedded Signup Callback & Template Dispatch")
    signup_payload = {
        "code": "sample_auth_code_from_meta_popup",
        "waba_id": "waba_tenant_1_hospital",
        "phone_number_id": "phone_tenant_1_hospital_id",
        "display_phone_number": "+1 (555) 900-1122",
        "verified_name": "City Care Hospital WhatsApp Desk",
        "business_account_id": "bacc_master_9988"
    }
    res_signup = client.post('/whatsapp/embedded-signup-callback', json=signup_payload, headers=org_hdr)
    check("Meta Embedded Signup Callback", res_signup.status_code == 200)
    w_cfg = WhatsAppConfig.query.filter_by(tenant_id=1).first()
    check("WABA Credentials Stored", w_cfg is not None and w_cfg.waba_id == "waba_tenant_1_hospital")
    check("Service Status Activated via Signup", w_cfg.service_status == "ACTIVE")
    check("Centralized Master Credit Line Assigned", w_cfg.meta_credit_line_status == "SHARED_MASTER")
    check("Access Token Encrypted At Rest", w_cfg.access_token_encrypted is not None and "EAAG" not in w_cfg.access_token_encrypted)

    # Outbound Template Dispatch (Active state)
    res_tmpl = client.post('/whatsapp/send-template', json={
        "recipient_phone": "+15550198888",
        "template_name": "appointment_confirmation",
        "language_code": "en_US",
        "components": [{"type": "body", "parameters": [{"type": "text", "text": "Dr. Sarah"}]}]
    }, headers=org_hdr)
    check("Outbound Template Dispatch While ACTIVE", res_tmpl.status_code == 200)

    # Outbound Standard Send (Active state)
    res_send = client.post('/whatsapp/send', json={
        "recipient_number": "+15550198888",
        "message": "Hello from verified City Care!"
    }, headers=org_hdr)
    check("Outbound Message Send While ACTIVE", res_send.status_code == 200)

    # ------------------------------------------------------------
    # LAYER 4: Razorpay Route Split Orders & Webhook Controller
    # ------------------------------------------------------------
    print("\n>>> LAYER 4: Razorpay Route Dynamic Split & Webhook Processing")
    # Link tenant 1 payment config
    p_cfg = PaymentConfig.query.filter_by(tenant_id=1).first()
    if not p_cfg:
        p_cfg = PaymentConfig(tenant_id=1, razorpay_account_id="acc_citycare_hospital_rzp", merchant_name="City Care Hospital", service_status="ACTIVE", platform_commission_rate=0.05)
        db.session.add(p_cfg)
    else:
        p_cfg.razorpay_account_id = "acc_citycare_hospital_rzp"
        p_cfg.service_status = "ACTIVE"
        p_cfg.platform_commission_rate = 0.05
    db.session.commit()

    # Create Split Order (Amount = ₹2,000.00 / 200,000 paise)
    res_order = client.post('/payments/create-order', json={
        "amount": 2000.0,
        "currency": "INR",
        "appointment_id": 101,
        "customer_name": "Jane Patient"
    }, headers=org_hdr)
    check("Create Razorpay Route Split Order", res_order.status_code == 201)
    order_data = res_order.get_json()
    split = order_data.get("split_details", {})
    # 5% of 200000 = 10000 paise (₹100), 95% = 190000 paise (₹1900)
    check("Platform 5% Fee Calculation", split.get("platform_fee_paise") == 10000 and split.get("platform_fee_amount") == 100.0)
    check("Merchant 95% Share Allocation", split.get("merchant_share_paise") == 190000 and split.get("merchant_net_amount") == 1900.0)
    check("Transfer Target Linked Sub-Account", split.get("merchant_account_id") == "acc_citycare_hospital_rzp")

    # Razorpay Webhook: payment.captured
    webhook_secret = "rzp_webhook_secret_secure_2026"
    import json
    capture_body = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_998811",
                    "amount": 200000,
                    "currency": "INR",
                    "status": "captured",
                    "notes": {
                        "tenant_id": "1",
                        "appointment_id": "1"
                    }
                }
            }
        }
    }
    raw_str = json.dumps(capture_body)
    sig = hmac.new(webhook_secret.encode("utf-8"), raw_str.encode("utf-8"), hashlib.sha256).hexdigest()
    res_hook = client.post('/payments/webhook', data=raw_str, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig})
    check("Razorpay Webhook (payment.captured) Signature & Execution", res_hook.status_code == 200)

    # Razorpay Webhook: transfer.processed
    transfer_body = {
        "event": "transfer.processed",
        "payload": {
            "transfer": {
                "entity": {
                    "id": "trf_sub_acc_7711",
                    "recipient": "acc_citycare_hospital_rzp",
                    "amount": 190000,
                    "currency": "INR",
                    "notes": {
                        "tenant_id": "1"
                    }
                }
            }
        }
    }
    raw_trf = json.dumps(transfer_body)
    sig_trf = hmac.new(webhook_secret.encode("utf-8"), raw_trf.encode("utf-8"), hashlib.sha256).hexdigest()
    res_hook_trf = client.post('/payments/webhook', data=raw_trf, headers={"Content-Type": "application/json", "X-Razorpay-Signature": sig_trf})
    check("Razorpay Webhook (transfer.processed) Split Routing Confirmation", res_hook_trf.status_code == 200)

    # ------------------------------------------------------------
    # LAYER 2: SuperAdmin Service Controls & Route Guards
    # ------------------------------------------------------------
    print("\n>>> LAYER 2: Superadmin Service Controls (Independent Feature Flags)")
    
    # 1. SuperAdmin Suspends WhatsApp for Tenant 1
    res_toggle_w = client.patch('/admin/tenants/1/toggle-service', json={
        "service": "whatsapp",
        "status": "SUSPENDED",
        "reason": "Payment overdue for messaging usage"
    }, headers=admin_hdr)
    check("SuperAdmin Suspend WhatsApp Service", res_toggle_w.status_code == 200 and res_toggle_w.get_json()['config']['status'] == "SUSPENDED")

    # Verify Route Guard BLOCKS outbound WhatsApp immediately with 403
    res_send_blocked = client.post('/whatsapp/send', json={
        "recipient_number": "+15550198888",
        "message": "Blocked attempt"
    }, headers=org_hdr)
    check("Route Guard Blocks WhatsApp When SUSPENDED (HTTP 403)", res_send_blocked.status_code == 403 and "WHATSAPP_SERVICE_SUSPENDED" in res_send_blocked.get_json().get("error", ""))

    res_tmpl_blocked = client.post('/whatsapp/send-template', json={
        "recipient_phone": "+15550198888",
        "template_name": "appointment_confirmation"
    }, headers=org_hdr)
    check("Route Guard Blocks WhatsApp Template When SUSPENDED (HTTP 403)", res_tmpl_blocked.status_code == 403)

    # 2. SuperAdmin Suspends Razorpay for Tenant 1
    res_toggle_p = client.patch('/admin/tenants/1/toggle-service', json={
        "service": "razorpay",
        "status": "SUSPENDED",
        "reason": "KYC document re-verification required"
    }, headers=admin_hdr)
    check("SuperAdmin Suspend Razorpay Service", res_toggle_p.status_code == 200 and res_toggle_p.get_json()['config']['status'] == "SUSPENDED")

    # Verify Route Guard BLOCKS order creation immediately with 403
    res_order_blocked = client.post('/payments/create-order', json={
        "amount": 500.0,
        "appointment_id": 102
    }, headers=org_hdr)
    check("Route Guard Blocks Razorpay Checkout When SUSPENDED (HTTP 403)", res_order_blocked.status_code == 403 and "PAYMENT_GATEWAY_SUSPENDED" in res_order_blocked.get_json().get("error", ""))

    # 3. SuperAdmin Re-activates Both Services
    res_reactivate_w = client.patch('/admin/tenants/1/toggle-service', json={
        "service": "whatsapp",
        "status": "ACTIVE"
    }, headers=admin_hdr)
    check("SuperAdmin Reactivate WhatsApp Service", res_reactivate_w.status_code == 200 and res_reactivate_w.get_json()['config']['status'] == "ACTIVE")

    res_reactivate_p = client.patch('/admin/tenants/1/toggle-service', json={
        "service": "razorpay",
        "status": "ACTIVE"
    }, headers=admin_hdr)
    check("SuperAdmin Reactivate Razorpay Service", res_reactivate_p.status_code == 200 and res_reactivate_p.get_json()['config']['status'] == "ACTIVE")

    # Verify Both Services Execute Cleanly Again
    res_send_ok = client.post('/whatsapp/send', json={
        "recipient_number": "+15550198888",
        "message": "Reactivated and working!"
    }, headers=org_hdr)
    check("WhatsApp Unblocked After Reactivation (HTTP 200)", res_send_ok.status_code == 200)

    res_order_ok = client.post('/payments/create-order', json={
        "amount": 750.0,
        "appointment_id": 103
    }, headers=org_hdr)
    check("Razorpay Order Unblocked After Reactivation (HTTP 201)", res_order_ok.status_code == 201)

    # 4. SuperAdmin Services Status Inspection
    res_status = client.get('/admin/tenants/1/services-status', headers=admin_hdr)
    check("SuperAdmin View Live Tenant Services Status", res_status.status_code == 200 and res_status.get_json()['services']['whatsapp']['status'] == "ACTIVE")

    print("\n============================================================")
    print(f"INTEGRATION TEST SUMMARY: {passed} PASSED, {failed} FAILED")
    if errors:
        print("FAILURES:")
        for err in errors:
            print(err)
    else:
        print("ALL 4 LAYERS (DB, MIDDLEWARE, META WABA, RAZORPAY ROUTE) VERIFIED 100% OPERATIONAL!")
    print("============================================================")
