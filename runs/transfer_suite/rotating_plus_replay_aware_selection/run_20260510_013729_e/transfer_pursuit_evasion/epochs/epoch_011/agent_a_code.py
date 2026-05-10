def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    ob = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ob.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in ob

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if self_is_evader:
        # Prefer corner farthest from opponent, but still maximize distance each move.
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        # Pursuer: prefer corner closest to opponent to tighten space (minor secondary).
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = sx, sy
        d_op = abs(nx - ox) + abs(ny - oy)
        d_t = abs(nx - tx) + abs(ny - ty)
        d_me_t = abs(sx - tx) + abs(sy - ty)
        # Avoid freezing on obstacle edges: reward improvement slightly.
        d_improve = d_me_t - d_t

        if self_is_evader:
            score = (d_op * 1000) + (d_improve * 10) - (abs(dx) + abs(dy)) * 0.01
        else:
            score = (-d_op * 1000) + (d_improve * 10) - (abs(dx) + abs(dy)) * 0.01

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]