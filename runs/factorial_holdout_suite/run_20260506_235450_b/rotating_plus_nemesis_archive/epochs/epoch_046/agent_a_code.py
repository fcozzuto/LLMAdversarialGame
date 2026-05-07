def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    # Pick a target: prefer resource closer than opponent; tie-break deterministically.
    best = None
    best_score = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        rel = sd - od
        key = (0 if rel <= 0 else 1, abs(rel), sd, rx, ry)
        if best is None or key < best_score:
            best_score = key
            best = (rx, ry)

    tx, ty = best
    # Choose neighbor that minimizes Manhattan distance to target; avoid obstacles.
    best_move = [0, 0]
    best_dist = None
    best_pref = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(tx - nx) + abs(ty - ny)
        pref = (d, abs(tx - (sx + dx)) + abs(ty - (sy + dy)) - d, dx, dy)
        if best_dist is None or pref < best_pref:
            best_dist = d
            best_pref = pref
            best_move = [dx, dy]
    if not ok(sx, sy):
        # Shouldn't happen, but keep deterministic.
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
    return best_move