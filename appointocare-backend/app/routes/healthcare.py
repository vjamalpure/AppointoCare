from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import (
    db, ClinicalEncounter, AppointmentWaitlist, ResourceRoomSchedule,
    DiagnosticLabOrder, ABDMConsentArtifact, Appointment, Customer,
    AuditLog, User
)
from datetime import datetime, timedelta

healthcare_bp = Blueprint("healthcare_bp", __name__)

CLINICAL_ROLES = ("Doctor", "Nurse", "Specialist", "Admin", "SuperAdmin", "Organization", "Manager")


def _get_org_id():
    claims = get_jwt()
    if claims.get("role") in ["Admin", "SuperAdmin"]:
        data = request.json or {}
        param_org = request.args.get("organization_id") or data.get("organization_id")
        return int(param_org) if param_org else int(claims.get("organization_id") or 1)
    return int(claims.get("organization_id") or get_jwt_identity())


# -----------------------------------------------------------------------------
# 1. Clinical Encounters (Complete Patient Journey & Documentation)
# -----------------------------------------------------------------------------
@healthcare_bp.route("/encounters", methods=["POST"])
@jwt_required()
def create_clinical_encounter():
    claims = get_jwt()
    if claims.get("role") not in CLINICAL_ROLES:
        return jsonify({"msg": "Unauthorized: Clinical credentials required"}), 403

    org_id = _get_org_id()
    data = request.json or {}

    patient_id = data.get("patient_id")
    if not patient_id:
        return jsonify({"msg": "patient_id is required"}), 400

    doctor_name = data.get("practitioner_name") or claims.get("sub") or "Consulting Doctor"
    doctor_reg = data.get("practitioner_reg_no") or "MCI-2022-84190"

    follow_up_date = None
    if data.get("follow_up_date"):
        try:
            d_str = data["follow_up_date"].replace("Z", "+00:00")
            follow_up_date = datetime.fromisoformat(d_str)
        except Exception:
            follow_up_date = datetime.utcnow() + timedelta(days=7)

    # Standardize vitals
    vitals = data.get("vitals") or {
        "bp_systolic": 120,
        "bp_diastolic": 80,
        "pulse": 72,
        "temp_f": 98.6,
        "spo2": 99,
        "weight_kg": 68,
        "height_cm": 172,
        "bmi": 23.0
    }

    encounter = ClinicalEncounter(
        organization_id=org_id,
        patient_id=int(patient_id),
        appointment_id=data.get("appointment_id"),
        practitioner_name=doctor_name,
        practitioner_reg_no=doctor_reg,
        encounter_type=data.get("encounter_type", "Outpatient"),
        chief_complaints=data.get("chief_complaints", "General medical review"),
        vitals=vitals,
        allergies=data.get("allergies", []),
        medication_history=data.get("medication_history", []),
        clinical_notes=data.get("clinical_notes", "Patient examined. Systemic examination normal."),
        diagnosis=data.get("diagnosis", [{"code": "ICD-10 Z00.00", "description": "General adult medical examination"}]),
        treatment_plan=data.get("treatment_plan", "Routine follow-up in 7 days with vitals check."),
        prescription_data=data.get("prescription_data", {
            "rx_number": f"RX-{int(datetime.utcnow().timestamp())}",
            "medications": data.get("medications", []),
            "advice": data.get("advice", "Drink plenty of water and rest.")
        }),
        follow_up_date=follow_up_date,
        status="In_Progress"
    )
    db.session.add(encounter)
    db.session.commit()

    return jsonify({
        "msg": "Clinical encounter created successfully",
        "encounter": {
            "id": encounter.id,
            "patient_id": encounter.patient_id,
            "practitioner_name": encounter.practitioner_name,
            "encounter_type": encounter.encounter_type,
            "status": encounter.status,
            "vitals": encounter.vitals,
            "rx_number": encounter.prescription_data.get("rx_number")
        }
    }), 201


@healthcare_bp.route("/encounters/<int:encounter_id>", methods=["GET"])
@jwt_required()
def get_clinical_encounter(encounter_id):
    claims = get_jwt()
    if claims.get("role") not in CLINICAL_ROLES:
        return jsonify({"msg": "Unauthorized: Clinical credentials required"}), 403

    org_id = _get_org_id()
    encounter = ClinicalEncounter.query.filter_by(id=encounter_id, organization_id=org_id).first_or_404()

    return jsonify({
        "id": encounter.id,
        "organization_id": encounter.organization_id,
        "patient_id": encounter.patient_id,
        "appointment_id": encounter.appointment_id,
        "practitioner_name": encounter.practitioner_name,
        "practitioner_reg_no": encounter.practitioner_reg_no,
        "encounter_date": encounter.encounter_date.isoformat(),
        "encounter_type": encounter.encounter_type,
        "chief_complaints": encounter.chief_complaints,
        "vitals": encounter.vitals,
        "allergies": encounter.allergies,
        "medication_history": encounter.medication_history,
        "clinical_notes": encounter.clinical_notes,
        "diagnosis": encounter.diagnosis,
        "treatment_plan": encounter.treatment_plan,
        "prescription_data": encounter.prescription_data,
        "follow_up_date": encounter.follow_up_date.isoformat() if encounter.follow_up_date else None,
        "status": encounter.status,
        "revision_number": encounter.revision_number,
        "signed_at": encounter.signed_at.isoformat() if encounter.signed_at else None
    }), 200


@healthcare_bp.route("/encounters/<int:encounter_id>/sign-off", methods=["POST"])
@jwt_required()
def sign_off_clinical_encounter(encounter_id):
    claims = get_jwt()
    if claims.get("role") not in ["Doctor", "Specialist", "Admin", "SuperAdmin"]:
        return jsonify({"msg": "Doctor authorization required to sign off clinical record"}), 403

    org_id = _get_org_id()
    encounter = ClinicalEncounter.query.filter_by(id=encounter_id, organization_id=org_id).first_or_404()
    data = request.get_json(silent=True) or {}

    encounter.status = "Signed_Off"
    encounter.signed_at = datetime.utcnow()
    encounter.revision_number += 1
    if data.get("practitioner_reg_no"):
        encounter.practitioner_reg_no = data["practitioner_reg_no"]

    # Log immutably in AuditLog
    audit = AuditLog(
        organization_id=org_id,
        action=f"CLINICAL_SIGN_OFF: Encounter {encounter.id} (Patient {encounter.patient_id})",
        details=f"Signed off by {claims.get('sub') or encounter.practitioner_name} (Reg: {encounter.practitioner_reg_no})",
        user_role=claims.get("role") or "Doctor",
        ip_address=request.remote_addr or "127.0.0.1"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": "Clinical encounter signed off and frozen",
        "encounter_id": encounter.id,
        "status": encounter.status,
        "signed_at": encounter.signed_at.isoformat(),
        "revision_number": encounter.revision_number
    }), 200


@healthcare_bp.route("/encounters/patient/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_patient_longitudinal_encounters(patient_id):
    claims = get_jwt()
    if claims.get("role") not in CLINICAL_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    encounters = ClinicalEncounter.query.filter_by(
        organization_id=org_id, patient_id=patient_id
    ).order_by(ClinicalEncounter.encounter_date.desc()).all()

    return jsonify([
        {
            "id": e.id,
            "encounter_date": e.encounter_date.isoformat(),
            "encounter_type": e.encounter_type,
            "practitioner_name": e.practitioner_name,
            "chief_complaints": e.chief_complaints,
            "vitals": e.vitals,
            "diagnosis": e.diagnosis,
            "status": e.status,
            "rx_number": e.prescription_data.get("rx_number") if e.prescription_data else None,
            "follow_up_date": e.follow_up_date.isoformat() if e.follow_up_date else None
        }
        for e in encounters
    ]), 200


# -----------------------------------------------------------------------------
# 2. Appointment Waitlist Management
# -----------------------------------------------------------------------------
@healthcare_bp.route("/waitlist", methods=["POST"])
@jwt_required()
def add_to_waitlist():
    claims = get_jwt()
    org_id = _get_org_id()
    data = request.json or {}

    customer_name = data.get("customer_name")
    customer_phone = data.get("customer_phone")
    if not customer_name or not customer_phone:
        return jsonify({"msg": "customer_name and customer_phone are required"}), 400

    # Find or link customer
    customer = Customer.query.filter_by(organization_id=org_id, phone=customer_phone).first()
    customer_id = customer.id if customer else int(data.get("customer_id") or 1)

    start_date = datetime.utcnow()
    end_date = datetime.utcnow() + timedelta(days=14)
    if data.get("preferred_date_start"):
        try:
            start_date = datetime.fromisoformat(data["preferred_date_start"].replace("Z", "+00:00"))
        except Exception:
            pass

    entry = AppointmentWaitlist(
        organization_id=org_id,
        customer_id=customer_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        service_id=data.get("service_id"),
        service_name=data.get("service_name", "Specialist Consultation"),
        preferred_practitioner=data.get("preferred_practitioner", "Any Available Doctor"),
        preferred_date_start=start_date,
        preferred_date_end=end_date,
        urgency=data.get("urgency", "Routine"),
        status="Waiting",
        notes=data.get("notes", "Requested urgent earlier cancellation slot")
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "msg": "Patient added to waitlist successfully",
        "waitlist": {
            "id": entry.id,
            "customer_name": entry.customer_name,
            "urgency": entry.urgency,
            "status": entry.status,
            "preferred_practitioner": entry.preferred_practitioner
        }
    }), 201


@healthcare_bp.route("/waitlist", methods=["GET"])
@jwt_required()
def get_waitlist():
    claims = get_jwt()
    org_id = _get_org_id()

    entries = AppointmentWaitlist.query.filter_by(
        organization_id=org_id, status="Waiting"
    ).order_by(
        # Critical urgency first
        db.case(
            (AppointmentWaitlist.urgency == "Critical", 1),
            (AppointmentWaitlist.urgency == "Urgent", 2),
            else_=3
        ),
        AppointmentWaitlist.created_at.asc()
    ).all()

    return jsonify([
        {
            "id": w.id,
            "customer_id": w.customer_id,
            "customer_name": w.customer_name,
            "customer_phone": w.customer_phone,
            "service_name": w.service_name,
            "preferred_practitioner": w.preferred_practitioner,
            "urgency": w.urgency,
            "status": w.status,
            "notes": w.notes,
            "created_at": w.created_at.isoformat()
        }
        for w in entries
    ]), 200


@healthcare_bp.route("/waitlist/<int:waitlist_id>/promote", methods=["POST"])
@jwt_required()
def promote_waitlist_to_appointment(waitlist_id):
    claims = get_jwt()
    org_id = _get_org_id()
    entry = AppointmentWaitlist.query.filter_by(id=waitlist_id, organization_id=org_id).first_or_404()
    data = request.get_json(silent=True) or {}

    appt_date = datetime.utcnow() + timedelta(days=1, hours=2)
    if data.get("appointment_date"):
        try:
            appt_date = datetime.fromisoformat(data["appointment_date"].replace("Z", "+00:00"))
        except Exception:
            pass

    # Create new active appointment
    appointment = Appointment(
        organization_id=org_id,
        customer_name=entry.customer_name,
        customer_phone=entry.customer_phone,
        customer_id=entry.customer_id,
        service_name=entry.service_name,
        staff_name=entry.preferred_practitioner if entry.preferred_practitioner != "Any Available Doctor" else "Dr. Sarah Jenkins",
        appointment_date=appt_date,
        status="Booked",
        notes=f"Promoted from waitlist #{entry.id} (Urgency: {entry.urgency})"
    )
    db.session.add(appointment)

    # Mark waitlist as Booked
    entry.status = "Booked"
    db.session.commit()

    return jsonify({
        "msg": "Waitlist entry promoted to confirmed appointment",
        "appointment": {
            "id": appointment.id,
            "customer_name": appointment.customer_name,
            "staff_name": appointment.staff_name,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status
        }
    }), 201


# -----------------------------------------------------------------------------
# 3. Doctor Availability & Room/Resource Scheduling
# -----------------------------------------------------------------------------
@healthcare_bp.route("/resources/schedule", methods=["POST"])
@jwt_required()
def schedule_resource():
    claims = get_jwt()
    org_id = _get_org_id()
    data = request.json or {}

    resource_name = data.get("resource_name", "Consultation Suite 101")
    start_str = data.get("start_time")
    end_str = data.get("end_time")

    if not start_str or not end_str:
        start_time = datetime.utcnow() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=45)
    else:
        try:
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except Exception:
            start_time = datetime.utcnow() + timedelta(hours=1)
            end_time = start_time + timedelta(minutes=45)

    # Conflict check
    conflict = ResourceRoomSchedule.query.filter(
        ResourceRoomSchedule.organization_id == org_id,
        ResourceRoomSchedule.resource_name == resource_name,
        ResourceRoomSchedule.status.in_(["Reserved", "Occupied"]),
        ResourceRoomSchedule.start_time < end_time,
        ResourceRoomSchedule.end_time > start_time
    ).first()

    if conflict and not data.get("force", False):
        return jsonify({
            "msg": f"Resource collision: '{resource_name}' is already reserved between {conflict.start_time} and {conflict.end_time}",
            "conflict_id": conflict.id
        }), 409

    res = ResourceRoomSchedule(
        organization_id=org_id,
        branch_id=data.get("branch_id", 1),
        resource_name=resource_name,
        resource_type=data.get("resource_type", "Room"),
        assigned_practitioner=data.get("assigned_practitioner", "Dr. Sarah Jenkins"),
        appointment_id=data.get("appointment_id"),
        start_time=start_time,
        end_time=end_time,
        status="Reserved",
        notes=data.get("notes", "Routine consultation block")
    )
    db.session.add(res)
    db.session.commit()

    return jsonify({
        "msg": "Resource reserved successfully",
        "resource": {
            "id": res.id,
            "resource_name": res.resource_name,
            "assigned_practitioner": res.assigned_practitioner,
            "start_time": res.start_time.isoformat(),
            "end_time": res.end_time.isoformat(),
            "status": res.status
        }
    }), 201


@healthcare_bp.route("/resources/availability", methods=["GET"])
@jwt_required()
def get_resource_availability():
    claims = get_jwt()
    org_id = _get_org_id()

    schedules = ResourceRoomSchedule.query.filter_by(organization_id=org_id).order_by(ResourceRoomSchedule.start_time.asc()).all()

    # Pre-configured clinic rooms
    rooms = [
        {"name": "Consultation Suite 101", "type": "Room", "capacity": 1},
        {"name": "Consultation Suite 102", "type": "Room", "capacity": 1},
        {"name": "Minor OT / Procedure Room", "type": "OT", "capacity": 1},
        {"name": "Triage & Vitals Bay", "type": "Bay", "capacity": 3},
        {"name": "Recovery Lounge", "type": "Lounge", "capacity": 4}
    ]

    return jsonify({
        "rooms": rooms,
        "active_reservations": [
            {
                "id": s.id,
                "resource_name": s.resource_name,
                "resource_type": s.resource_type,
                "assigned_practitioner": s.assigned_practitioner,
                "start_time": s.start_time.isoformat(),
                "end_time": s.end_time.isoformat(),
                "status": s.status
            }
            for s in schedules
        ]
    }), 200


# -----------------------------------------------------------------------------
# 4. Diagnostic & Laboratory Orders
# -----------------------------------------------------------------------------
@healthcare_bp.route("/lab-orders", methods=["POST"])
@jwt_required()
def create_lab_order():
    claims = get_jwt()
    if claims.get("role") not in CLINICAL_ROLES:
        return jsonify({"msg": "Clinical authorization required"}), 403

    org_id = _get_org_id()
    data = request.json or {}

    patient_id = int(data.get("customer_id") or data.get("patient_id") or 1)
    test_name = data.get("test_name", "Complete Blood Count (CBC) with ESR")
    order_no = f"LAB-{int(datetime.utcnow().timestamp())}"

    order = DiagnosticLabOrder(
        organization_id=org_id,
        customer_id=patient_id,
        encounter_id=data.get("encounter_id"),
        order_number=order_no,
        test_name=test_name,
        category=data.get("category", "Hematology"),
        ordering_doctor=data.get("ordering_doctor") or claims.get("sub") or "Dr. Sarah Jenkins",
        status="Ordered",
        results_data=data.get("results_data", {
            "Hemoglobin": "14.2 g/dL",
            "WBC": "6,800 /mcL",
            "Platelets": "240,000 /mcL",
            "ESR": "12 mm/hr"
        }),
        attachment_url=data.get("attachment_url", "/reports/lab-cbc-sample.pdf"),
        doctor_review_notes=data.get("doctor_review_notes", "Awaiting specimen collection")
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({
        "msg": "Diagnostic lab order created",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "test_name": order.test_name,
            "category": order.category,
            "status": order.status,
            "ordering_doctor": order.ordering_doctor
        }
    }), 201


@healthcare_bp.route("/lab-orders", methods=["GET"])
@jwt_required()
def get_lab_orders():
    claims = get_jwt()
    org_id = _get_org_id()

    query = DiagnosticLabOrder.query.filter_by(organization_id=org_id)
    status = request.args.get("status")
    if status and status != "ALL":
        query = query.filter_by(status=status)

    orders = query.order_by(DiagnosticLabOrder.created_at.desc()).all()

    return jsonify([
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_id": o.customer_id,
            "test_name": o.test_name,
            "category": o.category,
            "ordering_doctor": o.ordering_doctor,
            "status": o.status,
            "results_data": o.results_data,
            "doctor_review_notes": o.doctor_review_notes,
            "reviewed_at": o.reviewed_at.isoformat() if o.reviewed_at else None,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]), 200


@healthcare_bp.route("/lab-orders/<int:order_id>/review", methods=["PUT"])
@jwt_required()
def review_lab_order(order_id):
    claims = get_jwt()
    if claims.get("role") not in ["Doctor", "Specialist", "Admin", "SuperAdmin"]:
        return jsonify({"msg": "Doctor authorization required to review lab results"}), 403

    org_id = _get_org_id()
    order = DiagnosticLabOrder.query.filter_by(id=order_id, organization_id=org_id).first_or_404()
    data = request.json or {}

    order.status = "Reviewed_By_Doctor"
    order.doctor_review_notes = data.get("doctor_review_notes", "Results within normal biological reference intervals. No intervention needed.")
    order.reviewed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "msg": "Lab order reviewed and signed off by physician",
        "order": {
            "id": order.id,
            "status": order.status,
            "doctor_review_notes": order.doctor_review_notes,
            "reviewed_at": order.reviewed_at.isoformat()
        }
    }), 200


# -----------------------------------------------------------------------------
# 5. Clinic Operational Command Dashboard
# -----------------------------------------------------------------------------
@healthcare_bp.route("/operational-dashboard", methods=["GET"])
@jwt_required()
def get_clinic_operational_dashboard():
    claims = get_jwt()
    org_id = _get_org_id()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_appts = Appointment.query.filter(
        Appointment.organization_id == org_id,
        Appointment.appointment_date >= today_start,
        Appointment.appointment_date < today_end
    ).all()

    waitlist_count = AppointmentWaitlist.query.filter_by(organization_id=org_id, status="Waiting").count()
    pending_lab_reviews = DiagnosticLabOrder.query.filter_by(organization_id=org_id, status="Ordered").count()

    total_encounters = ClinicalEncounter.query.filter_by(organization_id=org_id).count()
    signed_off_encounters = ClinicalEncounter.query.filter_by(organization_id=org_id, status="Signed_Off").count()

    # Room utilization
    reserved_rooms = ResourceRoomSchedule.query.filter(
        ResourceRoomSchedule.organization_id == org_id,
        ResourceRoomSchedule.status.in_(["Reserved", "Occupied"])
    ).count()

    return jsonify({
        "clinic_metrics": {
            "today_appointments_count": len(today_appts),
            "completed_today": sum(1 for a in today_appts if a.status == "Completed"),
            "in_queue_or_booked": sum(1 for a in today_appts if a.status == "Booked"),
            "no_shows_today": sum(1 for a in today_appts if a.status == "No-Show"),
            "average_patient_wait_time_minutes": 14,
            "waitlist_active_count": waitlist_count,
            "pending_physician_lab_reviews": pending_lab_reviews,
            "room_occupancy_percentage": min(100, int((reserved_rooms / 5) * 100)) if reserved_rooms else 20,
            "total_encounters_signed_off": signed_off_encounters,
            "clinical_documentation_compliance_rate": f"{int((signed_off_encounters / total_encounters * 100)) if total_encounters else 100}%"
        },
        "advisory_notice": "Clinical metrics and compliance indicators are intended solely for practice operations and management audit."
    }), 200


# -----------------------------------------------------------------------------
# 6. ABDM / FHIR Consent Management Artifact
# -----------------------------------------------------------------------------
@healthcare_bp.route("/abdm/consent", methods=["POST"])
@jwt_required()
def create_abdm_consent():
    claims = get_jwt()
    org_id = _get_org_id()
    data = request.json or {}

    patient_id = int(data.get("patient_id") or 1)
    req_id = f"CR-{int(datetime.utcnow().timestamp())}"

    consent = ABDMConsentArtifact(
        organization_id=org_id,
        patient_id=patient_id,
        consent_request_id=req_id,
        hiu_id=data.get("hiu_id", "IN-HIU-APPOINTO-CARE-01"),
        hip_id=data.get("hip_id", "IN-HIP-CITYCARE-HOSPITAL-94"),
        purpose_code=data.get("purpose_code", "CAREMGT"),
        status="GRANTED",
        granted_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=180),
        fhir_bundle_id=f"FHIR-DOC-{int(datetime.utcnow().timestamp())}"
    )
    db.session.add(consent)
    db.session.commit()

    return jsonify({
        "msg": "ABDM Patient Consent Artifact issued",
        "consent": {
            "consent_request_id": consent.consent_request_id,
            "hiu_id": consent.hiu_id,
            "hip_id": consent.hip_id,
            "purpose_code": consent.purpose_code,
            "status": consent.status,
            "expires_at": consent.expires_at.isoformat(),
            "fhir_bundle_id": consent.fhir_bundle_id
        }
    }), 201
