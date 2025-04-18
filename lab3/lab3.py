from fastapi import FastAPI, Query
from pydantic import BaseModel
import random

app = FastAPI()

# Возможные операции
operations = ["+", "-", "*", "/"]

# Модель запроса для POST
class NumberRequest(BaseModel):
    jsonParam: float

# GET 
@app.get("/number/")
def get_number(param: float = Query(...)):
    random_number = random.uniform(1, 100)
    result = random_number * param
    return {"operation": "multiply", "random_number": random_number, "param": param, "result": result}

# POST 
@app.post("/number/")
def post_number(data: NumberRequest):
    random_number = random.uniform(1, 100)
    operation = random.choice(operations)

    if operation == "+":
        result = random_number + data.jsonParam
    elif operation == "-":
        result = random_number - data.jsonParam
    elif operation == "*":
        result = random_number * data.jsonParam
    elif operation == "/":
        result = random_number / data.jsonParam if data.jsonParam != 0 else "undefined"

    return {
        "random_number": random_number,
        "jsonParam": data.jsonParam,
        "operation": operation,
        "result": result
    }

# DELETE 
@app.delete("/number/")
def delete_number():
    random_number = random.uniform(1, 100)
    another_number = random.uniform(1, 10)
    operation = random.choice(operations)

    if operation == "+":
        result = random_number + another_number
    elif operation == "-":
        result = random_number - another_number
    elif operation == "*":
        result = random_number * another_number
    elif operation == "/":
        result = random_number / another_number if another_number != 0 else "undefined"

    return {
        "random_number": random_number,
        "another_number": another_number,
        "operation": operation,
        "result": result
    }

# step1 = 4 * 92.41465259095054  → 369.65861036380215

# step2 = step1 - 5  → 369.65861036380215 - 5 = 364.65861036380215

# step3 = step2 + 8.975019971451486  → 364.65861036380215 + 8.975019971451486
# = 373.6336303352536

# final = int(step3)  → int(373.6336303352536) = 373

# CURL

# step1 = 64.99956944412745 * 5.0  → 324.99784722063725

# step2 = step1 - 3.0  → 324.99784722063725 - 3.0 = 321.99784722063725

# step3 = step2 * 7.317109409773659  → 321.99784722063725 * 7.317109409773659
# = 2355.6407738874397

# final = int(step3)  → int(2355.6407738874397) = 2355
