import streamlit as st
import pandas as pd
import random
import requests
import json

# --- Simulation Backend ---
class SocietyState:
    def __init__(self, controls):
        self.controls = controls
        self.metrics = {
            "Happiness": max(0, 100 - (
                0.6 * controls["Leadership Power"] +
                0.6 * controls["Propaganda"] +
                0.5 * controls["Class Stratification"] +
                0.4 * controls["Surveillance"]
            )),
            "Innovation": max(0, (
                0.5 * controls["Education"] -
                0.7 * controls["Propaganda"] -
                0.6 * controls["Ideology"]
            )),
            "Cohesion": max(0, 100 - (
                0.7 * controls["Class Stratification"] +
                0.6 * controls["Freedom of Speech"]
            )),
            "Inequality": min(100, controls["Class Stratification"] + random.randint(-5, 5)),
            "Knowledge": max(0, (
                0.8 * controls["Education"] -
                0.8 * controls["Historical Revisionism"]
            )),
            "Productivity": 50,
            "Trust": max(0, 100 - (
                0.6 * controls["Leadership Power"] +
                0.5 * controls["Surveillance"] +
                0.5 * controls["Freedom of Speech"]
            )),
            "Rebellion Risk": 20 + 0.5 * controls["Class Stratification"]
        }

    def tick(self):
        c = self.controls
        m = self.metrics
        rand = lambda a=5: random.randint(-a, a)

        m["Happiness"] = max(0, min(100, (60 - 0.2 * c["Leadership Power"] - 0.2 * c["Surveillance"] - 0.2 * c["Propaganda"] - 0.2 * c["Class Stratification"] + 0.3 * c["Freedom of Speech"]) + rand()))
        m["Trust"] = max(0, min(100, (60 - 0.3 * c["Leadership Power"] - 0.2 * c["Surveillance"] - 0.2 * c["Propaganda"] + 0.2 * c["Education"] + 0.3 * c["Freedom of Speech"]) + rand()))
        m["Innovation"] = max(0, min(100, (0.4 * c["Education"] + 0.3 * c["Freedom of Speech"] + 0.2 * (100 - c["Propaganda"]) + 0.1 * (100 - c["Ideology"])) + rand()))
        m["Knowledge"] = max(0, min(100, (0.5 * c["Education"] + 0.3 * (100 - c["Historical Revisionism"]) + 0.2 * (100 - c["Propaganda"])) + rand()))
        m["Cohesion"] = max(0, min(100, (60 - 0.3 * c["Class Stratification"] - 0.2 * c["Surveillance"] - 0.2 * c["International Isolation"] + 0.3 * c["Freedom of Speech"]) + rand()))
        m["Productivity"] = max(0, min(100, (m["Happiness"] + m["Innovation"]) / 2 + rand()))
        m["Inequality"] = max(0, min(100, c["Class Stratification"] + rand()))
        m["Rebellion Risk"] = max(0, min(100, (10 + 0.25 * (100 - m["Happiness"]) + 0.25 * (100 - m["Trust"]) + 0.25 * m["Inequality"] + 0.2 * c["International Isolation"]) + rand(3)))

        event_pool = self.event_pool()
        if event_pool:
            event = random.choice(event_pool)
            effect_summary = []
            for key, delta in event["effects"].items():
                if key in m:
                    old_value = m[key]
                    m[key] = max(0, min(100, m[key] + delta))
                    effect_summary.append(f"{key}: {old_value:.1f} → {m[key]:.1f} ({'+' if delta >= 0 else ''}{delta})")
            effect_text = "; ".join(effect_summary) if effect_summary else "No metric changes."
            self.event_log.append({"description": event["description"], "effects": effect_text})

        self.history.append(m.copy())

    def run(self, years=20):
        self.history = []
        self.event_log = []
        ticks = int(years)  # Change here
        for _ in range(ticks):
            self.tick()
        return pd.DataFrame(self.history)

    def event_pool(self):
        c = self.controls
        m = self.metrics
        pool = [
            {"description": "Mass protests erupt across major cities demanding reform.", "effects": {"Trust": -15, "Cohesion": -10, "Rebellion Risk": +25}},
            {"description": "A violent uprising shakes the foundation of government control.", "effects": {"Happiness": -25, "Trust": -25, "Cohesion": -20, "Rebellion Risk": +15}},
            {"description": "A scientific breakthrough improves public health and technology.", "effects": {"Innovation": +10, "Happiness": +10, "Productivity": +5}},
            {"description": "Civic harmony leads to stronger communities and cooperation.", "effects": {"Cohesion": +10, "Trust": +10, "Productivity": +5}},
            {"description": "A major whistleblower reveals massive surveillance abuses.", "effects": {"Trust": -25, "Happiness": -10, "Rebellion Risk": +15}},
            {"description": "Censorship policies silence dissidents and stoke underground resistance.", "effects": {"Cohesion": -10, "Trust": -15, "Rebellion Risk": +20}},
            {"description": "Factories shut down as productivity hits new lows.", "effects": {"Happiness": -15, "Innovation": -10, "Rebellion Risk": +10}},
            {"description": "Growing wealth gap leads to unrest among the working class.", "effects": {"Inequality": +10, "Happiness": -10, "Rebellion Risk": +15}},
            {"description": "Widespread automation causes mass job displacement.", "effects": {"Happiness": -15, "Trust": -10, "Rebellion Risk": +15}},
            {"description": "Propaganda campaign backfires, causing public confusion.", "effects": {"Trust": -10, "Knowledge": -10, "Rebellion Risk": +5}},
            {"description": "Foreign investment boosts national industry.", "effects": {"Productivity": +10, "Innovation": +5, "Trust": +5}},
            {"description": "Extreme ideological enforcement sparks division.", "effects": {"Cohesion": -15, "Trust": -10, "Happiness": -10}},
            {"description": "Discovery of altered historical records undermines government credibility.", "effects": {"Knowledge": +10, "Trust": -15, "Rebellion Risk": +10}},
            {"description": "Grassroots movements promote reform and open dialogue.", "effects": {"Cohesion": +10, "Trust": +10, "Rebellion Risk": -5}},
            {"description": "Public festivals and arts flourish, boosting morale.", "effects": {"Happiness": +10, "Cohesion": +5}},
            {"description": "Economic sanctions cripple trade and lead to shortages.", "effects": {"Productivity": -20, "Happiness": -15, "Trust": -10}},
            {"description": "A new charismatic leader emerges, challenging the established order.", "effects": {"Rebellion Risk": +10, "Cohesion": -5, "Trust": -5}},
            {"description": "Government launches a massive public works program.", "effects": {"Productivity": +15, "Happiness": +10, "Inequality": -5}},
            {"description": "A period of severe drought leads to famine and unrest.", "effects": {"Happiness": -20, "Cohesion": -15, "Rebellion Risk": +20}},
            {"description": "The ruling party cracks down on dissent, arresting activists and journalists.", "effects": {"Freedom of Speech": -30, "Trust": -20, "Rebellion Risk": +10}},
            {"description": "Major technological advancement transforms daily life.", "effects": {"Innovation": +20, "Productivity": +10, "Knowledge": +10}},
            {"description": "War breaks out with a neighboring nation.", "effects": {"Happiness": -30, "Trust": -20, "Rebellion Risk": +25}},
            {"description": "A peace treaty is signed, ending a long and costly conflict.", "effects": {"Happiness": +20, "Trust": +15, "Productivity": +10}},
            {"description": "Inflation spirals out of control, devaluing wages and savings.", "effects": {"Happiness": -25, "Inequality": +15, "Rebellion Risk": +10}},
            {"description": "A new educational reform improves literacy and critical thinking.", "effects": {"Education": +20, "Knowledge": +15, "Innovation": +10}},
            {"description": "A cultural renaissance celebrates national identity and heritage.", "effects": {"Cohesion": +15, "Happiness": +10, "Trust": +5}},
            {"description": "Corruption scandal rocks the government, leading to widespread outrage.", "effects": {"Trust": -30, "Rebellion Risk": +20, "Cohesion": -10}},
            {"description": "Strict new environmental regulations are enacted.", "effects": {"Productivity": -10, "Innovation": +5, "Happiness": +5}},
            {"description": "A wave of immigration diversifies the population.", "effects": {"Cohesion": -10, "Innovation": +10, "Knowledge": +5}},
            {"description": "A natural disaster devastates a major city.", "effects": {"Happiness": -20, "Cohesion": -20, "Productivity": -15}},
            {"description": "The government seizes private property for the 'greater good'.", "effects": {"Trust": -25, "Rebellion Risk": +15, "Inequality": +10}},
            {"description": "International trade agreement boosts exports and economic growth.", "effects": {"Productivity": +20, "Innovation": +10, "Trust": +10}},
            {"description": "Outbreak of a deadly epidemic strains healthcare system.", "effects": {"Happiness": -25, "Trust": -15, "Cohesion": -15}},
            {"description": "Discovery of a new energy source transforms industry.", "effects": {"Productivity": +25, "Innovation": +20, "Environmental Impact": -10}},
            {"description": "A period of economic recession leads to widespread unemployment.", "effects": {"Happiness": -30, "Productivity": -20, "Rebellion Risk": +20}},
            {"description": "Government invests heavily in arts and culture.", "effects": {"Happiness": +15, "Cohesion": +10, "Innovation": +5}},
            {"description": "Space exploration program yields new scientific discoveries.", "effects": {"Knowledge": +20, "Innovation": +15, "Prestige": +10}},
            {"description": "A new social movement gains momentum, advocating for change.", "effects": {"Cohesion": -10, "Trust": +10, "Rebellion Risk": +5}},
            {"description": "Government imposes strict controls on information and media.", "effects": {"Freedom of Speech": -30, "Knowledge": -20, "Trust": -20}},
            {"description": "A period of relative peace and prosperity.", "effects": {"Happiness": +10, "Trust": +10, "Productivity": +10}},
            {"description": "New laws are enacted to promote equality and social justice.", "effects": {"Inequality": -15, "Cohesion": +10, "Trust": +10}},
            {"description": "The gap between rich and poor widens significantly.", "effects": {"Inequality": +20, "Happiness": -15, "Rebellion Risk": +15}},
            {"description": "A new form of art or music captivates the nation.", "effects": {"Happiness": +10, "Cohesion": +5, "Innovation": +5}},
            {"description": "The government's authority is questioned after a series of failures.", "effects": {"Trust": -25, "Leadership Power": -10, "Rebellion Risk": +10}},
            {"description": "Citizens become more politically engaged and active in civic life.", "effects": {"Freedom of Speech": +15, "Cohesion": +10, "Trust": +5}},
            {"description": "A new philosophical idea spreads, challenging traditional beliefs.", "effects": {"Knowledge": +10, "Ideology": +10, "Cohesion": -5}},
            {"description": "Advances in medicine increase life expectancy.", "effects": {"Happiness": +10, "Productivity": +5, "Healthcare Quality": +10}},
            {"description": "The nation's infrastructure is modernized.", "effects": {"Productivity": +15, "Innovation": +10, "Cohesion": +5}},
            {"description": "A period of rapid social change and upheaval.", "effects": {"Cohesion": -20, "Trust": -15, "Rebellion Risk": +20}},
            {"description": "The government successfully addresses a major social problem.", "effects": {"Happiness": +15, "Trust": +15, "Cohesion": +10}}
        ]
        return pool


# --- Streamlit Frontend ---
st.set_page_config(page_title="Orwellian Society Simulator", layout="wide")
st.title("🌍 Orwellian Society Simulator")

st.sidebar.header("Adjust Society Controls")
controls = {
    "Leadership Power": st.sidebar.slider("Leadership Power", 0, 100, 50),
    "Propaganda": st.sidebar.slider("Propaganda", 0, 100, 50),
    "Class Stratification": st.sidebar.slider("Class Stratification", 0, 100, 50),
    "Surveillance": st.sidebar.slider("Surveillance", 0, 100, 50),
    "Education": st.sidebar.slider("Education", 0, 100, 50),
    "Historical Revisionism": st.sidebar.slider("Historical Revisionism", 0, 100, 20),
    "Freedom of Speech": st.sidebar.slider("Freedom of Speech", 0, 100, 50),
    "International Isolation": st.sidebar.slider("International Isolation", 0, 100, 40),
    "Ideology": st.sidebar.slider("Ideology", 0, 100, 50),
}

years = st.sidebar.slider("Years to Simulate", 1, 50, 20)
society = SocietyState(controls)
df = society.run(years=years)

st.subheader("Society Metrics Over Time")
st.line_chart(df)

st.subheader("Society Analysis")
response = requests.post(
    "https://ai.hackclub.com/chat/completions",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "messages": [{"role": "user", "content": f"Summarize this simulated society: {df.iloc[-1:].to_dict()}. Do not reference quantitative data, create a detailed 3 paragraph qualitative summary about the intial state, evolution, and final state of the society. "}]
    })
)
if response.status_code == 200:
    summary = response.json()["choices"][0]["message"]["content"]
    st.markdown(f"<div style='border-left: 1px solid white; padding-left: 10px;'>{summary}</div>", unsafe_allow_html=True)
else:
    st.error("Failed to retrieve AI summary.")

st.subheader("Final Metrics")
st.table(df.iloc[-1:].T.rename(columns={df.index[-1]: "Value"}))

st.subheader("Event Log")
for year, event in enumerate(society.event_log, start=1): # changed tick to year
    st.markdown(f"**Year {year:.0f}**:  {event['description']}") # removed tick
    st.markdown(f"<span style='color: gray;'>  - Effects: {event['effects']}</span>", unsafe_allow_html=True)
