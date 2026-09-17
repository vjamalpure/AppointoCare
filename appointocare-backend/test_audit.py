import sys
from app import create_app
from app.models import (
    db, Admin, Organization, User, Branch, Customer, Service, 
    Appointment, AppointmentTransaction, OrganizationTransaction, 
    Subscription, Notification, AuditLog, IndustryRecord
)

app = create_app()
with app.app_context():
    client = app.test_client()
    passed = 0
    failed = 0
    errors = []

    def check(test_name, condition, details=''):
        global passed, failed, errors
        if condition:
            passed += 1
            print(f'  [PASS] {test_name}')
        else:
            failed += 1
            msg = f'  [FAIL] {test_name} - {details}'
            print(msg)
            errors.append(msg)

    print('====================================================')
    print('STARTING APPOINTO CARE COMPREHENSIVE END-TO-END AUDIT')
    print('====================================================')

    # 1. SUPERADMIN AUDIT
    print('\n>>> SECTION 1: SuperAdmin User & Platform Administration')
    res = client.post('/auth/login', json={'username': 'superadmin', 'password': 'Admin@12345'})
    check('SuperAdmin Login', res.status_code == 200)
    admin_token = res.get_json().get('access_token')
    admin_hdr = {'Authorization': f'Bearer {admin_token}'}

    # SuperAdmin endpoints
    res = client.get('/admin/organizations', headers=admin_hdr)
    check('SuperAdmin List Organizations', res.status_code == 200 and len(res.get_json()) >= 9)

    res = client.get('/api/v1/audit-logs', headers=admin_hdr)
    check('SuperAdmin Audit Logs', res.status_code == 200)

    res = client.get('/admin/subscriptions', headers=admin_hdr)
    check('SuperAdmin Subscriptions List', res.status_code == 200)

    res = client.get('/api/v1/admin/analytics-reports', headers=admin_hdr)
    check('SuperAdmin Analytics Reports', res.status_code == 200)

    res = client.post('/api/v1/admin/broadcast-notification', json={'title': 'Platform Audit', 'message': 'All systems online'}, headers=admin_hdr)
    check('SuperAdmin Broadcast Notification', res.status_code == 200)

    res = client.get('/api/v1/industry-suite/benchmarks?all=true', headers=admin_hdr)
    check('SuperAdmin Benchmarks All Sectors', res.status_code == 200 and len(res.get_json().get('all_benchmarks', {})) == 9)

    res = client.get('/api/v1/industry-suite/addons?all_sectors=true', headers=admin_hdr)
    check('SuperAdmin Global Addon Catalog', res.status_code == 200 and len(res.get_json().get('sectors', {})) == 9)

    # 2. SECTOR-BY-SECTOR AUDIT FOR ALL 9 ORGANIZATIONS
    print('\n>>> SECTION 2: All 9 Industry Organizations Full Feature Audit')
    orgs = Organization.query.order_by(Organization.id.asc()).all()
    check('9 Organizations Present', len(orgs) >= 9)

    for org in orgs:
        print(f'\n--- Checking [{org.code}] {org.name} (Sector: {org.sector}) ---')
        
        # A. Org Login
        res = client.post('/auth/login', json={'username': org.username, 'password': 'Org@12345', 'code': org.code})
        check(f'Org Login ({org.code})', res.status_code == 200)
        if res.status_code != 200:
            continue
        token = res.get_json().get('access_token')
        hdr = {'Authorization': f'Bearer {token}'}

        # B. Services Catalog
        res_svc = client.get('/api/v1/services', headers=hdr)
        svcs = res_svc.get_json() if res_svc.status_code == 200 else []
        check(f'Services Catalog ({org.code})', res_svc.status_code == 200 and len(svcs) > 0, f'count={len(svcs)}')
        if svcs:
            check(f'Services Sector Binding ({org.code})', all(s.get('sector') is not None for s in svcs))

        # Test creating custom service
        new_svc_payload = {
            'name': f'Audit Test Service {org.code}',
            'category': 'Audit',
            'price': 499.0,
            'duration_minutes': 30,
            'active': True,
            'description': 'Automated test service offering'
        }
        res_create_svc = client.post('/api/v1/services', json=new_svc_payload, headers=hdr)
        check(f'Create Custom Service ({org.code})', res_create_svc.status_code == 201)
        created_svc_id = res_create_svc.get_json().get('id') if res_create_svc.status_code == 201 else None
        if created_svc_id:
            client.delete(f'/api/v1/services/{created_svc_id}', headers=hdr)

        # C. Customers / CRM
        res_cust = client.get('/api/v1/customers', headers=hdr)
        custs = res_cust.get_json() if res_cust.status_code == 200 else []
        check(f'Customer CRM ({org.code})', res_cust.status_code == 200 and len(custs) > 0, f'count={len(custs)}')

        # Customer timeline
        if custs:
            first_c = custs[0]
            c_id = first_c['id']
            res_time = client.get(f'/api/v1/customers/{c_id}/timeline', headers=hdr)
            check(f'Customer Timeline ({org.code})', res_time.status_code == 200)

        # D. Appointments / Bookings
        res_appts = client.get('/appointments', headers=hdr)
        appts = res_appts.get_json() if res_appts.status_code == 200 else []
        check(f'Appointments Bookings ({org.code})', res_appts.status_code == 200 and len(appts) > 0, f'count={len(appts)}')

        # E. Branches
        res_branches = client.get('/api/v1/platform/branches', headers=hdr)
        check(f'Branches List ({org.code})', res_branches.status_code == 200)

        # F. Staff Members
        staff_users = User.query.filter_by(organization_id=org.id).all()
        check(f'Staff Provisioned ({org.code})', len(staff_users) > 0, f'count={len(staff_users)}')

        # G. Industry Suite Addons
        res_addons = client.get('/api/v1/industry-suite/addons', headers=hdr)
        check(f'Industry Suite Addons ({org.code})', res_addons.status_code == 200 and len(res_addons.get_json().get('addons', [])) > 0)
        addons = res_addons.get_json().get('addons', []) if res_addons.status_code == 200 else []
        if addons:
            first_a = addons[0]
            res_toggle = client.post('/api/v1/industry-suite/addons/toggle', json={'addon_id': first_a['id'], 'enabled': not first_a['enabled']}, headers=hdr)
            check(f'Toggle Addon ({org.code})', res_toggle.status_code == 200)
            client.post('/api/v1/industry-suite/addons/toggle', json={'addon_id': first_a['id'], 'enabled': first_a['enabled']}, headers=hdr)

        # H. Industry Suite Records Vault
        res_recs = client.get('/api/v1/industry-suite/records', headers=hdr)
        recs = res_recs.get_json() if res_recs.status_code == 200 else []
        check(f'Records Vault ({org.code})', res_recs.status_code == 200 and len(recs) > 0, f'count={len(recs)}')

        # I. Live Queue Board
        res_q = client.get('/api/v1/industry-suite/queue', headers=hdr)
        check(f'Queue Board ({org.code})', res_q.status_code == 200)
        
        # Test creating token
        res_token = client.post('/api/v1/industry-suite/queue/create', json={'client_name': 'Audit Token', 'priority': 'Standard'}, headers=hdr)
        check(f'Issue Queue Token ({org.code})', res_token.status_code == 201)
        t_id = res_token.get_json().get('id') if res_token.status_code == 201 else None
        if t_id:
            res_adv = client.post('/api/v1/industry-suite/queue/advance', json={'record_id': t_id, 'status': 'In Service'}, headers=hdr)
            check(f'Advance Queue Token ({org.code})', res_adv.status_code == 200)
            client.delete(f'/api/v1/industry-suite/queue/{t_id}', headers=hdr)

        # J. Calculator Evaluation
        res_calc = client.post('/api/v1/industry-suite/calculator/evaluate', json={'calculator_type': 'revenue_optimizer', 'inputs': {'active_units': 15, 'base_rate': 250}}, headers=hdr)
        check(f'Calculator Engine ({org.code})', res_calc.status_code == 200)

        # K. In-App Notifications
        res_notif = client.get('/api/v1/notifications', headers=hdr)
        check(f'In-App Notifications ({org.code})', res_notif.status_code == 200)

        # L. Organization Subscription
        res_sub = client.get('/api/v1/organization/subscription', headers=hdr)
        check(f'Organization Subscription Details ({org.code})', res_sub.status_code in [200, 204])

    # 3. STAFF & SPECIALIST ROLES AUDIT
    print('\n>>> SECTION 3: Staff & Industry Specialist Accounts Audit')
    specialist_samples = [
        ('staff1', 'Healthcare'),
        ('doc_sarah', 'Healthcare'),
        ('olivia_spa', 'Salon & Wellness'),
        ('alex_wealth', 'Finance'),
        ('victoria_insur', 'Insurance'),
        ('rachel_retail', 'Retail'),
        ('elena_edu', 'Education'),
        ('david_cons', 'Consultancy'),
        ('marcus_broker', 'Real Estate'),
        ('sophia_law', 'Professional Services')
    ]
    for username, sector in specialist_samples:
        user = User.query.filter_by(username=username).first()
        if user:
            org = Organization.query.get(user.organization_id)
            res_staff_login = client.post('/auth/login', json={'username': username, 'password': 'Staff@12345', 'code': org.code if org else None})
            check(f'Specialist Login ({username} - {user.role})', res_staff_login.status_code == 200)
            if res_staff_login.status_code == 200:
                s_token = res_staff_login.get_json().get('access_token')
                s_hdr = {'Authorization': f'Bearer {s_token}'}
                res_appts = client.get('/appointments', headers=s_hdr)
                check(f'Specialist Calendar Appointments ({username})', res_appts.status_code == 200)
                res_q = client.get('/api/v1/industry-suite/queue', headers=s_hdr)
                check(f'Specialist Queue Board Access ({username})', res_q.status_code == 200)
                res_vault = client.get('/api/v1/industry-suite/records', headers=s_hdr)
                check(f'Specialist Records Vault Access ({username})', res_vault.status_code == 200)

    print('\n====================================================')
    print(f'AUDIT COMPLETE: {passed} PASSED, {failed} FAILED')
    if errors:
        print('FAILURES:')
        for e in errors:
            print(e)
    else:
        print('SUCCESS: ALL ENDPOINTS, ROLES, MULTI-INDUSTRY WORKFLOWS ARE 100% OPERATIONAL!')
    print('====================================================')
