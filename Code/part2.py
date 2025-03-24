import sys, os, time, pickle, json, config

# from stable_baselines3 import PPO
# from stable_baselines3.common.env_checker import check_env

sys.path.append(os.path.join(os.path.dirname(__file__), "setup"))

from large_scale.sfc_generator import sfcs

# if os.path.exists("system.pkl"):
#     with open("system.pkl", "rb") as file:
#         system = pickle.load(file)
#     print("Loaded saved system object.")
# else:
#     from large_scale.system import system

#     print("Initialized a new system object.")
#     with open("system.pkl", "wb") as file:
#         pickle.dump(system, file)
#     print("System object saved successfully.")

from large_scale.sfc_generator import (
    # sfcs,
    convert_to_virtual_topology,
    # convert_to_virtual_topology_json,
)

from large_scale.topology_generator import (
    create_topology_from_system,
    # create_reduced_topology_from_system,
    visualize_reduced_topology,
)

from small_scale.system1 import system

from algorithms.VNFPlacement import (
    AvailabilityAwareVNFPlacement,
    CarbonAwareVNFPlacement,
    TradeoffAwareVNFPlacement,
)

from algorithms.BackupVNFPlacement import (
    GeneticBackupVNFPlacement,
    PSOBackupVNFPlacement,
    SABackupVNFPlacement,
    # BackupVNFPlacementEnv
)

# from classes import StepCallback

system.weight = 0.4
system.min_availability = 0.99
system.min_carbon_footprint = 10000
system.max_carbon_footprint = 10000000
start_time = time.time()

for sfc in sfcs:
    system.sfcs.append(sfc)
    sfc.system = system

policy = None
allocation = None

if config.EMBEDDING_POLICY == "AAE":
    policy = AvailabilityAwareVNFPlacement.AvailabilityAwareVNFPlacement(system)
elif config.EMBEDDING_POLICY == "CAE":
    policy = CarbonAwareVNFPlacement.CarbonAwareVNFPlacement(system)
elif config.EMBEDDING_POLICY == "TAE":
    policy = TradeoffAwareVNFPlacement.TradeoffAwareVNFPlacement(system)
else:
    raise ValueError("Invalid embedding policy")

if config.ALLOCATION_POLICY == "SA":
    allocation = SABackupVNFPlacement.SABackupVNFPlacement(policy=policy, initial_temperature=10, cooling_rate=0.75, iterations_per_temperature=1, min_temperature=1)
elif config.ALLOCATION_POLICY == "PSO":
    allocation = PSOBackupVNFPlacement.PSOBackupVNFPlacement(policy=policy, num_particles=5, max_iterations=10)
elif config.ALLOCATION_POLICY == "GA":
    allocation = GeneticBackupVNFPlacement.GeneticBackupVNFPlacement(policy=policy, population_size=50, generations=10, mutation_rate=0.1, selection_rate=0.2)

best_solution, best_fitness = allocation.optimize()
print(f"Best solution: {best_solution}, Best fitness: {best_fitness}")
system = allocation.apply_solution(best_solution)

# seed = 42
# env = BackupVNFPlacementEnv.BackupVNFPlacementEnv(system)
# check_env(env)
# step_callback = StepCallback.StepCallback(check_freq=1)
# model = PPO(
#     "MlpPolicy",
#     env,
#     verbose=1,
#     seed=seed,
# )
# model.learn(total_timesteps=1000, callback=step_callback, progress_bar=True)
# obs, info = env.reset(seed)
# done = False

# while not done:
#     action, _states = model.predict(obs, deterministic=True)
#     print(f"Action: {action}")
#     obs, reward, done, truncate, info = env.step(action)
#     system = info["system"]
#     system.solution = action
#     print(f"Reward: {reward}, Done: {done}")
#     print()

system.calculate_availability()
system.calculate_carbon_footprint()
system.print_placement()

end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken}")

G, physical_topology = create_topology_from_system(nodes=system.nodes, switches=system.switches, physical_links=system.physical_links)
# G, physical_topology = create_reduced_topology_from_system(system, 1)
visualize_reduced_topology(G)

virtual_topology = convert_to_virtual_topology(sfcs)
# virtual_topology = convert_to_virtual_topology_json(sfcs, "sfc-virtual.json")

# Create directory for policy combination
config.ensure_output_dir_exists()

# Write files using config paths
config.write_placement_file(system, config.get_placements_path())
config.write_placement_file(system, config.get_backup_placements_path())

with open(config.get_physical_json_path(), "w") as f:
    json.dump(physical_topology, f, indent=2)

with open(config.get_virtual_json_path(), "w") as f:
    json.dump(virtual_topology, f, indent=2)

with open(config.get_system_pkl_path(), "wb") as file:
    pickle.dump(system, file)

with open(config.get_system_backup_pkl_path(), "wb") as file:
    pickle.dump(system, file)

print("Simulator system state saved successfully.")
