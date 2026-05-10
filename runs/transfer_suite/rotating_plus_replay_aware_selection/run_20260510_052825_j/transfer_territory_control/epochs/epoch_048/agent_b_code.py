def choose_move(observation):
    sx, sy = observation["self_position"]
    width = observation["grid_width"]
    height = observation["grid_height"]
    edge_targets = [
        cell for cell in (observation.get("unclaimed_cells") or [])
        if cell[0] in (0, width - 1) or cell[1] in (0, height - 1)
    ]
    targets = edge_targets or observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
    if not targets:
        return [0, 0]
    target = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]