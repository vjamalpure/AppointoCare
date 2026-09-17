import urllib.request
import json
import sys

base = 'http://127.0.0.1:8000'

def post_json(url, data, token=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_json(url, token=None):
    req = urllib.request.Request(url)
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=" * 60)
print("Testing AppointoCare Multi-Industry Platform Backend & Migration Data")
print("=" * 60)

# 1. SuperAdmin
admin_res = post_json(f'{base}/auth/login', {'username': 'superadmin', 'password': 'Admin@12345'})
admin_tok = admin_res.get('access_token')
assert admin_tok, "SuperAdmin login failed"
print(f"✓ SuperAdmin Login OK (Role: {admin_res.get('role')})")

all_rec = get_json(f'{base}/api/v1/industry-suite/records?all=true', admin_tok)
print(f"✓ SuperAdmin All Industry Records count: {len(all_rec)}")
assert len(all_rec) == 27, f"Expected 27 records across 9 orgs, got {len(all_rec)}"

all_bench = get_json(f'{base}/api/v1/industry-suite/benchmarks?all=true', admin_tok)
sectors = list(all_bench.get('all_benchmarks', {}).keys())
print(f"✓ SuperAdmin Benchmarks for all {len(sectors)} sectors verified: {', '.join(sectors)}")
assert len(sectors) == 9, f"Expected 9 benchmark sectors, got {len(sectors)}"

# 2. Test All 9 Organizations
for i in range(1, 10):
    user = f"org{i}"
    org_res = post_json(f'{base}/auth/login', {'username': user, 'password': 'Org@12345'})
    tok = org_res.get('access_token')
    assert tok, f"Login failed for {user}"

    recs = get_json(f'{base}/api/v1/industry-suite/records', tok)
    addons = get_json(f'{base}/api/v1/industry-suite/addons', tok)
    bench = get_json(f'{base}/api/v1/industry-suite/benchmarks', tok)

    sector_name = addons['sector']
    peers = bench['benchmarks']['tier1_peers']
    rec_titles = [r['title'] for r in recs]

    print(f"✓ {user.upper()} [{sector_name}] | {len(recs)} records | {len(addons['addons'])} add-ons | Benchmarks: {peers[0]}")
    for title in rec_titles:
        print(f"    - {title}")

# 3. Test Staff Login (Doctor Sarah in Org1, Alex Wealth in Org3, Marcus Realty in Org8)
staff_tests = [
    ("staff1", "ORG1", "Staff"),
    ("doc_sarah", "ORG1", "Doctor"),
    ("olivia_spa", "ORG2", "Therapist"),
    ("alex_wealth", "ORG3", "Advisor"),
    ("victoria_insur", "ORG4", "Underwriter"),
    ("jeanluc_style", "ORG5", "Stylist"),
    ("elena_counsel", "ORG6", "Counselor"),
    ("eleanor_legal", "ORG7", "Partner"),
    ("marcus_realty", "ORG8", "Broker"),
    ("elizabeth_exec", "ORG9", "Consultant")
]

print("-" * 60)
print("Testing Specialist Staff Login across all 9 organizations...")
for uname, org_code, role in staff_tests:
    res = post_json(f'{base}/auth/login', {'username': uname, 'password': 'Staff@12345', 'code': org_code})
    assert res.get('access_token'), f"Staff login failed for {uname} in {org_code}"
    print(f"✓ Staff Specialist '{uname}' ({role}) authenticated successfully in {org_code}")

print("=" * 60)
print("ALL MULTI-INDUSTRY BACKEND & MIGRATION TESTS PASSED 100%!")
print("=" * 60)
