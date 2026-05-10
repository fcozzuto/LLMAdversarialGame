def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in self_role
    pursuer = (("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)) and not evader

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue
        d = dist2(nx, ny)
        if evader:
            score = -d  # maximize distance => minimize negative distance
        else:
            score = d   # minimize distance
        key = (score, dx, dy)  # deterministic tie-break
        if best is None or key < best:
            best = key
            best_val = (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_val[0]), int(best_val[1])]