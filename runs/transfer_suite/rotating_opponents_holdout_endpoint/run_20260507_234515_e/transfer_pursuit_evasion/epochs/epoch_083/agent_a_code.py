def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("pursue" in role)
    score_sign = 1 if pursuer else -1  # pursuer wants far if opponent is evader; otherwise wants close

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in rset:
            continue
        v = score_sign * cheb(nx, ny, ox, oy)
        if best_val is None or v > best_val or (v == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = v
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]