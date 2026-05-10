def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [] ) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Deterministic heuristic: flip opponent if possible, otherwise claim unclaimed, otherwise hold/advance toward center.
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue
        if (nx, ny) in opT:
            base = 220
        elif (nx, ny) in unT:
            base = 140
        elif (nx, ny) in selfT:
            base = 30
        else:
            base = 70  # previously-owned/unknown, still worth entering to improve mobility

        # Prefer moving toward center and away from edges slightly.
        center_bonus = - (abs(nx - cx) + abs(ny - cy))
        edge_penalty = - (min(nx, w - 1 - nx) + min(ny, h - 1 - ny)) * 0.5

        v = base + center_bonus + edge_penalty
        if v > bestv or (v == bestv and (dx, dy) < (best_move[0], best_move[1])):
            bestv = v
            best_move = [dx, dy]

    return best_move