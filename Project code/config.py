import os

EMBEDDING_POLICY = "TAE"  
ALLOCATION_POLICY = "SA"  

# Path configurations
def get_output_dir():
    output_dir = f"output/{EMBEDDING_POLICY}-{ALLOCATION_POLICY}"
    return output_dir

def get_system_pkl_path():
    return os.path.join(get_output_dir(), "system_simulator.pkl")

def get_placements_path():
    return os.path.join(get_output_dir(), "placements.txt")

def get_backup_placements_path():
    return os.path.join(get_output_dir(), "placements-backup.txt")

def get_physical_json_path():
    return os.path.join(get_output_dir(), "physical.json")

def get_virtual_json_path():
    return os.path.join(get_output_dir(), "virtual.json")

def get_system_backup_pkl_path():
    return os.path.join(get_output_dir(), "system_simulator_backup.pkl")

def ensure_output_dir_exists():
    if not os.path.exists(get_output_dir()):
        os.makedirs(get_output_dir())

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