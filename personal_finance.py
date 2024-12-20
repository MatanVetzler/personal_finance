import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# Page configuration
st.set_page_config(layout="wide", page_title="Finance Dashboard", page_icon="💰")

# Enhanced CSS Styling with enforced dark theme
st.markdown("""
    <style>
    /* Force dark theme */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"],
    section[data-testid="stSidebar"],
    [data-testid="stToolbar"] {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Ensure dark theme for all text elements */
    p, span, div, label, .stMarkdown p {
        color: #ffffff !important;
    }

    /* Style metrics containers */
    [data-testid="stMetric"] {
        background-color: #1e1e1e !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        border: 1px solid #2d2d2d !important;
    }

    /* Style metric values and labels */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.2rem !important;
    }

    /* Enhanced Select/Dropdown styling */
    select,
    .stSelectbox > div > div > select,
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] input {
        background-color: #262730 !important;
        color: #ffffff !important;
        border-color: #404040 !important;
    }

    /* Style all dropdown-related elements */
    div[data-baseweb="popover"] {
        background-color: #262730 !important;
    }

    div[data-baseweb="popover"] * {
        background-color: #262730 !important;
        color: #ffffff !important;
    }

    div[data-baseweb="select"] * {
        background-color: #262730 !important;
        color: #ffffff !important;
    }

    /* Style the dropdown options container */
    div[role="listbox"] {
        background-color: #262730 !important;
        border: 1px solid #404040 !important;
    }

    /* Style individual dropdown items */
    div[role="option"] {
        background-color: #262730 !important;
        color: #ffffff !important;
    }

    /* Style dropdown hover state */
    div[role="option"]:hover {
        background-color: #404040 !important;
    }

    /* Style selected option */
    div[aria-selected="true"] {
        background-color: #404040 !important;
        color: #ffffff !important;
    }

    /* Fix for white background in dropdowns */
    .stSelectbox > div,
    .stSelectbox > div > div {
        background-color: #262730 !important;
    }

    /* Style the select value container */
    div[data-baseweb="select"] div[data-testid="stMarkdown"] {
        background-color: #262730 !important;
        color: #ffffff !important;
    }

    [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #cccccc !important;
    }

    /* Style buttons consistently */
    button, [data-testid="baseButton-secondary"] {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
    }

    button:hover {
        border-color: #00ff88 !important;
    }

    /* Style expanders */
    [data-testid="stExpander"] {
        background-color: #1e1e1e !important;
        border-radius: 0.5rem !important;
        border: 1px solid #2d2d2d !important;
    }

    /* Form inputs */
    input, .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #262730 !important;
        color: #ffffff !important;
        border-color: #404040 !important;
    }

    /* Selectbox */
    .stSelectbox > div > div::before {
        background-color: #262730 !important;
    }

    /* Dataframe styling */
    .dataframe {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }

    .dataframe th {
        background-color: #262730 !important;
        color: #ffffff !important;
    }

    .dataframe td {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }

    /* Force white text for all markdown */
    .stMarkdown {
        color: #ffffff !important;
    }

    /* Style tooltips */
    .tooltip {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }

    /* Override any Streamlit defaults */
    .stApp {
        background-color: #0e1117 !important;
    }

    .streamlit-expanderHeader {
        color: #ffffff !important;
    }

    /* Sidebar */
    [data-testid="stSidebarNav"] {
        background-color: #0e1117 !important;
    }

    [data-testid="stSidebarNav"] li {
        background-color: #1e1e1e !important;
    }

    /* Mobile-specific adjustments */
    @media (max-width: 768px) {
        .stMetric {
            padding: 0.75rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }

        .main .block-container {
            padding: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Get current month for default selection
current_month = datetime.now().strftime("%B")
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# File for saving data
file_path = "finance_data.csv"

# Initialize data storage
if "data" not in st.session_state:
    if os.path.exists(file_path):
        st.session_state.data = pd.read_csv(file_path)
    else:
        st.session_state.data = pd.DataFrame(columns=[
            "Month", "Year", "Income Salary", "Income plus", "Expenses Day-to-day",
            "Expenses rent", "Expenses loan", "Expenses market",
            "Expenses taxes", "Expenses mortgage", "Monthly left"
        ])


def calculate_portfolio_value(df, yearly_return):
    if df.empty:
        return 0, 0, 0, 0, 0

    monthly_rate = (1 + yearly_return / 100) ** (1 / 12) - 1
    current_date = datetime.now()

    total_invested = 0
    current_portfolio_value = 0

    df['Date'] = pd.to_datetime(df.apply(lambda x: f"{x['Month']} {x['Year']}", axis=1))
    df_sorted = df.sort_values('Date')

    for _, row in df_sorted.iterrows():
        investment_date = row['Date']
        investment_amount = row['Expenses market']
        if investment_amount <= 0:
            continue

        months_passed = relativedelta(current_date, investment_date).months + \
                        12 * relativedelta(current_date, investment_date).years
        current_value = investment_amount * (1 + monthly_rate) ** months_passed

        total_invested += investment_amount
        current_portfolio_value += current_value

    portfolio_gains = current_portfolio_value - total_invested
    tax_amount = 0.25 * portfolio_gains if portfolio_gains > 0 else 0
    portfolio_after_tax = current_portfolio_value - tax_amount

    return current_portfolio_value, total_invested, portfolio_gains, tax_amount, portfolio_after_tax


# Main layout
st.title("💰 Personal Finance Dashboard")
col_input, col_summary, col_projection = st.columns([1.2, 1, 1])

with col_input:
    with st.expander("📝 Add New Month Data", expanded=True):
        with st.form("add_month_form", clear_on_submit=True):
            # Set current month as default
            month = st.selectbox("Month",
                                 options=months,
                                 index=months.index(current_month))
            current_year = st.number_input("Year", value=datetime.now().year, min_value=2000, max_value=2100)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Income")
                income_salary = st.number_input("Salary (₪)", value=0, step=100)
                income_plus = st.number_input("Additional Income (₪)", value=0, step=100)

            with c2:
                st.subheader("Expenses")
                expenses_day_to_day = st.number_input("Day-to-Day (₪)", value=0, step=100)
                expenses_rent = st.number_input("Rent (₪)", value=0, step=100)
                expenses_loan = st.number_input("Loan (₪)", value=0, step=100)
                expenses_market = st.number_input("Market Investment (₪)", value=0, step=100)
                expenses_taxes = st.number_input("Taxes (₪)", value=0, step=100)
                expenses_mortgage = st.number_input("Mortgage (₪)", value=0, step=100)

            monthly_left = income_salary + income_plus - (
                    expenses_day_to_day + expenses_rent + expenses_loan +
                    expenses_market + expenses_taxes + expenses_mortgage
            )

            submitted = st.form_submit_button("Add Month")
            if submitted:
                if not st.session_state.data.empty and any((st.session_state.data["Month"] == month) &
                                                           (st.session_state.data["Year"] == current_year)):
                    st.error(f"Data for {month} {current_year} already exists!")
                else:
                    new_row = {
                        "Month": month,
                        "Year": current_year,
                        "Income Salary": income_salary,
                        "Income plus": income_plus,
                        "Expenses Day-to-day": expenses_day_to_day,
                        "Expenses rent": expenses_rent,
                        "Expenses loan": expenses_loan,
                        "Expenses market": expenses_market,
                        "Expenses taxes": expenses_taxes,
                        "Expenses mortgage": expenses_mortgage,
                        "Monthly left": monthly_left,
                    }
                    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])],
                                                      ignore_index=True)
                    st.session_state.data.to_csv(file_path, index=False)
                    st.success(f"Added data for {month} {current_year}")

    if not st.session_state.data.empty:
        st.subheader("📊 Monthly Records")
        for index, row in st.session_state.data.iterrows():
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                st.write(f"{row['Month']} {row['Year']}: ₪{row['Monthly left']:,.2f}")
            with col2:
                if st.button("🗑", key=f"delete_{index}"):
                    st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
                    st.session_state.data.to_csv(file_path, index=False)
                    st.rerun()

with col_summary:
    st.subheader("📈 Financial Summary")

    if not st.session_state.data.empty:
        current_bank_account = st.session_state.data["Monthly left"].sum()
        yearly_return = st.slider("Yearly Stock Return (%)", min_value=0, max_value=20, value=7)

        current_portfolio, total_invested, portfolio_gains, tax_amount, portfolio_after_tax = \
            calculate_portfolio_value(st.session_state.data, yearly_return)

        overall_assets = current_bank_account + portfolio_after_tax

        st.metric("💳 Bank Account", f"₪{current_bank_account:,.2f}")
        st.metric("💰 Portfolio Investment", f"₪{total_invested:,.2f}")
        st.metric("📈 Portfolio Gains", f"₪{portfolio_gains:,.2f}")
        st.metric("💸 Tax Amount (25%)", f"₪{tax_amount:,.2f}")
        st.metric("📊 Portfolio After Tax", f"₪{portfolio_after_tax:,.2f}")
        st.metric("🏦 Total Assets", f"₪{overall_assets:,.2f}")

with col_projection:
    st.subheader("🔮 Portfolio Projection")

    if not st.session_state.data.empty:
        years = st.slider("Projection Years", min_value=1, max_value=10, value=5)
        future_months = pd.date_range(start=datetime.now(), periods=years * 12, freq="M")
        monthly_rate = (1 + yearly_return / 100) ** (1 / 12) - 1

        future_portfolio = [current_portfolio]
        for _ in range(len(future_months)):
            future_portfolio.append(future_portfolio[-1] * (1 + monthly_rate))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_months,
            y=future_portfolio[1:],
            mode='lines',
            name='Portfolio Value',
            line=dict(color="#00ff88", width=2)
        ))
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                title=None
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                title="Portfolio Value (₪)"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        final_portfolio_value = future_portfolio[-1]
        final_gains = final_portfolio_value - total_invested
        final_tax = 0.25 * final_gains if final_gains > 0 else 0
        final_value_after_tax = final_portfolio_value - final_tax

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Projected Value", f"₪{final_portfolio_value:,.2f}")
            st.metric("Projected Tax", f"₪{final_tax:,.2f}")
        with c2:
            st.metric("Projected Gains", f"₪{final_gains:,.2f}")
            st.metric("After Tax Value", f"₪{final_value_after_tax:,.2f}")

if not st.session_state.data.empty:
    with st.expander("📋 View Full Data Table"):
        st.dataframe(st.session_state.data, use_container_width=True)

st.markdown("---")
st.header("📊 Financial Analytics")

if not st.session_state.data.empty:
    # Prepare data
    df = st.session_state.data.copy()
    df['Date'] = pd.to_datetime(df.apply(lambda x: f"{x['Month']} {x['Year']}", axis=1))
    df = df.sort_values('Date')

    # Format dates for display
    df['Display_Date'] = df['Date'].dt.strftime('%b %Y')

    # 1. Income vs Expenses Breakdown
    st.subheader("Income vs Expenses Over Time")
    st.markdown(
        '<p style="font-size: 0.9em; color: #888888;">Shows your total monthly income (green) versus expenses (red), helping you track your spending relative to earnings.</p>',
        unsafe_allow_html=True)

    total_expenses = df['Expenses Day-to-day'] + df['Expenses rent'] + df['Expenses loan'] + \
                     df['Expenses market'] + df['Expenses taxes'] + df['Expenses mortgage']
    total_income = df['Income Salary'] + df['Income plus']

    fig_income_expenses = go.Figure()

    fig_income_expenses.add_trace(go.Scatter(
        x=df['Display_Date'],
        y=total_income,
        name='Total Income',
        line=dict(color='#00ff88', width=2),
        fill='tonexty'
    ))

    fig_income_expenses.add_trace(go.Scatter(
        x=df['Display_Date'],
        y=total_expenses,
        name='Total Expenses',
        line=dict(color='#ff4444', width=2),
        fill='tonexty'
    ))

    fig_income_expenses.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        yaxis_title="Amount (₪)",
        hovermode='x unified',
        xaxis_title=None
    )

    st.plotly_chart(fig_income_expenses, use_container_width=True)

    # 2. Expense Categories Breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Expense Distribution")
        st.markdown(
            '<p style="font-size: 0.9em; color: #888888;">Breakdown of your total expenses by category, showing where most of your money goes.</p>',
            unsafe_allow_html=True)

        expense_categories = {
            'Day-to-day': df['Expenses Day-to-day'].sum(),
            'Rent': df['Expenses rent'].sum(),
            'Loan': df['Expenses loan'].sum(),
            'Market Investment': df['Expenses market'].sum(),
            'Taxes': df['Expenses taxes'].sum(),
            'Mortgage': df['Expenses mortgage'].sum()
        }

        fig_pie = go.Figure(data=[go.Pie(
            labels=list(expense_categories.keys()),
            values=list(expense_categories.values()),
            hole=0.4,
            marker=dict(colors=['#00ff88', '#00cc88', '#008866', '#ff4444', '#cc4444', '#884444'])
        )])

        fig_pie.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Monthly Savings Rate")
        st.markdown(
            '<p style="font-size: 0.9em; color: #888888;">Your monthly savings as a percentage of income, with dashed line showing the average rate.</p>',
            unsafe_allow_html=True)

        savings_rate = (df['Monthly left'] / total_income * 100).round(2)

        fig_savings = go.Figure()

        fig_savings.add_trace(go.Scatter(
            x=df['Display_Date'],
            y=savings_rate,
            mode='lines+markers',
            name='Savings Rate',
            line=dict(color='#00ff88', width=2),
            marker=dict(size=8)
        ))

        fig_savings.add_hline(
            y=savings_rate.mean(),
            line_dash="dash",
            line_color="white",
            annotation_text=f"Average: {savings_rate.mean():.1f}%"
        )

        fig_savings.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            yaxis_title="Savings Rate (%)",
            yaxis_range=[0, max(100, savings_rate.max() * 1.1)],
            xaxis_title=None
        )

        st.plotly_chart(fig_savings, use_container_width=True)

    # 3. Monthly Investment Growth
    st.subheader("Investment Contributions Over Time")
    st.markdown(
        '<p style="font-size: 0.9em; color: #888888;">Monthly investment amounts (bars) and cumulative total invested (white line) over time.</p>',
        unsafe_allow_html=True)

    fig_investment = go.Figure()

    fig_investment.add_trace(go.Bar(
        x=df['Display_Date'],
        y=df['Expenses market'],
        name='Monthly Investment',
        marker_color='#00ff88'
    ))

    fig_investment.add_trace(go.Scatter(
        x=df['Display_Date'],
        y=df['Expenses market'].cumsum(),
        name='Cumulative Investment',
        line=dict(color='white', width=2),
        yaxis='y2'
    ))

    fig_investment.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        yaxis_title="Monthly Investment (₪)",
        yaxis2=dict(
            title="Cumulative Investment (₪)",
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        hovermode='x unified',
        xaxis_title=None
    )

    st.plotly_chart(fig_investment, use_container_width=True)

    # 4. Key Metrics
    st.subheader("Key Financial Metrics")
    st.markdown('''
            <p style="font-size: 0.9em; color: #888888;">
            Summary of important financial indicators and their trends:
            <br>• <b>Avg Monthly Savings</b>: Your average money left after all expenses each month. The delta shows how your latest month compares to this average.
            <br>• <b>Avg Savings Rate</b>: The percentage of your income you typically save each month. The delta indicates if your latest month's savings rate was above or below average.
            <br>• <b>Expense Efficiency</b>: The ratio of essential expenses (rent, mortgage, loan) to discretionary spending (day-to-day). Lower is better, indicating more controlled daily spending.
            <br>• <b>Monthly Investment Ratio</b>: Your average monthly investment as a percentage of monthly income. Shows investment consistency relative to earnings.
            </p>
            ''', unsafe_allow_html=True)

    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

    with metrics_col1:
        average_savings = df['Monthly left'].mean()
        st.metric(
            "Avg Monthly Savings",
            f"₪{average_savings:,.2f}",
            delta=f"₪{df['Monthly left'].iloc[-1] - average_savings:,.2f} vs avg"
        )

    with metrics_col2:
        avg_savings_rate = savings_rate.mean()
        st.metric(
            "Avg Savings Rate",
            f"{avg_savings_rate:.1f}%",
            delta=f"{savings_rate.iloc[-1] - avg_savings_rate:.1f}% vs avg"
        )

    with metrics_col3:
        # Calculate essential vs discretionary spending ratio
        essential_expenses = df['Expenses rent'] + df['Expenses mortgage'] + df['Expenses loan']
        discretionary_expenses = df['Expenses Day-to-day']
        expense_ratio = (essential_expenses / discretionary_expenses).mean()
        current_ratio = (essential_expenses.iloc[-1] / discretionary_expenses.iloc[-1])

        st.metric(
            "Expense Efficiency",
            f"{expense_ratio:.2f}",
            delta=f"{current_ratio - expense_ratio:.2f} vs avg",
            delta_color="inverse"  # Lower is better for this metric
        )

    with metrics_col4:
        # Calculate average monthly investment ratio
        monthly_investment_ratios = (df['Expenses market'] / (df['Income Salary'] + df['Income plus']) * 100)
        avg_monthly_investment_ratio = monthly_investment_ratios.mean()
        current_investment_ratio = monthly_investment_ratios.iloc[-1]

        st.metric(
            "Monthly Investment Ratio",
            f"{avg_monthly_investment_ratio:.1f}%",
            delta=f"{current_investment_ratio - avg_monthly_investment_ratio:.1f}% vs avg"
        )
else:
    st.info("Add some financial data to see the analytics!")
