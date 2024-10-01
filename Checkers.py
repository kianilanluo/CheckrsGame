import matplotlib.pyplot as plt
import numpy as np

# Define the data for Q-Learning
learning_rates = ['0.05', '0.09', '0.25']
wins_pre_training = [51379, 51473, 50569]
wins_post_training = [51486, 51437, 50043]

# Define the x-axis for plotting
x = np.arange(len(learning_rates))

# Create the plots
fig, ax = plt.subplots(figsize=(10, 6))
# ax.plot(x, wins_pre_training, marker='o', linestyle='-', color='blue', label='Pre-Training')
ax.plot(x, wins_post_training, marker='o', linestyle='-', color='green', label='Post-Training')

# Set the plot parameters
ax.set_xticks(x)
ax.set_xticklabels(learning_rates)
ax.set_xlabel('Learning Rate')
ax.set_ylabel('Number of Wins')
ax.set_title('Q-Learning Performance Across Learning Rates')
ax.legend()

# Display the plot
plt.grid(True)
plt.show()
