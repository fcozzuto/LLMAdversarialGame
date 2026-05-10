def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in self_role) or (("evader" in opp_role) and ("pursuer" not in self_role))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]
    prefer = [(1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    for dx, dy in prefer:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # Simple obstacle proximity penalty (prefer moves away from tight obstacle neighborhoods)
        near_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            tx, ty = nx + adx, ny + ady
            if (tx, ty) in obstacles:
                near_obs += 1
        # Also slight preference for moving toward center to avoid corner traps
        cx, cy = (w - 1) * 0.5, (h - 1) * 0.5
        center = cheb(nx, ny, int(cx), int(cy))

        if pursuer:
            # Minimize distance; break ties by higher obstacle clearance and slightly toward center
            score = (-d * 10.0) + (near_obs * 0.4) - (center * 0.03)
        else:
            # Maximize distance; break ties by higher obstacle clearance and toward center (better escape options)
            score = (d * 10.0) + (near_obs * 0.4) - (center * 0.03)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move