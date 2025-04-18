from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Возможные операции
operations = ["sum", "sub", "mul", "div"]

# GET 
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=float)
    random_number = random.uniform(1, 100)
    result = random_number * param
    return jsonify({
        "operation": "mul",
        "random_number": random_number,
        "param": param,
        "result": result
    })

# POST 
@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    json_param = data.get("jsonParam")
    random_number = random.uniform(1, 100)
    operation = random.choice(operations)

    if operation == "sum":
        result = random_number + json_param
    elif operation == "sub":
        result = random_number - json_param
    elif operation == "mul":
        result = random_number * json_param
    elif operation == "div":
        result = random_number / json_param if json_param != 0 else "undefined"

    return jsonify({
        "random_number": random_number,
        "jsonParam": json_param,
        "operation": operation,
        "result": result
    })

# DELETE 
@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_number = random.uniform(1, 100)
    another_number = random.uniform(1, 10)
    operation = random.choice(operations)

    if operation == "sum":
        result = random_number + another_number
    elif operation == "sub":
        result = random_number - another_number
    elif operation == "mul":
        result = random_number * another_number
    elif operation == "div":
        result = random_number / another_number if another_number != 0 else "undefined"

    return jsonify({
        "random_number": random_number,
        "another_number": another_number,
        "operation": operation,
        "result": result
    })

if __name__ == '__main__':
    app.run(debug=True)

# step1 = 5.0 * 68.47761488495044 → 342.3880744247522

# step2 = step1 - 3 → 342.3880744247522 - 3 = 339.3880744247522

# step3 = step2 + (75.43374824030951 / 9.033400806791706)
#       = 339.3880744247522 + 8.350537062807522
#       = 347.7386114875597

# final = int(step3) → int(347.7386114875597) = 347

# CURL

# step1 = 91.82320910642642 * 5  → 459.1160455321321

# step2 = step1 * 3  → 459.1160455321321 * 3 = 1377.3481365963964

# step3 = step2 / 7.720308652159832  
#       = 1377.3481365963964 / 7.720308652159832  
#       = 178.3787887164538

# final = int(step3) → int(178.3787887164538) = 178
