# Wine Quality Predictor 🍷

  A full-stack machine learning project that predicts **red wine quality** using both **regression** and **classification**, with a **modern web UI** and **SQLite history tracking**.

Built with:

- 🐍 **Python + Flask**
- 🤖 **scikit-learn** (Random Forest Regressor & Classifier)
- 🗄️ **SQLite** via Flask-SQLAlchemy
- 🎨 **HTML + CSS + Bootstrap + JS** (custom dark UI)

---

# Project Overview

Given the physicochemical properties of a red wine sample (acidity, pH, alcohol, etc.), the app:

1. Predicts a **numeric quality score** (0–10) using regression.
2. Maps it to a **quality label**:
   - `Low`
   - `Medium`
   - `High`
3. Displays the result in an attractive **circular gauge**, with stars and a short explanation.
4. Stores each prediction in a **SQLite database**, which can be viewed from a **History** modal.

---

## 🧠 Machine Learning

- Dataset: **Red Wine Quality** (UCI Machine Learning Repository)
- Target: `quality` (0–10 integer scores)
- Features:  
  `fixed acidity, volatile acidity, citric acid, residual sugar, chlorides, free sulfur dioxide, total sulfur dioxide, density, pH, sulphates, alcohol`

### Models

- **Regression**: `RandomForestRegressor`
- **Classification**: `RandomForestClassifier` on labels:
  - ≤ 5 → `Low`
  - 6–7 → `Medium`
  - ≥ 8 → `High`

Both models are wrapped with **`StandardScaler`** inside sklearn **Pipelines** and trained at app startup using `winequality-red.csv`.

---

# App Features

- Clean, responsive **single-page layout**.
- Input form for all 11 wine features.
- **Prediction card**:
  - Animated circular score (0–10)
  - Quality label badge (`Low / Medium / High`)
  - Star rating (0–5 stars mapped from score)
  - Text explanation for each label
- **History panel**:
  - Triggered by a **History** button with an icon.
  - Opens a modal showing the latest predictions (time, score, label, main features).
- **SQLite** database persists prediction history across runs.

---

# Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy
- **ML**: scikit-learn, pandas, numpy
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JS

---

# Project Structure

```text
.
├─ app.py                 # Flask app + model training + API routes
├─ requirements.txt       # Python dependencies
├─ README.md
├─ .gitignore
│
├─ winequality-red.csv    # Dataset (place here, or download separately)
│
├─ templates/
│   └─ index.html         # Main UI template
│
└─ static/
    ├─ styles.css         # Custom styles (dark theme, gauge, modal)
    └─ script.js          # Frontend logic (fetch, history, UI updates)
