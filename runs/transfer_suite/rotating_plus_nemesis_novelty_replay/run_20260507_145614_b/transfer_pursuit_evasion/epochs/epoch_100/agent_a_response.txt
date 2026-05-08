def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in self_role) or ("catcher" in self_role) or ("evader" in opp_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Target corner that evader would like most: closest corner to opponent.
    tcorner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        d_to_opp = dist2(nx, ny, ox, oy)
        # Obstacle proximity penalty (discourages hugging obstacles).
        min_obst = 10**9
        for ex, ey in obst:
            dd = abs(nx - ex) + abs(ny - ey)
            if dd < min_obst:
                min_obst = dd
        obst_pen = 0.0 if min_obst >= 2 else (2 - min_obst) * 2.0

        if pursuer:
            # Cut off: prefer reducing distance and approaching target corner line.
            d_corner = dist2(nx, ny, tcorner[0], tcorner[1])
            d_corner_opp = dist2(ox, oy, tcorner[0], tcorner[1])
            # If opponent already near corner, prioritize direct chase; otherwise intercept towards corner.
            intercept_bias = 1.6 if d_corner_opp <= 10 else 1.1
            val = (-d_to_opp) + intercept_bias * (-(d_corner)) - obst_pen
            # Additionally, discourage moving away from opponent.
        else:
            # Evader: maximize distance to opponent, and bias toward staying closer to target corner.
            d_opp = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, tcorner[0], tcorner[1])
            # Prefer moving toward corner while moving away from pursuer.
            val = d_opp - 0.35 * d_corner - obst_pen

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best)):
            best_val = val
            best = [dx, dy]

    # If all moves blocked, stay.
    return best if best in ([-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, 1]) else [0, 0]