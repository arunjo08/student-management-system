from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Student Management System</h1>
    <p>Welcome to my first Python web project!</p>
    """

if __name__ == "__main__":
    app.run(debug=True)
