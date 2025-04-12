import sys, os, time, config

sys.path.append(os.path.join(os.path.dirname(__file__), "setup"))

from large_scale.sfc_generator import sfcs

from small_scale.system1 import system

from algorithms.VNFPlacement import (
    AvailabilityAwareVNFPlacement,
    CarbonAwareVNFPlacement,
    TradeoffAwareVNFPlacement,
)


system.min_availability = 0.99
system.min_carbon_footprint = 10000
system.max_carbon_footprint = 500000
start_time = time.time()

for sfc in sfcs:
    system.sfcs.append(sfc)
    sfc.system = system

policy = None

if config.EMBEDDING_POLICY == "AAE":
    policy = AvailabilityAwareVNFPlacement.AvailabilityAwareVNFPlacement(system)
elif config.EMBEDDING_POLICY == "CAE":
    policy = CarbonAwareVNFPlacement.CarbonAwareVNFPlacement(system)
elif config.EMBEDDING_POLICY == "TAE":
    policy = TradeoffAwareVNFPlacement.TradeoffAwareVNFPlacement(system)
else:
    raise ValueError("Invalid embedding policy")
    
system = policy.placement()
system.calculate_availability()
system.calculate_carbon_footprint()

system.print_placement()

end_time = time.time()
time_taken = end_time - start_time
print(f"Time taken: {time_taken}")

# write_placement_file(system, "small-placement.txt")
