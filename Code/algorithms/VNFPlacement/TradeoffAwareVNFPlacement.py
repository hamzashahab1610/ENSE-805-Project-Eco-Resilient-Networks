import math


class TradeoffAwareVNFPlacement:
    def __init__(
        self,
        system,
    ):
        self.system = system
        self.candidate_nodes = sorted(
            [
                node
                for node in self.system.nodes
                if node.availability >= self.system.min_availability
            ],
            key=lambda node: self.get_node_score(node),
            reverse=True,
        )

    def placement(self):
        for sfc in self.system.sfcs:
            for vnf in sfc.vnfs:
                placed = False if vnf.node is None else True

                while self.candidate_nodes and not placed:
                    node = self.candidate_nodes[0]
                    success = self.system.vnf_placement(vnf, node, sfc)

                    if success:
                        placed = True
                    else:
                        self.candidate_nodes.pop(0)

                if not placed:
                    return False

            for virtual_link in sfc.virtual_links:
                path = self.system.get_candidate_path(
                    virtual_link.source.node, virtual_link.target.node
                )

                if path:
                    self.system.virtual_link_mapping(virtual_link, path, sfc)

        return self.system

    def get_node_score(self, candidate_node):
        normalized_availability = math.log(candidate_node.availability)
        normalized_carbon_footprint = math.log(candidate_node.carbon_footprint)

        # Edge nodes consideration
        # cpu_score = 0
        # if candidate_node.total_cpu < 16:
        #     cpu_score = 5

        score = normalized_availability - normalized_carbon_footprint
        # + cpu_score

        return score
