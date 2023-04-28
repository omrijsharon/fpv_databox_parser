import tkinter as tk
from tkinter import filedialog
from orangebox.parser import Parser
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils.helper_functions import process_blackbox_data, plot_orientation

# create a tkinter window
root = tk.Tk()
root.withdraw()  # hide the main window


# use a dialog box to select the blackbox file
file_path = filedialog.askopenfilename(title="Select Blackbox File", filetypes=[("Blackbox Files", "*.bbl")])
if not file_path:
    print("No file selected.")
    exit()

# Load the blackbox data from the file
blackbox_data = Parser.load(file_path)

# Get the list of available data fields in the blackbox file
field_names = blackbox_data.field_names

# Print the list of available data fields
print("Available fields:")
for name in field_names:
    print(name)

# Create a list of dictionaries to store the data
data = []
for frame in tqdm(blackbox_data.frames(), desc="Processing frames"):
    frame_data = {}
    for i, field in enumerate(frame.data):
        frame_data[field_names[i]] = field
    data.append(frame_data)

# Create a Pandas DataFrame from the data
df = pd.DataFrame(data)
df = process_blackbox_data(df)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plot_orientation(ax, fig, df)
window = tk.Tk()
window.title("Blackbox Data")
window.mainloop()