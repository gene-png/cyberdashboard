import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Assessment, AdminScore, AuditLog, GapFinding
from ..services.framework_loader import load_framework
from ..services.excel_service import build_customer_excel, build_consultant_excel
from ..services.report_generator import generate_findings, regenerate_finding
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
    assessment.status = "finalized"
    assessment.finalized_at = datetime.now(timezone.utc)
    log = AuditLog(
        assessment_id=assessment_id,
        user_id=current_user.id,
        action="finalize",
        target_type="assessment",
        target_id=assessment_id,
    )
    db.session.add(log)
    db.session.commit()
    flash("Assessment finalized.", "success")
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
