def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Minimax: choose our move that minimizes our distance to opponent after opponent best evasive reply.
    best = None
    best_val = None
    # Deterministic tie-break order: keep moves list order.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            nx, ny = sx, sy

        # If we can capture immediately, do it.
        if nx == ox and ny == oy:
            return [dxm, dym]

        worst_for_us = -1.0
        for dxe, dye in moves:
            ex, ey = ox + dxe, oy + dye
            if not ok(ex, ey):
                ex, ey = ox, oy
            if nx == ex and ny == ey:
                # opponent could be captured next; treat as very bad for them (good for us)
                val = -1e18
            else:
                val = dist(nx, ny, ex, ey)
            # opponent maximizes distance; we minimize that maximum
            if val > worst_for_us:
                worst_for_us = val

        # Secondary goal: prefer moves that also reduce current distance if equal under minimax.
        current_d = dist(sx, sy, ox, oy)
        next_d = dist(nx, ny, ox, oy)
        score = (worst_for_us, next_d)
        if best is None or score < best_val:
            best_val = score
            best = [dxm, dym]

    # Fallback (should never be None)
    if best is None:
        return [0, 0]
    return best