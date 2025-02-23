import sys, os, time, pickle

sys.path.append(os.path.join(os.path.dirname(__file__), "setup"))

from large_scale.sfc_generator import sfcs
from small_scale.system1 import system

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

from algorithms.VNFPlacement import (
    AvailabilityAwareVNFPlacement,
    CarbonAwareVNFPlacement,
    TradeoffAwareVNFPlacement,
)


def write_placement_file(system, filename):
    unique_placements = {}

    for sfc in system.sfcs:
        for vnf in sfc.vnfs:
            if vnf.node:
                unique_placements[vnf.name] = vnf.node.name

    with open(filename, "w") as f:
        f.write("# VNF name to host mapping\n")
        for vnf_name, node_name in unique_placements.items():
            f.write(f"{vnf_name},{node_name}\n")


system.min_availability = 0.99
system.min_carbon_footprint = 10000
system.max_carbon_footprint = 500000
start_time = time.time()

# for sfc in sfcs:
#     system.sfcs.append(sfc)
#     sfc.system = system

# availability_aware = AvailabilityAwareVNFPlacement.AvailabilityAwareVNFPlacement(system)
# system = availability_aware.placement()

# carbon_aware = CarbonAwareVNFPlacement.CarbonAwareVNFPlacement(system)
# system = carbon_aware.placement()

tradeoff_aware = TradeoffAwareVNFPlacement.TradeoffAwareVNFPlacement(system)
system = tradeoff_aware.placement()

system.calculate_availability()
system.calculate_carbon_footprint()

system.print_placement()

end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken}")

write_placement_file(system, "part1-small-placement.txt")
