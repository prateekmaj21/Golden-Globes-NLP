import json
import re
from collections import defaultdict, Counter

# Load the original JSON data
with open('gg2013.json', 'r') as file:
    tweets = json.load(file)#[:170000]

# Function to identify award patterns dynamically
def find_award_patterns(tweets):
    award_patterns = []
    for tweet in tweets:
        text = tweet['text'].lower()
        matches = re.findall(r'best [\w\s\-]+', text)
        for match in matches:
            award_patterns.append(match.strip())
    return award_patterns

# Find award patterns dynamically from the tweets
award_patterns = find_award_patterns(tweets)

# Count the frequency of each award pattern
award_counter = Counter(award_patterns)

# Get the top 25 most frequent awards
top_50_awards = award_counter.most_common(50)

# Convert to a dictionary for JSON output
top_50_awards_dict = {award: count for award, count in top_50_awards}

# Save the results to a new JSON file
with open('gg2013_top_awards.json', 'w') as outfile:
    json.dump(top_50_awards_dict, outfile, indent=4)

print("Analysis complete. Top awards saved to 'gg2013_top_awards.json'")
