import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def draw_rink(ax):
    # Set the rink dimensions
    rink_length = 200
    rink_width = 85
    goal_line = 11
    corner_radius = 28

    # Draw the outer rink with straight lines

    outer_line1 = plt.Line2D((-75, 75), (-42.5, -42.5), lw=3.5, color='black')
    ax.add_artist(outer_line1)

    outer_line2 = plt.Line2D((-75, 75), (42.5, 42.5), lw=3.5, color='black')
    ax.add_artist(outer_line2)

    outer_line3 = plt.Line2D((-100, -100), (-20, 20), lw=3.5, color='black')
    ax.add_artist(outer_line3)

    outer_line3 = plt.Line2D((100, 100), (-20, 20), lw=3.5, color='black')
    ax.add_artist(outer_line3)

    # Draw the rounded corners with quarter circles (Arcs)
    corner_arcs = [
        patches.Arc((-100 + corner_radius, -42.5 + corner_radius), 2 * corner_radius, 2 * corner_radius, theta1=180, theta2=270, lw=2, color='black'),
        patches.Arc((100 - corner_radius, -42.5 + corner_radius), 2 * corner_radius, 2 * corner_radius, theta1=270, theta2=360, lw=2, color='black'),
        patches.Arc((-100 + corner_radius, 42.5 - corner_radius), 2 * corner_radius, 2 * corner_radius, theta1=90, theta2=180, lw=2, color='black'),
        patches.Arc((100 - corner_radius, 42.5 - corner_radius), 2 * corner_radius, 2 * corner_radius, theta1=0, theta2=90, lw=2, color='black')
    ]
    for arc in corner_arcs:
        ax.add_artist(arc)


 # Draw the red line with a less bright red color
    red_line = plt.Line2D((0, 0), (-42.5, 42.5), lw=2, color='#B22222')
    ax.add_artist(red_line)

    # Draw the blue lines with a less bright blue color
    blue_line1 = plt.Line2D((-25, -25), (-42.5, 42.5), lw=2, color='#4169E1')
    blue_line2 = plt.Line2D((25, 25), (-42.5, 42.5), lw=2, color='#4169E1')
    ax.add_artist(blue_line1)
    ax.add_artist(blue_line2)

    # Draw the goal lines
    goal_line1 = plt.Line2D((-89, -89), (-36.5, 36.5), lw=2, color='black')
    goal_line2 = plt.Line2D((89, 89), (-36.5, 36.5), lw=2, color='black')
    ax.add_artist(goal_line1)
    ax.add_artist(goal_line2)

    # Draw the faceoff circles
    for x in (-69, 69):
        for y in (-22, 22):
            faceoff_circle = plt.Circle((x, y), 15, lw=2, edgecolor='black', facecolor='none')
            ax.add_artist(faceoff_circle)

    ax.set_xlim(-100, 100)
    ax.set_ylim(-42.5, 42.5)
    ax.set_aspect('equal')

    for spine in ax.spines.values():
        spine.set_visible(False)

        ax.set_xlim(-100, 100)
        ax.set_ylim(-42.5, 42.5)
        ax.set_aspect('equal')


df = pd.read_csv('./Linhac_df_keyed_20_games.csv')
fig, ax = plt.subplots()
draw_rink(ax)

# Filter the DataFrame to keep only rows with "check" in the "eventname" column
filtered_df = df[(df["eventname"] == "check")&(df["gameid"].isin([66445]))]
#(df["gameid"].isin([66445, 88237]))

# Filter the DataFrame for "body" and "stick" types
body_df = filtered_df[filtered_df["type"] == "body"]
stick_df = filtered_df[filtered_df["type"] == "stick"]

# Create a 2D scatter plot of the "xadjcoord" and "yadjcoord" columns for each type
plt.scatter(body_df["xadjcoord"], body_df["yadjcoord"], label="Body", marker='x', alpha=0.7, color='green')
plt.scatter(stick_df["xadjcoord"], stick_df["yadjcoord"], label="Stick", marker='x', alpha=0.7, color='purple')

plt.title("Different Types of Checks")
# Place the legend around the coordinates (x=50, y=0)
legend = plt.legend(loc='center', borderaxespad=0., ncol=1)
legend_x, legend_y = ax.transData.transform((43, 0))
legend_x_disp, legend_y_disp = ax.transAxes.inverted().transform((legend_x, legend_y))
legend.set_bbox_to_anchor((legend_x_disp, legend_y_disp))

# Remove x and y axis
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

plt.show()