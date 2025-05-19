from sqlalchemy.orm import Session
from models import QuestionnaireDB, QuestionnaireDecisionDB

def insert_questionnaire(db: Session, q_data: QuestionnaireDB, d_data: QuestionnaireDecisionDB):
    db.add(q_data)
    db.add(d_data)
    db.commit()

