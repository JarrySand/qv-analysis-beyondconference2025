import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Setting font to avoid font errors
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Load data
votes_df = pd.read_csv('data/votes.csv')
candidates_df = pd.read_csv('data/candidates.csv')

# Create DataFrame with English names
candidates_df_en = candidates_df.copy()
if 'title_en' in candidates_df.columns:
    # Use English title when available
    candidates_df_en['title'] = candidates_df['title_en']

# Calculate buried voices probabilistically
def calculate_buried_voices_probabilistic():
    # Identify maximum vote points for each voter
    max_votes = {}
    buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        voter_id = voter_row['voter_id']
        
        # Check votes for each candidate
        vote_values = {}
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                vote_values[i] = vote_value
        
        if not vote_values:
            continue
            
        # Find the maximum vote value
        max_vote_value = max(vote_values.values())
        
        # List candidates with maximum vote value
        max_candidates = [cand for cand, value in vote_values.items() if value == max_vote_value]
        
        # Distribute maximum vote probabilistically (in case of ties)
        probability_per_candidate = 1.0 / len(max_candidates)  # Distribute probability equally
        
        # Calculate "buried voices" - votes >= 4 and not the max vote candidate
        for candidate, vote_value in vote_values.items():
            if vote_value >= 4:
                if candidate in max_candidates:
                    # If max vote candidate, count (1-probability of being chosen) as buried voice
                    buried_voices[candidate] += (1 - probability_per_candidate)
                else:
                    # If not max vote candidate, count 100% as buried voice
                    buried_voices[candidate] += 1
    
    return buried_voices

# Compare different algorithms for calculating "buried voices"
def compare_algorithms():
    # Simple maximum vote method (only the first maximum found is considered)
    simple_buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        max_vote = 0
        max_candidate = None
        
        # Identify the maximum vote
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
                    max_candidate = i
        
        # Calculate buried voices
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value >= 4 and i != max_candidate:
                    simple_buried_voices[i] += 1
    
    # Probabilistic method
    probabilistic_buried_voices = calculate_buried_voices_probabilistic()
    
    # Original implementation method (vote_value < max_vote)
    original_buried_voices = {i: 0 for i in range(len(candidates_df))}
    
    for _, voter_row in votes_df.iterrows():
        max_vote = 0
        
        # Identify the maximum vote value
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value > max_vote:
                    max_vote = vote_value
        
        # Calculate buried voices (original method: vote_value >= 4 and vote_value < max_vote)
        for i in range(len(candidates_df)):
            col_name = f'candidate_{i}'
            if col_name in voter_row and not pd.isna(voter_row[col_name]):
                vote_value = voter_row[col_name]
                if vote_value >= 4 and vote_value < max_vote:
                    original_buried_voices[i] += 1
    
    # HTML/JS values
    html_buried = [21, 15, 14, 10, 9, 8, 7]
    html_projects = [
        'Chiba Youth Center PRISM',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Awaji Island Quest College',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ]
    
    # Create mapping between HTML/JS values and candidate IDs
    html_mapping = {}
    for i, project in enumerate(html_projects):
        for j in range(len(candidates_df)):
            title_en = candidates_df_en.loc[j, 'title']
            if title_en == project:
                html_mapping[j] = i
    
    # Display results
    print("\n=== Comparison of 'Buried Voices' Calculation Methods ===")
    print("candidate_id: Original / Simple Max / Probabilistic / HTML/JS value")
    
    for i in range(len(candidates_df)):
        title = candidates_df.loc[i, 'title']
        title_en = candidates_df_en.loc[i, 'title']
        html_val = html_buried[html_mapping[i]] if i in html_mapping else "N/A"
        
        print(f"{i}. {title_en}: " +
              f"{original_buried_voices[i]:.2f} / {simple_buried_voices[i]:.2f} / " +
              f"{probabilistic_buried_voices[i]:.2f} / {html_val}")
    
    # Prepare data for graph creation
    projects = candidates_df_en['title'].tolist()
    
    # Create directory if it doesn't exist
    os.makedirs('results/figures/comparison', exist_ok=True)
    
    # Create graph
    plt.figure(figsize=(14, 10))
    x = np.arange(len(candidates_df))
    bar_width = 0.2
    opacity = 0.8
    
    plt.bar(x - bar_width*1.5, [original_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='blue', label='Original Method')
    
    plt.bar(x - bar_width*0.5, [simple_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='red', label='Simple Max Method')
    
    plt.bar(x + bar_width*0.5, [probabilistic_buried_voices[i] for i in range(len(candidates_df))], 
            bar_width, alpha=opacity, color='green', label='Probabilistic Method')
    
    # Plot HTML/JS values
    html_values = [0] * len(candidates_df)
    for i in range(len(candidates_df)):
        if i in html_mapping:
            html_values[i] = html_buried[html_mapping[i]]
    
    plt.bar(x + bar_width*1.5, html_values, 
            bar_width, alpha=opacity, color='purple', label='HTML/JS Value')
    
    plt.xlabel('Projects')
    plt.ylabel('Number of Buried Voices')
    plt.title('Comparison of "Buried Voices" Calculation Methods')
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.savefig('results/figures/comparison/buried_voices_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved probabilistic buried voices comparison graph!")
    
    return {
        'original': original_buried_voices,
        'simple': simple_buried_voices,
        'probabilistic': probabilistic_buried_voices,
        'html': html_values
    }

if __name__ == "__main__":
    print("Running comparison analysis of 'Buried Voices' calculation methods...")
    results = compare_algorithms()
    
    print("\nAnalysis complete. Results saved to results/figures/comparison directory.")
    print("Compared three calculation methods with the original HTML/JS values.")
    print("In particular, for tie cases, the probabilistic method counts buried voices based on the probability of each candidate being chosen.") 