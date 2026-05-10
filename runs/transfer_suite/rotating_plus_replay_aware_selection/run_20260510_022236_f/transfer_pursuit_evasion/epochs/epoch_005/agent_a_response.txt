def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    role = (observation.get("self_role", "") or "").lower()
    evade = ("evad" in role) and ("purs" not in role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    chase_corner = corners[phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        corner = (nx - chase_corner[0]) * (nx - chase_corner[0]) + (ny - chase_corner[1]) * (ny - chase_corner[1])
        if evade:
            val = dist2 + 0.05 * corner
        else:
            val = -dist2 + 0.02 * (-corner)
        if best is None or (val > best_val):
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: try in bounds without obstacle filtering; deterministic tie-breaker by dx,dy order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            return [dx, dy]
    return [0, 0]