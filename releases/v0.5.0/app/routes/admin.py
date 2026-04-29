import io
import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file, current_app
from flask_login import login_required, current_user
import bleach
from ..extensions import db, limiter
from ..models import Assessment, AdminScore, AuditLog, GapFinding, AICallLog, SensitiveTerm, User
from ..services.framework_loader import load_framework
from ..services.excel_service import build_customer_excel, build_consultant_excel
from ..services.report_generator import generate_findings, regenerate_finding
from ..services.sharepoint_service import get_client_from_config, upload_assessment_outputs
from .auth import is_admin_unlocked

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    if not is_admin_unlocked():
        return redirect(url_for("auth.admin_unlock", next=request.url))
    return None


@admin_bp.route("/assessments/<assessment_id>/review")
@login_required
def review(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    framework = load_framework(assessment.framework)
    responses = {r.activity_id: r for r in assessment.responses}
    admin_scores = {s.pillar: s for s in assessment.admin_scores}
    return render_template(
        "admin/review.html",
        assessment=assessment,
        framework=framework,
        responses=responses,
        admin_scores=admin_scores,
        admin_unlocked=True,
    )


@admin_bp.route("/assessments/<assessment_id>/score", methods=["POST"])
@login_required
def save_scores(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    framework = load_framework(assessment.framework)

    for pillar in framework["pillars"]:
        pid = pillar["id"]
        current_score = request.form.get(f"current_score_{pid}", type=float)
        target_score = request.form.get(f"target_score_{pid}", type=float)
        gap_summary = request.form.get(f"gap_summary_{pid}", "").strip()
        consultant_rec = request.form.get(f"consultant_recommendation_{pid}", "").strip()

        score = AdminScore.query.filter_by(assessment_id=assessment_id, pillar=pid).first()
        if score:
            score.current_score = current_score
            score.target_score = target_score
            score.gap_summary = gap_summary
            score.consultant_recommendation = consultant_rec
        else:
            score = AdminScore(
                assessment_id=assessment_id,
                pillar=pid,
                current_score=current_score,
                target_score=target_score,
                gap_summary=gap_summary,
                consultant_recommendation=consultant_rec,
            )
            db.session.add(score)

    db.session.commit()
    flash("Admin scores saved.", "success")
    return redirect(url_for("admin.review", assessment_id=assessment_id))


@admin_bp.route("/assessments/<assessment_id>/export/customer")
@login_required
def export_customer(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    xlsx_bytes = build_customer_excel(assessment)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{assessment.customer_org.replace(' ', '_')}_{date_str}_customer_report.xlsx"
    return send_file(
        io.BytesIO(xlsx_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@admin_bp.route("/assessments/<assessment_id>/export/consultant")
@login_required
def export_consultant(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    xlsx_bytes = build_consultant_excel(assessment)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{assessment.customer_org.replace(' ', '_')}_{date_str}_consultant_report.xlsx"
    return send_file(
        io.BytesIO(xlsx_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@admin_bp.route("/assessments/<assessment_id>/finalize", methods=["POST"])
@login_required
def finalize(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)

    now = datetime.now(timezone.utc)
    assessment.status = "finalized"
    assessment.finalized_at = now

    log = AuditLog(
        assessment_id=assessment_id,
        user_id=current_user.id,
        action="finalize",
        target_type="assessment",
        target_id=assessment_id,
    )
    db.session.add(log)
    db.session.commit()

    # Build Excel files
    customer_xlsx = build_customer_excel(assessment)
    consultant_xlsx = build_consultant_excel(assessment)

    # Build response snapshot JSON
    responses_snapshot = [
        {
            "activity_id": r.activity_id,
            "pillar": r.pillar,
            "current_state_value": r.current_state_value,
            "target_state_value": r.target_state_value,
            "evidence_notes": r.evidence_notes,
        }
        for r in assessment.responses
    ]

    # Build audit CSV rows
    ai_log_rows = [
        {
            "timestamp": str(l.timestamp),
            "model": l.model,
            "tokens_in": l.tokens_in,
            "tokens_out": l.tokens_out,
            "duration_ms": l.duration_ms,
            "request_body_scrubbed": l.request_body_scrubbed or "",
            "response_body_scrubbed": l.response_body_scrubbed or "",
        }
        for l in assessment.ai_call_logs
    ]
    audit_rows = [
        {
            "timestamp": str(l.timestamp),
            "user_id": l.user_id or "",
            "action": l.action,
            "target_type": l.target_type or "",
            "target_id": l.target_id or "",
            "before_value": l.before_value or "",
            "after_value": l.after_value or "",
        }
        for l in assessment.audit_logs
    ]

    # Upload to SharePoint (no-op if not configured)
    sp_client = get_client_from_config(current_app.config)
    if sp_client:
        try:
            upload_assessment_outputs(
                client=sp_client,
                assessment_id=assessment_id,
                org_name=assessment.customer_org,
                finalized_at=now,
                customer_xlsx=customer_xlsx,
                consultant_xlsx=consultant_xlsx,
                responses_json=json.dumps(responses_snapshot, indent=2),
                ai_call_log_rows=ai_log_rows,
                audit_log_rows=audit_rows,
            )
            flash("Assessment finalized and uploaded to SharePoint.", "success")
        except Exception as e:
            flash(f"Assessment finalized but SharePoint upload failed: {e}", "warning")
    else:
        flash("Assessment finalized. (SharePoint not configured — download exports manually.)", "success")

    return redirect(url_for("admin.review", assessment_id=assessment_id))


@admin_bp.route("/assessments/<assessment_id>/reopen", methods=["POST"])
@login_required
def reopen(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    assessment.status = "reopened"
    log = AuditLog(
        assessment_id=assessment_id,
        user_id=current_user.id,
        action="reopen",
        target_type="assessment",
        target_id=assessment_id,
    )
    db.session.add(log)
    db.session.commit()
    flash("Assessment reopened.", "success")
    return redirect(url_for("admin.review", assessment_id=assessment_id))


@admin_bp.route("/assessments/<assessment_id>/findings")
@login_required
def findings(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)
    framework = load_framework(assessment.framework)

    # Build activity lookup for display names
    activity_lookup: dict = {}
    pillar_name_lookup: dict = {}
    for pillar in framework["pillars"]:
        for activity in pillar["activities"]:
            activity_lookup[activity["id"]] = activity
            pillar_name_lookup[activity["id"]] = pillar["name"]

    gap_findings = (
        GapFinding.query
        .filter_by(assessment_id=assessment_id)
        .order_by(GapFinding.pillar, GapFinding.activity_id)
        .all()
    )
    return render_template(
        "admin/findings.html",
        assessment=assessment,
        framework=framework,
        gap_findings=gap_findings,
        activity_lookup=activity_lookup,
        pillar_name_lookup=pillar_name_lookup,
        admin_unlocked=True,
    )


@admin_bp.route("/assessments/<assessment_id>/generate", methods=["POST"])
@login_required
def generate(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)

    try:
        result = generate_findings(assessment_id, triggered_by_user_id=current_user.id)
        msg = f"AI findings generated: {result['generated']} gaps processed."
        if result["errors"]:
            msg += f" {len(result['errors'])} errors — check logs."
            flash(msg, "warning")
        else:
            flash(msg, "success")
    except Exception as e:
        flash(f"Generation failed: {e}", "danger")

    return redirect(url_for("admin.findings", assessment_id=assessment_id))


@admin_bp.route("/assessments/<assessment_id>/findings/<activity_id>/regenerate", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def regenerate(assessment_id, activity_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)

    try:
        regenerate_finding(assessment_id, activity_id, triggered_by_user_id=current_user.id)
        flash(f"Finding for {activity_id} regenerated.", "success")
    except Exception as e:
        flash(f"Regeneration failed: {e}", "danger")

    return redirect(url_for("admin.findings", assessment_id=assessment_id))


@admin_bp.route("/assessments/<assessment_id>/audit")
@login_required
def audit_log(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)

    logs = (
        AuditLog.query
        .filter_by(assessment_id=assessment_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    user_map = {u.id: u.username for u in User.query.all()}
    return render_template(
        "admin/audit.html",
        assessment=assessment,
        logs=logs,
        user_map=user_map,
        admin_unlocked=True,
    )


@admin_bp.route("/assessments/<assessment_id>/terms", methods=["GET", "POST"])
@login_required
def sensitive_terms(assessment_id):
    redir = _require_admin()
    if redir:
        return redir
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        abort(404)

    if request.method == "POST":
        action = request.form.get("action", "add")

        if action == "add":
            raw_term = request.form.get("term", "").strip()
            term = bleach.clean(raw_term, tags=[], strip=True)
            if term:
                # Generate a sequential token name
                existing_user_count = SensitiveTerm.query.filter_by(
                    assessment_id=assessment_id, source="user_added"
                ).count()
                token = f"[CUSTOM_{existing_user_count + 1}]"
                st = SensitiveTerm(
                    assessment_id=assessment_id,
                    term=term,
                    replacement_token=token,
                    source="user_added",
                    is_active=True,
                )
                db.session.add(st)
                log = AuditLog(
                    assessment_id=assessment_id,
                    user_id=current_user.id,
                    action="add_sensitive_term",
                    target_type="sensitive_term",
                    target_id=token,
                    after_value=term,
                )
                db.session.add(log)
                db.session.commit()
                flash(f"Term added and mapped to {token}.", "success")
            else:
                flash("Term cannot be empty.", "warning")

        elif action == "deactivate":
            term_id = request.form.get("term_id", "").strip()
            st = db.session.get(SensitiveTerm, term_id)
            if st and st.assessment_id == assessment_id:
                st.is_active = False
                log = AuditLog(
                    assessment_id=assessment_id,
                    user_id=current_user.id,
                    action="deactivate_sensitive_term",
                    target_type="sensitive_term",
                    target_id=st.replacement_token,
                    before_value=st.term,
                )
                db.session.add(log)
                db.session.commit()
                flash(f"Term '{st.term}' deactivated.", "success")
            else:
                flash("Term not found.", "warning")

        return redirect(url_for("admin.sensitive_terms", assessment_id=assessment_id))

    terms = (
        SensitiveTerm.query
        .filter_by(assessment_id=assessment_id)
        .order_by(SensitiveTerm.source, SensitiveTerm.term)
        .all()
    )
    return render_template(
        "admin/terms.html",
        assessment=assessment,
        terms=terms,
        admin_unlocked=True,
    )
