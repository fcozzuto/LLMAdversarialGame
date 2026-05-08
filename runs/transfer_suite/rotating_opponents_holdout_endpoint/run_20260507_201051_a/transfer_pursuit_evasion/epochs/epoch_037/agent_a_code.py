def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_score = None
    # Deterministic tie-breaker: prefer lexicographically smaller (dx,dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = dist2(nx, ny)
        # For evader: maximize distance; for pursuer: minimize distance.
        base = d if i_am_evader else -d
        # Small deterministic bias to avoid aimless drifting: keep moving toward/away from opponent in primary axis.
        adx = abs(nx - ox)
        bias = (adx if i_am_evader else -adx) * 0.001 + (abs(ny - oy) if i_am_evader else -abs(ny - oy)) * 0.001
        score = base + bias
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]