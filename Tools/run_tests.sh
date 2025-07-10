# Path to our AI
# ../src/checkers-python/main.py

# Command to quickly run individually (in Tools)
# python3 AI_Runner.py 7 7 2 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py

# To run manually (in src)
# python3 main.py 7 7 2 m 0

# Notes!!!!!
# run - chmod +x run_tests.sh - to make scropt executable. ./run_tests in terminal (from Tools directory) to run
# Our AI should always be path for player1Black
# Remember to comment out show_board() in both players' GameLogic files
# Output time metrics are really only useful against Random_AI
# Only change variables defined here
# Path for Random_AI: Sample_AIs/Random_AI/main.py
# Path for Poor_AI: Sample_AIs/Poor_AI/main.py
# Path for Average_AI: Sample_AIs/Average_AI/main.py
#------------------------------------------------------
simulationsCount=50
pathForPlayer1Black=../src/checkers-python/main.py
pathForPlayer2White=Sample_AIs/Average_AI/main.py
codeChanges="Testing milestone2 ai against average ai."
m=7
n=7
p=2
#------------------------------------------------------




# make a directory to store results (deletes test_report directory if alr exists)
rm -rf test_report && mkdir test_report


# define paths to output files
simulationResults="test_report/simulationResults.txt"
time_file="test_report/iteration_times.txt"



 # print simulation details
echo "Testing features: $codeChanges" | tee -a "$simulationResults"
echo "Board Properties: m=$m, n=$n, p=$p" | tee -a "$simulationResults"
echo "Player1 = Our AI" | tee -a "$simulationResults"
echo "Player2 = $pathForPlayer2White" | tee -a "$simulationResults"
echo "---------------------------------------" | tee -a "$simulationResults"
echo "Running $simulationsCount Simulations..." | tee -a "$simulationResults"



start_time=$SECONDS  # Start total timer
total_iter_time=0  # Initialize variable to track total iteration time

# Run simulations
for ((i=1; i<=$simulationsCount; i++)); 
do 
    iter_start=$SECONDS  # Start iteration timer
    echo -n "Game $i: " | tee -a "$simulationResults"
    
    # Run the command and capture both stdout and stderr
    result=$(python3 AI_Runner.py $m $n $p l $pathForPlayer1Black $pathForPlayer2White 2>&1)
    
    iter_time=$(( SECONDS - iter_start ))  # Calculate iteration time
    total_iter_time=$(( total_iter_time + iter_time ))  # Add to the total iteration time
    
    # Log iteration time to separate file
    echo "$iter_time" >> "$time_file"

    echo "$result (Time: ${iter_time}s)" | tee -a "$simulationResults"
done




total_time=$(( SECONDS - start_time ))  # Calculate total time
average_time=$(( total_iter_time / simulationsCount ))  # Calculate average time

# Convert total time to minutes and seconds
total_minutes=$(( total_time / 60 ))
total_seconds=$(( total_time % 60 ))

# Convert average time to minutes and seconds
average_minutes=$(( average_time / 60 ))
average_seconds=$(( average_time % 60 ))



# Print time data
echo "---------------------------------------" | tee -a "$simulationResults"
echo "Total execution time: ${total_minutes}m ${total_seconds}s" | tee -a "$simulationResults"
echo "Average duration of game: ${average_minutes}m ${average_seconds}s" | tee -a "$simulationResults"
echo "---------------------------------------" | tee -a "$simulationResults"




# Python script to process and print winner count
python3 - <<EOF

# define winner counts
player1_win_count = 0
player2_win_count = 0
tie_count = 0

# Read and update count of winners
with open("$simulationResults", "r") as f:
    for line in f.readlines():
        if "player 1 wins" in line:
            player1_win_count += 1
        elif "player 2 wins" in line:
            player2_win_count += 1
        elif "Tie" in line:
            tie_count += 1

# Write who won how many times
with open("$simulationResults", "a") as f:
    f.write(f"Our AI won this many games: {player1_win_count}\n")
    f.write(f"Our opponent won this many games: {player2_win_count}\n")
    f.write(f"We tied this many times: {tie_count}\n")
EOF



# print note of histogram in another file
echo "---------------------------------------" | tee -a "$simulationResults"
echo "Histogram of game time distribution written to $time_file" | tee -a "$simulationResults"




# Python script to process iteration times
python3 - <<EOF
import numpy as np

# Read iteration times from file
with open("$time_file", "r") as f:
    times = [int(line.strip()) for line in f.readlines()]

# Sort times in ascending order
times.sort()

# Find min and max times
min_time = min(times)
max_time = max(times)

# Determine bucket ranges (increments of 10)
bins = list(range(min_time - (min_time % 10), max_time + 10, 10))
hist, _ = np.histogram(times, bins=bins)

# Write histogram output to file
with open("$time_file", "w") as f:
    f.write("Iteration Time Distribution (binned in 10s)\n")
    f.write("--------------------------------------------------\n")
    
    max_count = max(hist)  # Max occurrences for y-axis scaling
    for i in range(len(hist)):
        start = bins[i]
        end = bins[i + 1]
        bar = "#" * hist[i]  # Visual bar representation
        f.write(f"{start:3d}-{end-1:3d} | ({hist[i]}) {bar}\n")
EOF
