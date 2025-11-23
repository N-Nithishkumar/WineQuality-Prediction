import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline

# ---------------------------
# Flask + Database setup
# ---------------------------

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///predictions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------------------
# Database Model
# ---------------------------

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fixed_acidity = db.Column(db.Float)
    volatile_acidity = db.Column(db.Float)
    citric_acid = db.Column(db.Float)
    residual_sugar = db.Column(db.Float)
    chlorides = db.Column(db.Float)
    free_sulfur_dioxide = db.Column(db.Float)
    total_sulfur_dioxide = db.Column(db.Float)
    density = db.Column(db.Float)
    ph = db.Column(db.Float)
    sulphates = db.Column(db.Float)
    alcohol = db.Column(db.Float)

    predicted_quality = db.Column(db.Float)      # regression
    quality_label = db.Column(db.String(20))     # classification: Low / Medium / High

# ---------------------------
# ML Models (global)
# ---------------------------

regression_model = None
classification_model = None
label_encoder = None

# Order of features expected from frontend
INPUT_FEATURE_KEYS = [
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
]

# Corresponding order in CSV dataset
DATASET_FEATURE_COLUMNS = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
]

# ---------------------------
# Load + Train Models
# ---------------------------

def load_and_train_models():
    global regression_model, classification_model, label_encoder

    csv_path = os.path.join(os.path.dirname(__file__), "winequality-red.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset 'winequality-red.csv' not found in {os.path.dirname(__file__)}"
        )

    df = pd.read_csv(csv_path, sep=";")

    # Use a fixed column order
    X = df[DATASET_FEATURE_COLUMNS].values
    y_reg = df["quality"].values

    # Create classification labels from numeric quality
    # <=5 -> Low, 6-7 -> Medium, >=8 -> High
    def to_label(q):
        if q <= 5:
            return "Low"
        elif q <= 7:
            return "Medium"
        else:
            return "High"

    y_clf_labels = df["quality"].apply(to_label)

    le = LabelEncoder()
    y_clf = le.fit_transform(y_clf_labels)

    # Regression model
    regression_model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("rf_reg", RandomForestRegressor(n_estimators=200, random_state=42)),
        ]
    )
    regression_model.fit(X, y_reg)

    # Classification model
    classification_model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("rf_clf", RandomForestClassifier(n_estimators=200, random_state=42)),
        ]
    )
    classification_model.fit(X, y_clf)

    label_encoder = le
    print("Models trained successfully.")


# ---------------------------
# Helper: Get features from request
# ---------------------------

def extract_features(req_data):
    values = []
    for key in INPUT_FEATURE_KEYS:
        raw = req_data.get(key, None)
        if raw is None or raw == "":
            raise ValueError(f"Missing value for {key}")
        try:
            values.append(float(raw))
        except ValueError:
            raise ValueError(f"Invalid numeric value for {key}: {raw}")
    return values


# ---------------------------
# Routes
# ---------------------------

@app.route("/", methods=["GET"])
def index():
    history_items = (
        Prediction.query.order_by(Prediction.created_at.desc()).limit(10).all()
    )
    return render_template("index.html", history_items=history_items)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() or request.form

        features = extract_features(data)
        X_new = [features]

        # Regression
        reg_pred = regression_model.predict(X_new)[0]

        # Classification
        clf_pred_encoded = classification_model.predict(X_new)[0]
        label = label_encoder.inverse_transform([clf_pred_encoded])[0]

        # Save into DB
        pred = Prediction(
            fixed_acidity=features[0],
            volatile_acidity=features[1],
            citric_acid=features[2],
            residual_sugar=features[3],
            chlorides=features[4],
            free_sulfur_dioxide=features[5],
            total_sulfur_dioxide=features[6],
            density=features[7],
            ph=features[8],
            sulphates=features[9],
            alcohol=features[10],
            predicted_quality=float(reg_pred),
            quality_label=label,
        )
        db.session.add(pred)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "predicted_quality": round(float(reg_pred), 2),
                "quality_label": label,
            }
        )
    except Exception as e:
        print("Error in /predict:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/history", methods=["GET"])
def history():
    items = (
        Prediction.query.order_by(Prediction.created_at.desc()).limit(30).all()
    )
    result = []
    for p in items:
        result.append(
            {
                "id": p.id,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
                "fixed_acidity": p.fixed_acidity,
                "volatile_acidity": p.volatile_acidity,
                "citric_acid": p.citric_acid,
                "residual_sugar": p.residual_sugar,
                "chlorides": p.chlorides,
                "free_sulfur_dioxide": p.free_sulfur_dioxide,
                "total_sulfur_dioxide": p.total_sulfur_dioxide,
                "density": p.density,
                "ph": p.ph,
                "sulphates": p.sulphates,
                "alcohol": p.alcohol,
                "predicted_quality": round(p.predicted_quality, 2)
                if p.predicted_quality is not None
                else None,
                "quality_label": p.quality_label,
            }
        )

    return jsonify(result)


# ---------------------------
# App init
# ---------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        load_and_train_models()
    app.run(debug=True)
