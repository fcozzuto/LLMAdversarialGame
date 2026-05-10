def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist2(x, y, a=ox, b=oy):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Wall-running heuristic: stick to boundary by targeting a corner that best matches objective
    if evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        # Boundary bias: move toward target corner and toward/along walls
        corner_bias = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))  # closer is better
        wall_bias = (0 if nx not in (0, w - 1) and ny not in (0, h - 1) else 1)
        # Obstacle proximity penalty (light)
        prox = 0
        for oxp, oyp in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ax, ay = nx + oxp, ny + oyp
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs_set:
                prox -= 1

        val = (d * (-1 if not evader else 1)) + corner_bias * 0.05 + wall_bias * 0.5 + prox * 0.2
        # Deterministic tie-break: fixed order already; only strict improvements
        if best_val is None or (val > best_val if evader else val < best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best