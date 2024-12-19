import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# Page configuration
st.set_page_config(layout="wide", page_title="Finance Dashboard", page_icon="💰")

# CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    .row-widget.stButton {
        text-align: right;
    }
    div[data-testid="stExpander"] {
        background-color: #1e1e1e;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

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
            month = st.selectbox("Month", options=[
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ])
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
