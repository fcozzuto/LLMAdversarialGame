def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    if not resources:
        # Prefer drifting toward center to avoid getting stuck near corners
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Deterministic selection:
    # For each move, score by (opponent_distance_to_resource - self_distance_to_resource),
    # heavily favoring immediate collection / strict advantage, with tie-breaks.
    best_key = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            immediate = 1 if (nx == rx and ny == ry) else 0
            advantage = do - ds  # positive means we are closer than opponent
            # Larger is better: prioritize immediate, then advantage, then being closer and safer.
            key = (immediate, advantage, -ds, -do, -abs(nx - ox) - abs(ny - oy), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]