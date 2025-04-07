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
            used_nodes = set()  # Track nodes used by this SFC
            for vnf in sfc.vnfs:
                placed = False if vnf.node is None else True
                available_nodes = [
                    n for n in self.candidate_nodes if n not in used_nodes
                ]

                while available_nodes and not placed:
                    node = available_nodes[0]  # Try best candidate first
                    success = self.system.vnf_placement(vnf, node, sfc)

                    if success:
                        placed = True
                        used_nodes.add(node)
                    else:
                        # Remove failed node and try next best
                        available_nodes.pop(0)

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

        score = normalized_availability - normalized_carbon_footprint

        return score
