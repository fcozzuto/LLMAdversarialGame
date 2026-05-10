def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # "Evasion corner": farthest from us (typical corner-seeking evasion)
    tgt_corner = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))

    best = None
    best_val = -10**18 if pursuer else 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_tgt = cheb(nx, ny, tgt_corner[0], tgt_corner[1])
        # Deterministic weighting: pursuer blends chase + corner interception; evader blends escape + corner pursuit
        val = (-d_opp * 6 - d_tgt * 2) if pursuer else (d_opp * 6 - d_tgt * 2)
        # Slight tie-break toward diagonal/forward by ordering via stable arithmetic
        val += (dx + 1) * 0.0001 + (dy + 1) * 0.00001
        if (pursuer and val > best_val) or ((not pursuer) and val < best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best