def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_score = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if best is None or dist2 < best_score or (dist2 == best_score and (dx, dy) < best):
            best_score = dist2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]