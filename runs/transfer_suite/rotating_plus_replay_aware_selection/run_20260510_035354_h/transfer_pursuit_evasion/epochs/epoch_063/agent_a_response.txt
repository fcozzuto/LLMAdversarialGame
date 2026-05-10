def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in role)

    t = int(observation.get("turn_index", 0) or 0)
    parity = t & 1

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def score_cell(x, y, dx, dy):
        if (x, y) in obs:
            return 10**12
        d = dist2(x, y)
        # Tie-breakers: keep deterministic and avoid aimless drifting
        # Prefer diagonal only when it improves distance; otherwise favor straight.
        diag_pen = 3 if (dx != 0 and dy != 0) else 0
        center_bias = (3 - (abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2))) * 0.01
        parity_bias = (0.02 if ((x + y + parity) & 1) else 0.0)
        if evader:
            # maximize distance
            return -d + diag_pen * 0.1 - center_bias - parity_bias
        else:
            # minimize distance
            return d + diag_pen * 0.1 - center_bias + parity_bias

    best_delta = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny, dx, dy)
        if best_score is None or sc < best_score:
            best_score = sc
            best_delta = [dx, dy]

    return best_delta