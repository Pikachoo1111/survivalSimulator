import streamlit as st
import pandas as pd
import random

# --- Simulation Backend ---
class SocietyState:
    def __init__(self, controls):
        self.controls = controls
        # Set initial metrics based on the control variables
        self.metrics = {
            "Happiness": 70 - 0.4 * controls["Leadership Power"] - 0.3 * controls["Propaganda"],
            "Innovation": 70 - 0.6 * controls["Propaganda"] - 0.5 * controls["Ideology"],
            "Cohesion": 70 - 0.4 * controls["Class Stratification"] - 0.3 * controls["Freedom of Speech"],
            "Inequality": controls["Class Stratification"],
            "Knowledge": 80 - 0.7 * controls["Education"] - 0.4 * controls["Historical Revisionism"],
            "Productivity": 70,
            "Trust": 70 - 0.5 * controls["Leadership Power"] - 0.3 * controls["Surveillance"],
            "Rebellion Risk": 20 + 0.3 * controls["Class Stratification"],  # Base rebellion risk
        }
        self.history = []
        self.event_log = []

    def tick(self):
        c = self.controls
        m = self.metrics

        # Adjust happiness calculation based on controls
        happiness_effect = (
            0.4 * c["Leadership Power"] +
            0.3 * c["Propaganda"] +
            0.4 * c["Class Stratification"] +
            0.3 * c["Surveillance"] +
            0.3 * c["Freedom of Speech"]
        )
        m["Happiness"] = max(30, min(100, 70 - happiness_effect + random.randint(-7, 7)))  # Prevent below 30

        # Innovation, cohesion, inequality, knowledge, productivity, and trust calculations remain as before
        m["Innovation"] = max(0, min(100, 0.6 * (100 - c["Propaganda"]) + 0.5 * (100 - c["Ideology"]) + random.randint(-10, 10)))
        m["Cohesion"] = max(0, min(100, 70 - (0.4 * c["Class Stratification"] + 0.3 * c["Freedom of Speech"] + 0.3 * c["Surveillance"]) + random.randint(-5, 5)))
        m["Inequality"] = min(100, max(0, c["Class Stratification"] + random.randint(-7, 7)))
        m["Knowledge"] = max(0, min(100, 0.7 * (100 - c["Education"]) + 0.4 * (100 - c["Historical Revisionism"]) + random.randint(-7, 7)))
        m["Productivity"] = max(0, min(100, (m["Innovation"] + m["Happiness"]) / 2 + random.randint(-7, 7)))
        m["Trust"] = max(0, min(100, 70 - (0.5 * c["Leadership Power"] + 0.3 * c["Freedom of Speech"] + 0.3 * c["Surveillance"]) + random.randint(-5, 5)))

        # Rebellion risk now adjusts more dynamically, depending on the initial values and the current state
        m["Rebellion Risk"] = max(10, min(100, 20 + (100 - m["Happiness"] - m["Trust"] + m["Inequality"]) / 3 + random.randint(-5, 5)))

        # Increase event frequency to make them more common
        if random.random() < 0.5:  # 50% chance for an event (previously 20%)
            event = random.choice(self.event_pool())
            for key, delta in event["effects"].items():
                if key in m:
                    m[key] = max(0, min(100, m[key] + delta))
            self.event_log.append(event["description"])
        else:
            self.event_log.append("No significant event.")

        self.history.append(m.copy())

    def run(self, years=20):
        self.history = []
        self.event_log = []
        for year in range(years):
            # Simulate twice per year (every 6 months)
            for _ in range(2):
                self.tick()
        return pd.DataFrame(self.history)

    def event_pool(self):
        return [
            {
                "description": "A severe economic recession plunges society into chaos.",
                "effects": {"Happiness": -15, "Trust": -15, "Productivity": -10, "Rebellion Risk": +20}
            },
            {
                "description": "A viral epidemic overwhelms healthcare, leading to panic.",
                "effects": {"Trust": -20, "Happiness": -10, "Cohesion": -5, "Rebellion Risk": +15}
            },
            {
                "description": "An intense wave of protests leads to violent suppression.",
                "effects": {"Rebellion Risk": +30, "Happiness": -10, "Trust": -20}
            },
            {
                "description": "A new technology revolutionizes industry, spurring growth.",
                "effects": {"Innovation": +15, "Productivity": +10, "Happiness": +5}
            },
            {
                "description": "A major international treaty opens up trade and investment.",
                "effects": {"Trust": +15, "Innovation": +10, "Productivity": +10, "Happiness": +5}
            },
            {
                "description": "Corruption scandal leads to the resignation of key officials.",
                "effects": {"Trust": -30, "Happiness": -15, "Rebellion Risk": +25}
            },
            {
                "description": "A popular leader's speech reassures the public and boosts morale.",
                "effects": {"Happiness": +15, "Trust": +20, "Cohesion": +5}
            },
            {
                "description": "Unemployment rate spikes dramatically due to automation.",
                "effects": {"Happiness": -20, "Trust": -15, "Inequality": +10, "Rebellion Risk": +20}
            },
        ]

# --- Streamlit Frontend ---
st.set_page_config(page_title="Orwellian Society Simulator", layout="wide")
st.title("🌍 Orwellian Society Simulator")

st.markdown("Adjust the control sliders below to shape your society. Each year, a random event may occur that influences your simulation.")

# Control sliders
controls = {}
control_names = [
    "Leadership Power",
    "Propaganda",
    "Historical Revisionism",
    "Education",
    "Freedom of Speech",
    "Class Stratification",
    "Surveillance",
    "Police/Military Power",
    "Ideology",
    "International Isolation"
]

with st.sidebar:
    st.header("🛠️ Control Variables")
    for name in control_names:
        controls[name] = st.slider(name, 0, 100, 50)

years = st.slider("Years to Simulate", 1, 100, 20)

if st.button("Run Simulation"):
    society = SocietyState(controls)
    df = society.run(years)

    st.subheader("📊 Metric Trends Over Time")
    st.line_chart(df)

    st.subheader("📋 Final Metric Values")
    st.dataframe(df.iloc[-1].to_frame().T.style.highlight_max(axis=1))

    st.subheader("📜 Random Event Log")
    for year, event in enumerate(society.event_log, start=1):
        st.markdown(f"**Year {year}**: {event}")
