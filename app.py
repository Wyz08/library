import io
from flask import send_file

import pandas as pd

from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
er_dataframe = None


@app.route("/", methods=["GET", "POST"])
def index():
    er = None
    if request.method == "POST":
        try:
            likes = int(request.form["likes"])
            comments = int(request.form["comments"])
            shares = int(request.form["shares"])
            followers = int(request.form["followers"])
            
            if followers == 0:
                return "Jumlah followers tidak boleh 0!"

            # Hitung Engagement Rate
            er = ((likes + comments + shares) / followers) * 100

        except ValueError:
            return "Input tidak valid! Masukkan angka yang benar."

    return render_template("index.html", er=round(er, 2) if er is not None else None)
@app.route("/upload", methods=["GET", "POST"])
def upload():
    global er_dataframe
    er_dataframe = None
    er_data = None

    if request.method == "POST":
        file = request.files["file"]
        if file:
            try:
                df = pd.read_csv(file)
                required_cols = {"likes", "comments", "shares", "followers"}
                if not required_cols.issubset(set(df.columns)):
                    return "CSV tidak memiliki kolom yang diperlukan: likes, comments, shares, followers"

                required_cols = {"likes", "comments", "shares", "followers"}
                df["ER"] = ((df["likes"] + df["comments"] + df["shares"]) / df["followers"]) * 100
                er_dataframe = df
                er_data = df[["username", "ER"]].to_dict(orient="records")
            except Exception as e:
                return f"Terjadi kesalahan saat memproses file: {e}"

    return render_template("upload.html", er_data=er_data)

@app.route("/download/<tipe>")
def download(tipe):
    global er_dataframe
    if er_dataframe is None:
        return "Tidak ada data untuk didownload."

    output = io.BytesIO()

    if tipe == "csv":
        csv_data = er_dataframe.to_csv(index=False)
        output.write(csv_data.encode('utf-8'))
        output.seek(0)
        return send_file(output, mimetype="text/csv", as_attachment=True, download_name="hasil_er.csv")

    elif tipe == "excel":
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            er_dataframe.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="hasil_er.xlsx")

    else:
        return "Format file tidak dikenal."


if __name__ == "__main__":
    app.run(debug=True)

    