from flask import Flask

app = Flask(__name__)

@app.route('/button-clicked', methods=['GET'])
def button_clicked():
    return "Запрос получен!", 200

if __name__ == '__main__':
    app.run(port=5000)
