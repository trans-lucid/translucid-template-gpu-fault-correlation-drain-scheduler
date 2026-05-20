from __future__ import annotations

from collections import defaultdict
from typing import Any


def node_by_id(topology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {node["node_id"]: node for node in topology.get("nodes", [])}


def switch_for_node(topology: dict[str, Any], node_id: str) -> str | None:
    node = node_by_id(topology).get(node_id)
    if not node:
        return None
    return node.get("leaf_switch")


def rack_for_node(topology: dict[str, Any], node_id: str) -> str | None:
    node = node_by_id(topology).get(node_id)
    if not node:
        return None
    return node.get("rack_id")


def nodes_by_switch(topology: dict[str, Any]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for node in topology.get("nodes", []):
        grouped[node["leaf_switch"]].append(node["node_id"])
    return dict(grouped)


def nodes_by_rack(topology: dict[str, Any]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for node in topology.get("nodes", []):
        grouped[node["rack_id"]].append(node["node_id"])
    return dict(grouped)
