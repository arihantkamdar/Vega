from models import Questionnaire
import re
from datetime import datetime
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def basic_checks(data: Questionnaire):
    """
    Here we would be checking if the fiels that should be present always are present or not.
    These Fields include:
    0. Questionaire_id, 
    1. investor_name
    2. investor_address,
    3. investment_amount
    4. Investor_type,
    5. is_accredated, (if not present: we return, if present but false: we escalate)
    6. tax_ID_check, ((if not present: we return, if present but false: we return))
    7. Signature_check, (if not present, we retutn, if false we return)
    8. Submission Date, (check on the basis that wether the date is valie(it should not be 30th of Feb) and escalate)

    """
    return_flag = False
    return_details = []
    escalation_flag = False
    escalation_details = []
    mandatory_checks = {
        "Missing Flag" : False,
        "Missing Details" : [],
        "Escalate Flag" : False,
        "Escalate Details" : []
    }
    
    # string input checks first i.e all the fields other than amount and bools
    string_missing_fields_return = ["questionnaire_id", "investor_name", "investor_type", "investor_address"]
    for field in string_missing_fields_return:
        value = getattr(data, field)
        if value is None:
            return_flag = True
            return_details.append(f"{field}")
        elif isinstance(value, str) and not value.strip():
            return_flag = True
            return_details.append(f"{field}")
        elif not isinstance(value,str):
            return_flag = True
            return_details.append(f"{field}")

    numeric_fields = ["investment_amount"]
    for field in numeric_fields:
        value = getattr(data, field)
        if value is None:
            return_flag = True
            return_details.append(f"{field}")
        if isinstance(value, int) or isinstance(value, float):
            if value<0:
                escalation_flag = True
                escalation_details.append(f"{field} is negative") # since there is just investment amount, we could have it in a loop
                # however, we have to modify if more numeric values come 
            else:
                pass

    date_field = ["submission_date"]
    for field in date_field:
        value = getattr(data, field)
        if value is None:
            return_flag = True
            return_details.append(f"{field}")
        else:
            try:
                datetime.strptime(data.submission_date, "%Y-%m-%d") 
            except ValueError:
                escalation_flag = True
                escalation_details.append(f"{field} is not in right format")


    boolean_missing_fields_return = ["is_accredited_investor", "tax_id_provided", "signature_present"]
    for field in boolean_missing_fields_return:
        value = getattr(data, field)
        if value is None:
            return_flag = True
            return_details.append(f"{field}")
        elif isinstance(value, bool):
            if field == "is_accredited_investor":
                if value == False:
                    escalation_flag = True
                    escalation_details.append("is_accredited_investor is False")
            else:
                if value == False:
                    return_flag = True
                    return_details.append(f"{field}")
        elif not isinstance(value,bool):
            return_flag = True
            return_details.append(f"{field}")



    mandatory_checks = {
        "Missing Flag" : return_flag,
        "Missing Details" : ",".join(return_details),
        "Escalate Flag" : escalation_flag,
        "Escalate Details" : ".".join(escalation_details)
    }

    return mandatory_checks

    


def check_text_data(data: Questionnaire):
    escaltion_flag = False
    escaltion_details = []
    acrredatitaions_patterns = re.compile(
         r"\b("
    r"suspended|revoked|expired|pending|under investigation(s)?|non-compliant|fraud(s)?|"
    r"disqualified|probation(s)?|limited|restricted|temporar(y|ies)|conditional|revocation(s)?|"
    r"sanctioned|blacklisted|aml|kyc|violation(s)?|breach(es)?|penalt(y|ies)|fined|lawsuit(s)?|litigation(s)?|"
    r"legal action(s)?|non-verified|unverified|lack of certification(s)?|missing documentation(s)?|"
    r"bankrupt(cy|cies)|insolvent|default(s)?|debt(s)?|financial instabilit(y|ies)|risk(s)?|high risk(s)?|suspicious|"
    r"untrustworthy|questionable|disputed|self-certified|non-accredited|unrecognized|"
    r"not approved|not registered|fake|counterfeit(s)?|subject to ongoing review(s)?|"
    r"awaiting approval(s)?|temporary authorization(s)?|conditional acceptance(s)?|limited scope(s)?|"
    r"discontinued|under sanction(s)?|pending verification(s)?"
    r")\b", 
        flags=re.IGNORECASE
    )
    source_of_funds_pattern = re.compile(
    r"\b("
    r"cash(es)?|cryptocurrenc(y|ies)|bitcoin(s)?|lotter(y|ies)|inheritance(s)?|gambl(ing|ings)|illegal|unreported|"
    r"offshore(s)?|shell compan(y|ies)|anonymous|untraceable|smuggling(s)?|drug trade(s)?|"
    r"tax evasion(s)?|money laundering(s)?|embezzlement(s)?|briber(y|ies)|fraudulent|high risk(s)?|"
    r"suspicious|unverified source(s)?|black market(s)?|counterfeit(s)?|hawala(s)?|"
    r"fake document(s)?|undisclosed|kickbacks?|unlawful|"
    r"unexplained wealth(s)?|unusual transaction(s)?|rapid movement(s)?|"
    r"complex structure(s)?|third party payment(s)?|cash intensive|family contribution(s)?"
    r")\b",
    flags=re.IGNORECASE
)

    # Example usage:
    acrredatitaions_fields = ["accreditation_details"]
    for field in acrredatitaions_fields:
        value = getattr(data, field)
        if value is None:
            escaltion_flag = True
            escaltion_details.append(f"{field} is empty")
        elif isinstance(value, str) and not value.strip():
            escaltion_flag = True
            escaltion_details.append(f"{field} is empty")
        elif acrredatitaions_patterns.search(value):
            escaltion_flag = True
            escaltion_details.append("Accreditations are ambiguious or suspicious")

    

    # Example usage:
    acrredatitaions_fields = ["source_of_funds_description"]
    for field in acrredatitaions_fields:
        value = getattr(data, field)
        if value is None:
            escaltion_flag = True
            escaltion_details.append(f"{field} is empty")
        elif isinstance(value, str) and not value.strip():
            escaltion_flag = True
            escaltion_details.append(f"{field} is empty")
        elif source_of_funds_pattern.search(value):
            escaltion_flag = True
            escaltion_details.append("Source of funds are ambiguious or suspicious")

    return {
        "escalation_flag" : escaltion_flag,
        "escalation_details" : ",".join(escaltion_details)
    }



def check_text_data_llm(acc_text, fund_text):
    # text = data.source_of_funds_description
    escaltion_flag = False
    escaltion_details = []
    labels_for_accreditation = ["valid accreditation of investor", "ambiguious accreditation", "not valid accreditation details"]
    labels_for_funds = ["valid legitimate source", "unknown or illegitimate sources", "ambiguous"]
    
    result = classifier(acc_text, candidate_labels=labels_for_accreditation)
    acc_labels = result["labels"][0]
    if acc_labels != "valid accreditation of investor":
        escaltion_flag = True
        escaltion_details.append("Accreditations are ambiguious or suspicious")
    
    result = classifier(fund_text, candidate_labels=labels_for_funds)
    fund_label = result["labels"][0]
    if fund_label != "valid legitimate source":
        escaltion_flag = True
        escaltion_details.append("Source of funds are ambiguious or suspicious")
    return {
        "escalation_flag" : escaltion_flag,
        "escalation_details" : ".".join(escaltion_details)
    }
    
    
test_data = Questionnaire(questionnaire_id= "1a59843c-9ade-4b6d-8961-215c44c9ca6a", investor_name = "Mr and Mrs Simpson",
                        investor_type = "Joint Tenants", investor_address = "25, Springfield, New Jersey, United States",
                        investment_amount = 250000, is_accredited_investor = True,
                        accreditation_details = "Joint Income over $300k for past two years with expectation to continue.",
                        source_of_funds_description = "Various sources including bblack market.",
                        tax_id_provided = True, signature_present = True, submission_date = "2025-04-30")

# print(basic_checks(test_data))
# print(check_text_data(test_data))
