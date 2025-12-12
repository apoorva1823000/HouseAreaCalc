
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced Floorplan & Area Calculator", layout="wide")
st.title("Flexible Area Calculator with Auto Floorplan Visualizer")

# ---------------------------
# Helper Functions
# ---------------------------
def to_feet(feet, inches):
    return feet + inches / 12

def room_area(length_ft, length_in, breadth_ft, breadth_in):
    L = to_feet(length_ft, length_in)
    B = to_feet(breadth_ft, breadth_in)
    return L * B

def draw_floorplan(df):
    # If no rooms, don't draw
    if df.empty:
        st.warning("No rooms to display in floorplan.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 10))

    offset_y = 0  # Vertical stacking offset
    
    for _, row in df.iterrows():
        L = row["Length (ft)"]
        B = row["Breadth (ft)"]

        rect = plt.Rectangle((0, offset_y), L, B, fill=None, edgecolor='black')
        ax.add_patch(rect)

        # Label inside
        ax.text(L/2, offset_y + B/2,
                f"{row['Room']} ({row['Area (sqft)']:.1f})",
                ha='center', va='center', fontsize=9)

        offset_y += B + 1  # space between rooms
    
    ax.set_xlim(0, df["Length (ft)"].max() + 5)
    ax.set_ylim(0, offset_y + 5)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title("Auto-generated Floorplan (Diagrammatic Only)")
    ax.invert_yaxis()  # top-down view

    st.pyplot(fig)


# ---------------------------
# Room Categories
# ---------------------------
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

st.header("Select Number of Each Room Type")

room_counts = {}
for label in room_types:
    room_counts[label] = st.number_input(f"Number of {label}", min_value=0, max_value=10, value=0)

# Storage for summary table
summary = []

# ---------------------------
# Dynamic Room Inputs
# ---------------------------
st.header("Enter Room Dimensions")
total_area = 0

for label, prefix in room_types.items():
    count = room_counts[label]
    if count == 0:
        continue

    st.subheader(label)

    for i in range(1, count + 1):
        st.markdown(f"### {prefix} {i}")
        c1, c2, c3, c4 = st.columns(4)

        L_ft = c1.number_input(f"Length (ft) - {prefix} {i}", min_value=0.0, value=0.0, key=f"{prefix}_Lft_{i}")
        L_in = c2.number_input(f"Length (in) - {prefix} {i}", min_value=0.0, value=0.0, key=f"{prefix}_Lin_{i}")
        B_ft = c3.number_input(f"Breadth (ft) - {prefix} {i}", min_value=0.0, value=0.0, key=f"{prefix}_Bft_{i}")
        B_in = c4.number_input(f"Breadth (in) - {prefix} {i}", min_value=0.0, value=0.0, key=f"{prefix}_Bin_{i}")

        L = to_feet(L_ft, L_in)
        B = to_feet(B_ft, B_in)
        area = L * B

        total_area += area

        st.write(f"➤ **{prefix} {i} Area:** {area:.2f} sq ft")

        # Add to summary
        summary.append({
            "Room": f"{prefix} {i}",
            "Category": label,
            "Length (ft)": L,
            "Breadth (ft)": B,
            "Area (sqft)": area
        })

    st.write("---")


# ---------------------------
# Convert summary to DataFrame
# ---------------------------
df = pd.DataFrame(summary)

st.header("📋 Tabulated Summary")
if df.empty:
    st.info("No rooms added yet.")
else:
    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary as CSV", csv, "area_summary.csv", "text/csv")


# ---------------------------
# Floorplan Visualizer
# ---------------------------
st.header("📐 Auto Floorplan Visualizer")

draw_floorplan(df)


# ---------------------------
# Final Totals
# ---------------------------
st.header("Total Computed Areas")

total_sqft = total_area
total_sqyd = total_sqft / 9
claimed_area = total_sqft / 0.75

st.write(f"## 🧮 Total Carpet Area: **{total_sqft:.2f} sq ft**")
st.write(f"### = {total_sqyd:.2f} sq yd")

st.write("---")
st.write(f"## 🏷 Claimed Area (÷ 0.75): **{claimed_area:.2f} sq ft**")
st.write(f"### = {claimed_area / 9:.2f} sq yd")

st.success("Calculation complete!")
