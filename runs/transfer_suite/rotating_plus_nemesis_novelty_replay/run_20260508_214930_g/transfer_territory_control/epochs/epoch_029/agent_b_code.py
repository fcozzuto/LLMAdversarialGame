def choose_move(observation):
    sx, sy = observation["self_position"]
    targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
    if not targets:
        return [0, 0]
    target = min(targets, key=lambda item: (abs(item[0] - sx) + abs(item[1] - sy), item[1], item[0]))
    dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
    dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
    return [dx, dy]