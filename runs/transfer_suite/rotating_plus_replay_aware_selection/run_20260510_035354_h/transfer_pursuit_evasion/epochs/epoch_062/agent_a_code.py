def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obs = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = "evad" in role
    # Deterministic move ordering (diagonal first)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(x, y):
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        if (x, y) in obs:
            return -10**12 if not is_evader else 10**12
        # Favor staying closer (pursuer) or farther (evader) to opponent; slight tie-break toward forward progress.
        # Add tiny bias based on absolute displacement components.
        bias = (abs(x - sx) + abs(y - sy)) * 1e-3
        return (-d2) + bias if not is_evader else (d2) + bias

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        sc = score_move(nx, ny)
        if best_sc is None or (sc > best_sc):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        # If blocked, allow staying put unless it is inside obstacle (shouldn't happen).
        return [0, 0]
    return [best[0], best[1]]