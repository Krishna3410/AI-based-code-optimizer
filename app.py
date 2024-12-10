from flask import Flask, render_template, request
from analyzer import analyze_code  

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code_snippet = request.form.get("code_snippet")
        if code_snippet:
            # Analyze the code snippet using the analyze_code function
            suggestions = analyze_code(code_snippet)
            return render_template("results.html", suggestions=suggestions, code_snippet=code_snippet)
        else:
            error = "Please enter or upload a code snippet."
            return render_template("index.html", error=error)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
