import pandas as pd
from sklearn.ensemble import IsolationForest
from live_capture import capture_live


def run_detection(mode="live"):

    # ===============================
    # LOAD DATA
    # ===============================
    if mode == "live":
        data = capture_live(duration=15)
    else:
        data = pd.read_csv("network_data.csv", sep=",", engine="python")

    # If empty → return
    if data.empty:
        return data

    # ===============================
    #  CLEAN COLUMN NAMES
    # ===============================
    data.columns = data.columns.str.strip()

    # ===============================
    #  CHECK REQUIRED COLUMNS
    # ===============================
    required = ["IP_Address", "Requests", "Data_Size"]

    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(f"❌ Missing columns: {missing} | Found: {data.columns.tolist()}")

    # ===============================
    #  SELECT ONLY REQUIRED COLUMNS
    # ===============================
    data = data[required]

    # ===============================
    #  HANDLE MISSING VALUES
    # ===============================
    data = data.fillna(0)

    # Ensure numeric
    data["Requests"] = pd.to_numeric(data["Requests"], errors="coerce").fillna(0)
    data["Data_Size"] = pd.to_numeric(data["Data_Size"], errors="coerce").fillna(0)

    # ===============================
    # MODEL
    # ===============================
    features = data[["Requests", "Data_Size"]]

    model = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )

    model.fit(features)

    predictions = model.predict(features)
    scores = model.decision_function(features)

    # ===============================
    # RESULTS
    # ===============================
    data["Status"] = ["Anomaly" if p == -1 else "Normal" for p in predictions]

    reasons = []
    for i in range(len(data)):
        if data.loc[i, "Status"] == "Anomaly":
            if data.loc[i, "Requests"] > 100:
                reasons.append("High Traffic Spike")
            elif data.loc[i, "Data_Size"] > 1000:
                reasons.append("High Data Usage")
            else:
                reasons.append("Unusual Behavior")
        else:
            reasons.append("Normal Activity")

    data["Reason"] = reasons
    data["Score"] = scores

    return data
