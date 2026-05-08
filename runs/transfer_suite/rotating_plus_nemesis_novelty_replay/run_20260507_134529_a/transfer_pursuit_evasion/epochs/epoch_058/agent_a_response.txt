def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    obs = observation.get("obstacles")
    if isinstance(obs, (list, tuple)):
        for p in obs:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role") or "").lower()
    self_is_evader = "evader" in self_role
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity_opp = (ox + oy) & 1

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def wall_penalty(x, y):
        # Prefer positions with more free neighbors (evader) / more constrained (pursuer)
        free = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                free += 1
        return free

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        parity = (nx + ny) & 1
        parity_diff = 1 if parity != parity_opp else 0
        free = wall_penalty(nx, ny)
        # Key: deterministic ordering with strategy-dependent tie-breaks
        if self_is_evader:
            key = (d, parity_diff, free, -abs(nx - (w // 2)) - abs(ny - (h // 2)), -dx, -dy)
            better = best_key is None or key > best_key
        else:
            key = (-d, parity_diff, -free, -abs(nx - (w // 2)) - abs(ny - (h // 2)), -dx, -dy)
            better = best_key is None or key > best_key
        if better:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]