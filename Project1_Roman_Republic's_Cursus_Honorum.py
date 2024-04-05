import numpy as np
from scipy.stats import truncnorm
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Parameters
life_expectancy_mu = 55
life_expectancy_sigma = 10
life_expectancy_min = 25
life_expectancy_max = 80

min_age_quaestor = 30
min_age_aedile = 36
min_age_praetor = 39
min_age_consul = 42

min_service_aedile = 2
min_service_praetor = 2
min_service_consul = 2
reelection_interval_consul = 10

positions_available = {'Quaestor': 20, 'Aedile': 10, 'Praetor': 8, 'Consul': 2}

starting_psi = 100
psi_penalty_unfilled_position = -5
psi_penalty_reelection_consul = -10

annual_influx_mu = 15
annual_influx_sigma = 5

simulation_years = 200

# Initialize the truncated normal distribution for life expectancy
life_expectancy_dist = truncnorm((life_expectancy_min - life_expectancy_mu) / life_expectancy_sigma,
                                 (life_expectancy_max - life_expectancy_mu) / life_expectancy_sigma,
                                 loc=life_expectancy_mu, scale=life_expectancy_sigma)

# Initialize variables
psi = starting_psi
politicians = []

# Define functions
def generate_age():
    return int(np.clip(np.round(life_expectancy_dist.rvs()), life_expectancy_min, life_expectancy_max))

def election(candidate_pool, num_positions):
    if len(candidate_pool) <= num_positions:
        return candidate_pool
    else:
        return np.random.choice(candidate_pool, num_positions, replace=False).tolist()  # Convert to list

def update_psi():
    global psi
    unfilled_positions = sum(positions_available.values()) - sum(1 for p in politicians if p['position'] != 'Quaestor')
    psi += unfilled_positions * psi_penalty_unfilled_position
    reelection_penalty = sum(1 for p in politicians if p['position'] == 'Consul' and p['years_in_office'] < reelection_interval_consul) * psi_penalty_reelection_consul
    psi += reelection_penalty
    psi = psi + 55
    psi = min(psi, 100)

def career_progression():
    global politicians
    new_politicians = []
    for politician in politicians:
        politician['age'] += 1
        politician['years_in_office'] += 1
        if politician['age'] >= min_age_aedile and politician['position'] == 'Quaestor':
            politician['position'] = 'Aedile'
        if politician['age'] >= min_age_praetor and politician['position'] == 'Aedile' and politician['years_in_office'] >= min_service_aedile:
            politician['position'] = 'Praetor'
        if politician['age'] >= min_age_consul and politician['position'] == 'Praetor' and politician['years_in_office'] >= min_service_praetor:
            politician['position'] = 'Consul'
        if politician['age'] <= life_expectancy_max:  # Remove politicians who surpass life expectancy
            new_politicians.append(politician)
    politicians = new_politicians

# Simulation
end_of_simulation_psi_list = []
annual_fill_rate_list = {position: [] for position in positions_available}
age_distribution_list = {position: [] for position in positions_available}
for year in range(simulation_years):
    politicians = []  # Clear politicians list at the beginning of each year
    # Yearly cycle
    new_candidates = np.random.normal(annual_influx_mu, annual_influx_sigma)
    new_quaestors = int(new_candidates)
    candidate_pool = [{'age': generate_age(), 'position': 'Quaestor', 'years_in_office': 0} for _ in range(new_quaestors)]
    politicians += election(candidate_pool, positions_available['Quaestor'])

    politicians = sorted(politicians, key=lambda x: x['position'], reverse=True)  # Higher offices first
    for position, num_positions in positions_available.items():
        if position != 'Quaestor':
            candidate_pool = [{'age': generate_age(), 'position': position, 'years_in_office': 0} for _ in range(int(new_candidates))]
            elected = election(candidate_pool, num_positions)
            politicians += elected[:num_positions]  # Ensure only the required number of politicians are added

    # Update career progression and PSI
    career_progression()
    update_psi()

    # Store measurements for this year
    end_of_simulation_psi_list.append(psi)
    annual_fill_rate = {position: min((sum(1 for p in politicians if p['position'] == position) / positions_available[position]) * 100, 100) for position in positions_available}
    for position, rate in annual_fill_rate.items():
        annual_fill_rate_list[position].append(rate)
    
    # Calculate age distribution
    age_distribution = {position: {'mean': np.mean([p['age'] for p in politicians if p['position'] == position]),
                               'std': np.std([p['age'] for p in politicians if p['position'] == position])}
                    for position in positions_available}
    for position, distribution in age_distribution.items():
        age_distribution_list[position].append(distribution)

# Measurements
end_of_simulation_psi = end_of_simulation_psi_list[-1]

annual_fill_rate_avg = {}
for position, rate_list in annual_fill_rate_list.items():
    if rate_list:
        annual_fill_rate_avg[position] = sum(rate_list) / len(rate_list)
    else:
        annual_fill_rate_avg[position] = 0

age_distribution_avg = {}
for position, distribution_list in age_distribution_list.items():
    mean_list = [d['mean'] for d in distribution_list if not np.isnan(d['mean'])]
    std_list = [d['std'] for d in distribution_list if not np.isnan(d['std'])]
    mean = np.mean(mean_list) if mean_list else np.nan
    std = np.mean(std_list) if std_list else np.nan
    age_distribution_avg[position] = {'mean': mean, 'std': std}

# Print measurements
print("End-of-Simulation PSI:", end_of_simulation_psi)
print("Annual Fill Rate:")
for position, rate in annual_fill_rate_avg.items():
    print(f"{position}: {rate:.2f}%")
print("Age Distribution:")
for position, distribution in age_distribution_avg.items():
    print(f"{position}: Mean = {distribution['mean']:.2f}, Std = {distribution['std']:.2f}")