import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="E-commerce EDA Dashboard", layout="wide")
sns.set_context("paper", font_scale=0.7)

# --------------------------
# Title
# --------------------------
st.title("📊 Professional E-commerce EDA Dashboard")

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

    # --------------------------
    # Sidebar - Column Selection
    # --------------------------
    st.sidebar.header("⚙️ Settings")

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    # Let user define important columns
    price_col = st.sidebar.selectbox("Select Price Column", numeric_cols)
    qty_col = st.sidebar.selectbox("Select Quantity Column", numeric_cols)
    category_col = st.sidebar.selectbox("Select Category Column", categorical_cols) if categorical_cols else None
    date_col = st.sidebar.selectbox("Select Date Column", datetime_cols) if datetime_cols else None

    # --------------------------
    # Dashboard Tabs
    # --------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧹 Data Cleaning", 
        "📈 Univariate", 
        "📊 Categorical", 
        "📦 Bivariate", 
        "📉 Time & Correlation"
    ])

    # ==========================
    # Tab 1: Data Cleaning
    # ==========================
    with tab1:
        st.subheader("Data Cleaning & Summary")

        # Remove duplicates
        before_dupes = df.shape[0]
        df = df.drop_duplicates()
        after_dupes = df.shape[0]
        st.success(f"✅ Removed {before_dupes - after_dupes} duplicate rows")

        # Missing values
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

        # Remove invalid rows
        invalid_rows = df[(df[price_col] < 0) | (df[qty_col] <= 0)].shape[0]
        df = df[(df[price_col] >= 0) & (df[qty_col] > 0)]
        st.success(f"✅ Removed {invalid_rows} invalid rows")

        # Summary Statistics
        with st.expander("📑 Summary Statistics"):
            st.dataframe(df.describe(include="all").transpose())

        # Dataset Preview
        st.write("### Cleaned Dataset Preview")
        st.dataframe(df.head())
        st.info(f"📐 Dataset Shape after cleaning: {df.shape}")

    # ==========================
    # Tab 2: Univariate
    # ==========================
    with tab2:
        st.subheader("Univariate Analysis (Numeric)")
        if numeric_cols:
            col = st.selectbox("Select numeric column", numeric_cols)
            fig, ax = plt.subplots(figsize=(5, 3))
            if df[col].nunique() < 10:
                sns.countplot(x=col, data=df, ax=ax)
            else:
                sns.histplot(df[col], kde=True, ax=ax)
            ax.set_title(f"{col} Distribution", fontsize=9)
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("No numeric columns found!")

    # ==========================
    # Tab 3: Categorical
    # ==========================
    with tab3:
        st.subheader("Categorical Analysis")
        if categorical_cols:
            cat_col = st.selectbox("Select categorical column", categorical_cols)
            fig, ax = plt.subplots(figsize=(5, 3))
            df[cat_col].value_counts().head(20).plot(kind="bar", ax=ax)
            ax.set_title(f"{cat_col} Counts", fontsize=9)
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("No categorical columns found!")

    # ==========================
    # Tab 4: Bivariate
    # ==========================
    with tab4:
        st.subheader("Bivariate Analysis (Category vs Price)")
        if category_col and price_col:
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.boxplot(x=category_col, y=price_col, data=df, ax=ax)
            ax.set_title(f"{price_col} Distribution by {category_col}", fontsize=9)
            plt.xticks(rotation=45, fontsize=7)
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("Category or Price column not selected!")

    # ==========================
    # Tab 5: Time & Correlation
    # ==========================
    with tab5:
        # Time Series
        st.subheader("Time-based Candlestick Chart")
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
            fig.update_layout(
                title="Daily Price Movement (OHLC)",
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Date or Price column missing!")

        # Correlation Heatmap
        st.subheader("Correlation Heatmap")
        if numeric_cols:
            method = st.radio("Select Correlation Method:", ["pearson", "spearman", "kendall"])
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.heatmap(df[numeric_cols].corr(method=method), annot=True, cmap="coolwarm",
                        annot_kws={"size": 6}, ax=ax)
            ax.set_title(f"Correlation Heatmap ({method.title()})", fontsize=9)
            st.pyplot(fig, clear_figure=True)
        else:
            st.warning("No numeric columns for correlation heatmap!")
