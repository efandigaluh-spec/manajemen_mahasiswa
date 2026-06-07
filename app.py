from flask import Flask, render_template, request, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import re
import time
import csv
import json
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mahasiswa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# MODEL
class Mahasiswa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nim = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    jurusan = db.Column(db.String(100), nullable=False)


# BUBBLE SORT
def bubble_sort(data):
    data = list(data)
    n = len(data)

    for i in range(n):
        for j in range(0, n - i - 1):
            if data[j].nim > data[j + 1].nim:
                data[j], data[j + 1] = data[j + 1], data[j]

    return data


# HOME
@app.route('/')
def home():
    data_mahasiswa = Mahasiswa.query.all()
    total = Mahasiswa.query.count()

    return render_template(
        'index.html',
        mahasiswa=data_mahasiswa,
        waktu=0,
        total=total
    )


# TAMBAH
@app.route('/tambah', methods=['POST'])
def tambah():
    try:
        nim = request.form['nim']
        nama = request.form['nama']
        jurusan = request.form['jurusan']

        if not re.match(r'^[0-9]+$', nim):
            flash('NIM hanya boleh angka')
            return redirect('/')

        if Mahasiswa.query.filter_by(nim=nim).first():
            flash('NIM sudah terdaftar')
            return redirect('/')

        db.session.add(Mahasiswa(nim=nim, nama=nama, jurusan=jurusan))
        db.session.commit()

        flash('Data berhasil ditambahkan')

    except:
        flash('Terjadi kesalahan')

    return redirect('/')


# HAPUS
@app.route('/hapus/<int:id>')
def hapus(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    db.session.delete(mahasiswa)
    db.session.commit()

    flash('Data berhasil dihapus')
    return redirect('/')


# EDIT
@app.route('/edit/<int:id>')
def edit(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    return render_template('edit.html', mahasiswa=mahasiswa)


# UPDATE
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    try:
        mahasiswa = Mahasiswa.query.get_or_404(id)

        mahasiswa.nim = request.form['nim']
        mahasiswa.nama = request.form['nama']
        mahasiswa.jurusan = request.form['jurusan']

        db.session.commit()
        flash('Data berhasil diupdate')

    except:
        flash('Gagal update data')

    return redirect('/')


# SEARCH
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')

    start = time.perf_counter()

    data = Mahasiswa.query.filter(
        Mahasiswa.nama.like(f'%{keyword}%')
    ).all()

    end = time.perf_counter()

    return render_template(
        'index.html',
        mahasiswa=data,
        waktu=end - start,
        total=len(data)
    )


# SORT
@app.route('/sort')
def sort():
    data = Mahasiswa.query.all()
    sorted_data = bubble_sort(data)

    flash('Bubble Sort berhasil (O(n²))')

    return render_template(
        'index.html',
        mahasiswa=sorted_data,
        waktu=0,
        total=len(sorted_data)
    )


# EXPORT CSV
@app.route('/export/csv')
def export_csv():
    data = Mahasiswa.query.all()

    hasil = [
        {'nim': m.nim, 'nama': m.nama, 'jurusan': m.jurusan}
        for m in data
    ]

    df = pd.DataFrame(hasil)
    file_name = 'mahasiswa.csv'
    df.to_csv(file_name, index=False)

    return send_file(file_name, as_attachment=True)


# EXPORT JSON
@app.route('/export/json')
def export_json():
    data = Mahasiswa.query.all()

    hasil = [
        {'nim': m.nim, 'nama': m.nama, 'jurusan': m.jurusan}
        for m in data
    ]

    file_name = 'mahasiswa.json'

    with open(file_name, 'w') as file:
        json.dump(hasil, file)

    return send_file(file_name, as_attachment=True)


# IMPORT CSV
@app.route('/import', methods=['POST'])
def import_csv():
    try:
        file = request.files['file']

        csv_data = csv.DictReader(
            file.stream.read().decode('utf-8').splitlines()
        )

        for row in csv_data:
            if Mahasiswa.query.filter_by(nim=row['nim']).first():
                continue

            db.session.add(Mahasiswa(
                nim=row['nim'],
                nama=row['nama'],
                jurusan=row['jurusan']
            ))

        db.session.commit()
        flash('Import CSV berhasil')

    except:
        flash('Format CSV salah')

    return redirect('/')


# RUN (WAJIB UNTUK RENDER)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)