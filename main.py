from fastapi import FastAPI, Form, Request
from mandatory_checks import basic_checks,check_text_data
from models import Questionnaire,QuestionnaireDecision
from database import SessionLocal, engine
from models import Base, QuestionnaireDB, QuestionnaireDecisionDB
import crud
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils import runner, decision_dict_to_sqlalchemy, pydantic_to_sqlalchemy_questionnaire

app = FastAPI()
db = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)



@app.post("/submit_regex")
async def submit_questionnaire_regex(request_data: list[Questionnaire]):
    response = []
    for data in request_data:
        questionnaire_id = data.questionnaire_id
        questionnaire_db = db.query(QuestionnaireDB).filter_by(questionnaire_id=questionnaire_id).first()
        if questionnaire_db is not None:
            return {"msg" : f"Questionnaire ID {questionnaire_id} exist already"}

        resp = runner(data, regex= True) 
        response.append(resp)
        crud.insert_questionnaire(db, 
                                  q_data=pydantic_to_sqlalchemy_questionnaire(data),
                                  d_data=decision_dict_to_sqlalchemy(resp))

    return response


@app.post("/submit_llm")
async def submit_questionnaire_llm(request_data: list[Questionnaire]):
    response = []
    for data in request_data:
        questionnaire_id = data.questionnaire_id
        questionnaire_db = db.query(QuestionnaireDB).filter_by(questionnaire_id=questionnaire_id).first()
        if questionnaire_db is not None:
            return {"msg" : f"Questionnaire ID {questionnaire_id} exist already"}
        resp = runner(data, regex= False) 
        response.append(resp)
        crud.insert_questionnaire(db, 
                                  q_data=pydantic_to_sqlalchemy_questionnaire(data),
                                  d_data=decision_dict_to_sqlalchemy(resp))

    return response


@app.get("/questionnaire/{questionnaire_id}")
async def get_questionnaire(questionnaire_id: str, db: Session = Depends(get_db)):
    questionnaire = db.query(QuestionnaireDB).filter_by(questionnaire_id=questionnaire_id).first()
    decision = db.query(QuestionnaireDecisionDB).filter_by(questionnaire_id=questionnaire_id).first()

    if not questionnaire:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    return {
        "questionnaire": questionnaire,
        "decision": decision
    }



@app.post("/addhumaninput/{questionnaire_id}")
async def update_human_input_form(questionnaire_id: str, new_input: str = Form(...), db: Session = Depends(get_db)):
    decision_row = db.query(QuestionnaireDecisionDB).filter_by(questionnaire_id=questionnaire_id).first()
    if not decision_row:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision_row.human_input = new_input
    db.commit()
    db.refresh(decision_row)
    
    return {
        "message": "Human input updated",
        "questionnaire_id": decision_row.questionnaire_id,
        "updated_input": decision_row.human_input
    }
