from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pickle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laptop.db'
db = SQLAlchemy(app)

class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ram = db.Column(db.Integer)
    weight = db.Column(db.Float)
    company = db.Column(db.String(50))
    typename = db.Column(db.String(50))
    opsys = db.Column(db.String(50))
    cpuname = db.Column(db.String(50))
    gpuname = db.Column(db.String(50))
    touchscreen = db.Column(db.Boolean)
    ips = db.Column(db.Boolean)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

with app.app_context():
    db.create_all()

model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def root():
    laptops = Laptop.query.all()
    laptop_count = len(laptops)
    return render_template('index.html', laptops=laptops, laptop_count=laptop_count)

@app.route('/laptops_database', methods=['GET'])
def get_laptops():
    laptops = Laptop.query.all()
    return jsonify([laptop.to_dict() for laptop in laptops])

@app.route('/delete_laptop/<int:id>', methods=['DELETE'])
def delete_laptop(id):
    try:
        laptop = Laptop.query.get(id)
        if laptop is not None:
            db.session.delete(laptop)
            db.session.commit()
            return f"Deleted laptop with id {id}."
        else:
            return "Laptop not found."
    except:
        db.session.rollback()
        return "Error occurred while deleting data."

@app.route('/predict', methods=['POST', 'GET'])
def index():
    pred_value = 0
    if request.method == 'POST':
        ram = request.form['ram']
        weight = request.form['weight']
        company = request.form['company']
        typename = request.form['typename']
        opsys = request.form['opsys']
        cpuname = request.form['cpuname']
        gpuname = request.form['gpuname']
        touchscreen = bool(request.form.getlist('touchscreen'))
        ips = bool(request.form.getlist('ips'))

        laptop = Laptop(
            ram=ram,
            weight=weight,
            company=company,
            typename=typename,
            opsys=opsys,
            cpuname=cpuname,
            gpuname=gpuname,
            touchscreen=touchscreen,
            ips=ips,
        )
        db.session.add(laptop)
        db.session.commit()
        
        feature_list = []
        
        feature_list.append(int(ram))
        feature_list.append(float(weight))
        feature_list.append((touchscreen))
        feature_list.append((ips))

        company_list = ['acer','apple','asus','dell','hp','lenovo','msi','other','toshiba']
        typename_list = ['2in1convertible','gaming','netbook','notebook','ultrabook','workstation']
        opsys_list = ['linux','mac','other','windows']
        cpu_list = ['amd','intelcorei3','intelcorei5','intelcorei7','other']
        gpu_list = ['amd','intel','nvidia']

        def traverse_list(lst, value):
            for item in lst:
                if item == value:
                    feature_list.append(1)
                else:
                    feature_list.append(0) 

        traverse_list(company_list, company)
        traverse_list(typename_list, typename)
        traverse_list(opsys_list, opsys)
        traverse_list(cpu_list, cpuname)
        traverse_list(gpu_list, gpuname)

        feature_list = [feature_list]

        pred_value = model.predict(feature_list)

    laptops = Laptop.query.all()
    laptop_count = len(laptops)

    return render_template('cost.html', pred_value=pred_value, laptops=laptops, laptop_count=laptop_count)

if __name__ == '__main__':
    app.run(debug=True)