def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if is_evader else max(corners, key=lambda c: - (abs(c[0] - ox) + abs(c[1] - oy)))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dist_to_opp = cheb(nx, ny, ox, oy)
        dist_to_corner = abs(nx - cx) + abs(ny - cy)
        # Evader: maximize distance from opponent and stay biased toward a corner.
        # Pursuer: minimize distance to opponent while still heading toward that corner bias.
        score = (dist_to_opp * (10 if is_evader else -10)) + ((dist_to_corner if is_evader else -dist_to_corner) * 1.5)
        if best is None or score > best_score + 1e-12:
            best = [dx, dy]
            best_score = score
        elif best is not None and abs(score - best_score) <= 1e-12:
            # Deterministic tie-break: prefer fewer moves (toward staying), then smallest dx, then smallest dy.
            def tie_key(m):
                return (abs(m[0]) + abs(m[1]), m[0], m[1])
            if tie_key([dx, dy]) < tie_key(best):
                best = [dx, dy]
                best_score = score

    if best is None:
        return [0, 0]
    return best