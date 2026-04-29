import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Assessment, AdminScore, AuditLog, GapFinding
from ..services.framework_loader import load_framework
from ..services.excel_service import build_customer_excel, build_consultant_excel
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
