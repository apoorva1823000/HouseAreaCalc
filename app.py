import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# Page Setup
# -----------------------------------
st.set_page_config(page_title="Floorplan & Area Calculator", layout="wide")

st.title("🏠 Floorplan & Area Calculator")
st.caption("Enter room counts → dimensions → get areas + auto floorplan.")

# -----------------------------------
# Helper Functions
# -----------------------------------
def to_feet(ft, inch):
    return ft + inch / 12

def room_area(l_ft, l_in, b_ft, b_in):
    return to_feet(l_ft, l_in) * to_feet(b_ft, b_in)

def draw_floorplan(df):
    if df.empty:
        st.info("Add rooms to view floorplan.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 10))
    offset_y = 0

    for _, row in df.iterrows():
        L = row["Length (ft)"]
        B = row["Breadth (ft)"]

        rect = plt.Rectangle((0, offset_y), L, B, fill=None, edgecolor='black', linewidth=1.2)
        ax.add_patch(rect)

        ax.text(L/2, offset_y + B/2,
                f"{row['Room']}\n{row['Area (sqft)']:.1f} sq ft",
                ha='center', va='center', fontsize=8)

        offset_y += B + 1

    ax.set_xlim(0, df["Length (ft)"].max() + 3)
    ax.set_ylim(0, offset_y + 3)
    ax.set_aspect("equal")
    ax.set_title("Floorplan (Diagrammatic)")
    ax.invert_yaxis()

    st.pyplot(fig)

# -----------------------------------
# Define Room Types
# -----------------------------------
room_types = {
    "Bedrooms": "Bedroom",
    "Toilets": "Toilet",
    "Drawing Room": "Drawing",
    "Foyer": "Foyer",
    "Dining": "Dining",
    "Kitchen": "Kitchen",
    "Wash Area": "Wash",
    "Balcony": "Balcony",
    "Store Room": "Store"
}

# -----------------------------------
# Room Counts (Cleaner UI)
# -----------------------------------
st.subheader("1️⃣ Select Room Counts")

cols = st.columns(3)
room_counts = {}
i = 0

for label in room_types:
    room_counts[label] = cols[i].number_input(label, min_value=0, max_value=10, value=0)
    i = (i + 1) % 3


# -----------------------------------
# Room Inputs
# -----------------------------------
st.subheader("2️⃣ Enter Room Dimensions")

summary = []
total_area = 0

for label, prefix in room_types.items():
    count = room_counts[label]
    if count == 0:
        continue

    with st.expander(f"{label} ({count})"):
        for i in range(1, count + 1):
            cols = st.columns(4)
            
            L_ft = cols[0].number_input(f"L ft - {i}", min_value=0.0, key=f"{prefix}_Lft_{i}")
            L_in = cols[1].number_input(f"L in - {i}", min_value=0.0, key=f"{prefix}_Lin_{i}")
            B_ft = cols[2].number_input(f"B ft - {i}", min_value=0.0, key=f"{prefix}_Bft_{i}")
            B_in = cols[3].number_input(f"B in - {i}", min_value=0.0, key=f"{prefix}_Bin_{i}")

            area = room_area(L_ft, L_in, B_ft, B_in)
            total_area += area

            st.write(f"➡ **Room {i} Area:** {area:.2f} sq ft")

            summary.append({
                "Room": f"{prefix} {i}",
                "Category": label,
                "Length (ft)": to_feet(L_ft, L_in),
                "Breadth (ft)": to_feet(B_ft, B_in),
                "Area (sqft)": area
            })


# -----------------------------------
# Summary Table
# -----------------------------------
df = pd.DataFrame(summary)

st.subheader("3️⃣ Summary")

if df.empty:
    st.info("Add rooms to see data.")
else:
    st.dataframe(df, height=300)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "area_summary.csv", "text/csv")


# -----------------------------------
# Floorplan Visualizer
# -----------------------------------
st.subheader("4️⃣ Floorplan Preview")
draw_floorplan(df)


# -----------------------------------
# Totals
# -----------------------------------
st.subheader("5️⃣ Total Areas")

if not df.empty:
    total_sqft = total_area
    total_sqyd = total_sqft / 9
    claimed_area = total_sqft / 0.75

    st.metric("Carpet Area", f"{total_sqft:.1f} sq ft", "")
    st.metric("Carpet Area", f"{total_sqyd:.1f} sq yd")
    st.write("---")
    st.metric("Claimed Area", f"{claimed_area:.1f} sq ft")
    st.metric("Claimed Area", f"{claimed_area/9:.1f} sq yd")

    st.success("Done!")

