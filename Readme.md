# 🧠 Questionnaire NLP Validator

A **FastAPI-based backend** that uses **NLP + domain rules** to validate and analyze free-text responses from financial questionnaires. It automates review of key fields like `source_of_funds_description` and `accreditation_details`, and returns a clear decision: ✅ **Approve**, ⚠️ **Return**, or 🔺 **Escalate**.

---

## ✨ Features

1. **FastAPI Interface**  
   Easy to run, test, and demonstrate—no messy terminal executions needed.

2. **Two Validation Modes**  
   - 🔍 **Regex-based rules**: Fast, transparent, but brittle.  
   - 🤖 **Zero-shot NLP (facebook/bart-large-mnli)**: More robust for free-text edge cases and ambiguity.

3. **Switchable Logic**  
   Use `/submit_regex` for rule-based or `/submit_llm` for model-based validation. Just change the endpoint.

4. **Postman Collection**  
   Included for quick testing. Fill in sample data and instantly receive classification responses.

5. **Persistent Database**  
   - Avoid reprocessing by checking `questionnaire_id`.  
   - Store past responses + human feedback for potential future retraining and improvements.

6. **Clear Precedence-Based Rules**  
   Logic is deterministic: Return > Escalate > Approve



---

## 🏗️ System Design Overview

### Core Logic

- **Precedence Order**:
- `Return` has highest priority, followed by `Escalate`, then `Approve`.

- **Return Conditions**:
- Missing required fields (e.g. `questionnaire_id`, `investor_name`, etc.)
- `investment_amount` ≤ 0 or null
- `tax_id_provided` or `signature_present` = False
- Invalid `submission_date` (e.g. 30th Feb)

- **Escalate Conditions**:
- `is_accredited_investor` = False
- `accreditation_details` or `source_of_funds_description` seem vague/ambiguous (via LLM or regex)

- **Approve**: Only when none of the above conditions apply.

### Tech Stack

- **Python 3.11+** (Tested on 3.13.3, Windows)
- **FastAPI** for serving endpoints
- **SQLite** for persistence
- **Transformers (HuggingFace)**: Zero-shot classification model
- **Pydantic** for validation

---

## 🧪 How to Run

> 💡 Recommended: Use a virtual environment

```bash
# 1. Clone repo and move in
git clone https://github.com/arihantkamdar/Vega.git
cd questionnaire-nlp-validator

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run FastAPI server
uvicorn main:app --reload


```
Now open http://localhost:8000/docs to test via Swagger UI.



📬 API Endpoints

0. Refer to collection.json with this repo, it has everything you need to run this.

1. POST /submit_regex
Rule-based analysis (fast, brittle)
![image](https://github.com/user-attachments/assets/a6727da2-c83f-4927-ad5f-37887d2bef45)

2. POST /submit_llm
NLP-based classification (slower, robust)
![image](https://github.com/user-attachments/assets/ed557252-04c4-4469-b8e8-9cb1319a51ae)

Payload (for both):
```json
[{
  "questionnaire_id": "abc123",
  "investor_name": "Jane Doe",
  "investor_type": "Natural Person",
  "investor_address": "123 Main St",
  "investment_amount": 50000,
  "is_accredited_investor": true,
  "accreditation_details": "Based on net worth over $1M",
  "source_of_funds_description": "Income from tech startup",
  "tax_id_provided": true,
  "signature_present": true,
  "submission_date": "2025-05-19"
},
{...}]
```

3. GET /get_questionnaire/<id>
Retrieve stored questionnaire + decision.
![image](https://github.com/user-attachments/assets/9f294c9c-803e-47ab-888a-840436eff381)



4. POST /addhumaninput/<id>
Add manual feedback. Body:

```json
{
  "new_input": "Manually reviewed, flagged for further KYC check"
}
```
![image](https://github.com/user-attachments/assets/ae0056ea-6249-406c-b384-cc583e79efc7)

## System Design: 

Pretty Simple: i used fast apis as not one likes to run code on terminal espcially a smiple one like this. For logic there are couple of rules I could interpret like:
1. Order of Precedence Return > Escalate > Approve (like if decious is both return and escale, we return. We only approve if not escalte and return is detetcted)
2. How I figured out the rules:
   1. questionnaire_id is always present, some fields like id, investor_name, investor_type, investor_address and amount should always be present. If not, return
   2. If is_accreditation is false -> Escalate, if None -> Return
   3. If signature_check and tax_id_check are False -> Return
   4. (Not from the description but common sense) If amount is 0 or less than 0 or null -> return
   5. if submission date is not valid like 30th of Feb -> Return
   6. If Accreditation details and source of funds are not convincing -> Escalate (this could be from regex or LLM)
  
3. I used FastAPi, as it is easy to develop and quite fast. LLm does not take more than 2 sec TAT(turn aroudn time), so i figured for small batches of data then its for the best, if not, we could use a batch processing pipeline.
4. I implemented two methods to detect ambguity -> regex and LLm, ideally both works but has limitations like regex being brittle and too narrow and LLM for possible unexplainibilty and high computation requirement
5. A designed a pretty much monolithic architecture as I did not want to overstep time bounds(Readme typing took lot of my time to be honest)
6. AI usage -> I figured, you want to judge me on my abilty to solve problem and not ability to use AI, so I made the logics from hand, where I used AI is in db crud operations and some refactoring. No logic eas return by AI.



## Future Improvements: 

1. since we are collecting data, we would like to use the data to train or finetune NLP models specifically for ambiguity detections.
2. Esembling various methods like regex, NLP models, and Statiscal classifiers together to make a Bagging model would give a good result.
3. Also we could have a hierarchy in terms of model selections (regex being on top, then NLP models then statistical learning models).
4. Using heavy AI models could also be an option.
5. We could also use Deep RL to learn about How ambiguity text drifts (example 12-20 years ago crypto was not even a thing, not its the most secure way to send modey around black market without govt knowing leading to ambiguious source of income).
6. My database design is not optimal so might want to fix that.
7.  Also if we are processing multiple questionnaie in one go like [{..},{..}....], if one of them fails the API response breaks.
8.  ## Ofcource: I didnt use good coding conventions


## 🚧 Assumptions
Input schema is fixed

questionnaire_id is always unique

No support (yet) for processing millions of questionnaires in one call

Precedence order: Return > Escalate > Approve

🤝 Final Note
This project is a demonstration of NLP-driven rule systems, clarity in decision automation, and FastAPI best practices.
It aims to prove both practical problem-solving and technical fluency without relying heavily on pre-trained AI to do the thinking.

Built with ❤️ by [Arihant Kamdar]
