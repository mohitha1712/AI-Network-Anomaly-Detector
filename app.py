import streamlit as st
from model import run_detection
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="AI Network Surveillance System", layout="wide")

# 🔄 Refresh Button
if st.sidebar.button("🔄 Refresh Live Data"):
    st.rerun()

# ===============================
# 🩸 CSS (UNCHANGED)
# ===============================
st.markdown("""
<style>
.stApp {background: radial-gradient(circle at center, #1a0000, #000000 80%); color:#ff4d4d;}
.title {text-align:center;font-size:55px;color:#ff0000;text-shadow:0 0 20px red;animation:flicker 1.5s infinite;}
@keyframes flicker {50% {opacity:0.5;}}
.card {background: rgba(20,0,0,0.8);border:1px solid red;padding:20px;border-radius:12px;text-align:center;box-shadow:0 0 20px red;}
.alert {text-align:center;font-size:22px;color:red;animation:blink 1s infinite;}
@keyframes blink {50% {opacity:0.3;}}
</style>
""", unsafe_allow_html=True)

# ===============================
# TITLE (UPDATED)
# ===============================
st.markdown('<div class="title">⚠️ AI NETWORK SURVEILLANCE SYSTEM ⚠️</div>', unsafe_allow_html=True)

# ===============================
# SIDEBAR (UPDATED TEXT ONLY)
# ===============================
st.sidebar.title("🎛️ Control Panel")

panel = st.sidebar.radio("Select Mode", ["📡 Monitoring", "📊 Analysis", "🚨 Detection"])

live_mode = st.sidebar.toggle("🔴 Live Monitoring")
search_ip = st.sidebar.text_input("🔍 Search IP")

# ===============================
# LOAD DATA
# ===============================
mode = "live" if live_mode else "csv"
data = run_detection(mode=mode)

# fallback
if data.empty:
    data = run_detection(mode="csv")
    st.warning("⚠️ No live traffic detected → Using sample dataset")

# ===============================
# FILTER
# ===============================
if search_ip:
    data = data[data["IP_Address"].str.contains(search_ip)]

# ===============================
# SYSTEM HEALTH
# ===============================
anomaly_count = len(data[data["Status"] == "Anomaly"])
total = len(data)

ratio = anomaly_count / total if total > 0 else 0

if anomaly_count == 0:
    st.success("🟢 SYSTEM STATUS: SAFE")
elif ratio < 0.3:
    st.warning("🟡 SYSTEM STATUS: UNSTABLE")
else:
    st.error("🔴 SYSTEM STATUS: CRITICAL")

# ===============================
# CLOCK
# ===============================
st.write("🕒 Time:", datetime.datetime.now().strftime("%H:%M:%S"))

# ===============================
# RISK LEVEL
# ===============================
def risk(row):
    if row["Status"] == "Normal":
        return "LOW"
    if row["Requests"] > 700:
        return "CRITICAL"
    elif row["Requests"] > 300:
        return "HIGH"
    elif row["Data_Size"] > 1000:
        return "MEDIUM"
    return "LOW"

data["Risk"] = data.apply(risk, axis=1)

# ===============================
# TOP IP (UPDATED TEXT)
# ===============================
anomalies = data[data["Status"] == "Anomaly"]
if not anomalies.empty:
    st.error("🎯 Most Suspicious IP: " + str(anomalies.iloc[0]["IP_Address"]))

# ===============================
# KPI
# ===============================
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card">🌐 Total Signals<br><h2>{len(data)}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card">🟢 Normal Traffic<br><h2>{len(data[data["Status"]=="Normal"])}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card">🔴 Anomalies<br><h2>{len(data[data["Status"]=="Anomaly"])}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card">⚡ Critical Threats<br><h2>{len(data[data["Risk"]=="CRITICAL"])}</h2></div>', unsafe_allow_html=True)

# ===============================
# MONITORING
# ===============================
if panel == "📡 Monitoring":
    st.subheader("📡 Live Network Feed")
    st.dataframe(data)

# ===============================
# ANALYSIS
# ===============================
elif panel == "📊 Analysis":

    st.subheader("📊 Network Traffic Analysis")

    data = data.fillna(0)
    data = data.reset_index(drop=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data["Requests"],
        mode='lines+markers',
        name="Requests",
        connectgaps=True,
        line=dict(width=3, shape='spline')
    ))

    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data["Data_Size"],
        mode='lines+markers',
        name="Data Size",
        connectgaps=True,
        line=dict(width=3, shape='spline')
    ))

    anomalies = data[data["Status"] == "Anomaly"]

    fig.add_trace(go.Scatter(
        x=anomalies.index,
        y=anomalies["Requests"],
        mode='markers',
        name="Anomaly",
        marker=dict(size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Live Network Signal Flow",
        xaxis_title="Time Index",
        yaxis_title="Traffic Volume"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Anomaly Trend")
    st.line_chart(data["Status"].apply(lambda x: 1 if x == "Anomaly" else 0))

    st.subheader("📊 Traffic Distribution")
    st.bar_chart(data["Status"].value_counts())

# ===============================
# DETECTION
# ===============================
elif panel == "🚨 Detection":

    st.subheader("🚨 Threat Detection System")

    anomalies = data[data["Status"] == "Anomaly"]

    if not anomalies.empty:

        st.markdown('<div class="alert">⚠️ AI detected anomalous network activity</div>', unsafe_allow_html=True)

        anomalies = anomalies.sort_values(by="Requests", ascending=False)

        for i in range(len(anomalies)):

            row = anomalies.iloc[i]

            if row["Risk"] == "CRITICAL":
                st.error("🔥 CRITICAL THREAT DETECTED")
            elif row["Risk"] == "HIGH":
                st.warning("⚠️ HIGH RISK ACTIVITY")
            else:
                st.success("🟢 LOW RISK ACTIVITY")

            st.markdown(f"""
            **IP Address:** {row['IP_Address']}  
            **Requests:** {row['Requests']}  
            **Data Size:** {row['Data_Size']}  
            **Reason:** {row['Reason']}  
            """)

            st.markdown("---")

    else:
        st.success("System Stable — No Threats Detected")

# ===============================
# DOWNLOAD
# ===============================
csv = data.to_csv(index=False)
st.download_button("⬇️ Download Report", csv, "network_report.csv")

st.progress(90)
st.caption("⚡ Real-Time AI Network Monitoring System")