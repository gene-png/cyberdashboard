import uuid
from ..extensions import db


class ToolInventory(db.Model):
    __tablename__ = "tool_inventory"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = db.Column(db.String(36), db.ForeignKey("assessment.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    vendor = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    assessment = db.relationship("Assessment", back_populates="tool_inventory")

    def __repr__(self):
        return f"<ToolInventory {self.name}>"
