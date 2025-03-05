import os
import sys
import pandas as pd
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Production(db.Model):
    __tablename__ = 'production'

    id = db.Column(db.Integer, primary_key=True)
    quarter_1_production =  db.Column(db.Integer, nullable=False)
    quarter_2_production =  db.Column(db.Integer, nullable=False)
    quarter_3_production =  db.Column(db.Integer, nullable=False)
    quarter_4_production =  db.Column(db.Integer, nullable=False)


class EnergyWell(db.Model):
    __tablename__ = 'energy_well'

    id = db.Column(db.Integer, primary_key=True)
    api_well_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    oil_id = db.Column(db.Integer, db.ForeignKey('production.id'))
    gas_id = db.Column(db.Integer, db.ForeignKey('production.id'))
    brine_id = db.Column(db.Integer, db.ForeignKey('production.id'))
    
    # Relationships
    oil_production = db.relationship("Production", foreign_keys=[oil_id])
    gas_production = db.relationship("Production", foreign_keys=[gas_id])
    brine_production = db.relationship("Production", foreign_keys=[brine_id])

    def __repr__(self):
        return f'<EnergyWell {self.id}: {self.name} - {self.api_well_number}>'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/update_db/")
def update_db():

    df = pd.read_excel("resources\energy_data.xls")
    for index, row in df.iterrows():
        api_well_number = row["API WELL  NUMBER"]
        well_name = row["WELL NAME"]
        quarter = str(row["QUARTER 1,2,3,4"])
        energy_well = EnergyWell.query.filter_by(api_well_number=api_well_number).first()
        if not energy_well:
            oil = Production(
                quarter_1_production=int(row["OIL"]) if quarter == "1" else 0,
                quarter_2_production=int(row["OIL"]) if quarter == "2" else 0,
                quarter_3_production=int(row["OIL"]) if quarter == "3" else 0,
                quarter_4_production=int(row["OIL"]) if quarter == "4" else 0
            )
            gas = Production(
                quarter_1_production=int(row["GAS"]) if quarter == "1" else 0,
                quarter_2_production=int(row["GAS"]) if quarter == "2" else 0,
                quarter_3_production=int(row["GAS"]) if quarter == "3" else 0,
                quarter_4_production=int(row["GAS"]) if quarter == "4" else 0
            )
            brine = Production(
                quarter_1_production=int(row["BRINE"]) if quarter == "1" else 0,
                quarter_2_production=int(row["BRINE"]) if quarter == "2" else 0,
                quarter_3_production=int(row["BRINE"]) if quarter == "3" else 0,
                quarter_4_production=int(row["BRINE"]) if quarter == "4" else 0
            )
            db.session.add(oil)
            db.session.add(gas)
            db.session.add(brine)
            db.session.commit()

            energy_well = EnergyWell(
                api_well_number=api_well_number,
                name=well_name,
                oil_production=oil,
                gas_production=gas,
                brine_production=brine
            )
            db.session.add(energy_well)
            db.session.commit()
            sys.stdout.write(f"{index} {api_well_number} created\n")
        else:
            oil_production = Production.query.filter_by(id=energy_well.oil_id).first() 
            gas_production = Production.query.filter_by(id=energy_well.gas_id).first() 
            brine_production = Production.query.filter_by(id=energy_well.brine_id).first()

            quarter_map = {
                "1": "quarter_1_production",
                "2": "quarter_2_production",
                "3": "quarter_3_production",
                "4": "quarter_4_production"
            } 
            setattr(oil_production, quarter_map[quarter], int(row["OIL"]))
            setattr(gas_production, quarter_map[quarter], int(row["GAS"]))
            setattr(brine_production, quarter_map[quarter], int(row["BRINE"]))
            # Commit all changes
            db.session.commit()

            sys.stdout.write(f"{index} {api_well_number} updated\n")

    return "<p>data updated</p>"


@app.route('/data/', methods=['GET'])
def get_well_production():
    # Get well number from query parameter
    well_number = request.args.get('well')
    
    if not well_number:
        return jsonify({"error": "API Well number is required"}), 400
    
    OilProduction = aliased(Production)
    GasProduction = aliased(Production)
    BrineProduction = aliased(Production)

    production_subquery = db.session.query(
        EnergyWell.api_well_number,
        
        # Sum oil production
        (
            OilProduction.quarter_1_production + OilProduction.quarter_2_production +
            OilProduction.quarter_3_production + OilProduction.quarter_4_production
        ).label('total_oil'),
        
        # Sum gas production
        (
            GasProduction.quarter_1_production + GasProduction.quarter_2_production +
            GasProduction.quarter_3_production + GasProduction.quarter_4_production
        ).label('total_gas'),
        
        # Sum brine production
        (
            BrineProduction.quarter_1_production + BrineProduction.quarter_2_production +
            BrineProduction.quarter_3_production + BrineProduction.quarter_4_production
        ).label('total_brine')

    ).join(OilProduction, EnergyWell.oil_id == OilProduction.id, isouter=True) \
    .join(GasProduction, EnergyWell.gas_id == GasProduction.id, isouter=True) \
    .join(BrineProduction, EnergyWell.brine_id == BrineProduction.id, isouter=True) \
    .filter(EnergyWell.api_well_number == int(well_number)) \
    .group_by(EnergyWell.api_well_number) \
    .subquery()
    
    try:
        # Query the subquery
        result = db.session.query(
            production_subquery.c.total_oil,
            production_subquery.c.total_gas,
            production_subquery.c.total_brine
        ).first()
    except ValueError:
        return jsonify({"error": "Invalid well number"}), 400
    
    if not result:
        return jsonify({"error": "Well not found"}), 404
    
    # Prepare the response
    response = {
        "oil": result.total_oil or 0,
        "gas": result.total_gas or 0,
        "brine": result.total_brine or 0
    }
    
    return jsonify(response)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)