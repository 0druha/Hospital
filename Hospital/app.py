from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Akak_2007@localhost:5432/Hospital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(100), nullable=False)  # Фамилия
    s_name = db.Column(db.String(100), nullable=False)  # Имя
    pat = db.Column(db.String(100))  # Отчество
    b_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.relationship('Docp', backref='patient', lazy=True, cascade="all, delete-orphan")


class Docp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_type_id = db.Column(db.Integer, db.ForeignKey('doc_types.id'), nullable=False)
    seria = db.Column(db.String(20))
    nomer = db.Column(db.String(20))
    snils_nomer = db.Column(db.String(14), nullable=False)  # СНИЛС как строка
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)


class DocType(db.Model):
    __tablename__ = 'doc_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    documents = db.relationship('Docp', backref='doc_type', lazy=True)










with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('base.html')


@app.route('/patients')
def index():
    patients_data = db.session.query(Patient, Docp) \
        .join(Docp, Patient.id == Docp.patient_id) \
        .order_by(Patient.created_at.desc()) \
        .all()
    return render_template('index.html', patients_data=patients_data)


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        try:
            birth_date = datetime.strptime(request.form['b_date'], '%Y-%m-%d').date() if request.form['b_date'] else None
            new_patient = Patient(

                f_name = request.form['f_name'],
                s_name = request.form['s_name'],
                pat = request.form['pat'],
                b_date = birth_date
            )
            db.session.add(new_patient)
            db.session.flush()

            new_doc = Docp(
                doc_type_id=request.form['doc_type'],
                seria=request.form['seria'],
                nomer=request.form['nomer'],
                snils_nomer=request.form['snils_nomer'],
                patient_id=new_patient.id
            )
            db.session.add(new_doc)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"Произошла ошибка: {str(e)}"

    return render_template('add_patient.html')


@app.route('/patients/<int:id>/delete')
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        return redirect('/patients')
    except Exception as e:
        db.session.rollback()
        return f"При удалении произошла ошибка: {str(e)}"


@app.route('/patients/<int:id>/edit_patient', methods=['GET', 'POST'])
def edit_patient(id):
    patient = Patient.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Обновление данных пациента
            patient.f_name = request.form.get('f_name', patient.f_name)
            patient.s_name = request.form.get('s_name', patient.s_name)
            patient.pat = request.form.get('pat', patient.pat)
            b_date_str = request.form['b_date']
            if b_date_str:
                try:
                    patient.b_date = datetime.strptime(b_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return redirect(url_for('edit_patient', id=id))


            # Обновление документов пациента

            docp = patient.documents[0]  # Берем первый документ
            docp.doc_type_id = request.form.get('doc_type', docp.doc_type_id)
            docp.seria = request.form.get('seria', docp.seria)
            docp.nomer = request.form.get('nomer', docp.nomer)
            docp.snils_nomer = request.form.get('snils_nomer', docp.snils_nomer)


            db.session.commit()
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()

    # Для GET-запроса
    return render_template(
        'edit_patient.html',
        patient=patient,
        patient_id=id,
        current_date=datetime.now().strftime('%Y-%m-%d')
    )






if __name__ == '__main__':
    app.run(debug=True)
