from flask import Flask, render_template, request, redirect, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import re
import time
import csv
import json

app = Flask(__name__)
app.secret_key = 'secret123'

# IDENTITAS APLIKASI
APP_NAME = "Efandi"
APP_ID = "241011450231"

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


# HOME (SUDAH DIGANTI ALAMATNYA)
@app.route('/efandi-241011450231')
def home():
    data_mahasiswa = Mahasiswa.query.all()
    total = Mahasiswa.query.count()

    return render_template(
        'index.html',
        mahasiswa=data_mahasiswa,
        waktu=0,
        total=total,
        app_name=APP_NAME,
        app_id=APP_ID
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
            return redirect('/efandi-241011450231')

        cek = Mahasiswa.query.filter_by(nim=nim).first()
        if cek:
            flash('NIM sudah terdaftar')
            return redirect('/efandi-241011450231')

        mahasiswa_baru = Mahasiswa(nim=nim, nama=nama, jurusan=jurusan)
        db.session.add(mahasiswa_baru)
        db.session.commit()

        flash('Data berhasil ditambahkan')

    except:
        flash('Terjadi kesalahan')

    return redirect('/efandi-241011450231')


# HAPUS
@app.route('/hapus/<int:id>')
def hapus(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)
    db.session.delete(mahasiswa)
    db.session.commit()

    flash('Data berhasil dihapus')
    return redirect('/efandi-241011450231')


# EDIT
@app.route('/edit/<int:id>')
def edit(id):
    mahasiswa = Mahasiswa.query.get_or_404(id)

    return render_template(
        'edit.html',
        mahasiswa=mahasiswa,
        app_name=APP_NAME,
        app_id=APP_ID
    )


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

    return redirect('/efandi-241011450231')


# SEARCH
@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')

    start = time.perf_counter()

    data = Mahasiswa.query.filter(
        Mahasiswa.nama.like(f'%{keyword}%')
    ).all()

    end = time.perf_counter()

    waktu = end - start
    total = Mahasiswa.query.count()

    return render_template(
        'index.html',
        mahasiswa=data,
        waktu=waktu,
        total=total,
        app_name=APP_NAME,
        app_id=APP_ID
    )


# SORT
@app.route('/sort')
def sort():
    data = Mahasiswa.query.all()

    sorted_data = sorted(data, key=lambda x: x.nim)

    flash('Data berhasil diurutkan')

    return render_template(
        'index.html',
        mahasiswa=sorted_data,
        waktu=0,
        total=len(sorted_data),
        app_name=APP_NAME,
        app_id=APP_ID
    )


# EXPORT CSV
@app.route('/export/csv')
def export_csv():
    data = Mahasiswa.query.all()

    hasil = []
    for m in data:
        hasil.append({
            'nim': m.nim,
            'nama': m.nama,
            'jurusan': m.jurusan
        })

    df = pd.DataFrame(hasil)
    file_name = 'mahasiswa.csv'
    df.to_csv(file_name, index=False)

    return send_file(file_name, as_attachment=True)


# EXPORT JSON
@app.route('/export/json')
def export_json():
    data = Mahasiswa.query.all()

    hasil = []
    for m in data:
        hasil.append({
            'nim': m.nim,
            'nama': m.nama,
            'jurusan': m.jurusan
        })

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

    return redirect('/efandi-241011450231')


# RUN
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)