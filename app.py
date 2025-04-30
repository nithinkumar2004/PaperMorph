import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pdf2docx import Converter

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files["pdf_file"]

        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(pdf_path)

            docx_filename = filename.rsplit(".", 1)[0] + ".docx"
            docx_path = os.path.join(app.config["CONVERTED_FOLDER"], docx_filename)

            try:
                converter = Converter(pdf_path)
                converter.convert(docx_path)
                converter.close()
                flash("Conversion successful!")
                return redirect(url_for("download_file", filename=docx_filename))
            except Exception as e:
                flash(f"Conversion failed: {str(e)}")
                return redirect(request.url)

        flash("Invalid file type. Please upload a PDF.")
        return redirect(request.url)

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["CONVERTED_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
