def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    old_d = cheb(sx, sy)

    best_score = None
    best_move = (0, 0)

    # Deterministic tie-break: prefer lower dx, then lower dy (fixed iteration order)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        new_d = cheb(nx, ny)
        dist_gain = old_d - new_d  # positive if moving closer in cheb distance

        # For pursuer: maximize gain; for evader: minimize gain (maximize distance)
        primary = dist_gain if self_is_pursuer else -dist_gain

        # Secondary: keep pressure toward center (for pursuer) or away from center (for evader),
        # helping with zigzag evasion by reducing edge hugging.
        to_center = abs(nx - cx) + abs(ny - cy)
        secondary = -to_center if self_is_pursuer else to_center

        # Small deterministic penalty for staying still to prevent dithering (but allow if best).
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        score = primary * 10.0 + secondary * 0.1 - stay_pen * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]