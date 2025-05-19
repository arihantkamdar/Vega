from pydantic import BaseModel
from typing import Optional
from typing import Optional, List, Literal
from sqlalchemy import Column, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



# Pydantic Models not DB Models
class Questionnaire(BaseModel):
    questionnaire_id: str
    investor_name: Optional[str]
    investor_type: Optional[str]
    investor_address: Optional[str]
    investment_amount: Optional[float]
    is_accredited_investor: Optional[bool]
    accreditation_details: Optional[str]
    source_of_funds_description: Optional[str]
    tax_id_provided: Optional[bool]
    signature_present: Optional[bool]
    submission_date: str


class QuestionnaireDecision(BaseModel):
    questionnaire_id: str
    decision: Literal["Approve", "Return", "Escalate", "Human Input"]
    missing_fields: Optional[List[str]] = None
    escalation_reason: Optional[str] = None









# DB Models start here


class QuestionnaireDB(Base):
    __tablename__ = "questionnaires"

    questionnaire_id = Column(String, primary_key=True)
    investor_name = Column(String, nullable=True)
    investor_type = Column(String, nullable=True)
    investor_address = Column(String, nullable=True)
    investment_amount = Column(Float, nullable=True)
    is_accredited_investor = Column(Boolean, nullable=True)
    accreditation_details = Column(Text, nullable=True)
    source_of_funds_description = Column(Text, nullable=True)
    tax_id_provided = Column(Boolean, nullable=True)
    signature_present = Column(Boolean, nullable=True)
    submission_date = Column(String)

    decision = relationship("QuestionnaireDecisionDB", back_populates="questionnaire", uselist=False, cascade="all, delete-orphan")


class QuestionnaireDecisionDB(Base):
    __tablename__ = "decisions"

    questionnaire_id = Column(String, ForeignKey("questionnaires.questionnaire_id"), primary_key=True)
    decision = Column(String, nullable=True)
    missing_fields = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    human_input = Column(String, nullable=True)
    

    questionnaire = relationship("QuestionnaireDB", back_populates="decision")
