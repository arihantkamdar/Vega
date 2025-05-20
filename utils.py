from fastapi import FastAPI, Request
from mandatory_checks import basic_checks,check_text_data, check_text_data_llm
from models import Questionnaire,QuestionnaireDecision
from database import SessionLocal, engine
from models import Base, QuestionnaireDB, QuestionnaireDecisionDB
import crud
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session




def pydantic_to_sqlalchemy_questionnaire(q: Questionnaire) -> QuestionnaireDB:
    # converts pydanty to DB so we can store ir

    return QuestionnaireDB(**q.dict())



def decision_dict_to_sqlalchemy(decision_data: dict) -> QuestionnaireDecisionDB:
    # Convert missing_fields list to comma-separated string if present
    # converts pydanty to DB so we can store ir
    missing_fields = decision_data.get("missing_fields")
    if isinstance(missing_fields, list):
        decision_data["missing_fields"] = ",".join(missing_fields)
    return QuestionnaireDecisionDB(**decision_data)



def runner(data: Questionnaire, regex = True):
    result = {
            "questionnaire_id": data.questionnaire_id,
            "decision": "Approve",
            "missing_fields": "",
            "escalation_reason": ""}
    # runs basic check i.e missing field or invalid fields
    basic_checks_result = basic_checks(data=data)

    if basic_checks_result['Missing Flag']:
        result["decision"] = "Return"
        result['missing_fields'] += basic_checks_result['Missing Details'] + " , "
    elif basic_checks_result['Escalate Flag']:
        result["decision"] = "Escalate"
        result['escalation_reason'] += basic_checks_result['Escalate Details'] + " , "
    
    if regex:        
        # test for text field if it has ambuiguty using regex
        text_check = check_text_data(data=data)
        if text_check['escalation_flag']:
            if result['decision'] != "Return":
                result["decision"] = "Escalate"
                result['escalation_reason'] += text_check['escalation_details'] + " , "
    else:
        # test for text field ambiguity usign LLMs
        text_check = check_text_data_llm(acc_text= data.accreditation_details,
                                         fund_text= data.source_of_funds_description)
        if text_check['escalation_flag']:
            if result['decision'] != "Return":
                result["decision"] = "Escalate"
                result['escalation_reason'] +=  text_check['escalation_details'] + " , "
    return result

