import itertools

from system1 import system


def generate_all_placements(system):
    sfc = system.sfcs[0]
    num_vnfs = len(sfc.vnfs)
    num_nodes = len(system.nodes)
    # num_nodes = 4

    for placement in itertools.product(range(num_nodes), repeat=num_vnfs):
        yield list(placement)


def apply_placement(system, placement):
    sfc = system.sfcs[0]
    placed_vnfs = []

    system.reset()

    for vnf_index, node_index in enumerate(placement):
        vnf = sfc.vnfs[vnf_index]
        node = system.nodes[node_index]

        if not system.vnf_placement(
            vnf, node, sfc, False, placed_vnfs[-1].node if placed_vnfs else node
        ):
            return False

        placed_vnfs.append(vnf)

    for virtual_link in sfc.virtual_links:
        path = system.get_candidate_path(
            virtual_link.source.node,
            virtual_link.target.node,
        )

        system.virtual_link_mapping(virtual_link, path, sfc)

    return True


for placement in generate_all_placements(system):
    placement_successfull = apply_placement(system, placement)

    modified_placement = [item + 1 for item in placement]
    result = " ".join(map(str, modified_placement))

    if placement_successfull:
        system.calculate_availability()
        system.calculate_carbon_footprint()
        with open("placements-sfc1-2.csv", "a") as file:
            file.write(f"{result},{system.availability},{system.carbon_footprint}\n")
            print(result, system.availability, system.carbon_footprint)
