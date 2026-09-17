const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const app = express();
const PORT = 3000;
const HOST = '0.0.0.0';
const JWT_SECRET = process.env.JWT_SECRET_KEY || 'appointocare-secret-jwt-key-2026';

app.use(cors());
app.use(express.json());

// In-Memory Database & Seed Data
let nextOrgId = 4;
let nextUserId = 3;
let nextApptId = 7;
let nextTxnId = 9;

const admins = [
  {
    id: 1,
    username: process.env.ADMIN_USERNAME || 'superadmin',
    passwordHash: bcrypt.hashSync(process.env.ADMIN_PASSWORD || 'Admin@12345', 10),
    role: 'Admin',
    name: 'Platform SuperAdmin'
  }
];

const organizations = [
  {
    id: 1,
    name: 'City Care Hospital',
    code: 'ORG1',
    sector: 'Hospital',
    username: process.env.ORG_USERNAME || 'org1',
    passwordHash: bcrypt.hashSync(process.env.ORG_PASSWORD || 'Org@12345', 10),
    subscription_status: 'Active',
    subscription_plan: 'Professional',
    subscription_start: new Date(Date.now() - 30 * 86400000).toISOString(),
    subscription_end: new Date(Date.now() + 30 * 86400000).toISOString(),
    next_billing_date: new Date(Date.now() + 30 * 86400000).toISOString(),
    created_at: new Date(Date.now() - 60 * 86400000).toISOString()
  },
  {
    id: 2,
    name: 'Apex Dental Clinic',
    code: 'APEX01',
    sector: 'Hospital',
    username: 'apexdental',
    passwordHash: bcrypt.hashSync('Apex@12345', 10),
    subscription_status: 'Active',
    subscription_plan: 'Starter',
    subscription_start: new Date(Date.now() - 15 * 86400000).toISOString(),
    subscription_end: new Date(Date.now() + 15 * 86400000).toISOString(),
    next_billing_date: new Date(Date.now() + 15 * 86400000).toISOString(),
    created_at: new Date(Date.now() - 45 * 86400000).toISOString()
  },
  {
    id: 3,
    name: 'Summit Financial Advisory',
    code: 'SUMMIT',
    sector: 'Finance',
    username: 'summitfin',
    passwordHash: bcrypt.hashSync('Summit@12345', 10),
    subscription_status: 'Paused',
    subscription_plan: 'Enterprise',
    subscription_start: new Date(Date.now() - 90 * 86400000).toISOString(),
    subscription_end: new Date(Date.now() + 5 * 86400000).toISOString(),
    next_billing_date: new Date(Date.now() + 5 * 86400000).toISOString(),
    created_at: new Date(Date.now() - 90 * 86400000).toISOString()
  }
];

const users = [
  {
    id: 1,
    organization_id: 1,
    username: process.env.STAFF_USERNAME || 'staff1',
    passwordHash: bcrypt.hashSync(process.env.STAFF_PASSWORD || 'Staff@12345', 10),
    role: 'Staff',
    is_active: true,
    email: 'staff1@citycare.org',
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    organization_id: 1,
    username: 'manager1',
    passwordHash: bcrypt.hashSync('Manager@12345', 10),
    role: 'Manager',
    is_active: true,
    email: 'manager@citycare.org',
    created_at: new Date().toISOString()
  }
];

const appointments = [
  {
    id: 1,
    organization_id: 1,
    customer_name: 'John Smith',
    customer_phone: '+1 555-0101',
    appointment_date: new Date(Date.now() + 2 * 3600000).toISOString(),
    status: 'Booked',
    payment_status: 'Paid',
    amount: 500,
    payment_method: 'Card',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: null
  },
  {
    id: 2,
    organization_id: 1,
    customer_name: 'Sarah Connor',
    customer_phone: '+1 555-0102',
    appointment_date: new Date(Date.now() - 4 * 3600000).toISOString(),
    status: 'Completed',
    payment_status: 'Paid',
    amount: 750,
    payment_method: 'UPI',
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 3,
    organization_id: 1,
    customer_name: 'Michael Brown',
    customer_phone: '+1 555-0103',
    appointment_date: new Date(Date.now() + 24 * 3600000).toISOString(),
    status: 'Booked',
    payment_status: 'Pending',
    amount: 500,
    payment_method: 'Cash',
    created_at: new Date().toISOString(),
    updated_at: null
  },
  {
    id: 4,
    organization_id: 1,
    customer_name: 'Emily Davis',
    customer_phone: '+1 555-0104',
    appointment_date: new Date(Date.now() - 24 * 3600000).toISOString(),
    status: 'Cancelled',
    payment_status: 'Unpaid',
    amount: 300,
    payment_method: 'Card',
    created_at: new Date(Date.now() - 3 * 86400000).toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 5,
    organization_id: 2,
    customer_name: 'David Lee',
    customer_phone: '+1 555-0105',
    appointment_date: new Date(Date.now() + 48 * 3600000).toISOString(),
    status: 'Booked',
    payment_status: 'Paid',
    amount: 1200,
    payment_method: 'Card',
    created_at: new Date().toISOString(),
    updated_at: null
  },
  {
    id: 6,
    organization_id: 3,
    customer_name: 'Rachel Green',
    customer_phone: '+1 555-0106',
    appointment_date: new Date(Date.now() + 12 * 3600000).toISOString(),
    status: 'Booked',
    payment_status: 'Paid',
    amount: 2500,
    payment_method: 'NetBanking',
    created_at: new Date().toISOString(),
    updated_at: null
  }
];

const orgTransactions = [
  {
    id: 1,
    organization_id: 1,
    amount: 2499,
    transaction_type: 'Subscription',
    payment_method: 'Card',
    status: 'Success',
    remarks: 'Professional Monthly Plan Renewal',
    processed_by_type: 'Organization',
    created_at: new Date(Date.now() - 30 * 86400000).toISOString()
  },
  {
    id: 2,
    organization_id: 2,
    amount: 999,
    transaction_type: 'Subscription',
    payment_method: 'UPI',
    status: 'Success',
    remarks: 'Starter Monthly Plan Renewal',
    processed_by_type: 'Organization',
    created_at: new Date(Date.now() - 15 * 86400000).toISOString()
  },
  {
    id: 3,
    organization_id: 3,
    amount: 9999,
    transaction_type: 'Subscription',
    payment_method: 'NetBanking',
    status: 'Success',
    remarks: 'Enterprise Annual Plan',
    processed_by_type: 'Admin',
    created_at: new Date(Date.now() - 60 * 86400000).toISOString()
  }
];

const apptTransactions = [
  {
    id: 4,
    appointment_id: 1,
    organization_id: 1,
    amount: 500,
    transaction_type: 'Payment',
    payment_method: 'Card',
    status: 'Success',
    remarks: 'Online prepayment',
    processed_by_type: 'Staff',
    created_at: new Date(Date.now() - 86400000).toISOString()
  },
  {
    id: 5,
    appointment_id: 2,
    organization_id: 1,
    amount: 750,
    transaction_type: 'Payment',
    payment_method: 'UPI',
    status: 'Success',
    remarks: 'Counter payment',
    processed_by_type: 'Staff',
    created_at: new Date(Date.now() - 2 * 86400000).toISOString()
  },
  {
    id: 6,
    appointment_id: 5,
    organization_id: 2,
    amount: 1200,
    transaction_type: 'Payment',
    payment_method: 'Card',
    status: 'Success',
    remarks: 'Prepaid root canal consult',
    processed_by_type: 'Staff',
    created_at: new Date().toISOString()
  }
];

const subscriptionPlans = [
  {
    id: 1,
    name: 'Starter',
    description: 'Basic appointment scheduling for small practices',
    price: 999.0,
    billing_cycle: 'monthly',
    feature_limits: { users: 5, appointments_per_month: 500 },
    is_active: true
  },
  {
    id: 2,
    name: 'Professional',
    description: 'Multi-provider clinic management with WhatsApp integration',
    price: 2499.0,
    billing_cycle: 'monthly',
    feature_limits: { users: 25, appointments_per_month: 2500 },
    is_active: true
  },
  {
    id: 3,
    name: 'Enterprise',
    description: 'Multi-branch hospitals with bespoke custom workflows',
    price: 9999.0,
    billing_cycle: 'monthly',
    feature_limits: { users: -1, appointments_per_month: -1 },
    is_active: true
  }
];

const sectorTemplates = [
  {
    id: 1,
    name: 'Hospital',
    description: 'Healthcare, clinic, and doctor consultations',
    services: ['Doctor Consultation', 'Diagnostic Review', 'Specialist Assessment', 'Follow-up Checkup'],
    is_active: true
  },
  {
    id: 2,
    name: 'Finance',
    description: 'Banking, mortgage, and investment advisors',
    services: ['Loan Consultation', 'Financial Planning', 'Wealth Review', 'Tax Strategy'],
    is_active: true
  },
  {
    id: 3,
    name: 'Retail',
    description: 'In-store personal shopping & customer service',
    services: ['Store Visit', 'Product Consultation', 'VIP Fitting', 'Warranty Review'],
    is_active: true
  },
  {
    id: 4,
    name: 'Salon',
    description: 'Beauty, wellness, spa, and styling services',
    services: ['Hair Styling', 'Wellness Consultation', 'Facial Treatment', 'Full Spa Package'],
    is_active: true
  }
];

const campaigns = [
  {
    id: 1,
    organization_id: 1,
    name: 'Winter Wellness Checkup Reminder',
    channel: 'WhatsApp',
    message: 'Hello! Schedule your annual wellness consultation at City Care Hospital this month for 20% off.',
    audience_filter: { status: 'All Customers' },
    status: 'Sent',
    scheduled_at: new Date(Date.now() - 5 * 86400000).toISOString(),
    sent_at: new Date(Date.now() - 5 * 86400000).toISOString()
  }
];

const notifications = [
  {
    id: 1,
    organization_id: 1,
    title: 'New Appointment Booked',
    message: 'John Smith booked an appointment for tomorrow at 10:00 AM.',
    type: 'appointment',
    is_read: false,
    created_at: new Date().toISOString()
  }
];

const branches = [
  {
    id: 1,
    organization_id: 1,
    name: 'Main Campus',
    address: '100 Healthcare Blvd, Suite 100',
    phone: '+1 555-0100',
    is_active: true
  },
  {
    id: 2,
    organization_id: 1,
    name: 'Downtown Clinic',
    address: '450 City Center St',
    phone: '+1 555-0150',
    is_active: true
  }
];

// Helper: Generate JWT
function generateToken(payload, expiresIn = '8h') {
  return jwt.sign(payload, JWT_SECRET, { expiresIn });
}

// Helper: Verify JWT Middleware
function authenticateJWT(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ msg: 'Authorization token missing or invalid' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ msg: 'Invalid or expired token' });
  }
}

// ----------------------------------------------------
// Health & Ready
// ----------------------------------------------------
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'appointocare-api' });
});

app.get('/ready', (req, res) => {
  res.json({ status: 'ready', database: 'available' });
});

// ----------------------------------------------------
// Authentication Routes
// ----------------------------------------------------
app.post('/auth/login', (req, res) => {
  const { username, password, code } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ msg: 'Username and password are required' });
  }

  // 1. Check Admin
  const admin = admins.find(a => a.username === username);
  if (admin) {
    if (bcrypt.compareSync(password, admin.passwordHash)) {
      const claims = {
        sub: String(admin.id),
        username: admin.username,
        role: 'Admin'
      };
      const access_token = generateToken(claims);
      const refresh_token = generateToken(claims, '7d');
      return res.json({
        access_token,
        refresh_token,
        role: 'Admin',
        username: admin.username
      });
    }
    return res.status(401).json({ msg: 'Invalid password' });
  }

  // 2. Organization or Staff Login requires organization code
  if (!code) {
    return res.status(400).json({ msg: 'Organization code is required' });
  }

  const org = organizations.find(o => o.code.toUpperCase() === code.toUpperCase());
  if (!org) {
    return res.status(401).json({ msg: 'Invalid organization code' });
  }

  // Check Organization Admin
  if (org.username === username) {
    if (bcrypt.compareSync(password, org.passwordHash)) {
      const claims = {
        sub: String(org.id),
        username: org.username,
        role: 'Organization',
        organization_id: String(org.id),
        organization_name: org.name
      };
      const access_token = generateToken(claims);
      const refresh_token = generateToken(claims, '7d');
      return res.json({
        access_token,
        refresh_token,
        role: 'Organization',
        organization_id: String(org.id),
        organization_name: org.name
      });
    }
    return res.status(401).json({ msg: 'Invalid password' });
  }

  // Check Staff / Manager
  const staff = users.find(u => u.organization_id === org.id && u.username === username);
  if (staff && staff.is_active && bcrypt.compareSync(password, staff.passwordHash)) {
    const claims = {
      sub: String(staff.id),
      username: staff.username,
      role: staff.role,
      organization_id: String(org.id),
      organization_name: org.name
    };
    const access_token = generateToken(claims);
    const refresh_token = generateToken(claims, '7d');
    return res.json({
      access_token,
      refresh_token,
      role: staff.role,
      organization_id: String(org.id),
      organization_name: org.name,
      username: staff.username
    });
  }

  return res.status(401).json({ msg: 'Invalid credentials' });
});

app.post('/auth/refresh', (req, res) => {
  const { refresh_token } = req.body || {};
  if (!refresh_token) {
    return res.status(400).json({ msg: 'refresh_token required' });
  }
  try {
    const decoded = jwt.verify(refresh_token, JWT_SECRET);
    const newClaims = {
      sub: decoded.sub,
      username: decoded.username,
      role: decoded.role,
      organization_name: decoded.organization_name,
      organization_id: decoded.organization_id
    };
    const access_token = generateToken(newClaims);
    return res.json({ access_token });
  } catch (err) {
    return res.status(401).json({ msg: 'Invalid refresh token' });
  }
});

app.post('/auth/logout', (req, res) => {
  res.json({ msg: 'Logged out' });
});

app.post('/auth/change-password', authenticateJWT, (req, res) => {
  const { old_password, new_password } = req.body || {};
  if (!old_password || !new_password) {
    return res.status(400).json({ msg: 'old_password and new_password are required' });
  }

  const role = req.user.role;
  const sub = Number(req.user.sub);

  if (role === 'Admin') {
    const a = admins.find(x => x.id === sub);
    if (!a || !bcrypt.compareSync(old_password, a.passwordHash)) {
      return res.status(401).json({ msg: 'Invalid current password' });
    }
    a.passwordHash = bcrypt.hashSync(new_password, 10);
    return res.json({ msg: 'Password changed successfully' });
  } else if (role === 'Organization') {
    const o = organizations.find(x => x.id === sub);
    if (!o || !bcrypt.compareSync(old_password, o.passwordHash)) {
      return res.status(401).json({ msg: 'Invalid current password' });
    }
    o.passwordHash = bcrypt.hashSync(new_password, 10);
    return res.json({ msg: 'Password changed successfully' });
  } else {
    const u = users.find(x => x.id === sub);
    if (!u || !bcrypt.compareSync(old_password, u.passwordHash)) {
      return res.status(401).json({ msg: 'Invalid current password' });
    }
    u.passwordHash = bcrypt.hashSync(new_password, 10);
    return res.json({ msg: 'Password changed successfully' });
  }
});

app.post('/auth/forgot-password', (req, res) => {
  const { username, role, code } = req.body || {};
  if (!username || !role) {
    return res.status(400).json({ msg: 'username and role are required' });
  }

  let userObj = null;
  if (role === 'Admin') {
    userObj = admins.find(a => a.username === username);
  } else if (role === 'Organization') {
    userObj = organizations.find(o => o.username === username && (!code || o.code === code));
  } else {
    const org = organizations.find(o => o.code === code);
    if (org) {
      userObj = users.find(u => u.username === username && u.organization_id === org.id);
    }
  }

  const reset_token = generateToken({ sub: userObj ? userObj.id : 1, role, username }, '30m');
  return res.json({ msg: 'Password reset token generated.', reset_token });
});

app.post('/auth/reset-password', (req, res) => {
  const { token, new_password } = req.body || {};
  if (!token || !new_password) {
    return res.status(400).json({ msg: 'token and new_password are required' });
  }
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const id = Number(decoded.sub);
    if (decoded.role === 'Admin') {
      const a = admins.find(x => x.id === id);
      if (a) a.passwordHash = bcrypt.hashSync(new_password, 10);
    } else if (decoded.role === 'Organization') {
      const o = organizations.find(x => x.id === id);
      if (o) o.passwordHash = bcrypt.hashSync(new_password, 10);
    } else {
      const u = users.find(x => x.id === id);
      if (u) u.passwordHash = bcrypt.hashSync(new_password, 10);
    }
    return res.json({ msg: 'Password updated successfully' });
  } catch (err) {
    return res.status(400).json({ msg: 'Invalid or expired reset token' });
  }
});

// ----------------------------------------------------
// Admin Routes
// ----------------------------------------------------
app.get('/admin/dashboard', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });

  const booked = appointments.filter(a => a.status === 'Booked').length;
  const completed = appointments.filter(a => a.status === 'Completed').length;
  const cancelled = appointments.filter(a => a.status === 'Cancelled').length;

  const totalOrgTxn = orgTransactions.reduce((acc, t) => acc + (t.amount || 0), 0);
  const totalApptTxn = apptTransactions.reduce((acc, t) => acc + (t.amount || 0), 0);
  const activeOrgs = organizations.filter(o => o.subscription_status === 'Active').length;
  const pausedOrgs = organizations.filter(o => o.subscription_status === 'Paused').length;

  res.json({
    total_organizations: organizations.length,
    total_appointments: appointments.length,
    appointments_summary: {
      booked,
      completed,
      cancelled
    },
    total_transactions: totalOrgTxn + totalApptTxn,
    today_transactions: 3,
    today_transactions_amount: 1750,
    organizations_status: {
      active: activeOrgs,
      paused: pausedOrgs
    },
    recent_organizations: organizations.slice(-5),
    recent_appointments: appointments.slice(-5),
    recent_transactions: [...orgTransactions, ...apptTransactions].slice(-10)
  });
});

app.get('/admin/transactions/summary', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });

  const currentMonth = new Date().getMonth() + 1;
  const summary = [
    { month: 1, total: 4200 },
    { month: 2, total: 6800 },
    { month: 3, total: 8500 },
    { month: 4, total: 7200 },
    { month: 5, total: 9100 },
    { month: 6, total: 11400 },
    { month: 7, total: 10200 },
    { month: 8, total: 12500 },
    { month: 9, total: 14800 },
    { month: 10, total: 13900 },
    { month: 11, total: 16200 },
    { month: 12, total: 18500 }
  ];
  res.json(summary);
});

app.get('/admin/organizations', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  res.json(organizations);
});

app.post('/admin/organization/create', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const { name, code, sector, username, password, subscription_plan } = req.body || {};
  if (!name || !code || !sector || !username || !password) {
    return res.status(400).json({ msg: 'Missing required organization fields' });
  }

  const newOrg = {
    id: nextOrgId++,
    name,
    code: code.toUpperCase(),
    sector,
    username,
    passwordHash: bcrypt.hashSync(password, 10),
    subscription_status: 'Active',
    subscription_plan: subscription_plan || 'Basic',
    subscription_start: new Date().toISOString(),
    subscription_end: new Date(Date.now() + 30 * 86400000).toISOString(),
    next_billing_date: new Date(Date.now() + 30 * 86400000).toISOString(),
    created_at: new Date().toISOString()
  };
  organizations.push(newOrg);
  res.status(201).json({ msg: 'Organization created successfully', organization: newOrg });
});

app.patch('/admin/organization/:orgId/update', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const orgId = Number(req.params.orgId);
  const org = organizations.find(o => o.id === orgId);
  if (!org) return res.status(404).json({ msg: 'Organization not found' });

  const { name, sector, subscription_status, subscription_plan } = req.body || {};
  if (name) org.name = name;
  if (sector) org.sector = sector;
  if (subscription_status) org.subscription_status = subscription_status;
  if (subscription_plan) org.subscription_plan = subscription_plan;

  res.json({ msg: 'Organization updated successfully', organization: org });
});

app.delete('/admin/organization/:orgId/delete', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const orgId = Number(req.params.orgId);
  const index = organizations.findIndex(o => o.id === orgId);
  if (index === -1) return res.status(404).json({ msg: 'Organization not found' });

  organizations.splice(index, 1);
  res.json({ msg: 'Organization deleted successfully' });
});

app.get('/admin/organization/:orgId/users', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const orgId = Number(req.params.orgId);
  const orgUsers = users.filter(u => u.organization_id === orgId);
  res.json(orgUsers.map(u => ({ id: u.id, username: u.username, role: u.role, is_active: u.is_active, email: u.email })));
});

app.post('/admin/organization/:orgId/user/create', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const orgId = Number(req.params.orgId);
  const { username, password, role, email } = req.body || {};
  if (!username || !password) return res.status(400).json({ msg: 'Username and password required' });

  const newUser = {
    id: nextUserId++,
    organization_id: orgId,
    username,
    passwordHash: bcrypt.hashSync(password, 10),
    role: role || 'Staff',
    is_active: true,
    email: email || `${username}@example.com`,
    created_at: new Date().toISOString()
  };
  users.push(newUser);
  res.status(201).json({ msg: 'User created successfully', user: { id: newUser.id, username: newUser.username, role: newUser.role } });
});

app.patch('/admin/organization/:orgId/user/:userId/update', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const userId = Number(req.params.userId);
  const u = users.find(x => x.id === userId);
  if (!u) return res.status(404).json({ msg: 'User not found' });

  if (req.body.role) u.role = req.body.role;
  if (req.body.is_active !== undefined) u.is_active = req.body.is_active;
  if (req.body.password) u.passwordHash = bcrypt.hashSync(req.body.password, 10);

  res.json({ msg: 'User updated successfully' });
});

app.delete('/admin/organization/:orgId/user/:userId/delete', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const userId = Number(req.params.userId);
  const index = users.findIndex(x => x.id === userId);
  if (index !== -1) users.splice(index, 1);
  res.json({ msg: 'User deleted successfully' });
});

app.get('/admin/subscriptions', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const subs = organizations.map(o => ({
    organization_id: o.id,
    organization_name: o.name,
    organization_code: o.code,
    plan: o.subscription_plan,
    status: o.subscription_status,
    start_date: o.subscription_start,
    end_date: o.subscription_end,
    next_billing_date: o.next_billing_date
  }));
  res.json(subs);
});

app.get('/admin/transactions', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  const list = [
    ...orgTransactions.map(t => ({ ...t, source: 'Organization' })),
    ...apptTransactions.map(t => ({ ...t, source: 'Appointment' }))
  ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  res.json(list);
});

app.get('/admin/appointments', authenticateJWT, (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ msg: 'Unauthorized' });
  res.json(appointments);
});

// ----------------------------------------------------
// Organization Routes
// ----------------------------------------------------
app.get('/organization/dashboard', authenticateJWT, (req, res) => {
  const orgId = Number(req.user.organization_id || req.user.sub);
  const org = organizations.find(o => o.id === orgId) || organizations[0];

  const orgAppts = appointments.filter(a => a.organization_id === org.id);
  const orgTxns = orgTransactions.filter(t => t.organization_id === org.id);
  const apptTxns = apptTransactions.filter(t => t.organization_id === org.id);

  res.json({
    organization: {
      name: org.name,
      sector: org.sector,
      subscription: {
        status: org.subscription_status,
        plan: org.subscription_plan,
        start_date: org.subscription_start,
        end_date: org.subscription_end,
        next_billing_date: org.next_billing_date
      }
    },
    appointments_count: orgAppts.length,
    appointments: orgAppts,
    organization_transactions: orgTxns,
    appointment_transactions: apptTxns
  });
});

app.get('/organization/appointments', authenticateJWT, (req, res) => {
  const orgId = Number(req.user.organization_id || req.user.sub);
  const orgAppts = appointments.filter(a => a.organization_id === orgId);
  const formatted = orgAppts.map(a => {
    const txn = apptTransactions.find(t => t.appointment_id === a.id);
    return {
      id: a.id,
      customer_name: a.customer_name,
      customer_phone: a.customer_phone,
      appointment_date: a.appointment_date,
      status: a.status,
      payment_status: a.payment_status,
      amount: a.amount || (txn ? txn.amount : null),
      payment_method: a.payment_method || (txn ? txn.payment_method : null),
      transaction_status: txn ? txn.status : a.payment_status,
      created_at: a.created_at,
      updated_at: a.updated_at
    };
  });
  res.json(formatted);
});

app.get('/organization/transactions/summary', authenticateJWT, (req, res) => {
  const summary = [
    { month: 1, total: 1200 },
    { month: 2, total: 2100 },
    { month: 3, total: 3400 },
    { month: 4, total: 2900 },
    { month: 5, total: 3800 },
    { month: 6, total: 4500 },
    { month: 7, total: 4100 },
    { month: 8, total: 4900 },
    { month: 9, total: 5600 }
  ];
  res.json(summary);
});

app.post('/organization/message/send', authenticateJWT, (req, res) => {
  const { recipient_number, message_content, message_type } = req.body || {};
  res.json({ msg: 'Message sent successfully', recipient: recipient_number, type: message_type || 'WhatsApp' });
});

app.get('/organizations/:orgId/bookings', (req, res) => {
  const orgId = Number(req.params.orgId);
  const orgAppts = appointments.filter(a => a.organization_id === orgId);
  res.json(orgAppts);
});

app.post('/organizations/:orgId/bookings/:bookingId/cancel', (req, res) => {
  const bookingId = Number(req.params.bookingId);
  const appt = appointments.find(a => a.id === bookingId);
  if (appt) appt.status = 'Cancelled';
  res.json({ msg: 'Booking cancelled successfully' });
});

app.put('/organizations/:orgId/bookings/:bookingId', (req, res) => {
  const bookingId = Number(req.params.bookingId);
  const appt = appointments.find(a => a.id === bookingId);
  if (appt) {
    if (req.body.appointment_date) appt.appointment_date = req.body.appointment_date;
    if (req.body.status) appt.status = req.body.status;
  }
  res.json({ msg: 'Booking updated successfully', appointment: appt });
});

// ----------------------------------------------------
// Appointments CRUD
// ----------------------------------------------------
app.post(['/appointments', '/appointments/create'], authenticateJWT, (req, res) => {
  const orgId = Number(req.user.organization_id || req.user.sub || 1);
  const { customer_name, customer_phone, appointment_date, amount, payment_method, status, payment_status } = req.body || {};

  if (!customer_name || !customer_phone || !appointment_date) {
    return res.status(400).json({ msg: 'Missing required appointment fields' });
  }

  const newAppt = {
    id: nextApptId++,
    organization_id: orgId,
    customer_name,
    customer_phone,
    appointment_date: new Date(appointment_date).toISOString(),
    status: status || 'Booked',
    payment_status: payment_status || (amount ? 'Paid' : 'Pending'),
    amount: amount ? Number(amount) : 500,
    payment_method: payment_method || 'Card',
    created_at: new Date().toISOString(),
    updated_at: null
  };
  appointments.push(newAppt);

  if (amount) {
    apptTransactions.push({
      id: nextTxnId++,
      appointment_id: newAppt.id,
      organization_id: orgId,
      amount: Number(amount),
      transaction_type: 'Payment',
      payment_method: payment_method || 'Card',
      status: 'Success',
      remarks: 'Appointment booking payment',
      processed_by_type: req.user.role,
      created_at: new Date().toISOString()
    });
  }

  res.status(201).json({ msg: 'Appointment created successfully', appointment_id: newAppt.id });
});

app.get('/appointments/all', authenticateJWT, (req, res) => {
  const orgId = Number(req.user.organization_id || req.user.sub);
  const orgAppts = appointments.filter(a => a.organization_id === orgId);
  res.json(orgAppts);
});

app.get('/appointments/:id', authenticateJWT, (req, res) => {
  const appt = appointments.find(a => a.id === Number(req.params.id));
  if (!appt) return res.status(404).json({ msg: 'Appointment not found' });
  res.json(appt);
});

app.patch('/appointments/:id', authenticateJWT, (req, res) => {
  const appt = appointments.find(a => a.id === Number(req.params.id));
  if (!appt) return res.status(404).json({ msg: 'Appointment not found' });

  const { status, payment_status, appointment_date } = req.body || {};
  if (status) appt.status = status;
  if (payment_status) appt.payment_status = payment_status;
  if (appointment_date) appt.appointment_date = new Date(appointment_date).toISOString();
  appt.updated_at = new Date().toISOString();

  res.json({ msg: 'Appointment updated successfully', appointment: appt });
});

app.delete('/appointments/:id', authenticateJWT, (req, res) => {
  const index = appointments.findIndex(a => a.id === Number(req.params.id));
  if (index !== -1) appointments.splice(index, 1);
  res.json({ msg: 'Appointment deleted successfully' });
});

// ----------------------------------------------------
// Transactions Routes
// ----------------------------------------------------
app.post('/transactions/create', authenticateJWT, (req, res) => {
  const { transaction_type, amount, payment_method, appointment_id } = req.body || {};
  const orgId = Number(req.user.organization_id || req.user.sub || 1);

  const newTxn = {
    id: nextTxnId++,
    organization_id: orgId,
    appointment_id: appointment_id ? Number(appointment_id) : undefined,
    amount: Number(amount || 0),
    transaction_type: transaction_type || 'Payment',
    payment_method: payment_method || 'Card',
    status: 'Success',
    created_at: new Date().toISOString()
  };

  if (transaction_type === 'organization') {
    orgTransactions.push(newTxn);
  } else {
    apptTransactions.push(newTxn);
  }
  res.status(201).json({ msg: 'Transaction recorded', id: newTxn.id });
});

app.get('/transactions/all', authenticateJWT, (req, res) => {
  const orgId = Number(req.user.organization_id || req.user.sub);
  if (req.user.role === 'Admin') {
    res.json([...orgTransactions, ...apptTransactions]);
  } else {
    const list = [
      ...orgTransactions.filter(t => t.organization_id === orgId),
      ...apptTransactions.filter(t => t.organization_id === orgId)
    ];
    res.json(list);
  }
});

// ----------------------------------------------------
// Platform API v1 Routes
// ----------------------------------------------------
app.get('/api/v1/platform/plans', (req, res) => res.json(subscriptionPlans));
app.post('/api/v1/platform/plans', authenticateJWT, (req, res) => {
  const newPlan = { id: subscriptionPlans.length + 1, ...req.body, is_active: true };
  subscriptionPlans.push(newPlan);
  res.status(201).json({ id: newPlan.id, msg: 'Plan created' });
});

app.get('/api/v1/platform/templates', (req, res) => res.json(sectorTemplates));
app.post('/api/v1/platform/templates', authenticateJWT, (req, res) => {
  const newTemp = { id: sectorTemplates.length + 1, ...req.body, is_active: true };
  sectorTemplates.push(newTemp);
  res.status(201).json({ id: newTemp.id, msg: 'Sector template created' });
});

app.get('/api/v1/platform/campaigns', authenticateJWT, (req, res) => res.json(campaigns));
app.post('/api/v1/platform/campaigns', authenticateJWT, (req, res) => {
  const newCamp = { id: campaigns.length + 1, ...req.body, status: 'Active', created_at: new Date().toISOString() };
  campaigns.push(newCamp);
  res.status(201).json({ id: newCamp.id, msg: 'Campaign created' });
});

app.get('/api/v1/platform/notifications', authenticateJWT, (req, res) => res.json(notifications));
app.post('/api/v1/platform/notifications/:id/read', authenticateJWT, (req, res) => {
  const n = notifications.find(x => x.id === Number(req.params.id));
  if (n) n.is_read = true;
  res.json({ msg: 'Notification marked as read' });
});

app.get('/api/v1/platform/branches', authenticateJWT, (req, res) => res.json(branches));
app.post('/api/v1/platform/branches', authenticateJWT, (req, res) => {
  const b = { id: branches.length + 1, ...req.body, is_active: true };
  branches.push(b);
  res.status(201).json({ id: b.id, msg: 'Branch created' });
});

app.get('/api/v1/platform/reports/summary', authenticateJWT, (req, res) => {
  res.json({
    total_appointments: appointments.length,
    active_organizations: organizations.filter(o => o.subscription_status === 'Active').length,
    monthly_revenue: 28990,
    completion_rate: '87%'
  });
});

// ----------------------------------------------------
// Angular Frontend Static Serving with SPA Fallback
// ----------------------------------------------------
const distPath = path.join(__dirname, 'appointocare-frontend', 'dist', 'appointocare-frontend', 'browser');

// If frontend has not been compiled yet, compile it now
if (!fs.existsSync(path.join(distPath, 'index.html'))) {
  console.log('[AppointoCare] Building Angular frontend...');
  try {
    execSync('npm --prefix appointocare-frontend run build', { stdio: 'inherit' });
    console.log('[AppointoCare] Frontend build complete.');
  } catch (err) {
    console.error('[AppointoCare] Error building frontend:', err);
  }
}

app.use(express.static(distPath));

app.get('*', (req, res) => {
  const indexFile = path.join(distPath, 'index.html');
  if (fs.existsSync(indexFile)) {
    res.sendFile(indexFile);
  } else {
    res.status(404).send('Application bundle not found. Please run npm run build.');
  }
});

app.listen(PORT, HOST, () => {
  console.log(`AppointoCare server running at http://${HOST}:${PORT}`);
});
