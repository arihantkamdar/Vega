from sqlalchemy.orm import Session
from models import QuestionnaireDB, QuestionnaireDecisionDB

def insert_questionnaire(db: Session, q_data: QuestionnaireDB, d_data: QuestionnaireDecisionDB):
    """DB insert operation for both questionnair and decisions"""
    db.add(q_data)
    db.add(d_data)
    db.commit()

