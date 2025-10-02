import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="E-commerce EDA Dashboard", layout="wide")

# Global styling
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=0.9)

# --------------------------
# Custom CSS for Modern Look
# --------------------------
st.markdown("""
    <style>
        .main {background-color: #f8f9fa;}
        h1, h2, h3, h4 {color: #2c3e50;}
        .stMetric {background-color: white; padding: 15px; border-radius: 10px; 
                   box-shadow: 0px 2px 5px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Title
# --------------------------
st.title("📊 Modern E-commerce EDA Dashboard")

# --------------------------
# File Upload
# --------------------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()

    # Convert potential date columns
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Sidebar settings
    st.sidebar.header("⚙️ Dashboard Settings")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    price_col = st.sidebar.selectbox("💲 Select Price Column", numeric_cols)
    qty_col = st.sidebar.selectbox("📦 Select Quantity Column", numeric_cols)
    category_col = st.sidebar.selectbox("🏷️ Select Category Column", categorical_cols) if categorical_cols else None
    date_col = st.sidebar.selectbox("📅 Select Date Column", datetime_cols) if datetime_cols else None

    # ==========================
    # KPI Metrics
    # ==========================
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🛒 Total Orders", f"{df.shape[0]:,}")
    with col2:
        st.metric("💰 Total Revenue", f"${(df[price_col] * df[qty_col]).sum():,.2f}")
    with col3:
        st.metric("👥 Unique Customers", f"{df['customer_id'].nunique() if 'customer_id' in df else 'N/A'}")

    # ==========================
    # Dashboard Tabs
    # ==========================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧹 Data Cleaning", 
        "📈 Univariate", 
        "📊 Categorical", 
        "📦 Bivariate", 
        "📉 Time & Correlation"
    ])

    # ========== Tab 1: Data Cleaning ==========
    with tab1:
        st.subheader("🧹 Data Cleaning & Summary")
        before_dupes = df.shape[0]
        df = df.drop_duplicates()
        after_dupes = df.shape[0]
        st.success(f"✅ Removed {before_dupes - after_dupes} duplicate rows")

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Missing Values Before Cleaning")
            st.dataframe(df.isnull().sum())
        with col2:
            missing_option = st.radio(
                "Handle Missing Values:",
                ("Drop rows", "Fill with mean/median/mode", "Fill with constant (e.g., 0)")
            )

        if missing_option == "Drop rows":
            df = df.dropna()
        elif missing_option == "Fill with mean/median/mode":
            for col in df.columns:
                if df[col].dtype in ["int64", "float64"]:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode()[0], inplace=True)
        elif missing_option == "Fill with constant (e.g., 0)":
            for col in df.columns:
                if df[col].dtype in ["int64", "float64"]:
                    df[col].fillna(0, inplace=True)
                else:
                    df[col].fillna("Unknown", inplace=True)

        st.write("### Missing Values After Cleaning")
        st.dataframe(df.isnull().sum())

        invalid_rows = df[(df[price_col] < 0) | (df[qty_col] <= 0)].shape[0]
        df = df[(df[price_col] >= 0) & (df[qty_col] > 0)]
        st.success(f"✅ Removed {invalid_rows} invalid rows")

        with st.expander("📑 Summary Statistics"):
            st.dataframe(df.describe(include="all").transpose())

        st.write("### Dataset Preview")
        st.dataframe(df.head())

    # ========== Tab 2: Univariate ==========
    with tab2:
        st.subheader("📈 Univariate Analysis")
        if numeric_cols:
            col = st.selectbox("Select numeric column", numeric_cols)
            col1, col2 = st.columns([2, 1])
            with col1:
                fig, ax = plt.subplots(figsize=(6, 3))
                if df[col].nunique() < 10:
                    sns.countplot(x=col, data=df, ax=ax, palette="Set2")
                else:
                    sns.histplot(df[col], kde=True, ax=ax, color="skyblue")
                ax.set_title(f"{col} Distribution")
                st.pyplot(fig, clear_figure=True)
            with col2:
                st.write("📊 **Summary Stats**")
                st.dataframe(df[col].describe())
        else:
            st.warning("No numeric columns found!")

    # ========== Tab 3: Categorical ==========
    with tab3:
        st.subheader("📊 Categorical Analysis")
        if categorical_cols:
            cat_col = st.selectbox("Select categorical column", categorical_cols)
            fig, ax = plt.subplots(figsize=(6, 3))
            df[cat_col].value_counts().head(15).plot(kind="bar", ax=ax, color="teal")
            ax.set_title(f"{cat_col} Top 15 Counts")
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("No categorical columns found!")

    # ========== Tab 4: Bivariate ==========
    with tab4:
        st.subheader("📦 Bivariate Analysis")
        if category_col and price_col:
            fig, ax = plt.subplots(figsize=(7, 3))
            sns.boxplot(x=category_col, y=price_col, data=df, ax=ax, palette="Set3")
            ax.set_title(f"{price_col} by {category_col}")
            plt.xticks(rotation=45)
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("Category or Price column not selected!")

    # ========== Tab 5: Time & Correlation ==========
    with tab5:
        st.subheader("📉 Time Series & Correlation")
        if date_col and price_col:
            daily = df.groupby(df[date_col].dt.date).agg(
                open=(price_col, 'first'),
                high=(price_col, 'max'),
                low=(price_col, 'min'),
                close=(price_col, 'last')
            ).reset_index()

            fig = go.Figure(data=[go.Candlestick(
                x=daily[date_col],
                open=daily['open'],
                high=daily['high'],
                low=daily['low'],
                close=daily['close']
            )])
            fig.update_layout(title="Daily Price Movement", xaxis_rangeslider_visible=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        if numeric_cols:
            method = st.radio("Select Correlation Method:", ["pearson", "spearman", "kendall"], horizontal=True)
            fig, ax = plt.subplots(figsize=(6, 3))
            sns.heatmap(df[numeric_cols].corr(method=method), annot=True, cmap="coolwarm")
            ax.set_title(f"Correlation Heatmap ({method.title()})")
            st.pyplot(fig, clear_figure=True)
