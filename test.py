import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create a new figure
fig, ax = plt.subplots(figsize=(8, 10))

# Hide axes
ax.axis('off')

# Function to create a text box with rounded corners
def create_box(text, xy, ax):
    ax.text(xy[0], xy[1], text, ha='center', va='center', fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="lightgray", lw=2))

# Function to create arrows
def create_arrow(start, end, ax):
    ax.annotate('', xy=end, xycoords='data', xytext=start, textcoords='data',
                arrowprops=dict(arrowstyle="->", lw=2))

# Add process boxes for the flowchart
create_box("User Logs In", (0.5, 0.9), ax)
create_box("Emergency Request\n- Pickup location\n- Emergency type", (0.5, 0.75), ax)
create_box("System Assigns Ambulance", (0.5, 0.6), ax)
create_box("Real-time Tracking of Ambulance", (0.5, 0.45), ax)
create_box("Ambulance Arrives", (0.5, 0.3), ax)
create_box("Provide Feedback", (0.5, 0.15), ax)

# Add arrows between boxes
create_arrow((0.5, 0.87), (0.5, 0.78), ax)
create_arrow((0.5, 0.72), (0.5, 0.63), ax)
create_arrow((0.5, 0.57), (0.5, 0.48), ax)
create_arrow((0.5, 0.42), (0.5, 0.33), ax)
create_arrow((0.5, 0.27), (0.5, 0.18), ax)

# Display the flowchart
plt.title("Flowchart for User Requesting Ambulance", fontsize=14, pad=20)
plt.show()