

## ⚙️ Installation & Setup

Follow the steps below to run the **Interactive EDA Dashboard** locally on your machine:

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/interactive-eda-dashboard.git
cd interactive-eda-dashboard
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install Dependencies

Make sure you have **Python 3.8+** installed. Then install all required packages:

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Streamlit App

```bash
streamlit run app.py
```

After running the command, Streamlit will open the app in your browser at:
👉 `http://localhost:8501/`

---

## 📂 Project Structure

```
interactive-eda-dashboard/
│── app.py              # Main Streamlit application
│── requirements.txt    # Dependencies
│── sample_data.csv     # (Optional) Example dataset
│── README.md           # Documentation
```

---

## 🌍 Deployment on Streamlit Cloud (Free Hosting)

1. Push this repository to your **GitHub**.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your GitHub repo → Select `app.py`.
4. Click **Deploy** 🚀.
5. You’ll get a public URL like:

---

## ✅ Usage

* Upload any **CSV file** from your computer.
* Use the sidebar to navigate through tabs:

  * **Data Cleaning** → Handle missing values, duplicates, invalid rows.
  * **Univariate Analysis** → Distribution plots, histograms.
  * **Categorical Analysis** → Bar plots for categorical features.
  * **Bivariate Analysis** → Relationship between two variables.
  * **Time-Series Analysis** → Interactive line charts with Plotly.



Do you also want me to prepare a **`requirements.txt` file content** so you can just copy-paste it into your repo?
